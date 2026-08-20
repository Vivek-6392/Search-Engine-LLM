---
title: DeepSearch AI Backend
emoji: 🔍
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# DeepSearch AI — Backend API

This is the FastAPI backend for **DeepSearch AI**, a production-grade multi-agent research and knowledge engine built with LangGraph.

## API Endpoints

- `GET /` — Health check
- `POST /api/v1/auth/register` — Register a new user
- `POST /api/v1/auth/login` — Login and receive JWT token
- `POST /api/v1/chat` — Stream a research query (SSE)
- `GET /api/v1/conversations` — List conversations
- `POST /api/v1/documents/upload` — Upload a document for RAG

## Environment Variables

Set the following secrets in your HF Space **Settings → Variables and secrets**:

| Variable | Description |
|---|---|
| `JWT_SECRET` | A long random secret string |
| `GROQ_API_KEY` | Your Groq API key |
| `TAVILY_API_KEY` | Your Tavily search API key |
| `DATABASE_URL` | PostgreSQL connection string (from Neon.tech) |
| `REDIS_URL` | Redis connection string (from Upstash) |
| `QDRANT_URL` | Qdrant cluster URL |
| `QDRANT_API_KEY` | Qdrant API key |
