from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/api/v1/health", tags=["Health"])

@router.get("")
async def health_check():
    return {
        "status": "ok",
        "environment": settings.APP_ENV,
        "llm_provider": settings.LLM_PROVIDER
    }
