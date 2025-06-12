#!/usr/bin/env python3
"""
OpenRouter AI Service for Myanmar House Price Predictor.

Provides AI-powered property data enrichment, market insights, and intelligent analysis.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx
from loguru import logger

from ..core.config import settings
from ..core.exceptions import OpenRouterException
from ..core.logging import log_ai_enrichment
from ..models.schemas import PropertyBase, PropertyLocation


class OpenRouterService:
    """Service for interacting with OpenRouter AI API."""
    
    def __init__(self):
        self.client = None
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.OPENROUTER_MODEL
        self.headers = None
        
        if settings.OPENROUTER_API_KEY:
            self.headers = settings.get_openrouter_headers()
        else:
            logger.warning("OpenRouter API key not configured - AI enrichment will be disabled")
    
    async def __aenter__(self):
        """Async context manager entry."""
        if self.headers:
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                headers=self.headers
            )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()
    
    async def _make_request(self, messages: List[Dict[str, str]], max_tokens: int = 1000) -> str:
        """Make a request to OpenRouter API."""
        if not self.client or not self.headers:
            raise OpenRouterException("OpenRouter service not properly configured")
        
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"OpenRouter API error: {response.status_code} - {error_detail}")
                raise OpenRouterException(
                    f"OpenRouter API request failed: {response.status_code}",
                    api_error=error_detail
                )
            
            result = response.json()
            
            if "choices" not in result or not result["choices"]:
                raise OpenRouterException("Invalid response format from OpenRouter API")
            
            return result["choices"][0]["message"]["content"]
            
        except httpx.RequestError as e:
            logger.error(f"OpenRouter request error: {str(e)}")
            raise OpenRouterException(f"Request failed: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"OpenRouter response parsing error: {str(e)}")
            raise OpenRouterException(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected OpenRouter error: {str(e)}")
            raise OpenRouterException(f"Unexpected error: {str(e)}")
    
    async def enrich_property_data(self, property_data: PropertyBase) -> Dict[str, Any]:
        """Enrich property data with AI-generated insights."""
        if not settings.ENABLE_AI_ENRICHMENT or not self.headers:
            logger.info("AI enrichment disabled or not configured")
            return {}
        
        start_time = datetime.now()
        
        try:
            async with self:
                # Create enrichment prompt
                prompt = self._create_enrichment_prompt(property_data)
                
                messages = [
                    {
                        "role": "system",
                        "content": "You are a Myanmar real estate expert AI assistant. Provide detailed, accurate insights about properties in Myanmar, including market trends, location analysis, and investment potential. Always respond in valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
                
                # Make API request
                response = await self._make_request(messages, max_tokens=1500)
                
                # Parse response
                enriched_data = self._parse_enrichment_response(response)
                
                # Log enrichment
                processing_time = (datetime.now() - start_time).total_seconds()
                log_ai_enrichment(property_data.dict(), enriched_data, processing_time)
                
                return enriched_data
                
        except Exception as e:
            logger.error(f"Property enrichment failed: {str(e)}")
            # Return empty dict instead of raising exception to not break the main flow
            return {}
    
    def _create_enrichment_prompt(self, property_data: PropertyBase) -> str:
        """Create enrichment prompt for the AI."""
        property_summary = {
            "type": property_data.property_type.value,
            "condition": property_data.condition.value,
            "size_sqft": property_data.size_sqft,
            "bedrooms": property_data.features.bedrooms,
            "bathrooms": property_data.features.bathrooms,
            "location": {
                "city": property_data.location.city,
                "township": property_data.location.township,
                "ward": property_data.location.ward
            },
            "year_built": property_data.year_built,
            "amenities": {
                "elevator": property_data.features.has_elevator,
                "swimming_pool": property_data.features.has_swimming_pool,
                "security": property_data.features.has_security,
                "parking": property_data.features.parking_spaces > 0
            }
        }
        
        return f"""
Analyze this Myanmar property and provide enriched insights in JSON format:

Property Details:
{json.dumps(property_summary, indent=2)}

Please provide a JSON response with the following structure:
{{
  "location_analysis": {{
    "neighborhood_description": "Brief description of the neighborhood",
    "accessibility": "Transportation and accessibility info",
    "nearby_amenities": ["list of nearby amenities"],
    "development_potential": "Future development prospects"
  }},
  "market_insights": {{
    "price_trend": "Current price trend in the area",
    "demand_level": "high/medium/low",
    "investment_potential": "Investment attractiveness",
    "comparable_properties": "Info about similar properties"
  }},
  "property_highlights": {{
    "strengths": ["list of property strengths"],
    "considerations": ["list of considerations or potential issues"],
    "unique_features": ["unique aspects of this property"]
  }},
  "recommendations": {{
    "target_buyers": ["types of buyers this property suits"],
    "pricing_strategy": "Pricing recommendations",
    "marketing_points": ["key selling points"]
  }}
}}

Focus on Myanmar-specific market conditions, local preferences, and cultural factors.
"""
    
    def _parse_enrichment_response(self, response: str) -> Dict[str, Any]:
        """Parse AI enrichment response."""
        try:
            # Try to extract JSON from response
            response = response.strip()
            
            # Find JSON content (sometimes AI adds extra text)
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback: try to parse entire response
                return json.loads(response)
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse AI response as JSON: {str(e)}")
            # Return structured fallback
            return {
                "location_analysis": {
                    "neighborhood_description": "AI analysis unavailable",
                    "accessibility": "Information not available",
                    "nearby_amenities": [],
                    "development_potential": "Analysis pending"
                },
                "market_insights": {
                    "price_trend": "Stable",
                    "demand_level": "medium",
                    "investment_potential": "Moderate",
                    "comparable_properties": "Data not available"
                },
                "property_highlights": {
                    "strengths": ["Standard property features"],
                    "considerations": ["Standard due diligence recommended"],
                    "unique_features": []
                },
                "recommendations": {
                    "target_buyers": ["General buyers"],
                    "pricing_strategy": "Market-based pricing",
                    "marketing_points": ["Standard property listing"]
                }
            }
    
    async def generate_market_analysis(self, location: PropertyLocation, property_type: Optional[str] = None) -> Dict[str, Any]:
        """Generate market analysis for a specific location."""
        if not settings.ENABLE_AI_ENRICHMENT or not self.headers:
            return {}
        
        try:
            async with self:
                prompt = self._create_market_analysis_prompt(location, property_type)
                
                messages = [
                    {
                        "role": "system",
                        "content": "You are a Myanmar real estate market analyst. Provide comprehensive market analysis with current trends, pricing insights, and investment recommendations. Always respond in valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
                
                response = await self._make_request(messages, max_tokens=2000)
                return self._parse_market_analysis_response(response)
                
        except Exception as e:
            logger.error(f"Market analysis failed: {str(e)}")
            return {}
    
    def _create_market_analysis_prompt(self, location: PropertyLocation, property_type: Optional[str]) -> str:
        """Create market analysis prompt."""
        location_info = {
            "city": location.city,
            "township": location.township,
            "ward": location.ward
        }
        
        type_filter = f" for {property_type} properties" if property_type else ""
        
        return f"""
Provide a comprehensive real estate market analysis for {location.city}, {location.township} in Myanmar{type_filter}.

Location: {json.dumps(location_info, indent=2)}

Please provide analysis in JSON format:
{{
  "market_overview": {{
    "current_trends": "Current market trends",
    "price_direction": "rising/stable/declining",
    "market_activity": "high/medium/low",
    "supply_demand_balance": "Analysis of supply vs demand"
  }},
  "pricing_analysis": {{
    "average_price_range": {{
      "min_mmk": 0,
      "max_mmk": 0
    }},
    "price_per_sqft": {{
      "min_mmk": 0,
      "max_mmk": 0
    }},
    "price_factors": ["factors affecting pricing"]
  }},
  "location_factors": {{
    "infrastructure": "Infrastructure development status",
    "transportation": "Transportation connectivity",
    "amenities": ["nearby amenities and facilities"],
    "future_development": "Planned developments"
  }},
  "investment_outlook": {{
    "short_term": "6-12 month outlook",
    "long_term": "2-5 year outlook",
    "risk_factors": ["potential risks"],
    "opportunities": ["investment opportunities"]
  }},
  "recommendations": ["actionable recommendations"]
}}

Focus on Myanmar-specific factors including economic conditions, regulatory environment, and local market dynamics.
"""
    
    def _parse_market_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse market analysis response."""
        try:
            response = response.strip()
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return json.loads(response)
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse market analysis response: {str(e)}")
            return {
                "market_overview": {
                    "current_trends": "Analysis unavailable",
                    "price_direction": "stable",
                    "market_activity": "medium",
                    "supply_demand_balance": "Balanced"
                },
                "pricing_analysis": {
                    "average_price_range": {"min_mmk": 0, "max_mmk": 0},
                    "price_per_sqft": {"min_mmk": 0, "max_mmk": 0},
                    "price_factors": ["Location", "Size", "Condition"]
                },
                "location_factors": {
                    "infrastructure": "Standard infrastructure",
                    "transportation": "Accessible",
                    "amenities": ["Basic amenities available"],
                    "future_development": "Ongoing development"
                },
                "investment_outlook": {
                    "short_term": "Stable",
                    "long_term": "Positive",
                    "risk_factors": ["Market volatility"],
                    "opportunities": ["Standard investment potential"]
                },
                "recommendations": ["Conduct thorough due diligence"]
            }
    
    async def generate_property_description(self, property_data: PropertyBase) -> str:
        """Generate an attractive property description."""
        if not settings.ENABLE_AI_ENRICHMENT or not self.headers:
            return self._generate_fallback_description(property_data)
        
        try:
            async with self:
                prompt = f"""
Create an attractive, professional property description for this Myanmar property:

Property Type: {property_data.property_type.value}
Size: {property_data.size_sqft} sqft
Bedrooms: {property_data.features.bedrooms}
Bathrooms: {property_data.features.bathrooms}
Location: {property_data.location.city}, {property_data.location.township}
Condition: {property_data.condition.value}

Write a compelling 2-3 paragraph description that highlights the property's best features and appeals to potential buyers. Focus on lifestyle benefits and location advantages.
"""
                
                messages = [
                    {
                        "role": "system",
                        "content": "You are a professional real estate copywriter specializing in Myanmar properties. Write engaging, accurate property descriptions that appeal to local and international buyers."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
                
                response = await self._make_request(messages, max_tokens=500)
                return response.strip()
                
        except Exception as e:
            logger.error(f"Property description generation failed: {str(e)}")
            return self._generate_fallback_description(property_data)
    
    def _generate_fallback_description(self, property_data: PropertyBase) -> str:
        """Generate a basic property description as fallback."""
        return f"""
This {property_data.condition.value} {property_data.property_type.value} offers {property_data.size_sqft} square feet of living space with {property_data.features.bedrooms} bedrooms and {property_data.features.bathrooms} bathrooms. Located in {property_data.location.township}, {property_data.location.city}, this property provides comfortable living in a convenient location.

The property features modern amenities and is well-maintained, making it an excellent choice for families or investors looking for quality real estate in Myanmar.
"""
    
    async def health_check(self) -> bool:
        """Check if OpenRouter service is available."""
        if not self.headers:
            return False
        
        try:
            async with self:
                messages = [
                    {
                        "role": "user",
                        "content": "Hello, please respond with 'OK' to confirm the service is working."
                    }
                ]
                
                response = await self._make_request(messages, max_tokens=10)
                return "OK" in response.upper()
                
        except Exception as e:
            logger.error(f"OpenRouter health check failed: {str(e)}")
            return False