# Company Lens

A FastAPI service for automated company research and RAG-based chat. Given a company name, it searches the web, summarizes sources with an LLM, builds a structured profile, and stores it for retrieval-augmented conversations.

## Features

- **Automated research pipeline** — generates targeted search queries, fetches web sources via Tavily, summarizes them per topic, then synthesizes a full company profile (industry, overview, products, competitors, recent news)
- **RAG chat with streaming** — retrieves relevant context from ChromaDB embeddings and streams LLM responses over SSE
- **Guardrails** — query classification to keep chat on-topic
- **Session management** — persistent chat sessions per company with full message history
- **CLI** — research and chat from the terminal without touching the API directly

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| Database | PostgreSQL + SQLModel + Alembic |
| Vector store | ChromaDB |
| LLM | OpenRouter (configurable models) |
| Embeddings | OpenAI `text-embedding-3-small` (via OpenRouter) |
| Web search | Tavily |
| CLI | Rich |

## Architecture

```
Research pipeline
  └─ build_search_queries()   → topic-based queries for the company
  └─ search_company_web()     → Tavily web search per query
  └─ summarize_all()          → LLM summarizes each topic's sources
  └─ generate_profile()       → LLM synthesizes a full markdown profile
  └─ extract_structured_fields() → structured JSON (industry, products, etc.)

Embedding pipeline
  └─ build_research_document() → splits profile into chunks
  └─ store_chunks()            → embeds and persists to ChromaDB

RAG chat
  └─ guardrails check         → classify query relevance
  └─ retrieve context         → ChromaDB similarity search
  └─ stream_rag_response()    → SSE streaming response
```

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv)
- Docker (for PostgreSQL)

## Setup

1. Copy the example env file and fill in the values:

   ```bash
   cp .env.example .env
   ```

2. Install dependencies:

   ```bash
   uv sync
   ```

3. Start PostgreSQL:

   ```bash
   make db-up
   ```

4. Run migrations:

   ```bash
   make migrate
   ```

5. Start the API:

   ```bash
   make dev
   ```

API docs are available at `/scalar`.

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `OPENROUTER_API_KEY` | OpenRouter API key |
| `OPENROUTER_BASE_URL` | OpenRouter base URL |
| `LLM_MODEL_FAST` | Model for query classification, guardrails, and chat |
| `LLM_MODEL_STRONG` | Model for final research profile synthesis |
| `EMBEDDING_MODEL` | Embedding model (default: `openai/text-embedding-3-small`) |
| `TAVILY_API_KEY` | Tavily API key for web search |
| `API_BASE_URL` | API base URL used by the CLI (default: `http://127.0.0.1:8000`) |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/companies` | Research a company and store its profile |
| `GET` | `/companies` | List all researched companies |
| `GET` | `/companies/{id}` | Get a company's full profile |
| `DELETE` | `/companies/{id}` | Delete a company and all associated data |
| `POST` | `/companies/{id}/sessions` | Create a new chat session |
| `GET` | `/companies/{id}/sessions` | List chat sessions for a company |
| `POST` | `/companies/{id}/sessions/{sid}/messages` | Send a message (SSE streaming) |
| `GET` | `/companies/{id}/sessions/{sid}/messages` | Get message history |

## CLI Usage

The CLI is available as the `company-lens` command.

```bash
# Research a company (triggers the full pipeline)
uv run company-lens research Shopee

# List all researched companies
uv run company-lens list

# Show a company's profile
uv run company-lens show Shopee

# Delete a company
uv run company-lens delete Shopee

# Start an interactive chat session
uv run company-lens chat Shopee

# List chat sessions for a company
uv run company-lens sessions Shopee

# View message history for a session
uv run company-lens history Shopee <session_id>
```

## Makefile Commands

| Command | Description |
|---|---|
| `make dev` | Start the API with hot reload |
| `make db-up` | Start PostgreSQL via Docker Compose |
| `make db-down` | Stop PostgreSQL |
| `make db-logs` | Tail PostgreSQL logs |
| `make migrate` | Run Alembic migrations |
| `make revision MSG="..."` | Create a new migration revision |
| `make lint` | Run Ruff linter |
| `make format` | Run Ruff formatter |

## Storage

- **PostgreSQL** — companies, chat sessions, messages, and chunk metadata
- **ChromaDB** — vector embeddings persisted to `./chroma_data`
