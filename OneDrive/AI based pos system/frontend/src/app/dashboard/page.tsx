'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/lib/auth/AuthContext';
import { useRouter } from 'next/navigation';
import Button from '@/components/ui/Button';

/**
 * Dashboard page component
 */
export default function DashboardPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [isClient, setIsClient] = useState(false);
  
  // Ensure we're running on client side
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Handle logout
  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  // Handle navigation to POS
  const handleNavigateToPOS = () => {
    router.push('/pos');
  };

  // Handle navigation to orders
  const handleNavigateToOrders = () => {
    router.push('/orders');
  };

  // Handle navigation to products
  const handleNavigateToProducts = () => {
    router.push('/products');
  };

  if (!isClient) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <div className="flex items-center space-x-4">
            {user && (
              <span className="text-sm text-gray-700">
                Welcome, <span className="font-medium">{user.name}</span>
                {user.active_shop && (
                  <span className="ml-2 text-blue-600">
                    | Shop: {user.active_shop.name}
                  </span>
                )}
              </span>
            )}
            <Button variant="outline" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* POS Card */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-blue-500 rounded-md p-3">
                  <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dt className="text-lg font-medium text-gray-900 truncate">
                    Point of Sale
                  </dt>
                  <dd className="mt-1 text-sm text-gray-500">
                    Process sales and manage transactions
                  </dd>
                </div>
              </div>
              <div className="mt-5">
                <Button onClick={handleNavigateToPOS} className="w-full">
                  Open POS
                </Button>
              </div>
            </div>
          </div>

          {/* Orders Card */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-green-500 rounded-md p-3">
                  <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dt className="text-lg font-medium text-gray-900 truncate">
                    Orders
                  </dt>
                  <dd className="mt-1 text-sm text-gray-500">
                    View and manage all orders
                  </dd>
                </div>
              </div>
              <div className="mt-5">
                <Button onClick={handleNavigateToOrders} variant="secondary" className="w-full">
                  View Orders
                </Button>
              </div>
            </div>
          </div>

          {/* Products Card */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0 bg-purple-500 rounded-md p-3">
                  <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                  </svg>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dt className="text-lg font-medium text-gray-900 truncate">
                    Products
                  </dt>
                  <dd className="mt-1 text-sm text-gray-500">
                    Manage your product catalog
                  </dd>
                </div>
              </div>
              <div className="mt-5">
                <Button onClick={handleNavigateToProducts} variant="secondary" className="w-full">
                  View Products
                </Button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}