from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from app.llm.base import LLMProvider
from app.config import settings

class OpenAIProvider(LLMProvider):
    def get_model(self, model_name: str, streaming: bool = False, temperature: float = 0.0) -> BaseChatModel:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set")
        return ChatOpenAI(
            model=model_name,
            api_key=settings.OPENAI_API_KEY,
            streaming=streaming,
            temperature=temperature
        )
