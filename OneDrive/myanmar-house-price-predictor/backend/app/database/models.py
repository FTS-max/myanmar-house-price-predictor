#!/usr/bin/env python3
"""
SQLAlchemy database models for Myanmar House Price Predictor.

Defines database tables for properties, predictions, and related data.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.database.database import Base


class Property(Base):
    """Property model for storing property data."""
    __tablename__ = "properties"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic property information
    property_type = Column(String(50), nullable=False, index=True)
    condition = Column(String(50), nullable=False)
    size_sqft = Column(Float, nullable=False)
    lot_size_sqft = Column(Float, nullable=True)
    year_built = Column(Integer, nullable=True)
    
    # Location information
    city = Column(String(100), nullable=False, index=True)
    township = Column(String(100), nullable=False, index=True)
    ward = Column(String(100), nullable=True)
    street = Column(String(200), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_tier = Column(String(20), nullable=True)
    
    # Property features
    bedrooms = Column(Integer, nullable=False)
    bathrooms = Column(Integer, nullable=False)
    floors = Column(Integer, default=1)
    parking_spaces = Column(Integer, default=0)
    
    # Amenities (boolean flags)
    has_elevator = Column(Boolean, default=False)
    has_swimming_pool = Column(Boolean, default=False)
    has_gym = Column(Boolean, default=False)
    has_security = Column(Boolean, default=False)
    has_garden = Column(Boolean, default=False)
    has_air_conditioning = Column(Boolean, default=False)
    
    # Additional information
    description = Column(Text, nullable=True)
    images = Column(JSON, nullable=True)  # Store image URLs as JSON array
    
    # Market data and neighborhood features
    nearby_schools = Column(Integer, default=0)
    nearby_hospitals = Column(Integer, default=0)
    nearby_markets = Column(Integer, default=0)
    nearby_restaurants = Column(Integer, default=0)
    nearby_banks = Column(Integer, default=0)
    nearby_shopping_malls = Column(Integer, default=0)
    distance_to_city_center_km = Column(Float, nullable=True)
    distance_to_nearest_school_km = Column(Float, nullable=True)
    distance_to_nearest_hospital_km = Column(Float, nullable=True)
    public_transport_access = Column(Boolean, default=False)
    road_quality_score = Column(Float, nullable=True)  # 1-10 scale
    noise_level = Column(String(20), nullable=True)  # low, medium, high
    flood_risk = Column(String(20), nullable=True)  # low, medium, high
    crime_rate_score = Column(Float, nullable=True)  # 1-10 scale (lower is better)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    predictions = relationship("Prediction", back_populates="property", cascade="all, delete-orphan")
    
    # Indexes for better query performance
    __table_args__ = (
        Index('idx_property_location', 'city', 'township'),
        Index('idx_property_type_size', 'property_type', 'size_sqft'),
        Index('idx_property_price_range', 'size_sqft', 'bedrooms', 'bathrooms'),
    )


class Prediction(Base):
    """Prediction model for storing price predictions."""
    __tablename__ = "predictions"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to property
    property_id = Column(String, ForeignKey("properties.id"), nullable=False, index=True)
    
    # Prediction results
    predicted_price_mmk = Column(Float, nullable=False)
    predicted_price_usd = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    price_range_min_mmk = Column(Float, nullable=False)
    price_range_max_mmk = Column(Float, nullable=False)
    price_range_min_usd = Column(Float, nullable=False)
    price_range_max_usd = Column(Float, nullable=False)
    
    # Model information
    model_used = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=True)
    feature_importance = Column(JSON, nullable=True)  # Store feature importance as JSON
    
    # AI enrichment data
    ai_enriched = Column(Boolean, default=False)
    ai_enrichment_data = Column(JSON, nullable=True)
    market_analysis = Column(JSON, nullable=True)
    
    # Request metadata
    request_id = Column(String, nullable=True, index=True)
    batch_id = Column(String, nullable=True, index=True)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    property = relationship("Property", back_populates="predictions")
    
    # Indexes
    __table_args__ = (
        Index('idx_prediction_timestamp', 'created_at'),
        Index('idx_prediction_model', 'model_used', 'created_at'),
        Index('idx_prediction_batch', 'batch_id'),
    )


class ModelMetrics(Base):
    """Model performance metrics storage."""
    __tablename__ = "model_metrics"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Model information
    model_name = Column(String(100), nullable=False, index=True)
    model_version = Column(String(50), nullable=False)
    
    # Performance metrics
    mae = Column(Float, nullable=False)  # Mean Absolute Error
    rmse = Column(Float, nullable=False)  # Root Mean Square Error
    r2_score = Column(Float, nullable=False)  # R-squared
    mape = Column(Float, nullable=False)  # Mean Absolute Percentage Error
    
    # Training information
    training_samples = Column(Integer, nullable=False)
    validation_samples = Column(Integer, nullable=False)
    feature_count = Column(Integer, nullable=False)
    training_duration_seconds = Column(Float, nullable=False)
    
    # Feature importance and model details
    feature_importance = Column(JSON, nullable=True)
    hyperparameters = Column(JSON, nullable=True)
    cross_validation_scores = Column(JSON, nullable=True)
    
    # Timestamps
    trained_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_model_performance', 'model_name', 'trained_at'),
    )


class APIUsage(Base):
    """API usage tracking."""
    __tablename__ = "api_usage"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Request information
    endpoint = Column(String(200), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Float, nullable=False)
    
    # Request metadata
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True, index=True)
    request_size_bytes = Column(Integer, nullable=True)
    response_size_bytes = Column(Integer, nullable=True)
    
    # Feature usage
    ai_enrichment_used = Column(Boolean, default=False)
    model_used = Column(String(100), nullable=True)
    batch_size = Column(Integer, nullable=True)
    
    # Error information
    error_type = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_api_usage_endpoint_time', 'endpoint', 'timestamp'),
        Index('idx_api_usage_ip_time', 'ip_address', 'timestamp'),
        Index('idx_api_usage_status', 'status_code', 'timestamp'),
    )


class MarketData(Base):
    """Market data and trends storage."""
    __tablename__ = "market_data"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Location information
    city = Column(String(100), nullable=False, index=True)
    township = Column(String(100), nullable=False, index=True)
    property_type = Column(String(50), nullable=False, index=True)
    
    # Market metrics
    average_price_mmk = Column(Float, nullable=False)
    average_price_usd = Column(Float, nullable=False)
    median_price_mmk = Column(Float, nullable=False)
    median_price_usd = Column(Float, nullable=False)
    price_per_sqft_mmk = Column(Float, nullable=False)
    price_per_sqft_usd = Column(Float, nullable=False)
    
    # Market activity
    total_listings = Column(Integer, nullable=False)
    active_listings = Column(Integer, nullable=False)
    sold_listings = Column(Integer, nullable=False)
    average_days_on_market = Column(Float, nullable=True)
    
    # Price ranges
    min_price_mmk = Column(Float, nullable=False)
    max_price_mmk = Column(Float, nullable=False)
    price_distribution = Column(JSON, nullable=True)  # Price distribution data
    
    # Trends
    price_trend_1m = Column(Float, nullable=True)  # 1-month price change %
    price_trend_3m = Column(Float, nullable=True)  # 3-month price change %
    price_trend_6m = Column(Float, nullable=True)  # 6-month price change %
    price_trend_1y = Column(Float, nullable=True)  # 1-year price change %
    
    # Analysis period
    analysis_start_date = Column(DateTime(timezone=True), nullable=False)
    analysis_end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_market_location_type', 'city', 'township', 'property_type'),
        Index('idx_market_analysis_period', 'analysis_start_date', 'analysis_end_date'),
    )
