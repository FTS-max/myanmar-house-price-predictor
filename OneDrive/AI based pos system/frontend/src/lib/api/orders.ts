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

/**
 * Fetches a list of orders with optional filtering and pagination
 * @param params Optional parameters for filtering and pagination
 * @returns Promise with order list response
 */
export async function getOrders(params?: OrderParams): Promise<OrdersResponse> {
  const response = await apiClient.get('/orders', { params });
  return response.data;
}

/**
 * Fetches a single order by ID
 * @param id Order ID
 * @returns Promise with order data
 */
export async function getOrder(id: number): Promise<Order> {
  const response = await apiClient.get(`/orders/${id}`);
  return response.data;
}

/**
 * Creates a new order
 * @param order Order data
 * @returns Promise with created order data
 */
export async function createOrder(order: Partial<Order>): Promise<Order> {
  const response = await apiClient.post('/orders', order);
  return response.data;
}

/**
 * Updates an order's status
 * @param id Order ID
 * @param status New status
 * @returns Promise with updated order data
 */
export async function updateOrderStatus(id: number, status: Order['status']): Promise<Order> {
  const response = await apiClient.patch(`/orders/${id}/status`, { status });
  return response.data;
}

/**
 * Deletes an order
 * @param id Order ID
 * @returns Promise that resolves when deletion is complete
 */
export async function deleteOrder(id: number): Promise<void> {
  await apiClient.delete(`/orders/${id}`);
}