from typing import List, Dict, Any
from sentence_transformers import CrossEncoder

# Singleton for cross-encoder
_reranker = None

def get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512, device='cpu')
    return _reranker

def rerank_documents(query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Reranks a list of documents based on cross-encoder similarity with the query.
    Assumes each document dict has a 'content' field.
    """
    if not documents:
        return []
    
    reranker = get_reranker()
    pairs = [[query, doc.get("content", "")] for doc in documents]
    scores = reranker.predict(pairs)
    
    # Attach scores and sort
    for doc, score in zip(documents, scores):
        doc["relevance_score"] = float(score)
        
    documents.sort(key=lambda x: x["relevance_score"], reverse=True)
    return documents[:top_k]
