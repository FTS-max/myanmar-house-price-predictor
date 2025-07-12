'use client';

import { useState } from 'react';
import { PredictionForm } from '@/components/prediction/prediction-form';
import { PredictionResultDisplay } from '@/components/prediction/prediction-result';
import { PredictionResult } from '@/lib/api';

export default function Home() {
  const [predictionResult, setPredictionResult] = useState<PredictionResult | null>(null);

  return (
    <main className="container mx-auto py-8 px-4">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2">Myanmar House Price Predictor</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Enter your property details below to get an estimated market value
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <PredictionForm onPredictionResult={setPredictionResult} />
        </div>
        
        <div>
          {predictionResult ? (
            <PredictionResultDisplay result={predictionResult} />
          ) : (
            <div className="h-full flex items-center justify-center">
              <div className="text-center p-8 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">
                  No prediction yet
                </h3>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  Fill out the form to get a property price prediction.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
