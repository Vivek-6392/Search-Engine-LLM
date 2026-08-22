from __future__ import annotations

import logging
import os
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Langfuse client once at module load time.
# In Langfuse v4 (OTel-based), you MUST call Langfuse() to register the client
# before using CallbackHandler — otherwise it logs "No client initialized" and skips tracing.
_langfuse_initialized = False

def _ensure_langfuse_initialized() -> bool:
    """Initialize the Langfuse v4 client singleton if credentials are available."""
    global _langfuse_initialized
    if _langfuse_initialized:
        return True

    if not (settings.LANGFUSE_SECRET_KEY and settings.LANGFUSE_PUBLIC_KEY):
        return False

    try:
        # v4 reads credentials from env vars via OpenTelemetry exporter
        os.environ["LANGFUSE_SECRET_KEY"] = settings.LANGFUSE_SECRET_KEY
        os.environ["LANGFUSE_PUBLIC_KEY"] = settings.LANGFUSE_PUBLIC_KEY
        if settings.LANGFUSE_HOST:
            os.environ["LANGFUSE_HOST"] = settings.LANGFUSE_HOST

        from langfuse import Langfuse  # type: ignore[import]

        # Initialize the global Langfuse client — this registers it for CallbackHandler
        Langfuse(
            secret_key=settings.LANGFUSE_SECRET_KEY,
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            host=settings.LANGFUSE_HOST,
        )
        _langfuse_initialized = True
        logger.info("Langfuse client initialized (host=%s)", settings.LANGFUSE_HOST)
        return True

    except Exception as e:
        logger.warning("Langfuse initialization failed: %s", e)
        return False


def get_langfuse_handler(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
):
    """Return a Langfuse v4 LangchainCallbackHandler if credentials are configured.

    Pass the returned handler in the LangGraph/LangChain ``config`` dict::

        handler = get_langfuse_handler(user_id=..., session_id=...)
        config = {"callbacks": [handler]} if handler else {}
        graph.invoke(state, config=config)
    """
    if not _ensure_langfuse_initialized():
        return None

    try:
        from langfuse.langchain import CallbackHandler  # type: ignore[import]

        return CallbackHandler(public_key=settings.LANGFUSE_PUBLIC_KEY)

    except Exception as e:
        logger.warning("Failed to create Langfuse CallbackHandler: %s", e)
        return None
