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
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

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
export async function getMarketAnalysis(): Promise<{
  trends: MarketTrend[];
  areaComparison: AreaPricing[];
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/market-analysis`);
    
    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }
    
    return await response.json();
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