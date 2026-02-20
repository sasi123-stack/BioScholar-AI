"""
Minimal FastAPI application for Render deployment testing.
This version has minimal dependencies and memory footprint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="BioMed Scholar API - Minimal",
    description="Minimal version for deployment testing",
    version="1.0.0-minimal"
)

# CORS middleware - allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "BioMed Scholar API - Minimal Version",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

@app.get("/api/v1/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "elasticsearch": False,
        "models_loaded": False,
        "version": "1.0.0-minimal",
        "features": {
            "qa_enabled": False,
            "reranking_enabled": False,
            "search_enabled": False
        },
        "message": "Minimal version - core features disabled for testing"
    }

@app.get("/api/v1/statistics")
async def statistics():
    """Statistics endpoint - minimal version."""
    return {
        "total_documents": 0,
        "pubmed_articles": 0,
        "clinical_trials": 0,
        "message": "Minimal version - no data indexed"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app_minimal:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
