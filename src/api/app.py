"""
FastAPI application factory and configuration.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from src.api.routes import router
from src.api.dependencies import initialize_services, cleanup_services
from src.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting Biomedical Search API...")
    initialize_services()
    logger.info("✅ API ready to accept requests")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Biomedical Search API...")
    cleanup_services()
    logger.info("✅ API shutdown complete")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    app = FastAPI(
        title="Biomedical Search Engine API",
        description="Intelligent semantic search engine for biomedical literature and clinical trials",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # CORS middleware - allow all origins for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(router)
    
    # Root endpoint - redirect to docs
    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/docs")
    
    # Root health endpoint for monitoring services
    @app.get("/health", tags=["System"])
    async def global_health_check():
        """
        Global health check endpoint.
        Returns 200 OK if the API instance is running.
        """
        return {"status": "online", "message": "Biomedical Search API is running"}
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
