#!/bin/bash

# Ensure /tmp dirs exist
mkdir -p /tmp/logs

echo "🚀 Starting BioMed Scholar API..."
echo "💠 FastAPI server running on port 7860"

# Start Ollama daemon in background
echo "🦙 Starting Ollama..."
OLLAMA_HOST="127.0.0.1:11434" ollama serve > /tmp/logs/ollama.log 2>&1 &

echo "⏳ Waiting for Ollama to start..."
sleep 5

echo "📥 Pulling openclaw model (this may take a while)..."
ollama pull openclaw

# Start Maverick Telegram Bot in background
echo "🤖 Starting Maverick Telegram Bot..."
python maverick_telegram_bot.py &

# Run FastAPI server with uvicorn
exec uvicorn app_minimal:app --host 0.0.0.0 --port 7860
