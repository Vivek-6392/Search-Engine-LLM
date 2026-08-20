from langchain_ollama import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel
from app.llm.base import LLMProvider
from app.config import settings

class OllamaProvider(LLMProvider):
    def get_model(self, model_name: str, streaming: bool = False, temperature: float = 0.0) -> BaseChatModel:
        return ChatOllama(
            model=model_name,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=temperature,
            # Streaming is supported differently or natively by some versions, 
            # we'll handle standard Langchain integration.
        )
