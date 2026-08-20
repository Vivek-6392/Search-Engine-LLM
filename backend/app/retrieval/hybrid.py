from typing import List, Dict, Any
from langchain_core.documents import Document
from collections import defaultdict

def reciprocal_rank_fusion(
    bm25_results: List[Document], 
    vector_results: List[Document], 
    k: int = 60
) -> List[Dict[str, Any]]:
    """
    Combines results from BM25 and Vector Search using Reciprocal Rank Fusion (RRF).
    """
    # Create a mapping of document ID or content to score
    rrf_scores = defaultdict(float)
    docs_map = {}
    
    # Process BM25
    for rank, doc in enumerate(bm25_results, start=1):
        # We need a unique identifier. If doc doesn't have an ID, use content hash or text
        doc_id = doc.metadata.get("chunk_id", str(hash(doc.page_content)))
        rrf_scores[doc_id] += 1.0 / (k + rank)
        docs_map[doc_id] = doc
        
    # Process Vector Results
    for rank, doc in enumerate(vector_results, start=1):
        doc_id = doc.metadata.get("chunk_id", str(hash(doc.page_content)))
        rrf_scores[doc_id] += 1.0 / (k + rank)
        docs_map[doc_id] = doc
        
    # Sort by RRF score
    sorted_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Convert back to Dict format expected by reranker and final output
    fused_docs = []
    for doc_id, score in sorted_items:
        doc = docs_map[doc_id]
        fused_docs.append({
            "id": doc_id,
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "title": doc.metadata.get("title", ""),
            "url": doc.metadata.get("url"),
            "page": doc.metadata.get("page"),
            "rrf_score": score,
            "source_type": "document"
        })
        
    return fused_docs
