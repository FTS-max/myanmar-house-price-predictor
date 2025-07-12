import axios from 'axios';

/**
 * Base API URL from environment variables
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_ODOO_API_URL || 'http://localhost:8069';

/**
 * Axios instance configured for Odoo API communication
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor to attach authentication token
 */
apiClient.interceptors.request.use((config) => {
  // Only run on client side
  if (typeof window !== 'undefined') {
    const token = sessionStorage.getItem(process.env.NEXT_PUBLIC_AUTH_TOKEN_NAME || 'odoo_api_key');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

/**
 * Response interceptor to handle common errors
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle authentication errors
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      // Clear auth data and redirect to login
      sessionStorage.removeItem(process.env.NEXT_PUBLIC_AUTH_TOKEN_NAME || 'odoo_api_key');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export { apiClient };
export default apiClient;