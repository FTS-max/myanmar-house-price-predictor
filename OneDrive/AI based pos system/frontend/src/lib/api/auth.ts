import apiClient from './client';

/**
 * User role type definition
 */
export type UserRole = 'owner' | 'manager' | 'cashier';

/**
 * User interface definition
 */
export interface User {
  id: number;
  name: string;
  email: string;
  pos_role: UserRole;
  shop_ids: number[];
  active_shop_id?: number;
}

/**
 * Login response interface
 */
export interface LoginResponse {
  token: string;
  user: User;
}

/**
 * Authentication API functions
 */
const authApi = {
  /**
   * Login with username and password
   */
  login: async (username: string, password: string): Promise<LoginResponse> => {
    const response = await apiClient.post('/api/auth/login', {
      username,
      password,
      db: process.env.NEXT_PUBLIC_ODOO_DB || 'pos_system',
    });
    return response.data;
  },

  /**
   * Logout the current user
   */
  logout: async (): Promise<void> => {
    await apiClient.post('/api/auth/logout');
    // Clear auth data
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem(process.env.NEXT_PUBLIC_AUTH_TOKEN_NAME || 'odoo_api_key');
    }
  },

  /**
   * Get the current user's information
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get('/api/auth/user');
    return response.data;
  },

  /**
   * Set the active shop for the current user
   */
  setActiveShop: async (shopId: number): Promise<User> => {
    const response = await apiClient.post('/api/auth/set_active_shop', { shop_id: shopId });
    return response.data;
  },
};

export default authApi;