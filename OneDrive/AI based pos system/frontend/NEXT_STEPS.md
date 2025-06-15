# AI-Powered POS System: Next Steps Implementation

This document provides detailed implementation guidelines for enhancing the AI-based POS system frontend.

## 1. AI Assistant Integration

### Connecting to OpenRouter API

1. **Update Environment Variables**
   - Ensure `.env` file includes `NEXT_PUBLIC_OPENROUTER_API_KEY`

2. **Create AI Service Client**
   - Create a new file: `src/lib/api/ai.ts`

```typescript
// src/lib/api/ai.ts
import axios from 'axios';

const aiClient = axios.create({
  baseURL: 'https://openrouter.ai/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include API key
aiClient.interceptors.request.use((config) => {
  const apiKey = process.env.NEXT_PUBLIC_OPENROUTER_API_KEY;
  if (apiKey) {
    config.headers['Authorization'] = `Bearer ${apiKey}`;
  }
  return config;
});

export interface AIMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface AIResponse {
  id: string;
  content: string;
}

export async function generateAIResponse(
  messages: AIMessage[],
  contextInfo?: Record<string, any>
): Promise<AIResponse> {
  try {
    // Add system message with context if provided
    const allMessages = contextInfo
      ? [
          {
            role: 'system' as const,
            content: `You are an AI assistant for a POS system. Current context: ${JSON.stringify(contextInfo)}`,
          },
          ...messages,
        ]
      : messages;

    const response = await aiClient.post('/chat/completions', {
      model: 'openai/gpt-4-turbo',
      messages: allMessages,
    });

    return {
      id: response.data.id,
      content: response.data.choices[0].message.content,
    };
  } catch (error) {
    console.error('Error generating AI response:', error);
    throw new Error('Failed to generate AI response');
  }
}
```

3. **Update AIAssistantPanel Component**
   - Modify `src/components/ai/AIAssistantPanel.tsx` to use the real AI service

```typescript
// In AIAssistantPanel.tsx, replace the handleSendMessage function with:

import { generateAIResponse, AIMessage } from '@/lib/api/ai';

// ...

const handleSendMessage = async () => {
  if (!input.trim()) return;

  // Add user message
  const userMessage: Message = {
    id: generateId(),
    role: 'user',
    content: input,
    timestamp: new Date(),
  };

  setMessages((prev) => [...prev, userMessage]);
  setInput('');
  setIsLoading(true);

  try {
    // Prepare context information
    const contextInfo = {
      currentView: context?.currentView || 'unknown',
      activeOrder: context?.activeOrder,
      selectedProducts: context?.selectedProducts,
    };
    
    // Convert messages to AI message format
    const aiMessages: AIMessage[] = messages.map(msg => ({
      role: msg.role,
      content: msg.content
    }));
    
    // Add current user message
    aiMessages.push({
      role: 'user',
      content: input
    });
    
    // Get AI response
    const aiResponse = await generateAIResponse(aiMessages, contextInfo);
    
    // Add AI response to messages
    const assistantMessage: Message = {
      id: generateId(),
      role: 'assistant',
      content: aiResponse.content,
      timestamp: new Date(),
    };
    
    setMessages((prev) => [...prev, assistantMessage]);
  } catch (error) {
    console.error('Error getting AI response:', error);
    
    // Add error message
    const errorMessage: Message = {
      id: generateId(),
      role: 'assistant',
      content: 'Sorry, I encountered an error. Please try again later.',
      timestamp: new Date(),
    };
    
    setMessages((prev) => [...prev, errorMessage]);
  } finally {
    setIsLoading(false);
  }
};
```

## 2. Backend API Integration

### Products API

1. **Create Products API Client**
   - Create a new file: `src/lib/api/products.ts`

```typescript
// src/lib/api/products.ts
import { apiClient } from './client';

export interface Product {
  id: number;
  name: string;
  price: number;
  image_url?: string;
  barcode?: string;
  category_id?: number;
  category_name?: string;
  stock_quantity: number;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface ProductsResponse {
  data: Product[];
  total: number;
  page: number;
  limit: number;
}

export interface ProductParams {
  page?: number;
  limit?: number;
  search?: string;
  category_id?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export async function getProducts(params?: ProductParams): Promise<ProductsResponse> {
  const response = await apiClient.get('/products', { params });
  return response.data;
}

export async function getProduct(id: number): Promise<Product> {
  const response = await apiClient.get(`/products/${id}`);
  return response.data;
}

export async function createProduct(product: Partial<Product>): Promise<Product> {
  const response = await apiClient.post('/products', product);
  return response.data;
}

export async function updateProduct(id: number, product: Partial<Product>): Promise<Product> {
  const response = await apiClient.put(`/products/${id}`, product);
  return response.data;
}

export async function deleteProduct(id: number): Promise<void> {
  await apiClient.delete(`/products/${id}`);
}
```

### Orders API

1. **Create Orders API Client**
   - Create a new file: `src/lib/api/orders.ts`

```typescript
// src/lib/api/orders.ts
import { apiClient } from './client';

export interface OrderItem {
  id: number;
  product_id: number;
  product_name: string;
  quantity: number;
  price: number;
  discount?: number;
  total: number;
}

export interface Order {
  id: number;
  order_number: string;
  customer_id?: number;
  customer_name?: string;
  items: OrderItem[];
  subtotal: number;
  tax: number;
  discount?: number;
  total: number;
  payment_method: string;
  status: 'pending' | 'completed' | 'cancelled';
  created_at: string;
  updated_at: string;
}

export interface OrdersResponse {
  data: Order[];
  total: number;
  page: number;
  limit: number;
}

export interface OrderParams {
  page?: number;
  limit?: number;
  search?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export async function getOrders(params?: OrderParams): Promise<OrdersResponse> {
  const response = await apiClient.get('/orders', { params });
  return response.data;
}

export async function getOrder(id: number): Promise<Order> {
  const response = await apiClient.get(`/orders/${id}`);
  return response.data;
}

export async function createOrder(order: Partial<Order>): Promise<Order> {
  const response = await apiClient.post('/orders', order);
  return response.data;
}

export async function updateOrderStatus(id: number, status: Order['status']): Promise<Order> {
  const response = await apiClient.patch(`/orders/${id}/status`, { status });
  return response.data;
}

export async function deleteOrder(id: number): Promise<void> {
  await apiClient.delete(`/orders/${id}`);
}
```

## 3. Update POS Page with Real Data

1. **Modify POS Page**
   - Update `src/app/pos/page.tsx` to use real product data

```typescript
// In src/app/pos/page.tsx, update to use real API

import { useEffect, useState } from 'react';
import { getProducts, Product } from '@/lib/api/products';
import { createOrder } from '@/lib/api/orders';

// Replace the products state and mock data with:
const [products, setProducts] = useState<Product[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

// Add this useEffect to fetch products
useEffect(() => {
  async function fetchProducts() {
    try {
      setLoading(true);
      const response = await getProducts({
        limit: 50,
        search: searchTerm || undefined
      });
      setProducts(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching products:', err);
      setError('Failed to load products. Please try again.');
    } finally {
      setLoading(false);
    }
  }
  
  fetchProducts();
}, [searchTerm]);

// Update the handleCheckout function
const handleCheckout = async () => {
  if (cart.length === 0) return;
  
  try {
    setIsProcessing(true);
    
    const orderData = {
      items: cart.map(item => ({
        product_id: item.id,
        quantity: item.quantity,
        price: item.price,
        total: item.price * item.quantity
      })),
      subtotal: calculateTotal(),
      tax: calculateTotal() * 0.1, // 10% tax
      total: calculateTotal() * 1.1, // Total with tax
      payment_method: 'cash', // Default payment method
      status: 'completed' as const
    };
    
    const order = await createOrder(orderData);
    
    // Clear cart after successful order
    setCart([]);
    setIsOrderComplete(true);
    setOrderNumber(order.order_number);
    
    // Reset after 5 seconds
    setTimeout(() => {
      setIsOrderComplete(false);
      setOrderNumber('');
    }, 5000);
  } catch (err) {
    console.error('Error processing order:', err);
    alert('Failed to process order. Please try again.');
  } finally {
    setIsProcessing(false);
  }
};
```

## 4. Implement Offline Mode

1. **Create Service Worker**
   - Create a new file: `public/sw.js`

```javascript
// public/sw.js
const CACHE_NAME = 'pos-cache-v1';
const urlsToCache = [
  '/',
  '/dashboard',
  '/pos',
  '/products',
  '/orders',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Cache hit - return response
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
      .catch(() => {
        // If both cache and network fail, show offline page
        if (event.request.mode === 'navigate') {
          return caches.match('/offline');
        }
      })
  );
});

self.addEventListener('activate', (event) => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
```

2. **Register Service Worker**
   - Create a new file: `src/lib/serviceWorker.ts`

```typescript
// src/lib/serviceWorker.ts
export function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js').then(
        (registration) => {
          console.log('ServiceWorker registration successful with scope: ', registration.scope);
        },
        (err) => {
          console.log('ServiceWorker registration failed: ', err);
        }
      );
    });
  }
}
```

3. **Initialize Service Worker in Layout**
   - Update `src/app/layout.tsx` to register the service worker

```typescript
// In src/app/layout.tsx

'use client';

import { useEffect } from 'react';
import { registerServiceWorker } from '@/lib/serviceWorker';

// Inside your Layout component
useEffect(() => {
  registerServiceWorker();
}, []);
```

## 5. Create Offline Page

1. **Create Offline Page**
   - Create a new file: `src/app/offline/page.tsx`

```typescript
// src/app/offline/page.tsx
'use client';

import { useEffect, useState } from 'react';
import Button from '@/components/ui/Button';

export default function OfflinePage() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    setIsOnline(navigator.onLine);

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleRetry = () => {
    window.location.href = '/';
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 text-center">
      <svg
        className="w-24 h-24 text-gray-400 mb-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M18.364 5.636a9 9 0 010 12.728m-3.536-3.536a3 3 0 010-5.656M13 12a1 1 0 11-2 0 1 1 0 012 0z"
        />
      </svg>
      <h1 className="text-3xl font-bold mb-2">You're offline</h1>
      <p className="text-gray-600 mb-8 max-w-md">
        It looks like you've lost your internet connection. Some features may be unavailable until you're back online.
      </p>
      <div className="space-y-4">
        <p className="text-sm font-medium">
          Status: {isOnline ? 'Online' : 'Offline'}
        </p>
        <Button onClick={handleRetry}>
          Try Again
        </Button>
      </div>
    </div>
  );
}
```

This implementation plan provides concrete steps to enhance your AI-powered POS system with real API integration, offline capabilities, and improved user experience. Follow these steps to transform your frontend from using mock data to a fully functional application connected to your Odoo backend.