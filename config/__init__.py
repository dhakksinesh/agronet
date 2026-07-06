import os
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "agronet")
PINECONE_EMBEDDING_MODEL = os.getenv("PINECONE_EMBEDDING_MODEL", "llama-text-embed-v2")
try:
    PINECONE_EMBEDDING_DIM = int(os.getenv("PINECONE_EMBEDDING_DIM", "1024"))
except ValueError:
    PINECONE_EMBEDDING_DIM = 1024
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b")
WEATHER_API_BASE = os.getenv("WEATHER_API_BASE", "https://api.open-meteo.com/v1/forecast")

def validate_api_keys():
    issues = []

    if not PINECONE_API_KEY:
        issues.append("PINECONE_API_KEY is missing")

    if not OPENROUTER_API_KEY:
        issues.append("OPENROUTER_API_KEY is missing")

    return issues

from database import get_states as _get_states, get_districts as _get_districts, get_soil_types as _get_soil_types

def get_states() -> list:
    return _get_states()

def get_districts(state: str) -> list:
    return _get_districts(state)

def get_soil_types() -> list:
    return _get_soil_types()

from .llm import get_llm

__all__ = [
    "PINECONE_API_KEY",
    "PINECONE_INDEX_NAME",
    "PINECONE_EMBEDDING_MODEL",
    "PINECONE_EMBEDDING_DIM",
    "OPENROUTER_API_KEY",
    "OPENROUTER_BASE_URL",
    "OPENROUTER_MODEL",
    "WEATHER_API_BASE",
    "get_states",
    "get_districts",
    "get_soil_types",
    "validate_api_keys",
    "get_llm",
]