/**
 * Service Worker registration utility
 * This file provides functions to register and manage the service worker
 * for offline functionality in the POS system
 */

/**
 * Registers the service worker for offline capabilities
 */
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

/**
 * Checks if the application is currently online
 * @returns boolean indicating online status
 */
export function isOnline(): boolean {
  return typeof navigator !== 'undefined' ? navigator.onLine : true;
}

/**
 * Adds event listeners for online/offline status changes
 * @param onOnline Callback function when going online
 * @param onOffline Callback function when going offline
 * @returns Cleanup function to remove event listeners
 */
export function useOnlineStatus(
  onOnline: () => void,
  onOffline: () => void
): () => void {
  if (typeof window === 'undefined') return () => {};
  
  window.addEventListener('online', onOnline);
  window.addEventListener('offline', onOffline);
  
  return () => {
    window.removeEventListener('online', onOnline);
    window.removeEventListener('offline', onOffline);
  };
}