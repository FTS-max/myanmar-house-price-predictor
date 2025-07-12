'use client';

import { PredictionResult } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import React from 'react';

interface PredictionResultProps {
  result: PredictionResult;
}

export function PredictionResultDisplay({ result }: PredictionResultProps) {
  if (!result) return null;
  
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Estimated Property Value</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center">
            <div className="text-4xl font-bold text-primary">
              {formatCurrency(result.predictedPrice)}
            </div>
            
            <div className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              Prediction confidence: {result.accuracy}%
            </div>
            
            <div className="mt-4 w-full max-w-md bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
              <div 
                className="bg-primary h-2.5 rounded-full" 
                style={{ width: `${result.accuracy}%` }}
              ></div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      
      
      {result.comparableProperties && result.comparableProperties.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Comparable Properties</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Location</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Size</TableHead>
                  <TableHead>Price</TableHead>
                  <TableHead>Similarity</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {result.comparableProperties.map((property, index) => (
                  <TableRow key={index}>
                    <TableCell>{property.location}</TableCell>
                    <TableCell>{property.propertyType}</TableCell>
                    <TableCell>{property.size} sq ft</TableCell>
                    <TableCell>{formatCurrency(property.price)}</TableCell>
                    <TableCell>
                      <div className="flex items-center">
                        <span className="mr-2">{property.similarity}%</span>
                        <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                          <div 
                            className="bg-primary h-1.5 rounded-full" 
                            style={{ width: `${property.similarity}%` }}
                          ></div>
                        </div>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
      
      
    </div>
  );
}