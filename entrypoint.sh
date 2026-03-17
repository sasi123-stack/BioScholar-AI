#!/bin/bash

# Ensure /tmp dirs exist
mkdir -p /tmp/logs

echo "🚀 Starting BioMed Scholar API..."
echo "💠 FastAPI server running on port 7860"

# Start Maverick Telegram Bot in background (uses Groq API directly)
echo "🤖 Starting Maverick Telegram Bot..."
python maverick_telegram_bot.py &

# Run FastAPI server with uvicorn
exec uvicorn app_minimal:app --host 0.0.0.0 --port 7860
