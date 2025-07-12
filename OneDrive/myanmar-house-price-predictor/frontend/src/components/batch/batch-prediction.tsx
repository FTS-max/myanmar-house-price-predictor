'use client';

import { useState } from 'react';
import { FileUpload } from '@/components/ui/file-upload';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { formatCurrency } from '@/lib/utils';
import { batchPredict } from '@/lib/api';

interface BatchPredictionResult {
  id: string;
  location: string;
  propertyType: string;
  size: number;
  bedrooms: number;
  bathrooms: number;
  yearBuilt?: number;
  predictedPrice: number;
  confidenceScore: number;
}

export function BatchPrediction() {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<BatchPredictionResult[]>([]);
  const [error, setError] = useState<string>('');
  
  const handleFileChange = (file: File | null) => {
    setFile(file);
    setError('');
  };
  
  const handleSubmit = async () => {
    if (!file) {
      setError('Please select a CSV file to upload');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      const results = await batchPredict(file);
      const formattedResults = results.map((result, index) => ({
        ...result,
        id: `result-${index}`,
        location: 'N/A',
        propertyType: 'N/A',
        size: 0,
        bedrooms: 0,
        bathrooms: 0,
        confidenceScore: result.accuracy * 100,
      }));
      setResults(formattedResults);
    } catch (err) {
      console.error('Error processing batch prediction:', err);
      setError('Failed to process the CSV file. Please check the format and try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  
  
  const downloadResults = () => {
    if (!results.length) return;
    
    const headers = ['ID', 'Location', 'Property Type', 'Size (sq ft)', 'Bedrooms', 'Bathrooms', 'Year Built', 'Predicted Price', 'Confidence'];
    const csvContent = [
      headers.join(','),
      ...results.map(row => [
        row.id,
        `"${row.location}"`,
        `"${row.propertyType}"`,
        row.size,
        row.bedrooms,
        row.bathrooms,
        row.yearBuilt || '',
        row.predictedPrice,
        `${row.confidenceScore}%`
      ].join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'prediction_results.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Batch Property Price Prediction</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Upload a CSV file with property details to get price predictions for multiple properties at once.
              The CSV should include columns for location, property_type, size, bedrooms, bathrooms, and year_built (optional).
            </p>
            
            <FileUpload
              accept=".csv"
              maxSize={5 * 1024 * 1024} // 5MB
              onChange={handleFileChange}
              
            />
            
            {error && (
              <div className="text-sm text-red-500 mt-2">{error}</div>
            )}
          </div>
        </CardContent>
        <CardFooter>
          <Button onClick={handleSubmit} isLoading={isLoading} disabled={!file || isLoading}>
            Process Batch
          </Button>
        </CardFooter>
      </Card>
      
      {results.length > 0 && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Prediction Results</CardTitle>
            <Button variant="outline" onClick={downloadResults}>
              Download CSV
            </Button>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Location</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Size</TableHead>
                    <TableHead>Bedrooms</TableHead>
                    <TableHead>Bathrooms</TableHead>
                    <TableHead>Year Built</TableHead>
                    <TableHead>Predicted Price</TableHead>
                    <TableHead>Confidence</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {results.map((result) => (
                    <TableRow key={result.id}>
                      <TableCell>{result.location}</TableCell>
                      <TableCell>{result.propertyType}</TableCell>
                      <TableCell>{result.size} sq ft</TableCell>
                      <TableCell>{result.bedrooms}</TableCell>
                      <TableCell>{result.bathrooms}</TableCell>
                      <TableCell>{result.yearBuilt || 'N/A'}</TableCell>
                      <TableCell>{formatCurrency(result.predictedPrice)}</TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          <span className="mr-2">{result.confidenceScore}%</span>
                          <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                            <div 
                              className="bg-primary h-1.5 rounded-full" 
                              style={{ width: `${result.confidenceScore}%` }}
                            ></div>
                          </div>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}