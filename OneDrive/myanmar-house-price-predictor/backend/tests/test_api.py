#!/usr/bin/env python3
"""
API endpoint tests for Myanmar House Price Predictor.

Tests all REST API endpoints for functionality and error handling.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    async def test_health_check(self, test_client: AsyncClient):
        """Test basic health check endpoint."""
        response = await test_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "components" in data
    
    async def test_health_detailed(self, test_client: AsyncClient):
        """Test detailed health check endpoint."""
        response = await test_client.get("/health/detailed")
        assert response.status_code == 200
        
        data = response.json()
        assert "services" in data
        assert "uptime_seconds" in data


class TestPredictionEndpoints:
    """Test prediction endpoints."""
    
    @patch('app.services.ml_service.MLModelManager.predict')
    async def test_single_prediction(self, mock_predict, test_client: AsyncClient, sample_prediction_request, test_utils):
        """Test single property prediction."""
        # Mock ML service response
        mock_predict.return_value = {
            "predicted_price_mmk": 150000000.0,
            "predicted_price_usd": 75000.0,
            "confidence_score": 0.85,
            "price_range_mmk": {"min": 140000000.0, "max": 160000000.0},
            "price_range_usd": {"min": 70000.0, "max": 80000.0},
            "model_used": "ensemble",
            "feature_importance": {"size_sqft": 0.3, "location": 0.25}
        }
        
        response = await test_client.post("/api/v1/predict", json=sample_prediction_request)
        assert response.status_code == 200
        
        data = response.json()
        test_utils.assert_prediction_response(data)
        assert data["model_used"] == "ensemble"
    
    @patch('app.services.ml_service.MLModelManager.predict_batch')
    async def test_batch_prediction(self, mock_predict_batch, test_client: AsyncClient, sample_batch_prediction_request, test_utils):
        """Test batch property prediction."""
        # Mock ML service response
        mock_predict_batch.return_value = {
            "predictions": [
                {
                    "predicted_price_mmk": 150000000.0,
                    "predicted_price_usd": 75000.0,
                    "confidence_score": 0.85,
                    "price_range_mmk": {"min": 140000000.0, "max": 160000000.0},
                    "price_range_usd": {"min": 70000.0, "max": 80000.0},
                    "model_used": "ensemble",
                    "feature_importance": {"size_sqft": 0.3}
                }
            ] * 2,
            "batch_id": "test-batch-123",
            "processing_time_seconds": 1.5
        }
        
        response = await test_client.post("/api/v1/predict/batch", json=sample_batch_prediction_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "predictions" in data
        assert "batch_id" in data
        assert "total_processed" in data
        assert len(data["predictions"]) == 2
        
        for prediction in data["predictions"]:
            test_utils.assert_prediction_response(prediction)
    
    async def test_prediction_validation_error(self, test_client: AsyncClient, test_utils):
        """Test prediction with invalid data."""
        invalid_request = {
            "property_type": "invalid_type",
            "condition": "good",
            "size_sqft": -100,  # Invalid negative size
        }
        
        response = await test_client.post("/api/v1/predict", json=invalid_request)
        assert response.status_code == 422
        
        data = response.json()
        assert "detail" in data
    
    async def test_prediction_missing_fields(self, test_client: AsyncClient):
        """Test prediction with missing required fields."""
        incomplete_request = {
            "property_type": "apartment"
            # Missing required fields
        }
        
        response = await test_client.post("/api/v1/predict", json=incomplete_request)
        assert response.status_code == 422


class TestMarketAnalysisEndpoints:
    """Test market analysis endpoints."""
    
    @patch('app.services.openrouter_service.OpenRouterService.analyze_market')
    async def test_market_analysis(self, mock_analyze, test_client: AsyncClient, sample_market_analysis_request):
        """Test market analysis endpoint."""
        # Mock OpenRouter service response
        mock_analyze.return_value = {
            "location_summary": {
                "area": "Kamayut Township, Yangon",
                "description": "Prime residential area"
            },
            "average_price_mmk": 180000000.0,
            "average_price_usd": 90000.0,
            "price_trends": {
                "1_month": 2.5,
                "3_months": 5.0,
                "6_months": 8.0
            },
            "market_activity": {
                "total_listings": 150,
                "active_listings": 45
            },
            "recommendations": [
                "Good investment potential",
                "Strong rental demand"
            ]
        }
        
        response = await test_client.post("/api/v1/market/analyze", json=sample_market_analysis_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "location_summary" in data
        assert "average_price_mmk" in data
        assert "price_trends" in data
        assert "recommendations" in data
    
    async def test_market_analysis_invalid_location(self, test_client: AsyncClient):
        """Test market analysis with invalid location."""
        invalid_request = {
            "location": {
                "city": "",  # Empty city
                "township": "Kamayut"
            }
        }
        
        response = await test_client.post("/api/v1/market/analyze", json=invalid_request)
        assert response.status_code == 422


class TestModelEndpoints:
    """Test ML model endpoints."""
    
    @patch('app.services.ml_service.MLModelManager.get_model_performance')
    async def test_model_performance(self, mock_performance, test_client: AsyncClient):
        """Test model performance endpoint."""
        # Mock ML service response
        mock_performance.return_value = {
            "ensemble": {
                "model_name": "ensemble",
                "mae": 15000000.0,
                "rmse": 25000000.0,
                "r2_score": 0.85,
                "mape": 12.5,
                "training_samples": 1000,
                "last_updated": "2024-01-01T00:00:00Z",
                "feature_count": 15
            }
        }
        
        response = await test_client.get("/api/v1/models/performance")
        assert response.status_code == 200
        
        data = response.json()
        assert "ensemble" in data
        assert data["ensemble"]["model_name"] == "ensemble"
        assert "mae" in data["ensemble"]
        assert "r2_score" in data["ensemble"]
    
    @patch('app.services.ml_service.MLModelManager.retrain_models')
    async def test_model_retrain(self, mock_retrain, test_client: AsyncClient):
        """Test model retraining endpoint."""
        mock_retrain.return_value = {
            "status": "success",
            "models_retrained": ["xgboost", "lightgbm", "random_forest"],
            "training_time_seconds": 120.5
        }
        
        response = await test_client.post("/api/v1/models/retrain")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "models_retrained" in data
        assert "training_time_seconds" in data


class TestAIEndpoints:
    """Test AI-powered endpoints."""
    
    @patch('app.services.openrouter_service.OpenRouterService.generate_property_description')
    async def test_generate_description(self, mock_generate, test_client: AsyncClient, sample_property_data):
        """Test AI property description generation."""
        # Mock OpenRouter service response
        mock_generate.return_value = {
            "description": "Beautiful 3-bedroom apartment in prime Kamayut location...",
            "key_highlights": [
                "Prime location in Kamayut",
                "Modern amenities",
                "Excellent connectivity"
            ],
            "suggested_price_range": "140-160 million MMK"
        }
        
        request_data = {
            "property_data": sample_property_data,
            "style": "professional",
            "language": "english",
            "max_length": 500
        }
        
        response = await test_client.post("/api/v1/ai/generate-description", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "description" in data
        assert "key_highlights" in data
        assert len(data["description"]) > 0
        assert isinstance(data["key_highlights"], list)


class TestStatsEndpoints:
    """Test statistics endpoints."""
    
    async def test_api_stats(self, test_client: AsyncClient):
        """Test API usage statistics endpoint."""
        response = await test_client.get("/api/v1/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_predictions" in data
        assert "predictions_today" in data
        assert "average_response_time_ms" in data
        assert "active_models" in data
        assert "uptime_hours" in data
    
    async def test_config_info(self, test_client: AsyncClient):
        """Test configuration information endpoint."""
        response = await test_client.get("/api/v1/config")
        assert response.status_code == 200
        
        data = response.json()
        assert "app_name" in data
        assert "version" in data
        assert "features" in data
        assert "rate_limits" in data


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    async def test_rate_limit_exceeded(self, test_client: AsyncClient, sample_prediction_request):
        """Test rate limiting when limit is exceeded."""
        # Make multiple rapid requests to trigger rate limiting
        responses = []
        for _ in range(70):  # Exceed the default limit of 60 per minute
            response = await test_client.post("/api/v1/predict", json=sample_prediction_request)
            responses.append(response)
        
        # At least one response should be rate limited
        rate_limited = any(r.status_code == 429 for r in responses)
        assert rate_limited, "Rate limiting should have been triggered"


class TestErrorHandling:
    """Test error handling scenarios."""
    
    async def test_404_endpoint(self, test_client: AsyncClient):
        """Test non-existent endpoint."""
        response = await test_client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    async def test_method_not_allowed(self, test_client: AsyncClient):
        """Test wrong HTTP method."""
        response = await test_client.delete("/api/v1/predict")
        assert response.status_code == 405
    
    @patch('app.services.ml_service.MLModelManager.predict')
    async def test_internal_server_error(self, mock_predict, test_client: AsyncClient, sample_prediction_request, test_utils):
        """Test internal server error handling."""
        # Mock ML service to raise an exception
        mock_predict.side_effect = Exception("Internal error")
        
        response = await test_client.post("/api/v1/predict", json=sample_prediction_request)
        assert response.status_code == 500
        
        data = response.json()
        test_utils.assert_error_response(data)