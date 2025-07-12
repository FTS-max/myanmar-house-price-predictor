'use client';

import { ModelPerformanceDisplay } from '@/components/model/model-performance';

export default function ModelPerformancePage() {
  return (
    <main className="container mx-auto py-8 px-4">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2">Model Performance Metrics</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Explore the accuracy and performance of our house price prediction model
        </p>
      </div>
      
      <ModelPerformanceDisplay />
    </main>
  );
}