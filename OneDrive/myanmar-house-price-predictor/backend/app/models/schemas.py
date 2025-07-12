#!/usr/bin/env python3
"""
Pydantic models for Myanmar House Price Predictor API.

Defines request/response schemas, data validation, and serialization models.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
import re


class PropertyType(str, Enum):
    """Property type enumeration."""
    APARTMENT = "apartment"
    HOUSE = "house"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    VILLA = "villa"
    COMMERCIAL = "commercial"
    LAND = "land"


class PropertyCondition(str, Enum):
    """Property condition enumeration."""
    NEW = "new"
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    RENOVATION_NEEDED = "renovation_needed"


class LocationTier(str, Enum):
    """Location tier based on desirability and development."""
    TIER_1 = "tier_1"  # Prime locations (Yangon CBD, etc.)
    TIER_2 = "tier_2"  # Secondary locations
    TIER_3 = "tier_3"  # Developing areas
    TIER_4 = "tier_4"  # Rural/remote areas


class PropertyLocation(BaseModel):
    """Property location information."""
    city: str = Field(..., min_length=1, max_length=100)
    township: str = Field(..., min_length=1, max_length=100)
    ward: Optional[str] = Field(None, max_length=100)
    street: Optional[str] = Field(None, max_length=200)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    location_tier: Optional[LocationTier] = None
    
    @field_validator('city', 'township')
    @classmethod
    def validate_location_names(cls, v):
        if not re.match(r'^[a-zA-Z\s\u1000-\u109F]+$', v):
            raise ValueError('Location names must contain only letters and spaces (English/Myanmar)')
        return v.strip().title()


class NoiseLevel(str, Enum):
    """Noise level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskLevel(str, Enum):
    """Risk level enumeration for flood and other risks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PropertyFeatures(BaseModel):
    """Property features and amenities."""
    bedrooms: int = Field(..., ge=0, le=20)
    bathrooms: int = Field(..., ge=0, le=20)
    floors: int = Field(1, ge=1, le=50)
    parking_spaces: int = Field(0, ge=0, le=20)
    balconies: int = Field(0, ge=0, le=10)
    
    # Amenities
    has_elevator: bool = False
    has_swimming_pool: bool = False
    has_gym: bool = False
    has_security: bool = False
    has_generator: bool = False
    has_water_tank: bool = False
    has_garden: bool = False
    has_garage: bool = False
    
    # Utilities
    has_internet: bool = False
    has_cable_tv: bool = False
    has_air_conditioning: bool = False
    
    @field_validator('bathrooms')
    @classmethod
    def validate_bathrooms(cls, v, info):
        if info.data and 'bedrooms' in info.data and v > info.data['bedrooms'] + 2:
            raise ValueError('Number of bathrooms seems unrealistic compared to bedrooms')
        return v


class NeighborhoodFeatures(BaseModel):
    """Neighborhood and location-based features for enhanced ML predictions."""
    nearby_schools: int = Field(0, ge=0, le=50, description="Number of schools within 2km")
    nearby_hospitals: int = Field(0, ge=0, le=20, description="Number of hospitals within 5km")
    nearby_markets: int = Field(0, ge=0, le=100, description="Number of markets within 1km")
    nearby_restaurants: int = Field(0, ge=0, le=200, description="Number of restaurants within 1km")
    nearby_banks: int = Field(0, ge=0, le=50, description="Number of banks within 2km")
    nearby_shopping_malls: int = Field(0, ge=0, le=10, description="Number of shopping malls within 5km")
    
    # Distance-based features
    distance_to_city_center_km: Optional[float] = Field(None, ge=0, le=200, description="Distance to city center in km")
    distance_to_nearest_school_km: Optional[float] = Field(None, ge=0, le=50, description="Distance to nearest school in km")
    distance_to_nearest_hospital_km: Optional[float] = Field(None, ge=0, le=100, description="Distance to nearest hospital in km")
    
    # Quality and risk factors
    public_transport_access: bool = Field(False, description="Access to public transportation")
    road_quality_score: Optional[float] = Field(None, ge=1, le=10, description="Road quality score (1-10, higher is better)")
    noise_level: Optional[NoiseLevel] = Field(None, description="Neighborhood noise level")
    flood_risk: Optional[RiskLevel] = Field(None, description="Flood risk assessment")
    crime_rate_score: Optional[float] = Field(None, ge=1, le=10, description="Crime rate score (1-10, lower is better)")
    
    @field_validator('distance_to_nearest_school_km')
    @classmethod
    def validate_school_distance(cls, v, info):
        if v is not None and info.data and 'nearby_schools' in info.data:
            if info.data['nearby_schools'] > 0 and v > 10:
                raise ValueError('If schools are nearby, distance should be reasonable')
        return v


class PropertyBase(BaseModel):
    """Base property model with common fields."""
    property_type: PropertyType
    condition: PropertyCondition
    size_sqft: float = Field(..., gt=0, le=50000)
    lot_size_sqft: Optional[float] = Field(None, gt=0, le=1000000)
    year_built: Optional[int] = Field(None, ge=1900, le=2030)
    location: PropertyLocation
    features: PropertyFeatures
    neighborhood: Optional[NeighborhoodFeatures] = Field(None, description="Neighborhood and location-based features")
    description: Optional[str] = Field(None, max_length=2000)
    
    @field_validator('year_built')
    @classmethod
    def validate_year_built(cls, v):
        if v and v > datetime.now().year + 2:
            raise ValueError('Year built cannot be more than 2 years in the future')
        return v
    
    @field_validator('lot_size_sqft')
    @classmethod
    def validate_lot_size(cls, v, info):
        if v and info.data and 'size_sqft' in info.data and v < info.data['size_sqft']:
            raise ValueError('Lot size cannot be smaller than building size')
        return v


class PropertyCreate(PropertyBase):
    """Schema for creating a new property."""
    pass


class PropertyUpdate(BaseModel):
    """Schema for updating an existing property."""
    property_type: Optional[PropertyType] = None
    condition: Optional[PropertyCondition] = None
    size_sqft: Optional[float] = Field(None, gt=0, le=50000)
    lot_size_sqft: Optional[float] = Field(None, gt=0, le=1000000)
    year_built: Optional[int] = Field(None, ge=1900, le=2030)
    location: Optional[PropertyLocation] = None
    features: Optional[PropertyFeatures] = None
    neighborhood: Optional[NeighborhoodFeatures] = None
    description: Optional[str] = Field(None, max_length=2000)


class PropertyInDB(PropertyBase):
    """Property model as stored in database."""
    id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class PropertyResponse(PropertyInDB):
    """Property response model."""
    pass


class PredictionRequest(PropertyBase):
    """Request model for price prediction."""
    enable_ai_enrichment: bool = Field(default=True, description="Enable AI-powered data enrichment")
    model_preference: Optional[str] = Field(None, description="Preferred ML model (xgboost, lightgbm, ensemble)")
    
    model_config = {"protected_namespaces": ()}


class PredictionResponse(BaseModel):
    """Response model for price prediction."""
    predicted_price_mmk: float = Field(..., description="Predicted price in Myanmar Kyat")
    predicted_price_usd: float = Field(..., description="Predicted price in USD")
    confidence_score: float = Field(..., ge=0, le=1, description="Prediction confidence (0-1)")
    price_range_mmk: Dict[str, float] = Field(..., description="Price range (min, max) in MMK")
    price_range_usd: Dict[str, float] = Field(..., description="Price range (min, max) in USD")
    model_used: str = Field(..., description="ML model used for prediction")
    feature_importance: Dict[str, float] = Field(..., description="Feature importance scores")
    market_insights: Optional[Dict[str, Any]] = Field(None, description="AI-generated market insights")
    comparable_properties: Optional[List[Dict[str, Any]]] = Field(None, description="Similar properties for comparison")
    prediction_id: str = Field(..., description="Unique prediction identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {"protected_namespaces": ()}


class BatchPredictionRequest(BaseModel):
    """Request model for batch price predictions."""
    properties: List[PredictionRequest] = Field(..., max_items=100)
    enable_ai_enrichment: bool = Field(default=True)
    model_preference: Optional[str] = None
    
    model_config = {"protected_namespaces": ()}


class BatchPredictionResponse(BaseModel):
    """Response model for batch price predictions."""
    predictions: List[PredictionResponse]
    batch_id: str
    total_processed: int
    processing_time_seconds: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MarketAnalysisRequest(BaseModel):
    """Request model for market analysis."""
    location: PropertyLocation
    property_type: Optional[PropertyType] = None
    size_range: Optional[Dict[str, float]] = Field(None, description="Size range (min_sqft, max_sqft)")
    price_range: Optional[Dict[str, float]] = Field(None, description="Price range (min_mmk, max_mmk)")
    time_period_months: int = Field(12, ge=1, le=60, description="Analysis time period in months")


class MarketAnalysisResponse(BaseModel):
    """Response model for market analysis."""
    location_summary: Dict[str, Any]
    average_price_mmk: float
    average_price_usd: float
    price_trends: Dict[str, Any]
    market_activity: Dict[str, Any]
    price_distribution: Dict[str, Any]
    recommendations: List[str]
    analysis_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ModelPerformanceMetrics(BaseModel):
    """Model performance metrics."""
    model_name: str
    mae: float = Field(..., description="Mean Absolute Error")
    rmse: float = Field(..., description="Root Mean Square Error")
    r2_score: float = Field(..., description="R-squared score")
    mape: float = Field(..., description="Mean Absolute Percentage Error")
    training_samples: int
    last_updated: datetime
    feature_count: int
    
    model_config = {"protected_namespaces": ()}


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str
    service: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    components: Dict[str, str] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response model."""
    error: bool = True
    status_code: int
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)