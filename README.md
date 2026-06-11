# MindFlow — AI Second Brain

Capture everything. Query anything. MindFlow is a personal AI knowledge API that ingests content from multiple sources, embeds it using vector search, and lets you query your own knowledge base using natural language.

---

## Architecture

```
Ingest (text / URL / PDF / voice)
         ↓
  Save to PostgreSQL
         ↓
  Background: chunk → embed → store vectors (pgvector)
         ↓
Query: semantic search → hybrid BM25 + vector → Cohere rerank → LLM answer
```

---

## Tech Stack

- **FastAPI** — async REST API
- **PostgreSQL + pgvector** — storage and vector search
- **LangChain + Mistral AI** — embeddings and LLM
- **Cohere** — reranking
- **BM25** — keyword search (hybrid retrieval)
- **LangGraph** — agent with context decision node
- **Redis** — response caching
- **faster-whisper** — voice transcription
- **Docker + Supabase** — infrastructure
- **Alembic** — database migrations

---

## Endpoints

| Method | Endpoint | What it does |
|--------|----------|-------------|
| POST | `/ingest` | Ingest text, URL, PDF, or voice |
| GET | `/search?q=` | Semantic search across knowledge base |
| POST | `/ask` | Answer a question from your knowledge base |
| POST | `/agent/ask` | LangGraph agent — decides if context needed |
| GET | `/digest` | AI daily digest of last 24h content |
| POST | `/actions` | Extract action items from last 24h |
| GET | `/items` | List all ingested items with filters |
| GET | `/health` | Health check |

---

## Setup

```bash
git clone https://github.com/deepak-aibuilds/mindflow
cd mindflow

cp .env.example .env
# fill in: DATABASE_URL, MISTRAL_API_KEY, GROQ_API_KEY, COHERE_API_KEY, REDIS_URL

uv sync
alembic upgrade head

uv run uvicorn app.main:app --reload
```

---

## Demo

```bash
uv pip install streamlit
streamlit run demo.py
```

---

## License

MIT