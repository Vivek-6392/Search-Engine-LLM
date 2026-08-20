from langchain_huggingface import HuggingFaceEmbeddings

# Singleton for embeddings to avoid reloading the model
_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        # Using a strong, open-source embedding model (BGE)
        _embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={'device': 'cpu'}, # Use 'cuda' if GPU is available
            encode_kwargs={'normalize_embeddings': True}
        )
    return _embeddings
