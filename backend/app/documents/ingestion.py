from typing import BinaryIO
from app.documents.loader import load_pdf, load_text
from app.documents.chunker import chunk_documents
from app.retrieval.vector_store import get_vector_store

def ingest_document(file_stream: BinaryIO, filename: str, document_id: str, user_id: str):
    """
    Complete pipeline for document ingestion.
    In a real production app, this should be executed in a Celery worker.
    """
    
    # 1. Parsing & Loading
    if filename.lower().endswith(".pdf"):
        docs = load_pdf(file_stream, filename)
    else:
        docs = load_text(file_stream, filename)
        
    # 2. Chunking
    chunks = chunk_documents(docs, document_id)
    
    # 3. Embedding and Storing
    if chunks:
        # User-specific collection or tenant routing can be used. 
        # Here we use a single collection and rely on metadata filtering.
        vector_store = get_vector_store("deepsearch_documents")
        
        # Add user_id to all chunks for filtering
        for chunk in chunks:
            chunk.metadata["user_id"] = user_id
            
        vector_store.add_documents(chunks)
        
    return len(chunks)
