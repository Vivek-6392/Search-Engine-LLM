from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore as Qdrant
from app.retrieval.embeddings import get_embeddings
from app.config import settings

def get_qdrant_client() -> QdrantClient:
    return QdrantClient(host="qdrant", port=6333)

def get_vector_store(collection_name: str) -> Qdrant:
    client = get_qdrant_client()
    embeddings = get_embeddings()
    
    # Ensure collection exists before initializing the vector store wrapper
    try:
        collections = client.get_collections().collections
        if not any(c.name == collection_name for c in collections):
            from qdrant_client.http.models import Distance, VectorParams
            # Create collection with default vector size for all-MiniLM-L6-v2 (384)
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Error checking/creating collection: {e}")
        
    return Qdrant(
        client=client,
        collection_name=collection_name,
        embedding=embeddings
    )
