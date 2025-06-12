#!/usr/bin/env python3
"""
Machine Learning Service for Myanmar House Price Predictor.

Handles model training, prediction, and performance monitoring with multiple ML algorithms.
"""

import asyncio
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
from loguru import logger

# ML imports
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import lightgbm as lgb

from ..core.config import settings
from ..core.exceptions import MLModelException
from ..core.logging import log_ml_prediction, log_model_performance
from ..models.schemas import (
    PropertyBase, PredictionResponse, ModelPerformanceMetrics,
    PropertyType, PropertyCondition, LocationTier
)


class FeatureEngineer:
    """Feature engineering for property data."""
    
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_fitted = False
    
    def create_features(self, property_data: PropertyBase) -> Dict[str, float]:
        """Create engineered features from property data."""
        features = {}
        
        # Basic property features
        features['size_sqft'] = property_data.size_sqft
        features['lot_size_sqft'] = property_data.lot_size_sqft or property_data.size_sqft
        features['bedrooms'] = property_data.features.bedrooms
        features['bathrooms'] = property_data.features.bathrooms
        features['floors'] = property_data.features.floors
        features['parking_spaces'] = property_data.features.parking_spaces
        
        # Property age and age-related features
        current_year = datetime.now().year
        features['property_age'] = current_year - (property_data.year_built or current_year)
        features['is_new_construction'] = 1.0 if features['property_age'] <= 2 else 0.0
        features['is_vintage'] = 1.0 if features['property_age'] >= 30 else 0.0
        
        # Enhanced derived features
        features['sqft_per_bedroom'] = property_data.size_sqft / max(property_data.features.bedrooms, 1)
        features['bathroom_bedroom_ratio'] = property_data.features.bathrooms / max(property_data.features.bedrooms, 1)
        features['lot_building_ratio'] = features['lot_size_sqft'] / property_data.size_sqft
        features['parking_per_bedroom'] = property_data.features.parking_spaces / max(property_data.features.bedrooms, 1)
        
        # Amenity score
        amenities = [
            property_data.features.has_elevator,
            property_data.features.has_swimming_pool,
            property_data.features.has_gym,
            property_data.features.has_security,
            property_data.features.has_generator,
            property_data.features.has_water_tank,
            property_data.features.has_garden,
            property_data.features.has_garage,
            property_data.features.has_internet,
            property_data.features.has_cable_tv,
            property_data.features.has_air_conditioning
        ]
        features['amenity_score'] = sum(amenities) / len(amenities)
        features['luxury_amenity_score'] = sum([
            property_data.features.has_elevator,
            property_data.features.has_swimming_pool,
            property_data.features.has_gym
        ]) / 3.0
        
        # Neighborhood features (enhanced)
        if property_data.neighborhood:
            neighborhood = property_data.neighborhood
            
            # Direct neighborhood counts
            features['nearby_schools'] = neighborhood.nearby_schools
            features['nearby_hospitals'] = neighborhood.nearby_hospitals
            features['nearby_markets'] = neighborhood.nearby_markets
            features['nearby_restaurants'] = neighborhood.nearby_restaurants
            features['nearby_banks'] = neighborhood.nearby_banks
            features['nearby_shopping_malls'] = neighborhood.nearby_shopping_malls
            
            # Distance features
            features['distance_to_city_center_km'] = neighborhood.distance_to_city_center_km or 50.0
            features['distance_to_nearest_school_km'] = neighborhood.distance_to_nearest_school_km or 10.0
            features['distance_to_nearest_hospital_km'] = neighborhood.distance_to_nearest_hospital_km or 20.0
            
            # Convenience scores
            features['education_convenience'] = min(neighborhood.nearby_schools / 5.0, 1.0) * (1.0 / max(features['distance_to_nearest_school_km'], 0.1))
            features['healthcare_convenience'] = min(neighborhood.nearby_hospitals / 3.0, 1.0) * (1.0 / max(features['distance_to_nearest_hospital_km'], 0.1))
            features['commercial_convenience'] = (neighborhood.nearby_markets + neighborhood.nearby_restaurants + neighborhood.nearby_banks) / 50.0
            
            # Quality and risk factors
            features['public_transport_access'] = 1.0 if neighborhood.public_transport_access else 0.0
            features['road_quality_score'] = neighborhood.road_quality_score or 5.0
            
            # Encode categorical risk factors
            noise_mapping = {'low': 1.0, 'medium': 0.5, 'high': 0.0}
            risk_mapping = {'low': 1.0, 'medium': 0.5, 'high': 0.0}
            
            features['noise_quality_score'] = noise_mapping.get(neighborhood.noise_level.value if neighborhood.noise_level else 'medium', 0.5)
            features['flood_safety_score'] = risk_mapping.get(neighborhood.flood_risk.value if neighborhood.flood_risk else 'medium', 0.5)
            features['crime_safety_score'] = (10.0 - (neighborhood.crime_rate_score or 5.0)) / 10.0
            
            # Composite neighborhood score
            features['neighborhood_quality_score'] = (
                features['education_convenience'] * 0.25 +
                features['healthcare_convenience'] * 0.20 +
                features['commercial_convenience'] * 0.15 +
                features['public_transport_access'] * 0.15 +
                (features['road_quality_score'] / 10.0) * 0.10 +
                features['noise_quality_score'] * 0.05 +
                features['flood_safety_score'] * 0.05 +
                features['crime_safety_score'] * 0.05
            )
        else:
            # Default values for backward compatibility
            default_neighborhood_features = {
                'nearby_schools': 2, 'nearby_hospitals': 1, 'nearby_markets': 5,
                'nearby_restaurants': 10, 'nearby_banks': 2, 'nearby_shopping_malls': 1,
                'distance_to_city_center_km': 25.0, 'distance_to_nearest_school_km': 5.0,
                'distance_to_nearest_hospital_km': 10.0, 'education_convenience': 0.4,
                'healthcare_convenience': 0.3, 'commercial_convenience': 0.3,
                'public_transport_access': 0.0, 'road_quality_score': 5.0,
                'noise_quality_score': 0.5, 'flood_safety_score': 0.5,
                'crime_safety_score': 0.5, 'neighborhood_quality_score': 0.4
            }
            features.update(default_neighborhood_features)
        
        # Categorical features (will be encoded)
        features['property_type'] = property_data.property_type.value
        features['condition'] = property_data.condition.value
        features['city'] = property_data.location.city.lower()
        features['township'] = property_data.location.township.lower()
        features['location_tier'] = property_data.location.location_tier.value if property_data.location.location_tier else 'tier_3'
        
        # Location-based features
        if property_data.location.latitude and property_data.location.longitude:
            # Distance from Yangon CBD (approximate coordinates)
            yangon_cbd_lat, yangon_cbd_lon = 16.7967, 96.1610
            features['distance_from_cbd'] = self._calculate_distance(
                property_data.location.latitude, property_data.location.longitude,
                yangon_cbd_lat, yangon_cbd_lon
            )
        else:
            features['distance_from_cbd'] = features.get('distance_to_city_center_km', 50.0)
        
        return features
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers."""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def fit_transform(self, features_list: List[Dict[str, Any]]) -> np.ndarray:
        """Fit encoders and transform features."""
        df = pd.DataFrame(features_list)
        
        # Encode categorical features
        categorical_cols = ['property_type', 'condition', 'city', 'township', 'location_tier']
        for col in categorical_cols:
            if col in df.columns:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        
        # Store feature names
        self.feature_names = df.columns.tolist()
        
        # Scale numerical features
        scaled_features = self.scaler.fit_transform(df)
        self.is_fitted = True
        
        return scaled_features
    
    def transform(self, features: Dict[str, Any]) -> np.ndarray:
        """Transform single feature set."""
        if not self.is_fitted:
            raise MLModelException("FeatureEngineer not fitted yet")
        
        # Create DataFrame with single row
        df = pd.DataFrame([features])
        
        # Encode categorical features
        categorical_cols = ['property_type', 'condition', 'city', 'township', 'location_tier']
        for col in categorical_cols:
            if col in df.columns and col in self.label_encoders:
                le = self.label_encoders[col]
                try:
                    df[col] = le.transform(df[col].astype(str))
                except ValueError:
                    # Handle unseen categories
                    df[col] = 0  # Default to first category
        
        # Ensure all features are present
        for feature_name in self.feature_names:
            if feature_name not in df.columns:
                df[feature_name] = 0
        
        # Reorder columns to match training
        df = df[self.feature_names]
        
        # Scale features
        scaled_features = self.scaler.transform(df)
        
        return scaled_features[0]


class MLModelManager:
    """Manages multiple ML models for ensemble predictions."""
    
    def __init__(self):
        self.models = {}
        self.feature_engineer = FeatureEngineer()
        self.model_metrics = {}
        self.last_training_time = None
        self.exchange_rate_usd_mmk = 2100.0  # Default exchange rate
    
    async def initialize(self):
        """Initialize the ML service."""
        logger.info("Initializing ML Service...")
        
        # Create models directory
        model_path = Path(settings.MODEL_PATH)
        model_path.mkdir(parents=True, exist_ok=True)
        
        # Try to load existing models
        await self._load_models()
        
        # If no models exist, create and train default models
        if not self.models:
            logger.info("No existing models found, creating default models")
            await self._create_default_models()
        
        logger.info(f"ML Service initialized with {len(self.models)} models")
    
    async def _create_default_models(self):
        """Create default ML models."""
        # Generate synthetic training data for initial models
        synthetic_data = self._generate_synthetic_data(1000)
        
        # Train models
        await self.train_models(synthetic_data)
    
    def _generate_synthetic_data(self, n_samples: int) -> List[Tuple[Dict[str, Any], float]]:
        """Generate synthetic training data for initial model training."""
        import random
        
        data = []
        cities = ['yangon', 'mandalay', 'naypyidaw', 'bago', 'mawlamyine']
        townships = ['downtown', 'north', 'south', 'east', 'west']
        
        for _ in range(n_samples):
            # Generate random property features
            size_sqft = random.uniform(500, 5000)
            bedrooms = random.randint(1, 6)
            bathrooms = random.randint(1, bedrooms + 1)
            
            features = {
                'size_sqft': size_sqft,
                'lot_size_sqft': size_sqft * random.uniform(1.0, 3.0),
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'floors': random.randint(1, 4),
                'parking_spaces': random.randint(0, 3),
                'property_age': random.randint(0, 30),
                'sqft_per_bedroom': size_sqft / bedrooms,
                'bathroom_bedroom_ratio': bathrooms / bedrooms,
                'lot_building_ratio': random.uniform(1.0, 3.0),
                'amenity_score': random.uniform(0.0, 1.0),
                'property_type': random.choice(['apartment', 'house', 'condo']),
                'condition': random.choice(['new', 'excellent', 'good', 'fair']),
                'city': random.choice(cities),
                'township': random.choice(townships),
                'location_tier': random.choice(['tier_1', 'tier_2', 'tier_3']),
                'distance_from_cbd': random.uniform(1.0, 50.0)
            }
            
            # Generate price based on features (simplified formula)
            base_price = size_sqft * 1000  # Base price per sqft
            
            # Adjust for location
            if features['city'] == 'yangon':
                base_price *= 2.0
            elif features['city'] == 'mandalay':
                base_price *= 1.5
            
            # Adjust for condition
            condition_multiplier = {
                'new': 1.3, 'excellent': 1.2, 'good': 1.0, 'fair': 0.8
            }
            base_price *= condition_multiplier[features['condition']]
            
            # Add some randomness
            price = base_price * random.uniform(0.8, 1.2)
            
            data.append((features, price))
        
        return data
    
    async def train_models(self, training_data: List[Tuple[Dict[str, Any], float]]):
        """Train all ML models."""
        logger.info(f"Training models with {len(training_data)} samples")
        
        # Prepare features and targets
        features_list = [item[0] for item in training_data]
        targets = np.array([item[1] for item in training_data])
        
        # Fit feature engineer and transform features
        X = self.feature_engineer.fit_transform(features_list)
        y = targets
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Define models
        model_configs = {
            'xgboost': xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            ),
            'lightgbm': lgb.LGBMRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                verbose=-1
            ),
            'random_forest': RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            ),
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
        }
        
        # Train each model
        for name, model in model_configs.items():
            logger.info(f"Training {name} model...")
            
            # Train model
            model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test)
            metrics = {
                'mae': mean_absolute_error(y_test, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                'r2_score': r2_score(y_test, y_pred),
                'mape': np.mean(np.abs((y_test - y_pred) / y_test)) * 100
            }
            
            # Store model and metrics
            self.models[name] = model
            self.model_metrics[name] = ModelPerformanceMetrics(
                model_name=name,
                mae=metrics['mae'],
                rmse=metrics['rmse'],
                r2_score=metrics['r2_score'],
                mape=metrics['mape'],
                training_samples=len(X_train),
                last_updated=datetime.utcnow(),
                feature_count=X.shape[1]
            )
            
            log_model_performance(name, metrics)
            logger.info(f"{name} model trained - R²: {metrics['r2_score']:.3f}, RMSE: {metrics['rmse']:.0f}")
        
        # Save models
        await self._save_models()
        self.last_training_time = datetime.utcnow()
        
        logger.info("Model training completed")
    
    async def predict(self, property_data: PropertyBase, model_preference: Optional[str] = None) -> PredictionResponse:
        """Make price prediction for a property."""
        try:
            # Create features
            features = self.feature_engineer.create_features(property_data)
            
            # Transform features
            X = self.feature_engineer.transform(features)
            
            # Choose model
            if model_preference and model_preference in self.models:
                model_name = model_preference
                model = self.models[model_preference]
                predictions = {model_name: model.predict([X])[0]}
            else:
                # Use ensemble prediction
                predictions = {}
                for name, model in self.models.items():
                    predictions[name] = model.predict([X])[0]
                
                # Weighted average (better models get higher weight)
                weights = {}
                for name in predictions.keys():
                    if name in self.model_metrics:
                        # Use R² score as weight
                        weights[name] = max(0.1, self.model_metrics[name].r2_score)
                    else:
                        weights[name] = 0.5
                
                total_weight = sum(weights.values())
                ensemble_prediction = sum(
                    pred * weights[name] / total_weight 
                    for name, pred in predictions.items()
                )
                
                predictions['ensemble'] = ensemble_prediction
                model_name = 'ensemble'
            
            # Get final prediction
            predicted_price_mmk = predictions[model_name]
            predicted_price_usd = predicted_price_mmk / self.exchange_rate_usd_mmk
            
            # Calculate confidence score (simplified)
            confidence_score = min(0.95, max(0.5, 
                self.model_metrics.get(model_name.replace('ensemble', 'xgboost'), 
                                     self.model_metrics.get('xgboost', type('obj', (object,), {'r2_score': 0.7})())).r2_score
            ))
            
            # Calculate price range (±20%)
            price_range_mmk = {
                'min': predicted_price_mmk * 0.8,
                'max': predicted_price_mmk * 1.2
            }
            price_range_usd = {
                'min': predicted_price_usd * 0.8,
                'max': predicted_price_usd * 1.2
            }
            
            # Feature importance (simplified)
            feature_importance = {
                'size_sqft': 0.25,
                'location': 0.20,
                'condition': 0.15,
                'bedrooms': 0.12,
                'amenities': 0.10,
                'age': 0.08,
                'other': 0.10
            }
            
            # Generate prediction ID
            import uuid
            prediction_id = str(uuid.uuid4())
            
            # Log prediction
            log_ml_prediction(model_name, features, predicted_price_mmk, confidence_score)
            
            return PredictionResponse(
                predicted_price_mmk=predicted_price_mmk,
                predicted_price_usd=predicted_price_usd,
                confidence_score=confidence_score,
                price_range_mmk=price_range_mmk,
                price_range_usd=price_range_usd,
                model_used=model_name,
                feature_importance=feature_importance,
                prediction_id=prediction_id
            )
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise MLModelException(f"Prediction failed: {str(e)}")
    
    async def _save_models(self):
        """Save trained models to disk."""
        model_path = Path(settings.MODEL_PATH)
        
        # Save models
        for name, model in self.models.items():
            joblib.dump(model, model_path / f"{name}_model.pkl")
        
        # Save feature engineer
        joblib.dump(self.feature_engineer, model_path / "feature_engineer.pkl")
        
        # Save metrics
        metrics_data = {
            name: {
                'mae': metrics.mae,
                'rmse': metrics.rmse,
                'r2_score': metrics.r2_score,
                'mape': metrics.mape,
                'training_samples': metrics.training_samples,
                'last_updated': metrics.last_updated.isoformat(),
                'feature_count': metrics.feature_count
            }
            for name, metrics in self.model_metrics.items()
        }
        
        with open(model_path / "model_metrics.json", 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        logger.info("Models saved successfully")
    
    async def _load_models(self):
        """Load trained models from disk."""
        model_path = Path(settings.MODEL_PATH)
        
        try:
            # Load feature engineer
            fe_path = model_path / "feature_engineer.pkl"
            if fe_path.exists():
                self.feature_engineer = joblib.load(fe_path)
                logger.info("Feature engineer loaded")
            
            # Load models
            for model_file in model_path.glob("*_model.pkl"):
                model_name = model_file.stem.replace("_model", "")
                self.models[model_name] = joblib.load(model_file)
                logger.info(f"Loaded {model_name} model")
            
            # Load metrics
            metrics_path = model_path / "model_metrics.json"
            if metrics_path.exists():
                with open(metrics_path, 'r') as f:
                    metrics_data = json.load(f)
                
                for name, data in metrics_data.items():
                    self.model_metrics[name] = ModelPerformanceMetrics(
                        model_name=name,
                        mae=data['mae'],
                        rmse=data['rmse'],
                        r2_score=data['r2_score'],
                        mape=data['mape'],
                        training_samples=data['training_samples'],
                        last_updated=datetime.fromisoformat(data['last_updated']),
                        feature_count=data['feature_count']
                    )
                
                logger.info("Model metrics loaded")
        
        except Exception as e:
            logger.warning(f"Failed to load existing models: {str(e)}")
    
    def get_model_metrics(self) -> Dict[str, ModelPerformanceMetrics]:
        """Get performance metrics for all models."""
        return self.model_metrics
    
    async def should_retrain(self) -> bool:
        """Check if models should be retrained."""
        if not self.last_training_time:
            return True
        
        time_since_training = datetime.utcnow() - self.last_training_time
        return time_since_training > timedelta(hours=settings.MODEL_RETRAIN_INTERVAL_HOURS)


class MLService:
    """Main ML service class."""
    
    def __init__(self):
        self.model_manager = MLModelManager()
    
    async def initialize(self):
        """Initialize the ML service."""
        await self.model_manager.initialize()
    
    async def predict_price(self, property_data: PropertyBase, model_preference: Optional[str] = None) -> PredictionResponse:
        """Predict property price."""
        return await self.model_manager.predict(property_data, model_preference)
    
    async def batch_predict(self, properties: List[PropertyBase], model_preference: Optional[str] = None) -> List[PredictionResponse]:
        """Predict prices for multiple properties."""
        predictions = []
        for property_data in properties:
            prediction = await self.predict_price(property_data, model_preference)
            predictions.append(prediction)
        return predictions
    
    def get_model_metrics(self) -> Dict[str, ModelPerformanceMetrics]:
        """Get model performance metrics."""
        return self.model_manager.get_model_metrics()
    
    async def retrain_models_if_needed(self, training_data: Optional[List[Tuple[Dict[str, Any], float]]] = None):
        """Retrain models if needed."""
        if await self.model_manager.should_retrain():
            if training_data:
                await self.model_manager.train_models(training_data)
            else:
                logger.info("Model retraining needed but no training data provided")