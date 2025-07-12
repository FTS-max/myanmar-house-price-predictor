#!/usr/bin/env python3
"""
Myanmar House Price Predictor - Main Application Entry Point

A production-ready FastAPI backend for predicting real estate prices in Myanmar
with ML models, OpenRouter AI enrichment, and comprehensive REST API.
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import api_router
from app.core.exceptions import setup_exception_handlers
from app.core.exceptions import RateLimitException
from app.api.routes import rate_limit_exception_handler
from app.services.ml_service import MLService
from app.services.openrouter_service import OpenRouterService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Myanmar House Price Predictor API...")
    
    # Initialize ML service
    ml_service = MLService()
    await ml_service.initialize()
    app.state.ml_service = ml_service
    
    # Initialize OpenRouter service
    openrouter_service = OpenRouterService()
    app.state.openrouter_service = openrouter_service
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Myanmar House Price Predictor API...")
    # Cleanup resources if needed
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Setup logging
    setup_logging()
    
    # Create FastAPI app
    app = FastAPI(
        title="Myanmar House Price Predictor API",
        description="A production-ready API for predicting real estate prices in Myanmar using ML and AI enrichment",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Setup exception handlers
    setup_exception_handlers(app)
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "Myanmar House Price Predictor"}
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )