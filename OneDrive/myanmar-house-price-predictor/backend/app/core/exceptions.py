#!/usr/bin/env python3
"""
Custom exceptions and error handlers for Myanmar House Price Predictor.

Provides structured error handling with proper HTTP status codes and logging.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from loguru import logger
from typing import Any, Dict, Optional
import traceback
from datetime import datetime


class BaseCustomException(Exception):
    """Base class for custom exceptions."""
    
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class MLModelException(BaseCustomException):
    """Exception raised when ML model operations fail."""
    
    def __init__(self, message: str, model_name: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)
        self.model_name = model_name


class DataValidationException(BaseCustomException):
    """Exception raised when data validation fails."""
    
    def __init__(self, message: str, field_errors: Optional[Dict[str, str]] = None):
        details = {"field_errors": field_errors} if field_errors else {}
        super().__init__(message, status_code=422, details=details)


class OpenRouterException(BaseCustomException):
    """Exception raised when OpenRouter API operations fail."""
    
    def __init__(self, message: str, api_error: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=503, details=details)
        self.api_error = api_error


class DatabaseException(BaseCustomException):
    """Exception raised when database operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)
        self.operation = operation


class RateLimitException(BaseCustomException):
    """Exception raised when rate limits are exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(message, status_code=429, details=details)


class PropertyNotFoundException(BaseCustomException):
    """Exception raised when a property is not found."""
    
    def __init__(self, property_id: str):
        message = f"Property with ID {property_id} not found"
        super().__init__(message, status_code=404, details={"property_id": property_id})


def create_error_response(status_code: int, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create standardized error response."""
    response = {
        "error": True,
        "status_code": status_code,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if details:
        response["details"] = details
    
    return response


async def custom_exception_handler(request: Request, exc: BaseCustomException) -> JSONResponse:
    """Handle custom exceptions."""
    logger.error(
        f"Custom exception: {exc.__class__.__name__}: {exc.message}",
        extra={
            "exception_type": exc.__class__.__name__,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": str(request.url),
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            message=exc.message,
            details=exc.details
        )
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.warning(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": str(request.url),
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            message=str(exc.detail)
        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation exceptions."""
    errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field_path,
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation error: {len(errors)} field(s) failed validation",
        extra={
            "validation_errors": errors,
            "path": str(request.url),
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=422,
        content=create_error_response(
            status_code=422,
            message="Validation failed",
            details={"validation_errors": errors}
        )
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(
        f"Unexpected exception: {exc.__class__.__name__}: {str(exc)}",
        extra={
            "exception_type": exc.__class__.__name__,
            "traceback": traceback.format_exc(),
            "path": str(request.url),
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=500,
        content=create_error_response(
            status_code=500,
            message="Internal server error",
            details={"type": exc.__class__.__name__} if not isinstance(exc, Exception) else None
        )
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup all exception handlers for the FastAPI app."""
    
    # Custom exception handlers
    app.add_exception_handler(BaseCustomException, custom_exception_handler)
    app.add_exception_handler(MLModelException, custom_exception_handler)
    app.add_exception_handler(DataValidationException, custom_exception_handler)
    app.add_exception_handler(OpenRouterException, custom_exception_handler)
    app.add_exception_handler(DatabaseException, custom_exception_handler)
    # Use the specific rate limit handler from routes.py instead of the generic custom_exception_handler
    from app.api.routes import rate_limit_exception_handler
    app.add_exception_handler(RateLimitException, rate_limit_exception_handler)
    app.add_exception_handler(PropertyNotFoundException, custom_exception_handler)
    
    # Standard exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Catch-all exception handler
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers configured")