#!/bin/bash

# Ensure /tmp dirs exist
mkdir -p /tmp/logs

echo "🚀 Starting BioMed Scholar API..."
echo "💠 FastAPI server running on port 7860"

# Run FastAPI server with uvicorn
exec uvicorn app_minimal:app --host 0.0.0.0 --port 7860
