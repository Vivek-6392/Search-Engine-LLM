# DeepSearch AI

DeepSearch AI is a production-grade multi-agent research and knowledge engine. It replaces traditional single-agent LLM wrappers with a robust, observable, and stateful LangGraph architecture capable of autonomous query planning, parallel web and academic research, hybrid retrieval, and evidence verification.

## 🌟 Key Features

- **Multi-Agent Orchestration**: Router, Planner, Researchers (Web, Academic, Document), Synthesizer, and Critic agents built with LangGraph.
- **Hybrid RAG Pipeline**: Combines Dense Vector Search (BGE) with BM25 using Reciprocal Rank Fusion, followed by Cross-Encoder Reranking.
- **Hallucination Detection**: The Critic agent verifies draft answers against retrieved evidence before returning them to the user.
- **Real-time Streaming**: Server-Sent Events (SSE) provide real-time feedback on agent thought processes and state transitions.
- **Production Infrastructure**: FastAPI, PostgreSQL, Redis, Qdrant, Docker, JWT Authentication, and Rate Limiting.
- **Observability**: Langfuse integration for tracing latency, costs, and agent execution paths.

## 🏗️ Architecture

![Architecture](docs/architecture.md)

1. **User** sends a query via the **Next.js Frontend**.
2. **FastAPI Gateway** authenticates the user and passes the query to the **Router Agent**.
3. For complex queries, the **Planner Agent** generates subtasks.
4. **Research Agents** execute searches in parallel across Web (DuckDuckGo/Tavily), ArXiv, and local Documents (Qdrant).
5. Evidence is retrieved, reranked, and formatted.
6. The **Synthesizer Agent** writes an answer with inline citations.
7. The **Critic Agent** verifies the answer. If hallucinations are detected, it triggers a revision.
8. The verified answer is streamed back to the user.

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- API Keys for OpenAI, Groq, or Ollama (Local)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Vivek-6392/Search-Engine-LLM.git
   cd Search-Engine-LLM
   ```

2. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` to include your API keys.*

3. Start the infrastructure and backend:
   ```bash
   docker compose up --build -d
   ```

4. Start the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. Access the application at `http://localhost:3000`.

## 🧪 Evaluation Methodology

DeepSearch AI uses the **Ragas** framework to evaluate the performance of the retrieval and synthesis pipelines. 
Run the evaluation script to measure:
- **Context Precision**: Are the most relevant chunks ranked highest?
- **Context Recall**: Did we retrieve all necessary information to answer the question?
- **Faithfulness**: Is the answer derived *only* from the context?
- **Answer Relevancy**: Does the answer directly address the user's query?

```bash
python scripts/evaluate.py
```

## 📂 Project Structure

- `backend/`: FastAPI application, LangGraph agents, Database models, and Retrieval logic.
- `frontend/`: Next.js 14+ App Router, Tailwind CSS UI.
- `legacy_streamlit/`: Original Streamlit prototype (preserved for backward compatibility).
- `evaluation/`: Scripts and datasets for Ragas evaluation.
- `docs/`: Architectural decision records and design documentation.

## 🛡️ Security
- Passwords hashed using bcrypt.
- JWT-based authentication for all API endpoints.
- Dependency isolation via Docker containers.
- Secrets managed exclusively via `.env` files (never committed).

## 💡 Future Improvements
- **Semantic Caching**: Cache identical queries using Redis to save API costs.
- **GraphRAG Integration**: Extract entities and relationships from documents into a Knowledge Graph for multi-hop reasoning.
- **User-Level RBAC**: Introduce Organization and Admin roles for document sharing.

---
*Built as a flagship AI Engineering portfolio project.*
