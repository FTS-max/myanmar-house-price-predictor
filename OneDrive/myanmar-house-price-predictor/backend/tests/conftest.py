#!/usr/bin/env python3
"""
Pytest configuration and fixtures for Myanmar House Price Predictor tests.

Provides test database, client, and common fixtures.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
import tempfile
import os

from app.main import app
from app.database.database import Base, get_db
from app.core.config import Settings
from app.services.ml_service import MLModelManager
from app.services.openrouter_service import OpenRouterService


# Test settings
test_settings = Settings(
    DATABASE_URL="sqlite+aiosqlite:///:memory:",
    DEBUG=True,
    SECRET_KEY="test-secret-key",
    OPENROUTER_API_KEY="test-api-key",
    MODEL_PATH="./test_models",
    DATA_PATH="./test_data",
    ENABLE_AI_ENRICHMENT=False,  # Disable for tests
    ENABLE_MODEL_MONITORING=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        test_settings.DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def test_client(test_session) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client."""
    # Override database dependency
    async def override_get_db():
        yield test_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def sample_property_data():
    """Sample property data for testing."""
    return {
        "property_type": "apartment",
        "condition": "good",
        "size_sqft": 1200.0,
        "lot_size_sqft": None,
        "year_built": 2015,
        "location": {
            "city": "Yangon",
            "township": "Kamayut",
            "ward": "Ward 1",
            "street": "Main Street",
            "latitude": 16.8661,
            "longitude": 96.1951
        },
        "features": {
            "bedrooms": 3,
            "bathrooms": 2,
            "floors": 1,
            "parking_spaces": 1,
            "has_elevator": True,
            "has_swimming_pool": False,
            "has_gym": False,
            "has_security": True,
            "has_garden": False,
            "has_air_conditioning": True
        },
        "description": "Beautiful apartment in prime location"
    }


@pytest.fixture
def sample_prediction_request(sample_property_data):
    """Sample prediction request for testing."""
    return {
        **sample_property_data,
        "enable_ai_enrichment": False,
        "model_preference": "ensemble"
    }


@pytest.fixture
def sample_batch_prediction_request(sample_property_data):
    """Sample batch prediction request for testing."""
    return {
        "properties": [sample_property_data, sample_property_data],
        "enable_ai_enrichment": False,
        "model_preference": "ensemble"
    }


@pytest.fixture
def sample_market_analysis_request():
    """Sample market analysis request for testing."""
    return {
        "location": {
            "city": "Yangon",
            "township": "Kamayut"
        },
        "property_type": "apartment",
        "size_range": {"min_sqft": 800, "max_sqft": 1500},
        "price_range": {"min_mmk": 100000000, "max_mmk": 300000000},
        "time_period_months": 12
    }


@pytest.fixture
async def mock_ml_service():
    """Mock ML service for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        ml_service = MLModelManager(model_path=temp_dir)
        # Initialize with minimal training data
        await ml_service.initialize()
        yield ml_service


@pytest.fixture
def mock_openrouter_service():
    """Mock OpenRouter service for testing."""
    service = OpenRouterService(
        api_key="test-key",
        base_url="http://test-api",
        model="test-model"
    )
    return service


@pytest.fixture
def mock_property_in_db():
    """Mock property database record."""
    from app.database.models import Property
    from datetime import datetime
    
    return Property(
        id="test-property-id",
        property_type="apartment",
        condition="good",
        size_sqft=1200.0,
        year_built=2015,
        city="Yangon",
        township="Kamayut",
        bedrooms=3,
        bathrooms=2,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def mock_prediction_in_db():
    """Mock prediction database record."""
    from app.database.models import Prediction
    from datetime import datetime
    
    return Prediction(
        id="test-prediction-id",
        property_id="test-property-id",
        predicted_price_mmk=150000000.0,
        predicted_price_usd=75000.0,
        confidence_score=0.85,
        price_range_min_mmk=140000000.0,
        price_range_max_mmk=160000000.0,
        price_range_min_usd=70000.0,
        price_range_max_usd=80000.0,
        model_used="ensemble",
        created_at=datetime.utcnow()
    )


# Test utilities
class TestUtils:
    """Utility functions for tests."""
    
    @staticmethod
    def assert_prediction_response(response_data: dict):
        """Assert prediction response structure."""
        required_fields = [
            "predicted_price_mmk",
            "predicted_price_usd",
            "confidence_score",
            "price_range_mmk",
            "price_range_usd",
            "model_used",
            "prediction_id",
            "timestamp"
        ]
        
        for field in required_fields:
            assert field in response_data, f"Missing field: {field}"
        
        assert 0 <= response_data["confidence_score"] <= 1
        assert response_data["predicted_price_mmk"] > 0
        assert response_data["predicted_price_usd"] > 0
    
    @staticmethod
    def assert_error_response(response_data: dict):
        """Assert error response structure."""
        required_fields = ["error", "message", "timestamp"]
        
        for field in required_fields:
            assert field in response_data, f"Missing field: {field}"
        
        assert response_data["error"] is True


@pytest.fixture
def test_utils():
    """Test utilities fixture."""
    return TestUtils