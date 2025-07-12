#!/usr/bin/env python3
"""
API Routes for Myanmar House Price Predictor.

Defines all REST API endpoints for property price prediction, market analysis, and data management.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from loguru import logger

from ..core.config import settings
from ..core.exceptions import (
    MLModelException, OpenRouterException, DataValidationException,
    PropertyNotFoundException, RateLimitException
)
from ..core.logging import RequestLogger
from ..models.schemas import (
    PropertyCreate, PropertyUpdate, PropertyResponse,
    PredictionRequest, PredictionResponse,
    BatchPredictionRequest, BatchPredictionResponse,
    MarketAnalysisRequest, MarketAnalysisResponse,
    ModelPerformanceMetrics, HealthCheckResponse
)
from ..services.ml_service import MLService
from ..services.openrouter_service import OpenRouterService

# Create API router
api_router = APIRouter()

# Rate limiting storage (in production, use Redis)
rate_limit_storage = {}


def get_ml_service(request: Request) -> MLService:
    """Dependency to get ML service from app state."""
    return request.app.state.ml_service


def get_openrouter_service(request: Request) -> OpenRouterService:
    """Dependency to get OpenRouter service from app state."""
    return request.app.state.openrouter_service


def check_rate_limit(request: Request) -> None:
    """Simple rate limiting check."""
    client_ip = request.client.host
    current_time = datetime.now()
    
    # Clean old entries
    cutoff_time = current_time.timestamp() - 60  # 1 minute window
    if client_ip in rate_limit_storage:
        rate_limit_storage[client_ip] = [
            timestamp for timestamp in rate_limit_storage[client_ip]
            if timestamp > cutoff_time
        ]
    
    # Check rate limit
    if client_ip not in rate_limit_storage:
        rate_limit_storage[client_ip] = []
    
    if len(rate_limit_storage[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
        raise RateLimitException(retry_after=60)
    
    # Add current request
    rate_limit_storage[client_ip].append(current_time.timestamp())


@api_router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    request: Request,
    ml_service: MLService = Depends(get_ml_service),
    openrouter_service: OpenRouterService = Depends(get_openrouter_service)
):
    """Health check endpoint."""
    request_id = str(uuid.uuid4())
    
    with RequestLogger(request_id, "/health", "GET"):
        components = {
            "ml_service": "healthy",
            "openrouter_service": "healthy" if settings.OPENROUTER_API_KEY else "disabled"
        }
        
        # Check OpenRouter if enabled
        if settings.ENABLE_AI_ENRICHMENT and settings.OPENROUTER_API_KEY:
            try:
                is_healthy = await openrouter_service.health_check()
                components["openrouter_service"] = "healthy" if is_healthy else "unhealthy"
            except Exception:
                components["openrouter_service"] = "unhealthy"
        
        return HealthCheckResponse(
            status="healthy",
            service="Myanmar House Price Predictor",
            version=settings.VERSION,
            components=components
        )


@api_router.post("/predict", response_model=PredictionResponse)
async def predict_price(
    prediction_request: PredictionRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    ml_service: MLService = Depends(get_ml_service),
    openrouter_service: OpenRouterService = Depends(get_openrouter_service)
):
    """Predict property price with optional AI enrichment."""
    check_rate_limit(request)
    request_id = str(uuid.uuid4())
    
    with RequestLogger(request_id, "/predict", "POST"):
        try:
            # Get base prediction
            prediction = await ml_service.predict_price(
                prediction_request,
                prediction_request.model_preference
            )
            
            # Add AI enrichment if enabled
            if prediction_request.enable_ai_enrichment and settings.ENABLE_AI_ENRICHMENT:
                try:
                    enriched_data = await openrouter_service.enrich_property_data(prediction_request)
                    
                    if enriched_data:
                        prediction.market_insights = enriched_data.get("market_insights")
                        
                        # Add comparable properties info
                        if "recommendations" in enriched_data:
                            prediction.comparable_properties = [{
                                "analysis": enriched_data["recommendations"]
                            }]
                
                except Exception as e:
                    logger.warning(f"AI enrichment failed: {str(e)}")
                    # Continue without enrichment
            
            logger.info(f"Price prediction completed: {prediction.predicted_price_mmk:,.0f} MMK")
            return prediction
            
        except MLModelException as e:
            logger.error(f"ML prediction failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Prediction request failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Prediction service temporarily unavailable")


@api_router.post("/predict/batch", response_model=BatchPredictionResponse)
async def batch_predict_prices(
    batch_request: BatchPredictionRequest,
    request: Request,
    ml_service: MLService = Depends(get_ml_service),
    openrouter_service: OpenRouterService = Depends(get_openrouter_service)
):
    """Batch predict property prices."""
    check_rate_limit(request)
    request_id = str(uuid.uuid4())
    
    with RequestLogger(request_id, "/predict/batch", "POST"):
        if len(batch_request.properties) > settings.MAX_PREDICTION_BATCH_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Batch size exceeds maximum of {settings.MAX_PREDICTION_BATCH_SIZE}"
            )
        
        start_time = datetime.now()
        
        try:
            # Process predictions
            predictions = []
            
            for property_data in batch_request.properties:
                # Convert to PredictionRequest
                pred_request = PredictionRequest(
                    **property_data.dict(),
                    enable_ai_enrichment=batch_request.enable_ai_enrichment,
                    model_preference=batch_request.model_preference
                )
                
                prediction = await ml_service.predict_price(
                    pred_request,
                    batch_request.model_preference
                )
                predictions.append(prediction)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return BatchPredictionResponse(
                predictions=predictions,
                batch_id=str(uuid.uuid4()),
                total_processed=len(predictions),
                processing_time_seconds=processing_time
            )
            
        except Exception as e:
            logger.error(f"Batch prediction failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Batch prediction service temporarily unavailable")


@api_router.post("/market/analysis", response_model=MarketAnalysisResponse)
async def market_analysis(
    analysis_request: MarketAnalysisRequest,
    request: Request,
    openrouter_service: OpenRouterService = Depends(get_openrouter_service)
):
    """Generate market analysis for a location."""
    check_rate_limit(request)
    request_id = str(uuid.uuid4())
    
    with RequestLogger(request_id, "/market/analysis", "POST"):
        try:
            # Generate AI-powered market analysis
            market_data = await openrouter_service.generate_market_analysis(
                analysis_request.location,
                analysis_request.property_type.value if analysis_request.property_type else None
            )
            
            # Create response with fallback data
            if not market_data:
                market_data = {
                    "market_overview": {
                        "current_trends": "Market analysis unavailable",
                        "price_direction": "stable",
                        "market_activity": "medium"
                    },
                    "pricing_analysis": {
                        "average_price_range": {"min_mmk": 0, "max_mmk": 0}
                    }
                }
            
            return MarketAnalysisResponse(
                location_summary={
                    "city": analysis_request.location.city,
                    "township": analysis_request.location.township,
                    "analysis_period": f"{analysis_request.time_period_months} months"
                },
                average_price_mmk=market_data.get("pricing_analysis", {}).get("average_price_range", {}).get("min_mmk", 0),
                average_price_usd=market_data.get("pricing_analysis", {}).get("average_price_range", {}).get("min_mmk", 0) / 2100,
                price_trends=market_data.get("market_overview", {}),
                market_activity=market_data.get("market_overview", {}),
                price_distribution=market_data.get("pricing_analysis", {}),
                recommendations=market_data.get("recommendations", ["Conduct thorough market research"]),
                analysis_id=str(uuid.uuid4())
            )
            
        except Exception as e:
            logger.error(f"Market analysis failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Market analysis service temporarily unavailable")


@api_router.get("/models/performance", response_model=Dict[str, ModelPerformanceMetrics])
async def get_model_performance(
    request: Request,
    ml_service: MLService = Depends(get_ml_service)
):
    """Get ML model performance metrics."""
    request_id = str(uuid.uuid4())
    
    with RequestLogger(request_id, "/models/performance", "GET"):
        try:
            metrics = ml_service.get_model_metrics()
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get model metrics: {str(e)}")
            raise HTTPException(status_code=500, detail="Model metrics unavailable")


@api_router.post("/property/description")
async def generate_property_description(
    property_data: PropertyCreate,
    request: Request,
    openrouter_service: OpenRouterService = Depends(get_openrouter_service)
):
    """Generate AI-powered property description."""
    check_rate_limit(request)
    request_id = str(uuid.uuid4())
    
    with RequestLogger(request_id, "/property/description", "POST"):
        try:
            description = await openrouter_service.generate_property_description(property_data)
            
            return {
                "description": description,
                "generated_at": datetime.utcnow().isoformat(),
                "property_id": str(uuid.uuid4())
            }
            
        except Exception as e:
            logger.error(f"Description generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Description generation service temporarily unavailable")


@api_router.get("/stats")
async def get_api_stats(request: Request):
    """Get API usage statistics."""
    request_id = str(uuid.uuid4())
    
    with RequestLogger(request_id, "/stats", "GET"):
        # Simple stats (in production, use proper metrics storage)
        total_requests = sum(len(requests) for requests in rate_limit_storage.values())
        
        return {
            "total_requests_last_minute": total_requests,
            "active_clients": len(rate_limit_storage),
            "service_uptime": "Available",
            "timestamp": datetime.utcnow().isoformat()
        }


@api_router.get("/config")
async def get_api_config(request: Request):
    """Get API configuration information."""
    return {
        "version": settings.VERSION,
        "features": {
            "ai_enrichment": settings.ENABLE_AI_ENRICHMENT,
            "model_monitoring": settings.ENABLE_MODEL_MONITORING,
            "batch_prediction": True,
            "market_analysis": True
        },
        "limits": {
            "max_batch_size": settings.MAX_PREDICTION_BATCH_SIZE,
            "rate_limit_per_minute": settings.RATE_LIMIT_PER_MINUTE
        },
        "supported_models": ["xgboost", "lightgbm", "random_forest", "gradient_boosting", "ensemble"],
        "supported_property_types": ["apartment", "house", "condo", "townhouse", "villa", "commercial", "land"],
        "supported_locations": ["yangon", "mandalay", "naypyidaw", "bago", "mawlamyine"]
    }


# Error handlers for specific exceptions
# Note: Exception handlers should be added to the main app, not the router
# This will be moved to main.py
async def rate_limit_exception_handler(request: Request, exc: RateLimitException):
    """Handle rate limit exceptions."""
    return JSONResponse(
        status_code=429,
        content={
            "error": True,
            "message": "Rate limit exceeded",
            "retry_after": exc.details.get("retry_after", 60)
        },
        headers={"Retry-After": str(exc.details.get("retry_after", 60))}
    )