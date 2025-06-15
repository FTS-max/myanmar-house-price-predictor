'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import authApi, { User, UserRole } from '@/lib/api/auth';

/**
 * Authentication context state interface
 */
interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  setActiveShop: (shopId: number) => Promise<void>;
  hasPermission: (requiredRole: UserRole | UserRole[]) => boolean;
}

/**
 * Create the authentication context
 */
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Authentication provider props
 */
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Authentication provider component
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Check if the user has a valid session on mount
   */
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check if we have a token
        const token = sessionStorage.getItem(
          process.env.NEXT_PUBLIC_AUTH_TOKEN_NAME || 'odoo_api_key'
        );
        
        if (!token) {
          setIsLoading(false);
          return;
        }
        
        // Get current user info
        const userData = await authApi.getCurrentUser();
        setUser(userData);
      } catch (err) {
        console.error('Authentication check failed:', err);
        // Clear any invalid auth data
        sessionStorage.removeItem(
          process.env.NEXT_PUBLIC_AUTH_TOKEN_NAME || 'odoo_api_key'
        );
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  /**
   * Login function
   */
  const login = async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await authApi.login(username, password);
      
      // Store the token
      sessionStorage.setItem(
        process.env.NEXT_PUBLIC_AUTH_TOKEN_NAME || 'odoo_api_key',
        response.token
      );
      
      // Set user data
      setUser(response.user);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Login failed. Please check your credentials.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Logout function
   */
  const logout = async () => {
    setIsLoading(true);
    
    try {
      await authApi.logout();
      setUser(null);
    } catch (err) {
      console.error('Logout failed:', err);
    } finally {
      // Always clear local auth data even if API call fails
      sessionStorage.removeItem(
        process.env.NEXT_PUBLIC_AUTH_TOKEN_NAME || 'odoo_api_key'
      );
      setIsLoading(false);
    }
  };

  /**
   * Set active shop function
   */
  const setActiveShop = async (shopId: number) => {
    setIsLoading(true);
    
    try {
      const updatedUser = await authApi.setActiveShop(shopId);
      setUser(updatedUser);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to set active shop.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Check if user has required role(s)
   */
  const hasPermission = (requiredRole: UserRole | UserRole[]): boolean => {
    if (!user) return false;
    
    // Convert single role to array for consistent handling
    const requiredRoles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];
    
    // Role hierarchy: owner > manager > cashier
    if (user.pos_role === 'owner') return true;
    if (user.pos_role === 'manager' && !requiredRoles.includes('owner')) return true;
    if (user.pos_role === 'cashier' && requiredRoles.includes('cashier')) return true;
    
    return false;
  };

  const value = {
    user,
    isLoading,
    error,
    login,
    logout,
    setActiveShop,
    hasPermission,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to use the authentication context
 */
export function useAuth() {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}