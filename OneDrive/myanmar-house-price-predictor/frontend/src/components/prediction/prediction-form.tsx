'use client';

import { PropertyDetails, predictPrice, PredictionResult } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import React, { useState } from 'react';

const propertyTypes = [
  { value: 'apartment', label: 'Apartment' },
  { value: 'condo', label: 'Condominium' },
  { value: 'house', label: 'House' },
  { value: 'villa', label: 'Villa' },
  { value: 'land', label: 'Land' },
];

const locations = [
  { value: 'yangon', label: 'Yangon' },
  { value: 'mandalay', label: 'Mandalay' },
  { value: 'naypyidaw', label: 'Naypyidaw' },
  { value: 'bago', label: 'Bago' },
  { value: 'mawlamyine', label: 'Mawlamyine' },
];

const amenities = [
  { value: 'pool', label: 'Swimming Pool' },
  { value: 'gym', label: 'Gym' },
  { value: 'security', label: '24/7 Security' },
  { value: 'parking', label: 'Parking' },
  { value: 'garden', label: 'Garden' },
];

interface PredictionFormProps {
  onPredictionResult?: (result: PredictionResult) => void;
}

export function PredictionForm({ onPredictionResult }: PredictionFormProps) {
  const [formData, setFormData] = useState<PropertyDetails>({
    location: '',
    propertyType: '',
    size: 0,
    bedrooms: 0,
    bathrooms: 0,
    yearBuilt: undefined,
    amenities: [],
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    
    // Convert numeric inputs to numbers
    const parsedValue = type === 'number' ? (value ? parseFloat(value) : 0) : value;
    
    setFormData(prev => ({
      ...prev,
      [name]: parsedValue,
    }));
    
    // Clear error when field is edited
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: '',
      }));
    }
  };
  
  const handleSelectChange = (name: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    
    // Clear error when field is edited
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: '',
      }));
    }
  };
  
  const handleAmenityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value, checked } = e.target;
    
    setFormData(prev => {
      const currentAmenities = prev.amenities || [];
      
      if (checked) {
        return {
          ...prev,
          amenities: [...currentAmenities, value],
        };
      } else {
        return {
          ...prev,
          amenities: currentAmenities.filter(item => item !== value),
        };
      }
    });
  };
  
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.location) {
      newErrors.location = 'Location is required';
    }
    
    if (!formData.propertyType) {
      newErrors.propertyType = 'Property type is required';
    }
    
    if (!formData.size || formData.size <= 0) {
      newErrors.size = 'Valid size is required';
    }
    
    if (formData.bedrooms < 0) {
      newErrors.bedrooms = 'Bedrooms cannot be negative';
    }
    
    if (formData.bathrooms < 0) {
      newErrors.bathrooms = 'Bathrooms cannot be negative';
    }
    
    if (formData.yearBuilt && (formData.yearBuilt < 1900 || formData.yearBuilt > new Date().getFullYear())) {
      newErrors.yearBuilt = 'Please enter a valid year';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsLoading(true);
    
    try {
      const result = await predictPrice(formData);
      if (onPredictionResult) {
        onPredictionResult(result);
      }
    } catch (error) {
      console.error('Prediction error:', error);
      // Handle error state here
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Property Details</CardTitle>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Select
              label="Location"
              options={locations}
              value={formData.location}
              onChange={(value) => handleSelectChange('location', value)}
              error={errors.location}
            />
            
            <Select
              label="Property Type"
              options={propertyTypes}
              value={formData.propertyType}
              onChange={(value) => handleSelectChange('propertyType', value)}
              error={errors.propertyType}
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              type="number"
              name="size"
              label="Size (sq ft)"
              value={formData.size || ''}
              onChange={handleInputChange}
              error={errors.size}
            />
            
            <Input
              type="number"
              name="bedrooms"
              label="Bedrooms"
              value={formData.bedrooms || ''}
              onChange={handleInputChange}
              error={errors.bedrooms}
            />
            
            <Input
              type="number"
              name="bathrooms"
              label="Bathrooms"
              value={formData.bathrooms || ''}
              onChange={handleInputChange}
              error={errors.bathrooms}
            />
          </div>
          
          <Input
            type="number"
            name="yearBuilt"
            label="Year Built"
            value={formData.yearBuilt || ''}
            onChange={handleInputChange}
            error={errors.yearBuilt}
          />
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Amenities
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {amenities.map((amenity) => (
                <div key={amenity.value} className="flex items-center">
                  <input
                    type="checkbox"
                    id={`amenity-${amenity.value}`}
                    value={amenity.value}
                    checked={formData.amenities?.includes(amenity.value) || false}
                    onChange={handleAmenityChange}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label
                    htmlFor={`amenity-${amenity.value}`}
                    className="ml-2 block text-sm text-gray-700 dark:text-gray-300"
                  >
                    {amenity.label}
                  </label>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
        
        <CardFooter>
          <Button type="submit" isLoading={isLoading}>
            Predict Price
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}