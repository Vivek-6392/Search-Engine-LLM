from __future__ import annotations

from typing import Optional

from app.config import settings


def get_langfuse_handler(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
):
    """Return a Langfuse LangChain CallbackHandler if credentials are configured.

    Pass the returned handler in the LangGraph/LangChain ``config`` dict::

        handler = get_langfuse_handler(user_id=..., session_id=...)
        config = {"callbacks": [handler]} if handler else {}
        graph.invoke(state, config=config)

    Returns ``None`` when Langfuse keys are missing so callers can skip
    tracing without crashing.
    """
    if not (settings.LANGFUSE_SECRET_KEY and settings.LANGFUSE_PUBLIC_KEY):
        return None

    try:
        from langfuse.callback import CallbackHandler  # type: ignore[import]

        return CallbackHandler(
            secret_key=settings.LANGFUSE_SECRET_KEY,
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            host=settings.LANGFUSE_HOST,
            user_id=user_id,
            session_id=session_id,
        )
    except Exception:
        # Langfuse not installed or misconfigured — degrade gracefully
        return None
