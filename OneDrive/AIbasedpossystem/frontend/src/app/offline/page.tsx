'use client';

import { useEffect, useState } from 'react';
import Button from '@/components/ui/Button';
import { isOnline, setupOnlineStatusListeners } from '@/lib/serviceWorker';

/**
 * Offline Page Component
 * Displays when the user is offline and attempts to access the application
 */
export default function OfflinePage() {
  const [online, setOnline] = useState(true);

  useEffect(() => {
    // Set initial online status
    setOnline(isOnline());

    // Setup listeners for online/offline events
    const cleanup = setupOnlineStatusListeners(
      () => setOnline(true),
      () => setOnline(false)
    );

    return cleanup;
  }, []);

  /**
   * Handles retry attempt when user clicks the Try Again button
   */
  const handleRetry = () => {
    if (online) {
      window.location.href = '/';
    } else {
      // If still offline, show a message
      alert('Still offline. Please check your internet connection.');
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 text-center bg-gray-50">
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
      
      <h1 className="text-3xl font-bold mb-2">You&apos;re offline</h1>
      
      <p className="text-gray-600 mb-8 max-w-md">
        It looks like you&apos;ve lost your internet connection. Some features may be unavailable until you&apos;re back online.
        The POS system will continue to work with limited functionality.
      </p>
      
      <div className="space-y-4">
        <div className="flex items-center justify-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${online ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <p className="text-sm font-medium">
            Status: {online ? 'Online' : 'Offline'}
          </p>
        </div>
        
        <Button onClick={handleRetry} className="px-6">
          Try Again
        </Button>
        
        {online && (
          <p className="text-sm text-green-600 mt-2">
            You&apos;re back online! Click Try Again to continue.
          </p>
        )}
      </div>
      
      <div className="mt-12 text-sm text-gray-500">
        <p>While offline, you can still:</p>
        <ul className="mt-2 list-disc list-inside">
          <li>View cached products</li>
          <li>Create new orders (will sync when back online)</li>
          <li>Access basic POS functionality</li>
        </ul>
      </div>
    </div>
  );
}
