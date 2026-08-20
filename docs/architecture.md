# DeepSearch AI Architecture

## Overview
DeepSearch AI is a production-grade multi-agent research platform. It leverages LangGraph to orchestrate multiple specialized agents capable of web search, academic research, and document-based retrieval (RAG).

## Core Components

### 1. API Gateway (FastAPI)
The entry point is a FastAPI application that handles routing, authentication (JWT), and rate limiting. It provides both synchronous endpoints (for document management and history) and asynchronous Server-Sent Events (SSE) streaming for real-time agent feedback.

### 2. Multi-Agent System (LangGraph)
We replaced the simple LangChain ReAct agent with a stateful LangGraph workflow.
- **Router Agent**: Classifies query intent (WEB, ACADEMIC, DOCUMENT, RESEARCH).
- **Planner Agent**: For complex queries, breaks the goal into parallel subtasks.
- **Research Agents (Web, Academic, RAG)**: Specialized agents that retrieve evidence.
- **Synthesizer Agent**: Compiles evidence into a coherent answer with citations.
- **Critic Agent**: Verifies the draft answer against retrieved evidence to prevent hallucinations. Triggers a revision loop if unsupported claims are found.

### 3. Retrieval & RAG Pipeline
- **Vector Store**: Qdrant is used for fast, scalable vector search.
- **Embeddings**: BAAI/bge-small-en-v1.5 via HuggingFace for dense vector representation.
- **Hybrid Search**: Combines Dense Vectors and BM25 using Reciprocal Rank Fusion (RRF) to capture both semantic meaning and exact keyword matches.
- **Cross-Encoder Reranker**: Refines the final top-K documents for maximum relevance.

### 4. Database & Memory
- **PostgreSQL**: Stores users, conversations, messages, and document metadata.
- **Redis**: Used for rate limiting, background job queuing, and caching.

### 5. Frontend (Next.js)
A modern, responsive UI built with Next.js, Tailwind CSS, and Lucide React. It consumes the SSE stream to display real-time progress as agents execute their tasks.

## Why these technologies?
- **LangGraph vs. ReAct**: ReAct agents can loop infinitely or get confused on complex tasks. LangGraph provides deterministic state transitions, parallel execution, and explicit human-in-the-loop capabilities.
- **Qdrant**: Chosen for its high performance in Rust, robust API, and ease of deployment via Docker compared to managing pgvector extensions in some environments, though pgvector remains a valid alternative.
- **Hybrid Retrieval**: Dense vectors struggle with out-of-vocabulary terms (like specific IDs or acronyms), whereas BM25 excels at them. Combining them yields the best of both worlds.
- **Reranking**: Bi-encoders (used for embeddings) are fast but less accurate. Cross-encoders are slow but highly accurate. We use bi-encoders to retrieve the top 50, and cross-encoders to rerank the top 5.
