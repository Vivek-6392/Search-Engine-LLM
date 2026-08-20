from langchain_core.language_models.chat_models import BaseChatModel
from app.config import settings
from app.llm.openai import OpenAIProvider
from app.llm.groq import GroqProvider
from app.llm.ollama import OllamaProvider

def get_llm(streaming: bool = False, temperature: float = 0.0) -> BaseChatModel:
    provider_name = settings.LLM_PROVIDER.lower()
    
    if provider_name == "openai":
        provider = OpenAIProvider()
    elif provider_name == "groq":
        provider = GroqProvider()
    elif provider_name == "ollama":
        provider = OllamaProvider()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")
        
    return provider.get_model(settings.MODEL_NAME, streaming=streaming, temperature=temperature)
