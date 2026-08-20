from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from typing import List

def get_bm25_retriever(documents: List[Document]) -> BM25Retriever:
    """
    Creates a BM25 retriever from a list of documents.
    In a real production environment with millions of documents, BM25 should be 
    backed by Elasticsearch or a similar inverted index engine. 
    For this implementation, we use LangChain's in-memory BM25 for simplicity, 
    but it could be swapped out for a persistent store like Elasticsearch.
    """
    if not documents:
        return None
    
    retriever = BM25Retriever.from_documents(documents)
    # Don't restrict k too heavily here since it's part of hybrid search
    retriever.k = 10 
    return retriever
