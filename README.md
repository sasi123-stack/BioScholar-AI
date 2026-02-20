---
title: BioScholar AI Unified
emoji: 🔬
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# 🚀 BioScholar AI Unified Engine

This Space hosts both the **FastAPI Backend API** and the **Maverick Telegram Bot**.

### 🛠️ Components
- **Backend**: FastAPI search engine integrated with BioBERT.
- **Bot**: Persistent-memory Llama 4 Maverick.

### 🔐 Setup Secrets
The following secrets are required in your Space Settings:
- `TELEGRAM_BOT_TOKEN`
- `GROQ_API_KEY`
- `DATABASE_URL` (Neon Postgres)
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD` (Upstash)
- `ELASTICSEARCH_HOST`, `ELASTICSEARCH_USERNAME`, `ELASTICSEARCH_PASSWORD` (Bonsai)
