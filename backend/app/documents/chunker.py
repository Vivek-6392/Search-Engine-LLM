from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid

def chunk_documents(documents: List[Document], document_id: str) -> List[Document]:
    """Splits documents into smaller chunks and adds required metadata."""
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks = text_splitter.split_documents(documents)
    
    # Add unique chunk_id and document_id metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata["document_id"] = document_id
        chunk.metadata["chunk_id"] = str(uuid.uuid4())
        # Ensure page exists
        if "page" not in chunk.metadata:
            chunk.metadata["page"] = 1
            
    return chunks
