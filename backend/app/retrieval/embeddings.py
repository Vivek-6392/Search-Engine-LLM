from langchain_huggingface import HuggingFaceEmbeddings
from app.config import settings

# Singleton for embeddings to avoid reloading the model
_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        # Using a strong, open-source embedding model (BGE)
        _embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True},
            # Pass HF token to avoid rate limit warnings on download
            huggingface_hub_kwargs={"token": settings.HF_TOKEN} if settings.HF_TOKEN else {},
        )
    return _embeddings
