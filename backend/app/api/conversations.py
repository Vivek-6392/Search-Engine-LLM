from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database.session import get_db
from app.database.models import User, Conversation, Message
from app.api.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/conversations", tags=["Conversations"])

class ConversationCreate(BaseModel):
    title: str = "New Conversation"

@router.post("")
async def create_conversation(data: ConversationCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    conv = Conversation(user_id=current_user.id, title=data.title)
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return {"id": str(conv.id), "title": conv.title, "created_at": conv.created_at}

@router.get("")
async def get_conversations(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Conversation).where(Conversation.user_id == current_user.id).order_by(Conversation.updated_at.desc()))
    conversations = result.scalars().all()
    return [{"id": str(c.id), "title": c.title, "updated_at": c.updated_at} for c in conversations]

@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == conversation_id)
        .where(Conversation.user_id == current_user.id)
    )
    conv = result.scalars().first()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    messages = [{"id": str(m.id), "role": m.role, "content": m.content, "metadata": m.metadata_, "created_at": m.created_at} for m in conv.messages]
    
    return {
        "id": str(conv.id),
        "title": conv.title,
        "messages": messages
    }

@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id).where(Conversation.user_id == current_user.id))
    conv = result.scalars().first()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    await db.delete(conv)
    await db.commit()
    
    return {"message": "Conversation deleted"}
