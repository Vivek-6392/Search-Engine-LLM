from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid

from app.database.session import get_db
from app.database.models import User, Document
from app.api.auth import get_current_user
from app.documents.ingestion import ingest_document

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

def background_ingest(file_content: bytes, filename: str, doc_id: str, user_id: str):
    """Wrapper for background execution of ingestion."""
    from io import BytesIO
    try:
        stream = BytesIO(file_content)
        # Note: synchronous ingest function called in background task
        # In a real app this should be async or submitted to a Celery queue
        ingest_document(stream, filename, doc_id, user_id)
        
        # We would typically update document status in DB to "indexed" here, 
        # requiring a separate DB session since it's background
    except Exception as e:
        print(f"Ingestion failed: {e}")
        # Update status to failed

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.endswith((".pdf", ".txt", ".csv")):
        raise HTTPException(status_code=400, detail="Unsupported file format")
        
    doc = Document(user_id=current_user.id, filename=file.filename, status="processing")
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    
    # Read file content before passing to background task
    content = await file.read()
    
    # Queue ingestion
    background_tasks.add_task(background_ingest, content, file.filename, str(doc.id), str(current_user.id))
    
    return {"message": "Document upload started", "document_id": str(doc.id)}

@router.get("")
async def get_documents(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.user_id == current_user.id))
    documents = result.scalars().all()
    return [{"id": str(d.id), "filename": d.filename, "status": d.status, "created_at": d.created_at} for d in documents]

@router.delete("/{document_id}")
async def delete_document(document_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == document_id).where(Document.user_id == current_user.id))
    doc = result.scalars().first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    await db.delete(doc)
    await db.commit()
    
    # Also need to delete from vector store in a full implementation
    
    return {"message": "Document deleted"}
