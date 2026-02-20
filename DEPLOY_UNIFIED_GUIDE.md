# 🚀 BioMedScholar AI: Unified Deployment Guide

This guide explains how to host the **FastAPI Backend** and the **Maverick Telegram Bot** in a single Hugging Face Space.

---

## 🏗️ 1. Architecture Overview
- **Hugging Face Space**: Runs the application logic (Python).
- **Docker**: Containerizes the system to run multiple processes.
- **external Clouds**:
  - **Bonsai.io**: Managed Elasticsearch (Search data).
  - **Neon.tech**: Managed PostgreSQL (User data).
  - **Upstash.com**: Managed Redis (Cache).

---

## 🔐 2. Required Secrets
Go to **Settings > Variables and secrets** in your Hugging Face Space and add these:

### AI & Core
- `GROQ_API_KEY`: Your Groq API key (for Llama 4).
- `TELEGRAM_BOT_TOKEN`: From @BotFather.
- `APP_ENV`: Set to `production`.

### Databases (Cloud)
- `DATABASE_URL`: Your full Neon Postgres string.
- `ELASTICSEARCH_HOST`: Your Bonsai cluster domain.
- `ELASTICSEARCH_USERNAME`: Your Bonsai username.
- `ELASTICSEARCH_PASSWORD`: Your Bonsai password.
- `REDIS_HOST`: Your Upstash endpoint.
- `REDIS_PASSWORD`: Your Upstash password.

---

## 🚀 3. Deploying from Local
To send your latest code to Hugging Face, run these commands in your project root:

```powershell
# 1. Ensure you are on the main branch
git checkout main

# 2. Stage all changes
git add .

# 3. Commit
git commit -m "Deploy: Unified Backend & Bot Hub"

# 4. Push to Hugging Face
git push space main --force
```

---

## 📂 4. Project File Roles
- **`Dockerfile`**: Sets up the Python environment and system dependencies.
- **`entrypoint.sh`**: Launches the FastAPI server (Background) and the Telegram Bot (Foreground).
- **`app_maverick.py`**: The logic for the Telegram Bot with persistent memory.
- **`src/api/app.py`**: The main FastAPI application.
- **`README.md`**: Provides metadata instructions to Hugging Face.

---

## 🐛 5. Troubleshooting
- **"No application file"**: Check that the YAML metadata at the top of `README.md` has `sdk: docker`.
- **"Port 7860 Busy"**: Make sure you aren't trying to run two servers on the same port inside `entrypoint.sh`.
- **"Bot not responding"**: Check the `Container Logs` in the Space for `[CRITICAL]` errors or connection timeouts.
- **"Search results empty"**: Ensure you have run your local ingestion scripts (e.g., `ingest_to_cloud.py`) pointing to your Bonsai credentials.

---
**Guide updated: February 20, 2026**
