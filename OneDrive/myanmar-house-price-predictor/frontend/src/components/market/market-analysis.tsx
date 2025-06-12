'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select } from '@/components/ui/select';
import { Chart } from '@/components/ui/chart';
import { formatCurrency, formatPercentage } from '@/lib/utils';
import { getMarketAnalysis, MarketTrend, AreaPricing } from '@/lib/api';

const timeRanges = [
  { value: '1m', label: 'Last Month' },
  { value: '3m', label: 'Last 3 Months' },
  { value: '6m', label: 'Last 6 Months' },
  { value: '1y', label: 'Last Year' },
  { value: '3y', label: 'Last 3 Years' },
];

const propertyTypes = [
  { value: 'all', label: 'All Types' },
  { value: 'apartment', label: 'Apartment' },
  { value: 'condo', label: 'Condominium' },
  { value: 'house', label: 'House' },
  { value: 'villa', label: 'Villa' },
  { value: 'land', label: 'Land' },
];

export function MarketAnalysis() {
  const [timeRange, setTimeRange] = useState('1y');
  const [propertyType, setPropertyType] = useState('all');
  const [isLoading, setIsLoading] = useState(true);
  const [marketData, setMarketData] = useState<{
    trends: MarketTrend[];
    hotAreas: AreaPricing[];
    priceDistribution: { range: string; count: number }[];
    growthByType: { type: string; growth: number }[];
  } | null>(null);
  
  useEffect(() => {
    const fetchMarketData = async () => {
      setIsLoading(true);
      try {
        const data = await getMarketAnalysis(timeRange, propertyType);
        setMarketData(data);
      } catch (error) {
        console.error('Error fetching market data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchMarketData();
  }, [timeRange, propertyType]);
  
  const handleTimeRangeChange = (value: string) => {
    setTimeRange(value);
  };
  
  const handlePropertyTypeChange = (value: string) => {
    setPropertyType(value);
  };
  
  // Calculate average price and growth
  const calculateAveragePrice = () => {
    if (!marketData?.trends || marketData.trends.length === 0) return 0;
    return marketData.trends[marketData.trends.length - 1].averagePrice;
  };
  
  const calculatePriceGrowth = () => {
    if (!marketData?.trends || marketData.trends.length < 2) return 0;
    const firstPrice = marketData.trends[0].averagePrice;
    const lastPrice = marketData.trends[marketData.trends.length - 1].averagePrice;
    return ((lastPrice - firstPrice) / firstPrice) * 100;
  };
  
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4 justify-between">
        <div className="w-full sm:w-48">
          <Select
            label="Time Range"
            options={timeRanges}
            value={timeRange}
            onChange={handleTimeRangeChange}
          />
        </div>
        <div className="w-full sm:w-48">
          <Select
            label="Property Type"
            options={propertyTypes}
            value={propertyType}
            onChange={handlePropertyTypeChange}
          />
        </div>
      </div>
      
      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        </div>
      ) : marketData ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Price Trends</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <Chart
                    type="line"
                    data={{
                      labels: marketData.trends.map(trend => trend.date),
                      datasets: [{
                        label: 'Average Price',
                        data: marketData.trends.map(trend => trend.averagePrice),
                        color: '#3b82f6'
                      }]
                    }}
                  />
                </div>
                <div className="mt-4 grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Average Price</p>
                    <p className="text-xl font-semibold">{formatCurrency(calculateAveragePrice())}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Price Growth</p>
                    <p className={`text-xl font-semibold ${calculatePriceGrowth() >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {formatPercentage(calculatePriceGrowth() / 100)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Price Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <Chart
                    type="bar"
                    data={{
                      labels: marketData.priceDistribution.map(item => item.range),
                      datasets: [{
                        label: 'Number of Properties',
                        data: marketData.priceDistribution.map(item => item.count),
                        color: '#8b5cf6'
                      }]
                    }}
                  />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Hot Areas</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {marketData.hotAreas.map((area, index) => (
                    <div key={index} className="flex justify-between items-center">
                      <div>
                        <p className="font-medium">{area.area}</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {formatPercentage(area.growthRate / 100)} growth
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">{formatCurrency(area.averagePrice)}</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          Avg. price
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Growth by Property Type</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <Chart
                    type="bar"
                    data={{
                      labels: marketData.growthByType.map(item => item.type),
                      datasets: [{
                        label: 'Growth Rate',
                        data: marketData.growthByType.map(item => item.growth),
                        color: '#ec4899'
                      }]
                    }}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      ) : (
        <div className="text-center p-8">
          <p>No market data available</p>
        </div>
      )}
    </div>
  );
}