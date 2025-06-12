'use client';

import { BatchPrediction } from '@/components/batch/batch-prediction';

export default function BatchPage() {
  return (
    <main className="container mx-auto py-8 px-4">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2">Batch Property Price Prediction</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Upload a CSV file to predict prices for multiple properties at once
        </p>
      </div>
      
      <BatchPrediction />
    </main>
  );
}