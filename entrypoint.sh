#!/bin/bash

# Ensure /tmp dirs exist
mkdir -p /tmp/logs

echo "🚀 Starting BioMed Scholar API..."
echo "💠 FastAPI server running on port 7860"

# Start Maverick Telegram Bot in background with auto-restart supervisor
if [ "$RUN_BOT" != "false" ]; then
    echo "🤖 Starting Maverick Telegram Bot with auto-restart supervisor..."
    (
        while true; do
            echo "[$(date)] Starting maverick_telegram_bot.py..." >> /tmp/logs/telegram_bot.log
            python -u maverick_telegram_bot.py >> /tmp/logs/telegram_bot.log 2>&1
            echo "[$(date)] Bot process exited (code $?). Restarting in 5s..." >> /tmp/logs/telegram_bot.log
            sleep 5
        done
    ) &
else
    echo "⏭️ Skipping Telegram Bot (RUN_BOT=false detected)"
fi

# Run FastAPI server with uvicorn
exec uvicorn app_minimal:app --host 0.0.0.0 --port "${PORT:-7860}"
