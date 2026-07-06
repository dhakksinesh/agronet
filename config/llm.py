from crewai import LLM
from . import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL

def get_llm(model: str = None, temperature: float = 0.1) -> LLM:
    model_name = model or OPENROUTER_MODEL
    if "/" in model_name and not model_name.startswith(("openrouter/", "hosted_vllm/")):
        model_name = f"hosted_vllm/{model_name}"
    return LLM(
        model=model_name,
        temperature=temperature,
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
    )