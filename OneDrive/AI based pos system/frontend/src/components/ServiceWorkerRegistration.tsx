'use client';

import { useEffect } from 'react';
import { registerServiceWorker } from '@/lib/serviceWorker';

/**
 * Client component to register service worker
 * This is used in the root layout to enable offline functionality
 */
export default function ServiceWorkerRegistration() {
  useEffect(() => {
    registerServiceWorker();
  }, []);

  return null; // This component doesn't render anything
}