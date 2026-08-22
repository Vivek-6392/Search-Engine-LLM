from __future__ import annotations

from typing import Optional

from app.config import settings


def get_langfuse_handler(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
):
    """Return a Langfuse v4 LangchainCallbackHandler if credentials are configured.

    In Langfuse v4, credentials (secret key, host) are read from environment
    variables LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_HOST
    automatically via OpenTelemetry. The CallbackHandler only accepts
    ``public_key`` and an optional ``trace_context``.

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
        import os
        # Langfuse v4 reads credentials from env vars via OpenTelemetry.
        # Ensure they are set for the current process.
        os.environ.setdefault("LANGFUSE_SECRET_KEY", settings.LANGFUSE_SECRET_KEY)
        os.environ.setdefault("LANGFUSE_PUBLIC_KEY", settings.LANGFUSE_PUBLIC_KEY)
        if settings.LANGFUSE_HOST:
            os.environ.setdefault("LANGFUSE_HOST", settings.LANGFUSE_HOST)

        from langfuse.langchain import CallbackHandler  # type: ignore[import]

        # v4 CallbackHandler signature: (*, public_key=None, trace_context=None)
        # user_id / session_id are set as OTel resource attributes on the Langfuse
        # client level, not on the handler. The handler itself is lightweight.
        handler = CallbackHandler(public_key=settings.LANGFUSE_PUBLIC_KEY)
        return handler

    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Langfuse handler init failed: %s", e)
        return None
