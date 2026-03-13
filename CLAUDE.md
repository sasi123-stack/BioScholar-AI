# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BioMedScholar AI is an evidence-based biomedical research intelligence platform with:
- **Web Frontend**: Vanilla HTML/CSS/JS hosted on Firebase (biomed-scholar.web.app)
- **Backend API**: FastAPI with BioBERT semantic search (HF Space)
- **Telegram Bot**: @Meverick_AI_bot for AI-powered biomedical research queries

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run a specific test
pytest tests/test_integration.py -v

# Start development server (requires Elasticsearch and Redis)
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 7860

# Deploy frontend to Firebase
cd frontend && firebase deploy

# Run with production backend
python app_maverick.py
python app_minimal.py
```

## Project Structure

```
├── app_maverick.py       # Main FastAPI backend with Groq integration
├── app_minimal.py        # Minimal FastAPI backend
├── src/
│   ├── api/              # FastAPI routes (routes.py, models.py, app.py)
│   ├── search/           # Search functionality
│   ├── nlp_engine/       # BioBERT embeddings and text processing
│   ├── data_pipeline/    # Data processing pipelines
│   └── utils/            # Utility functions
├── frontend/
│   ├── app.js            # Main frontend JavaScript (250KB+)
│   ├── index.html        # Main HTML file
│   └── chat_styles.css   # Chat UI styling
├── tests/                # Pytest test suites
├── configs/              # YAML configuration files
└── requirements.txt      # Python dependencies
```

## Key Technologies

- **Frontend**: Vanilla JS, Firebase Hosting, Firebase Auth, Firestore
- **Backend**: FastAPI, Uvicorn, Gunicorn
- **AI/ML**: BioBERT, Groq GPT OSS 120B, sentence-transformers
- **Search**: Elasticsearch (Bonsai), OpenSearch
- **Database**: SQLite (conversation history), Neon PostgreSQL
- **Caching**: Upstash Redis
- **Telegram Bot**: python-telegram-bot v20+

## API Endpoints

- `GET /health` - Service health check
- `POST /api/v1/search` - Biomedical literature search
- `POST /api/v1/maverick/chat` - AI chat with Groq
- `GET /api/v1/maverick/history` - Retrieve chat history

## Environment Variables

Required for backend (see `.env.example`):
- `GROQ_API_KEY` - Groq API for GPT inference
- `ELASTICSEARCH_HOST` - Bonsai Elasticsearch URL
- `ELASTICSEARCH_USER` / `ELASTICSEARCH_PASSWORD` - Elasticsearch credentials
- `TELEGRAM_BOT_TOKEN` - Telegram bot token (for bot)
- `SERPER_API_KEY` - For web search integration
- `DATABASE_URL` - Neon PostgreSQL connection string
- `REDIS_HOST` / `REDIS_PORT` / `REDIS_PASSWORD` - Upstash Redis

## Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message & quick start |
| `/help` | Show all commands |
| `/search <topic>` | AI biomedical literature search |
| `/clear` | Clear conversation memory |
| `/claude <task>` | Execute Claude Code command |
| `/history` | View recent conversation |
| `/about` | About Maverick AI |

## Deployment

- **Frontend**: Firebase Hosting (auto-deploy from GitHub)
- **Backend API**: HuggingFace Spaces (Docker)
- **Telegram Bot**: HuggingFace Spaces (Docker)

## Code Patterns

- **HTML Response Formatting**: HTML tags in responses are sanitized via `verify_sanitization.py` to ensure Telegram-compatible output
- **DNS Resolution**: `app_maverick.py` includes a custom socket monkeypatch for robust DNS resolution on HF Spaces
- **Fallback Models**: Multiple fallback models are defined for resilience (see recent commits)
- **Chat History**: SQLite at `/tmp/conversation_history.db` for HF Spaces compatibility

## Testing

The project uses pytest with test files in `tests/`:
- `test_integration.py` - Integration tests
- `test_telegram_web.py` - Telegram bot tests
- `test_ui_articles.py` - UI article rendering tests

## Important Notes

- The frontend is a large single-page application (app.js is 265KB+)
- Elasticsearch/Bonsai connection uses HTTP Basic Auth
- Frontend stores user chat history in Firestore under `users/{uid}/chat_history`
- Scheduled reminders system in frontend uses localStorage