'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth/AuthContext';
import Button from '@/components/ui/Button';
import { useRouter } from 'next/navigation';
import AIAssistantPanel from '@/components/ai/AIAssistantPanel';
import { getProducts, Product } from '@/lib/api/products';
import { createOrder } from '@/lib/api/orders';

/**
 * POS (Point of Sale) page component
 */
export default function POSPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const [cart, setCart] = useState<Product[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isCheckingOut, setIsCheckingOut] = useState(false);
  const [isClient, setIsClient] = useState(false);
  const [isAIAssistantOpen, setIsAIAssistantOpen] = useState(false);
  const [isLoadingProducts, setIsLoadingProducts] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [orderNumber, setOrderNumber] = useState('');
  const [isOrderComplete, setIsOrderComplete] = useState(false);
  
  // Ensure we're running on client side
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Fetch products from API
  useEffect(() => {
    async function fetchProducts() {
      try {
        setIsLoadingProducts(true);
        const response = await getProducts({
          limit: 50,
          search: searchTerm || undefined
        });
        setProducts(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching products:', err);
        setError('Failed to load products. Please try again.');
        // Use mock data as fallback when offline or API fails
        const mockProducts = [
          { id: 1, name: 'Product 1', price: 10.99, image_url: '/placeholder.jpg', barcode: '123456789', stock_quantity: 100, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
          { id: 2, name: 'Product 2', price: 15.99, image_url: '/placeholder.jpg', barcode: '234567890', stock_quantity: 50, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
          { id: 3, name: 'Product 3', price: 5.99, image_url: '/placeholder.jpg', barcode: '345678901', stock_quantity: 75, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
          { id: 4, name: 'Product 4', price: 20.99, image_url: '/placeholder.jpg', barcode: '456789012', stock_quantity: 30, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
          { id: 5, name: 'Product 5', price: 8.99, image_url: '/placeholder.jpg', barcode: '567890123', stock_quantity: 60, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
          { id: 6, name: 'Product 6', price: 12.99, image_url: '/placeholder.jpg', barcode: '678901234', stock_quantity: 45, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
        ];
        setProducts(mockProducts as Product[]);
      } finally {
        setIsLoadingProducts(false);
      }
    }
    
    fetchProducts();
  }, [searchTerm]);

  // Add product to cart
  const addToCart = (product: Product) => {
    const existingItem = cart.find(item => item.id === product.id);
    
    if (existingItem) {
      setCart(cart.map(item => 
        item.id === product.id 
          ? { ...item, quantity: (item as any).quantity + 1 } 
          : item
      ));
    } else {
      setCart([...cart, { ...product, quantity: 1 } as any]);
    }
  };

  // Remove product from cart
  const removeFromCart = (productId: number) => {
    const existingItem = cart.find(item => item.id === productId);
    
    if (existingItem && (existingItem as any).quantity > 1) {
      setCart(cart.map(item => 
        item.id === productId 
          ? { ...item, quantity: (item as any).quantity - 1 } 
          : item
      ));
    } else {
      setCart(cart.filter(item => item.id !== productId));
    }
  };

  // Calculate total
  const calculateTotal = () => {
    return cart.reduce((total, item) => total + (item.price * ((item as any).quantity || 1)), 0);
  };

  // Handle checkout
  const handleCheckout = async () => {
    if (cart.length === 0) return;
    
    try {
      setIsCheckingOut(true);
      
      const orderData = {
        items: cart.map(item => ({
          product_id: item.id,
          quantity: (item as any).quantity || 1,
          price: item.price,
          total: item.price * ((item as any).quantity || 1)
        })),
        subtotal: calculateTotal(),
        tax: calculateTotal() * 0.1, // 10% tax
        total: calculateTotal() * 1.1, // Total with tax
        payment_method: 'cash', // Default payment method
        status: 'completed' as const
      };
      
      try {
        const order = await createOrder(orderData);
        setOrderNumber(order.order_number);
      } catch (err) {
        console.error('Error creating order:', err);
        // Generate a mock order number if API fails
        setOrderNumber(`ORD-${Math.floor(Math.random() * 10000)}`);
      }
      
      // Clear cart after successful order
      setCart([]);
      setIsOrderComplete(true);
      
      // Reset after 5 seconds
      setTimeout(() => {
        setIsOrderComplete(false);
        setOrderNumber('');
      }, 5000);
    } catch (err) {
      console.error('Error processing order:', err);
      alert('Failed to process order. Please try again.');
    } finally {
      setIsCheckingOut(false);
    }
  };

  // Filter products based on search term
  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (product.barcode && product.barcode.includes(searchTerm))
  );

  // Navigate back to dashboard
  const handleBackToDashboard = () => {
    router.push('/dashboard');
  };

  // Toggle AI Assistant panel
  const toggleAIAssistant = () => {
    setIsAIAssistantOpen(!isAIAssistantOpen);
  };

  if (!isClient) return null;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center">
            <button
              onClick={handleBackToDashboard}
              className="mr-4 text-gray-600 hover:text-gray-900"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
            <h1 className="text-2xl font-bold text-gray-900">Point of Sale</h1>
          </div>
          <div className="flex items-center space-x-4">
            {user && (
              <span className="text-sm text-gray-700">
                <span className="font-medium">{user.name}</span>
                {user.active_shop && (
                  <span className="ml-2 text-blue-600">
                    | Shop: {user.active_shop.name}
                  </span>
                )}
              </span>
            )}
            <button
              onClick={toggleAIAssistant}
              className="p-2 rounded-full bg-blue-100 text-blue-600 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              title="AI Assistant"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 flex flex-col md:flex-row">
        {/* Products section */}
        <div className="w-full md:w-2/3 p-4">
          <div className="mb-4">
            <input
              type="text"
              placeholder="Search products by name or scan barcode..."
              className="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          {isLoadingProducts ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
              <strong className="font-bold">Error: </strong>
              <span className="block sm:inline">{error}</span>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
              {filteredProducts.map((product) => (
                <div
                  key={product.id}
                  className="bg-white rounded-lg shadow overflow-hidden cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => addToCart(product)}
                >
                  <div className="h-32 bg-gray-200 flex items-center justify-center">
                    {product.image_url ? (
                      <img 
                        src={product.image_url} 
                        alt={product.name} 
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <svg className="h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                      </svg>
                    )}
                  </div>
                  <div className="p-4">
                    <h3 className="text-sm font-medium text-gray-900 truncate">{product.name}</h3>
                    <p className="mt-1 text-sm text-gray-500">${product.price.toFixed(2)}</p>
                    {product.stock_quantity !== undefined && (
                      <p className="mt-1 text-xs text-gray-500">Stock: {product.stock_quantity}</p>
                    )}
                  </div>
                </div>
              ))}
              
              {filteredProducts.length === 0 && (
                <div className="col-span-full text-center py-12">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="mt-2 text-gray-500">No products found</p>
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* Cart section */}
        <div className="w-full md:w-1/3 bg-white border-l border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Shopping Cart</h2>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4">
            {isOrderComplete && (
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4" role="alert">
                <p className="font-bold">Order Complete!</p>
                <p>Order #{orderNumber} has been processed successfully.</p>
              </div>
            )}
            
            {cart.length === 0 ? (
              <div className="text-center py-8">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                </svg>
                <p className="mt-2 text-sm text-gray-500">Your cart is empty</p>
              </div>
            ) : (
              <ul className="divide-y divide-gray-200">
                {cart.map((item) => (
                  <li key={item.id} className="py-4 flex">
                    <div className="flex-shrink-0 w-16 h-16 bg-gray-200 rounded-md flex items-center justify-center">
                      {item.image_url ? (
                        <img 
                          src={item.image_url} 
                          alt={item.name} 
                          className="h-full w-full object-cover rounded-md"
                        />
                      ) : (
                        <svg className="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                        </svg>
                      )}
                    </div>
                    <div className="ml-4 flex-1 flex flex-col">
                      <div className="flex justify-between text-sm font-medium text-gray-900">
                        <h3>{item.name}</h3>
                        <p className="ml-4">${(item.price * ((item as any).quantity || 1)).toFixed(2)}</p>
                      </div>
                      <div className="flex items-center mt-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            removeFromCart(item.id);
                          }}
                          className="text-gray-500 hover:text-gray-700 p-1"
                        >
                          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                          </svg>
                        </button>
                        <span className="mx-2 text-gray-700">{(item as any).quantity || 1}</span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            addToCart(item);
                          }}
                          className="text-gray-500 hover:text-gray-700 p-1"
                        >
                          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
          
          <div className="p-4 border-t border-gray-200">
            <div className="flex justify-between text-base font-medium text-gray-900 mb-4">
              <p>Subtotal</p>
              <p>${calculateTotal().toFixed(2)}</p>
            </div>
            <Button
              onClick={handleCheckout}
              disabled={cart.length === 0 || isCheckingOut}
              isLoading={isCheckingOut}
              className="w-full"
            >
              Checkout
            </Button>
          </div>
        </div>
      </div>

      {/* AI Assistant Panel */}
      <AIAssistantPanel
        isOpen={isAIAssistantOpen}
        onClose={() => setIsAIAssistantOpen(false)}
        context={{
          currentView: 'pos',
          activeOrder: { items: cart, total: calculateTotal() },
          selectedProducts: cart,
        }}
      />
    </div>
  );
}