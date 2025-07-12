#!/usr/bin/env python3
"""
Logging configuration for Myanmar House Price Predictor.

Provides structured logging with Loguru, including request tracing and performance monitoring.
"""

import sys
from loguru import logger
from typing import Optional
import json
from datetime import datetime

from .config import settings


def serialize_record(record):
    """Serialize log record to JSON format."""
    # Create a dictionary with the log record data
    log_data = {
        "time": record["time"].isoformat(),  # Use 'time' instead of 'timestamp'
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
        "extra": record["extra"]
    }
    return json.dumps(log_data)


def setup_logging():
    """Configure logging for the application."""
    
    # Remove default logger
    logger.remove()
    
    # Console logging format
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    # Add console handler
    logger.add(
        sys.stdout,
        format=console_format,
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # Add file handler if specified
    if settings.LOG_FILE:
        logger.add(
            settings.LOG_FILE,
            format=serialize_record,
            level=settings.LOG_LEVEL,
            rotation="100 MB",
            retention="30 days",
            compression="gz",
            serialize=True
        )
    
    # Add structured JSON logging for production
    if settings.is_production:
        logger.add(
            "logs/app.json",
            format=serialize_record,
            level="INFO",
            rotation="50 MB",
            retention="7 days",
            compression="gz",
            serialize=True
        )
    
    logger.info(f"Logging configured with level: {settings.LOG_LEVEL}")


class RequestLogger:
    """Context manager for request logging with timing."""
    
    def __init__(self, request_id: str, endpoint: str, method: str):
        self.request_id = request_id
        self.endpoint = endpoint
        self.method = method
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        logger.info(
            f"Request started: {self.method} {self.endpoint}",
            extra={"request_id": self.request_id, "event": "request_start"}
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            logger.info(
                f"Request completed: {self.method} {self.endpoint} in {duration:.3f}s",
                extra={
                    "request_id": self.request_id,
                    "event": "request_complete",
                    "duration_seconds": duration
                }
            )
        else:
            logger.error(
                f"Request failed: {self.method} {self.endpoint} after {duration:.3f}s - {exc_val}",
                extra={
                    "request_id": self.request_id,
                    "event": "request_error",
                    "duration_seconds": duration,
                    "error_type": exc_type.__name__,
                    "error_message": str(exc_val)
                }
            )


def log_ml_prediction(model_name: str, features: dict, prediction: float, confidence: Optional[float] = None):
    """Log ML prediction for monitoring and debugging."""
    logger.info(
        f"ML Prediction: {model_name} -> {prediction}",
        extra={
            "event": "ml_prediction",
            "model_name": model_name,
            "prediction": prediction,
            "confidence": confidence,
            "feature_count": len(features)
        }
    )


def log_ai_enrichment(property_data: dict, enriched_data: dict, processing_time: float):
    """Log AI enrichment process for monitoring."""
    logger.info(
        f"AI Enrichment completed in {processing_time:.3f}s",
        extra={
            "event": "ai_enrichment",
            "processing_time_seconds": processing_time,
            "original_fields": len(property_data),
            "enriched_fields": len(enriched_data)
        }
    )


def log_model_performance(model_name: str, metrics: dict):
    """Log model performance metrics."""
    logger.info(
        f"Model Performance: {model_name}",
        extra={
            "event": "model_performance",
            "model_name": model_name,
            **metrics
        }
    )