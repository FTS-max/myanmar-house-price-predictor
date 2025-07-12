'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart } from '@/components/ui/chart';
import { formatPercentage } from '@/lib/utils';
import { getModelPerformance, ModelPerformance } from '@/lib/api';

export function ModelPerformanceDisplay() {
  const [isLoading, setIsLoading] = useState(true);
  const [performanceData, setPerformanceData] = useState<ModelPerformance | null>(null);
  
  useEffect(() => {
    const fetchPerformanceData = async () => {
      setIsLoading(true);
      try {
        const data = await getModelPerformance();
        setPerformanceData(data);
      } catch (error) {
        console.error('Error fetching model performance data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchPerformanceData();
  }, []);
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  if (!performanceData) {
    return (
      <div className="text-center p-8">
        <p>No model performance data available</p>
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard 
          title="R² Score" 
          value={performanceData.r2Score} 
          description="Coefficient of determination" 
          format="percentage"
          color="text-blue-500"
        />
        
        <MetricCard 
          title="Mean Absolute Error" 
          value={performanceData.meanAbsoluteError} 
          description="Average absolute difference" 
          format="number"
          color="text-purple-500"
        />
        
        
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Feature Importance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <BarChart
                data={performanceData.featureImportance.map(feature => ({ label: feature.feature, value: feature.importance }))}
                barColor="#3b82f6"
              />
            </div>
          </CardContent>
        </Card>
        
        
      </div>
      
      
      
      
    </div>
  );
}

interface MetricCardProps {
  title: string;
  value: number;
  description: string;
  format: 'percentage' | 'number';
  color: string;
}

function MetricCard({ title, value, description, format, color }: MetricCardProps) {
  const formattedValue = format === 'percentage' 
    ? formatPercentage(value)
    : value.toLocaleString();
  
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">{title}</h3>
          <div className={`mt-2 text-3xl font-bold ${color}`}>
            {formattedValue}
          </div>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {description}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
