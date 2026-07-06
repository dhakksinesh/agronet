from typing import List
from utils import logger
from config import PINECONE_API_KEY
from crewai.tools.base_tool import tool

@tool("Get eligible government schemes for a crop and state")
def get_eligible_schemes(crop: str, state: str) -> List[dict]:
    """Retrieve government schemes from RAG for the given crop and state."""
    try:
        logger.debug(f"Fetching schemes for {state}, {crop} from RAG")
        if not PINECONE_API_KEY:
            logger.error("PINECONE_API_KEY not configured - cannot fetch schemes from RAG")
            raise ConnectionError("Government schemes require RAG access. Configure PINECONE_API_KEY and add PDF documents to data/ folder.")
        from rag.retriever import retrieve_knowledge
        query = f"government schemes {crop} {state} India farmer subsidies"
        result = retrieve_knowledge.run(query)
        if "not available" in result.lower() or "no relevant" in result.lower():
            logger.error("RAG knowledge base unavailable")
            raise ConnectionError("Government schemes knowledge base not available. Add PDF documents to data/ folder and ensure Pinecone is configured.")
        schemes = _parse_schemes_from_rag(result, crop, state)
        if not schemes:
            logger.error("No schemes found in RAG knowledge base")
            raise ConnectionError("No government schemes found in knowledge base. Add relevant PDF documents to data/ folder.")
        logger.debug(f"Found {len(schemes)} schemes for {state}, {crop}")
        return schemes
    except ConnectionError:
        raise
    except Exception as e:
        logger.error(f"Error getting eligible schemes: {e}")
        raise ConnectionError(f"Failed to fetch government schemes: {str(e)}")

def _parse_schemes_from_rag(rag_result: str, crop: str, state: str) -> List[dict]:
    schemes = []
    scheme_keywords = [
        "PM-KISAN", "Pradhan Mantri Kisan", "Kisan Samman Nidhi",
        "PMFBY", "Pradhan Mantri Fasal Bima", "Crop Insurance",
        "KVY", "Krishi Vikas Yojana",
        "NHM", "National Horticulture Mission",
        "RKVY", "Rashtriya Krishi Vikas"
    ]
    for line in rag_result.split('\n'):
        line_lower = line.lower()
        for keyword in scheme_keywords:
            if keyword.lower() in line_lower and ("scheme" in line_lower or len(line) > 50):
                schemes.append({
                    "name": keyword,
                    "description": line.strip(),
                    "scheme_key": keyword.replace(" ", "_").upper(),
                    "eligibility": "Government scheme"
                })
    return schemes
