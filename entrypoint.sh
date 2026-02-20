#!/bin/bash

# Ensure /tmp/logs exists for our fallback logger
mkdir -p /tmp/logs

# Start the Maverick Telegram Bot in the background with a restart loop
echo "🦞 Initializing Maverick Telegram Bot background process..."
(
    while true; do
        echo "🦞 Attempting to start Maverick Bot..."
        python3 app_maverick.py >> /tmp/maverick_bot.log 2>&1
        echo "🦞 Bot process exited. Logs last few lines:"
        tail -n 10 /tmp/maverick_bot.log
        echo "🦞 Restarting Bot in 30s..."
        sleep 30
    done
) &

# Start the FastAPI Backend in the foreground
# Exec ensures that it receives signals (like SIGTERM) from Hugging Face
echo "🚀 Starting FastAPI Backend Engine..."
echo "ℹ️ Note: Large AI models may take 2-5 minutes to load on first boot."
exec python3 -m uvicorn src.api.app:app --host 0.0.0.0 --port 7860 --log-level info
