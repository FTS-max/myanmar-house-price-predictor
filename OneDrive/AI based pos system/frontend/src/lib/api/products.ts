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

/**
 * Fetches a list of products with optional filtering and pagination
 * @param params Optional parameters for filtering and pagination
 * @returns Promise with product list response
 */
export async function getProducts(params?: ProductParams): Promise<ProductsResponse> {
  const response = await apiClient.get('/products', { params });
  return response.data;
}

/**
 * Fetches a single product by ID
 * @param id Product ID
 * @returns Promise with product data
 */
export async function getProduct(id: number): Promise<Product> {
  const response = await apiClient.get(`/products/${id}`);
  return response.data;
}

/**
 * Creates a new product
 * @param product Product data
 * @returns Promise with created product data
 */
export async function createProduct(product: Partial<Product>): Promise<Product> {
  const response = await apiClient.post('/products', product);
  return response.data;
}

/**
 * Updates an existing product
 * @param id Product ID
 * @param product Updated product data
 * @returns Promise with updated product data
 */
export async function updateProduct(id: number, product: Partial<Product>): Promise<Product> {
  const response = await apiClient.put(`/products/${id}`, product);
  return response.data;
}

/**
 * Deletes a product
 * @param id Product ID
 * @returns Promise that resolves when deletion is complete
 */
export async function deleteProduct(id: number): Promise<void> {
  await apiClient.delete(`/products/${id}`);
}