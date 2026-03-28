#!/bin/bash

# Ensure /tmp dirs exist
mkdir -p /tmp/logs

echo "🚀 Starting BioMed Scholar API..."
echo "💠 FastAPI server running on port 7860"

# Start Maverick Telegram Bot in background (if enabled)
if [ "$RUN_BOT" != "false" ]; then
    echo "🤖 Starting Maverick Telegram Bot..."
    python maverick_telegram_bot.py &
else
    echo "⏭️ Skipping Telegram Bot (RUN_BOT=false detected)"
fi

# Run FastAPI server with uvicorn
exec uvicorn app_minimal:app --host 0.0.0.0 --port 7860
