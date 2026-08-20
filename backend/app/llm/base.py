from abc import ABC, abstractmethod
from langchain_core.language_models.chat_models import BaseChatModel

class LLMProvider(ABC):
    @abstractmethod
    def get_model(self, model_name: str, streaming: bool = False, temperature: float = 0.0) -> BaseChatModel:
        """Returns a configured LangChain ChatModel instance."""
        pass
