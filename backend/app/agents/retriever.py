from app.graph.state import ResearchState
from app.retrieval.vector_store import get_vector_store
from app.retrieval.reranker import rerank_documents
import logging

logger = logging.getLogger(__name__)

def document_research(state: ResearchState) -> ResearchState:
    """Retrieves evidence from user documents using vector search and reranking."""
    query = state.get("rewritten_query") or state["query"]
    user_id = state.get("user_id")
    
    if not user_id:
        logger.warning("No user_id provided for document research")
        return {"evidence": []}
        
    try:
        vector_store = get_vector_store("deepsearch_documents")
        
        # In a real scenario, use hybrid search. Here we use vector search as a baseline
        from qdrant_client.http import models

        # filter by user_id to ensure privacy
        filter_obj = models.Filter(
            must=[
                models.FieldCondition(
                    key="metadata.user_id",
                    match=models.MatchValue(value=user_id)
                )
            ]
        )
        
        # K=10 for initial retrieval
        docs = vector_store.similarity_search(query, k=10, filter=filter_obj)
        
        raw_evidence = []
        for doc in docs:
            raw_evidence.append({
                "id": doc.metadata.get("chunk_id", ""),
                "content": doc.page_content,
                "source": doc.metadata.get("source", "document"),
                "title": doc.metadata.get("title", ""),
                "url": None,
                "page": doc.metadata.get("page", 1),
                "source_type": "document"
            })
            
        # Rerank to top 5
        reranked = rerank_documents(query, raw_evidence, top_k=5)
        
        return {"evidence": reranked}
        
    except Exception as e:
        logger.error(f"Document research error: {e}")
        return {"evidence": []}
