from typing import List, BinaryIO
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
import tempfile
import os

def load_pdf(file_stream: BinaryIO, filename: str) -> List[Document]:
    """Loads a PDF from a stream, saves it to a temp file, and extracts Documents."""
    docs = []
    
    # PyPDFLoader needs a file path, so we use a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(file_stream.read())
        temp_pdf_path = temp_pdf.name
        
    try:
        loader = PyPDFLoader(temp_pdf_path)
        docs = loader.load()
        # Clean up metadata
        for doc in docs:
            doc.metadata["source"] = filename
            doc.metadata["title"] = filename
    finally:
        os.unlink(temp_pdf_path)
        
    return docs

def load_text(file_stream: BinaryIO, filename: str) -> List[Document]:
    """Loads a text file from a stream."""
    content = file_stream.read().decode("utf-8")
    return [Document(page_content=content, metadata={"source": filename, "title": filename, "page": 1})]
