from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel
from app.llm.base import LLMProvider
from app.config import settings

class GroqProvider(LLMProvider):
    def get_model(self, model_name: str, streaming: bool = False, temperature: float = 0.0) -> BaseChatModel:
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set")
        return ChatGroq(
            model=model_name,
            api_key=settings.GROQ_API_KEY,
            streaming=streaming,
            temperature=temperature
        )
