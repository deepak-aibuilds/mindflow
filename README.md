# MindFlow — AI Second Brain

> Capture everything. Query anything. Your knowledge, always within reach.

MindFlow is a personal AI knowledge API that ingests content from multiple sources — notes, PDFs, URLs, voice recordings, and Telegram messages — embeds them using vector search, and lets you query your own knowledge base using natural language.

---

## What It Does

- **Ingest** notes, PDFs, URLs, voice recordings, and Telegram messages
- **Embed** content automatically in the background using Mistral AI
- **Search** semantically — find relevant notes by meaning, not just keywords
- **Ask** — an AI agent answers questions using only your own notes as context
- **Automate** — n8n connects Telegram, Notion, Obsidian, and more

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI |
| Database | Supabase (PostgreSQL) |
| Vector Search | pgvector |
| ORM | SQLAlchemy (async) |
| Migrations | Alembic |
| LLM | Mistral AI via LangChain |
| Embeddings | Mistral `mistral-embed` (1024 dims) |
| Transcription | faster-whisper |
| Automation | n8n |
| Logging | JSON structured logging |
| Packaging | uv |

---

## Features

### Input Sources
| Source | How |
|---|---|
| Manual text | `POST /ingest` with `source_type=manual` |
| URL | `POST /ingest` with `source_type=url` — auto-scraped |
| PDF | `POST /ingest` with file upload |
| Voice/Audio | `POST /ingest` with audio file — auto-transcribed |
| Telegram | n8n Telegram bot → `POST /ingest` |

### Output
| Endpoint | What |
|---|---|
| `GET /search?q=` | Semantic search across all your notes |
| `POST /ask` | AI answers questions from your knowledge base |
| `GET /health` | Health check with DB ping |

---

## Project Structure

```
mindflow/
├── app/
│   ├── core/
│   │   ├── config.py          # Pydantic BaseSettings
│   │   └── logger.py          # JSON structured logging
│   ├── db/
│   │   └── db.py              # Async SQLAlchemy engine + session
│   ├── models/
│   │   └── item.py            # Item SQLAlchemy model
│   ├── schemas/
│   │   └── item.py            # Pydantic request/response schemas
│   ├── routes/
│   │   ├── ingest_route.py    # All ingestion endpoints
│   │   └── query_routes.py    # Search + ask endpoints
│   ├── services/
│   │   ├── save_db.py         # DB save helper
│   │   ├── scraper_service.py # URL scraping
│   │   ├── pdf_service.py     # PDF text extraction
│   │   ├── audio_service.py   # Voice transcription
│   │   ├── embedding_service.py # Vector embedding + storage
│   │   ├── search_service.py  # Semantic search
│   │   └── rag_service.py     # AI question answering
│   └── main.py                # App entry point + middleware
├── alembic/                   # Database migrations
├── Dockerfile
├── pyproject.toml
└── .env.example
```

---

## Setup

### Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Supabase account with pgvector extension enabled
- Mistral AI API key

### 1. Clone and install

```bash
git clone https://github.com/deepakpoudel121/mindflow
cd mindflow
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
```

Fill in your `.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:[password]@db.[project].supabase.co:5432/postgres
MISTRAL_API_KEY=your_mistral_api_key
SUPABASE_URL=https://[project].supabase.co
SUPABASE_KEY=your_supabase_anon_key
SECRET_KEY=your_secret_key
```

### 3. Enable pgvector in Supabase

Go to **Supabase Dashboard → Database → Extensions → vector → Enable**

### 4. Run migrations

```bash
uv run alembic upgrade head
```

### 5. Start the server

```bash
uv run uvicorn app.main:app --reload
```

API docs available at: `http://localhost:8000/docs`

---

## Usage Examples

### Ingest a note
```bash
curl -X POST http://localhost:8000/ingest \
  -F "source_type=manual" \
  -F "title=Meeting Notes" \
  -F "content=We decided to use FastAPI for the backend"
```

### Ingest a URL
```bash
curl -X POST http://localhost:8000/ingest \
  -F "source_type=url" \
  -F "source_url=https://fastapi.tiangolo.com"
```

### Ingest a PDF
```bash
curl -X POST http://localhost:8000/ingest \
  -F "source_type=pdf" \
  -F "file=@/path/to/document.pdf"
```

### Search your knowledge
```bash
curl "http://localhost:8000/search?q=FastAPI+backend&limit=5"
```

### Ask a question
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What did we decide about the backend?"}'
```

---

## n8n Automation

MindFlow works with n8n for automated ingestion from external sources.

**Telegram → MindFlow:**
1. Create a Telegram bot via @BotFather
2. Add n8n Telegram Trigger node
3. Add HTTP Request node pointing to `POST /ingest`
4. Set body: `content={{ $json.message.text }}`, `source_type=telegram_message`

---

## Deployment

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

Add environment variables in Railway dashboard.

### Docker

```bash
docker build -t mindflow .
docker run -p 8000:8000 --env-file .env mindflow
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | PostgreSQL connection string (asyncpg) |
| `MISTRAL_API_KEY` | ✅ | Mistral AI API key |
| `SUPABASE_URL` | ✅ | Supabase project URL |
| `SUPABASE_KEY` | ✅ | Supabase anon key |
| `SECRET_KEY` | ❌ | JWT secret (for future auth) |
| `DEBUG` | ❌ | Enable debug mode (default: false) |

---

## Roadmap

- [ ] `GET /digest` — AI summary of recent notes → email/Slack via n8n
- [ ] `POST /actions` — extract action items → Telegram via n8n
- [ ] `GET /items` — paginated list with filters
- [ ] `GET /connections/{id}` — find semantically related notes
- [ ] Authentication — JWT-based user accounts
- [ ] Redis caching for search results
- [ ] Celery for long audio processing
- [ ] Rate limiting

---

## License

MIT