#!/bin/bash

# Ensure /tmp dirs exist
mkdir -p /tmp/logs

echo "🚀 Starting Maverick AI Telegram Bot..."
echo "💠 Bot serves Flask health check on port 7860"

# Run bot directly as the main foreground process
# The bot has its own Flask thread for port 7860
exec python3 app_maverick.py
