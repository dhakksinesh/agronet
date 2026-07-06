import json
import re
import uuid
import requests
from pathlib import Path
from typing import Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.embeddings import BaseEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.node_parser import SentenceSplitter
import pinecone
from config import (
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    PINECONE_EMBEDDING_MODEL,
    PINECONE_EMBEDDING_DIM
)
from crewai.tools.base_tool import tool
from utils import logger

_rag_index = None
_index_initialized = False
_ingestion_done = False
_bm25 = None
_bm25_docs = []

PINECONE_EMBED_URL = "https://api.pinecone.io/embed"
PINECONE_API_VERSION = "2026-04"
RAG_DATA_DIR = Path(__file__).parent.parent / "data"
CHUNKS_FILE = RAG_DATA_DIR / "_chunks.json"
HASHES_FILE = RAG_DATA_DIR / "_file_hashes.json"
RRF_K = 60
HYBRID_TOP_K = 5

try:
    from rank_bm25 import BM25Okapi
    _BM25_AVAILABLE = True
except ImportError:
    _BM25_AVAILABLE = False
    logger.warning("rank_bm25 not installed — hybrid search disabled, falling back to pure vector")

def _tokenize(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())

def _load_bm25():
    global _bm25, _bm25_docs
    if not _BM25_AVAILABLE:
        return
    if not CHUNKS_FILE.exists():
        logger.warning(f"No chunks file at {CHUNKS_FILE}, BM25 unavailable")
        return
    try:
        with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
            _bm25_docs = json.load(f)
        tokenized = [_tokenize(d) for d in _bm25_docs]
        _bm25 = BM25Okapi(tokenized)
        logger.info(f"BM25 index built with {len(_bm25_docs)} documents")
    except Exception as e:
        logger.error(f"Failed to load BM25 index: {e}")
        _bm25 = None

import hashlib

def _compute_file_hashes(data_path: str) -> dict:
    hashes = {}
    for pdf in sorted(Path(data_path).glob("*.pdf")):
        h = hashlib.sha256()
        h.update(pdf.read_bytes())
        hashes[pdf.name] = h.hexdigest()
    return hashes

def _load_file_hashes() -> dict:
    if HASHES_FILE.exists():
        try:
            with open(HASHES_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save_file_hashes(hashes: dict):
    RAG_DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(HASHES_FILE, "w") as f:
        json.dump(hashes, f, indent=2)

def _rrf_fuse(vector_results: list, bm25_results: list, k: int = RRF_K) -> List[str]:
    scores = {}
    for rank_minus_1, text in enumerate(vector_results):
        scores[text] = scores.get(text, 0) + 1 / (k + rank_minus_1 + 1)
    for rank_minus_1, text in enumerate(bm25_results):
        scores[text] = scores.get(text, 0) + 1 / (k + rank_minus_1 + 1)
    ranked = sorted(scores, key=scores.get, reverse=True)
    return ranked[:HYBRID_TOP_K]

def check_and_create_index() -> bool:
    global _index_initialized
    if _index_initialized:
        return True
    if not PINECONE_API_KEY:
        logger.warning("PINECONE_API_KEY not configured")
        return False
    try:
        pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
        existing = pc.list_indexes()
        existing_indexes = [idx.name for idx in existing]
        if PINECONE_INDEX_NAME not in existing_indexes:
            logger.info(f"Creating Pinecone index: {PINECONE_INDEX_NAME}")
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=PINECONE_EMBEDDING_DIM,
                metric="cosine",
                spec=pinecone.ServerlessSpec(cloud="aws", region="us-east-1")
            )
            logger.info(f"Index {PINECONE_INDEX_NAME} created successfully")
        _index_initialized = True
        return True
    except Exception as e:
        logger.error(f"Error checking/creating Pinecone index: {e}")
        return False

def get_index_stats() -> Optional[int]:
    try:
        if not PINECONE_API_KEY:
            return None
        pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
        existing = pc.list_indexes()
        existing_indexes = [idx.name for idx in existing]
        if PINECONE_INDEX_NAME not in existing_indexes:
            return None
        stats = pc.Index(PINECONE_INDEX_NAME).describe_index_stats()
        return stats.total_vector_count
    except Exception as e:
        logger.error(f"Error getting index stats: {e}")
        return None

@tool("Retrieve agricultural knowledge from RAG")
def retrieve_knowledge(query: str) -> str:
    """Query the hybrid RAG (vector + BM25) knowledge base."""
    index = initialize_rag()
    if index is None:
        return "Knowledge base not available. Check Pinecone configuration and ensure documents are ingested."
    try:
        vector_nodes = []
        if index is not None:
            retriever = index.as_retriever(similarity_top_k=10)
            vector_nodes = retriever.retrieve(query)
        vector_texts = [n.text for n in vector_nodes]

        bm25_texts = []
        if _bm25 is not None and _bm25_docs:
            tokenized_q = _tokenize(query)
            bm25_scores = _bm25.get_scores(tokenized_q)
            top_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:10]
            bm25_texts = [_bm25_docs[i] for i in top_indices if bm25_scores[i] > 0]

        if _bm25 is not None and bm25_texts:
            fused = _rrf_fuse(vector_texts, bm25_texts)
            logger.debug(f"Hybrid RRF returned {len(fused)} results for query: [{query[:80]}]")
        else:
            fused = vector_texts[:HYBRID_TOP_K]
            logger.debug(f"Pure vector returned {len(fused)} results for query: [{query[:80]}]")

        if not fused:
            return "No relevant information found in the knowledge base."
        return "\n\n".join(fused)
    except Exception as e:
        logger.error(f"Error retrieving knowledge: {e}")
        return f"Error retrieving knowledge: {str(e)}"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_pinecone_embedding(text: str, task_type: str = "passage") -> List[float]:
    if not PINECONE_API_KEY:
        raise ValueError("PINECONE_API_KEY not configured")
    headers = {
        "Api-Key": PINECONE_API_KEY,
        "Content-Type": "application/json",
        "X-Pinecone-Api-Version": PINECONE_API_VERSION,
    }
    payload = {
        "model": PINECONE_EMBEDDING_MODEL,
        "parameters": {
            "input_type": task_type,
            "truncate": "END",
        },
        "inputs": [{"text": text}],
    }
    if PINECONE_EMBEDDING_DIM != 1024:
        payload["parameters"]["dimension"] = PINECONE_EMBEDDING_DIM
    response = requests.post(PINECONE_EMBED_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()["data"][0]["values"]

class PineconeEmbeddingModel(BaseEmbedding):
    def _get_text_embedding(self, text: str) -> List[float]:
        return get_pinecone_embedding(text, "passage")

    def _get_query_embedding(self, query: str) -> List[float]:
        return get_pinecone_embedding(query, "query")

    def _get_agg_embedding(self, embeddings: List[List[float]]) -> List[float]:
        if not embeddings:
            raise ValueError("No embeddings provided")
        return embeddings[0]

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embedding(text)

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)

def initialize_rag():
    global _rag_index
    if _rag_index is not None:
        return _rag_index
    if not PINECONE_API_KEY:
        logger.warning("PINECONE_API_KEY not configured")
        return None
    try:
        if not check_and_create_index():
            return None
        pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)
        vector_store = PineconeVectorStore(pinecone_index=index)
        embed_model = PineconeEmbeddingModel()
        Settings.embed_model = embed_model
        _rag_index = VectorStoreIndex.from_vector_store(vector_store)
        logger.info("RAG index initialized successfully")
        _load_bm25()
        return _rag_index
    except Exception as e:
        logger.error(f"Error initializing RAG: {e}")
        return None

def ingest_documents(data_path: str = None):
    global _rag_index
    data_path = data_path or str(RAG_DATA_DIR)
    if not PINECONE_API_KEY:
        raise ValueError("PINECONE_API_KEY not configured")
    data_path_obj = Path(data_path)
    if not data_path_obj.exists():
        logger.warning(f"Data path {data_path} does not exist, skipping ingestion")
        return None
    pdf_files = list(data_path_obj.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {data_path}")
        return None
    try:
        logger.info(f"Found {len(pdf_files)} PDF files to ingest")
        if not check_and_create_index():
            logger.error("Failed to create/check Pinecone index")
            return None
        logger.info("Setting up Pinecone vector store...")
        pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)
        logger.info("Loading PDF documents...")
        documents = SimpleDirectoryReader(data_path).load_data()
        logger.info(f"Loaded {len(documents)} page(s)")
        logger.info("Chunking documents...")
        splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
        nodes = splitter.get_nodes_from_documents(documents)
        logger.info(f"Created {len(nodes)} chunks")
        from collections import Counter
        doc_counts = Counter(n.metadata.get("file_name", "unknown") for n in nodes)
        for doc_name, count in doc_counts.most_common():
            logger.info(f"  {doc_name}: {count} chunks")
        BATCH_SIZE = 10
        total = len(nodes)
        all_texts = []
        for i in range(0, total, BATCH_SIZE):
            batch = nodes[i:i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1
            total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
            logger.info(f"Embedding batch {batch_num}/{total_batches} ({len(batch)} chunks)...")
            vectors = []
            for j, node in enumerate(batch):
                embedding = get_pinecone_embedding(node.text, "passage")
                chunk_id = f"{uuid.uuid4().hex[:12]}"
                vectors.append((
                    chunk_id,
                    embedding,
                    {"text": node.text, "file_name": node.metadata.get("file_name", "unknown")}
                ))
                all_texts.append(node.text)
            index.upsert(vectors=vectors)
            logger.info(f"  Batch {batch_num} upserted")
        logger.info(f"Successfully ingested {total} chunks into {PINECONE_INDEX_NAME}")
        RAG_DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
            json.dump(all_texts, f, ensure_ascii=False)
        logger.info(f"Saved {len(all_texts)} chunks for BM25")
        _rag_index = initialize_rag()
        return _rag_index
    except Exception as e:
        logger.error(f"Error ingesting documents: {e}")
        raise

def auto_ingest_if_needed(data_path: str = None):
    global _ingestion_done
    data_path = data_path or str(RAG_DATA_DIR)
    if _ingestion_done:
        return initialize_rag()
    data_path_obj = Path(data_path)
    if not data_path_obj.exists():
        logger.warning(f"Data path {data_path} does not exist, skipping ingestion")
        return None
    current_hashes = _compute_file_hashes(data_path)
    if not current_hashes:
        logger.warning(f"No PDF files found in {data_path}")
        return None
    stored_hashes = _load_file_hashes()
    if current_hashes == stored_hashes:
        logger.info("All PDFs unchanged — loading existing index")
        _ingestion_done = True
        result = initialize_rag()
        return result
    logger.info("PDF changes detected — re-ingesting documents")
    result = ingest_documents(data_path)
    if result is not None:
        _save_file_hashes(current_hashes)
    _ingestion_done = True
    return result

__all__ = [
    "retrieve_knowledge",
    "ingest_documents",
    "initialize_rag",
    "check_and_create_index",
    "auto_ingest_if_needed",
    "get_pinecone_embedding",
    "PineconeEmbeddingModel",
    "get_index_stats",
]
