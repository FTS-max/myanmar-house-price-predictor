/**
 * API service for communicating with the backend
 */

// Types for API requests and responses
export interface PropertyDetails {
  location: string;
  propertyType: string;
  size: number; // in square feet
  bedrooms: number;
  bathrooms: number;
  yearBuilt?: number;
  amenities?: string[];
}

export interface PredictionResult {
  predictedPrice: number;
  confidenceLow: number;
  confidenceHigh: number;
  accuracy: number;
  comparableProperties?: ComparableProperty[];
}

export interface ComparableProperty {
  id: string;
  location: string;
  propertyType: string;
  size: number;
  price: number;
  soldDate?: string;
  similarity: number; // how similar to the queried property (0-1)
}

export interface MarketTrend {
  period: string; // month/year
  averagePrice: number;
  volumeSold: number;
  priceChange: number; // percentage
}

export interface AreaPricing {
  area: string;
  averagePrice: number;
  pricePerSqFt: number;
  numberOfProperties: number;
}

export interface ModelPerformance {
  accuracy: number;
  r2Score: number;
  meanAbsoluteError: number;
  featureImportance: {
    feature: string;
    importance: number;
  }[];
}

// API base URL - can be configured based on environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Predict house price based on property details
 */
export async function predictPrice(propertyDetails: PropertyDetails): Promise<PredictionResult> {
  try {
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(propertyDetails),
    });
    
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to predict price:', error);
    throw error;
  }
}

/**
 * Upload CSV file for batch prediction
 */
export async function batchPredict(file: File): Promise<PredictionResult[]> {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/batch-predict`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to process batch prediction:', error);
    throw error;
  }
}

/**
 * Get market analysis data
 */
export async function getMarketAnalysis(
  timeRange: string,
  propertyType: string
): Promise<{
  trends: MarketTrend[];
  areaComparison: AreaPricing[];
  priceDistribution: { range: string; count: number }[];
  growthByType: { type: string; growth: number }[];
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/market/analysis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        location: {
          city: "Yangon",
          township: "All"
        },
        property_type: propertyType === 'all' ? null : propertyType,
        time_period_months: parseInt(timeRange.replace('m', '').replace('y', '')) * (timeRange.includes('y') ? 12 : 1)
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
    
    const data = await response.json();
    // The backend response does not match the frontend's expected format.
    // This is a temporary mapping to avoid breaking the UI.
    // This should be fixed in the backend or the frontend component should be updated.
    return {
      trends: data.price_trends?.history || [],
      areaComparison: data.location_summary?.area_comparison || [],
      priceDistribution: data.price_distribution?.distribution || [],
      growthByType: data.market_activity?.by_type || [],
    };
  } catch (error) {
    console.error('Failed to fetch market analysis:', error);
    throw error;
  }
}

/**
 * Get model performance metrics
 */
export async function getModelPerformance(): Promise<ModelPerformance> {
  try {
    const response = await fetch(`${API_BASE_URL}/model-performance`);
    
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch model performance:', error);
    throw error;
  }
}