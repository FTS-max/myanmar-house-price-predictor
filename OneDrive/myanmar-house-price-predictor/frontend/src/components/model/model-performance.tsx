'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PieChart } from '@/components/ui/chart';
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
        
        <MetricCard 
          title="Mean Squared Error" 
          value={performanceData.meanSquaredError} 
          description="Average squared difference" 
          format="number"
          color="text-pink-500"
        />
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Feature Importance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <Chart
                type="bar"
                data={{
                  labels: performanceData.featureImportance.map(feature => feature.name),
                  datasets: [{
                    label: 'Importance',
                    data: performanceData.featureImportance.map(feature => feature.importance),
                    color: '#3b82f6'
                  }]
                }}
                options={{ horizontal: true }}
              />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Prediction vs Actual</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <Chart
                type="scatter"
                data={{
                  labels: performanceData.predictionVsActual.map((_, i) => `Point ${i + 1}`),
                  datasets: [{
                    label: 'Predictions',
                    data: performanceData.predictionVsActual.map(point => ({ 
                      x: point.actual, 
                      y: point.predicted 
                    })),
                    color: '#10b981'
                  }]
                }}
              />
            </div>
          </CardContent>
        </Card>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Error Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <Chart
              type="bar"
              data={{
                labels: performanceData.errorDistribution.map(bin => bin.range),
                datasets: [{
                  label: 'Count',
                  data: performanceData.errorDistribution.map(bin => bin.count),
                  color: '#f59e0b'
                }]
              }}
            />
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>Cross Validation Results</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead>
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Fold</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">R² Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">MAE</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">MSE</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {performanceData.crossValidation.map((fold, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">Fold {index + 1}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{formatPercentage(fold.r2Score)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{fold.meanAbsoluteError.toLocaleString()}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{fold.meanSquaredError.toLocaleString()}</td>
                  </tr>
                ))}
                <tr className="bg-gray-50 dark:bg-gray-800">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">Average</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {formatPercentage(
                      performanceData.crossValidation.reduce((sum, fold) => sum + fold.r2Score, 0) / 
                      performanceData.crossValidation.length
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {(
                      performanceData.crossValidation.reduce((sum, fold) => sum + fold.meanAbsoluteError, 0) / 
                      performanceData.crossValidation.length
                    ).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {(
                      performanceData.crossValidation.reduce((sum, fold) => sum + fold.meanSquaredError, 0) / 
                      performanceData.crossValidation.length
                    ).toLocaleString()}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
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
