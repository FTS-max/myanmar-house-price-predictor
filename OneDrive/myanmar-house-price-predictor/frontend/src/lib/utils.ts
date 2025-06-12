/**
 * Utility functions for the application
 */

/**
 * Combines multiple class names into a single string
 */
export function cn(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ');
}

/**
 * Format a number as Myanmar Kyats (MMK)
 */
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-MM', {
    style: 'currency',
    currency: 'MMK',
    maximumFractionDigits: 0,
  }).format(value);
}

/**
 * Format a number with thousands separators
 */
export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en').format(value);
}

/**
 * Format a number as a percentage
 */
export function formatPercentage(value: number): string {
  return new Intl.NumberFormat('en', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value / 100);
}

/**
 * Format a date as a string
 */
export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('en-MM', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Debounce a function call
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  
  return function(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };
    
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Generate a random ID
 */
export function generateId(): string {
  return Math.random().toString(36).substring(2, 9);
}

/**
 * Truncate a string to a maximum length
 */
export function truncate(str: string, length: number): string {
  if (str.length <= length) return str;
  return str.slice(0, length) + '...';
}

/**
 * Calculate the similarity percentage (0-100) between two numbers
 */
export function calculateSimilarity(value1: number, value2: number): number {
  const max = Math.max(value1, value2);
  const min = Math.min(value1, value2);
  
  if (max === 0) return 100; // Both values are 0
  
  const similarity = (1 - (max - min) / max) * 100;
  return Math.round(similarity);
}