#!/bin/bash

# Ensure /tmp dirs exist
mkdir -p /tmp/logs

echo "🚀 Starting Maverick AI Research API..."
echo "💠 API serves Flask health check and research endpoints on port 7860"

# Run Flask server directly as the main foreground process
exec python3 app_maverick.py
