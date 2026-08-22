from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.database.session import get_db
from app.database.models import User, Conversation, Message
from app.api.auth import get_current_user
from app.graph.workflow import build_graph
from app.graph.state import ResearchState
from app.observability import get_langfuse_handler

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])
graph = build_graph()

class ChatRequest(BaseModel):
    query: str
    conversation_id: str = None
    stream: bool = True

@router.post("")
async def chat(request: ChatRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # 1. Create conversation if not exists
    if not request.conversation_id:
        title = " ".join(request.query.split()[:5])
        if len(title) > 0: title += "..."
        conv = Conversation(user_id=current_user.id, title=title or "New Conversation")
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        request.conversation_id = str(conv.id)
    
    # 2. Save User Message
    user_msg = Message(conversation_id=request.conversation_id, role="user", content=request.query)
    db.add(user_msg)
    await db.commit()

    state: ResearchState = {
        "query": request.query,
        "user_id": str(current_user.id),
        "conversation_id": request.conversation_id,
        "evidence": [],
        "search_results": [],
        "retrieved_chunks": [],
        "retry_count": 0,
    }

    # Build LangGraph run config — attaches Langfuse tracing when keys are set
    langfuse_handler = get_langfuse_handler(
        user_id=str(current_user.id),
        session_id=request.conversation_id,
    )
    run_config = {"callbacks": [langfuse_handler]} if langfuse_handler else {}

    if request.stream:
        async def event_generator():
            try:
                # Yield conversation id so frontend can update URL / Active Conv
                yield f"data: {json.dumps({'event': 'conversation_created', 'conversation_id': request.conversation_id})}\n\n"
                
                final_answer = ""
                # We use stream instead of astream for simplicity in this implementation,
                # but in production astream with async agents is preferred.
                for s in graph.stream(state, config=run_config):
                    # Each yield from graph.stream is a dictionary with the node name as key and the state update as value
                    for node_name, state_update in s.items():
                        yield f"data: {json.dumps({'event': 'node_update', 'node': node_name})}\n\n"
                        
                        if node_name == "synthesize" and "final_answer" in state_update:
                            final_answer = state_update['final_answer']
                            yield f"data: {json.dumps({'event': 'final_answer', 'content': final_answer})}\n\n"
                            
                        if node_name == "critic" and "critique" in state_update:
                            yield f"data: {json.dumps({'event': 'critique', 'content': state_update['critique']})}\n\n"
                
                # 3. Save Assistant Message
                if final_answer:
                    ast_msg = Message(conversation_id=request.conversation_id, role="assistant", content=final_answer)
                    db.add(ast_msg)
                    await db.commit()
                
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'event': 'error', 'content': str(e)})}\n\n"
                
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    else:
        # Non-streaming
        result = graph.invoke(state, config=run_config)
        return {
            "answer": result.get("final_answer"),
            "citations": result.get("citations"),
            "intent": result.get("intent")
        }
