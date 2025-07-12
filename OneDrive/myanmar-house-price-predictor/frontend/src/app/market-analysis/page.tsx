'use client';

import { MarketAnalysis } from '@/components/market/market-analysis';

export default function MarketAnalysisPage() {
  return (
    <main className="container mx-auto py-8 px-4">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2">Myanmar Real Estate Market Analysis</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Explore current market trends, hot areas, and price distributions
        </p>
      </div>
      
      <MarketAnalysis />
    </main>
  );
}