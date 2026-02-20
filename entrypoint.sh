#!/bin/bash

# Start the FastAPI Backend in the background
echo "🚀 Starting FastAPI Backend on port 7860..."
python3 -m uvicorn src.api.app:app --host 0.0.0.0 --port 7860 &

# Wait a few seconds for backend to initialize
sleep 5

# Start the Maverick Telegram Bot in the foreground
# Foreground is important so the container doesn't exit
echo "🦞 Starting Maverick Telegram Bot..."
python3 app_maverick.py
