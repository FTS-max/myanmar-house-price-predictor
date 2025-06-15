import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Define paths that don't require authentication
const publicPaths = [
  '/login',
  // Add other public paths here
];

/**
 * Middleware function to handle authentication and route protection
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Check if the path is public
  const isPublicPath = publicPaths.some(path => 
    pathname === path || pathname.startsWith(`${path}/`)
  );
  
  // Get auth token from cookies
  const authToken = request.cookies.get(
    process.env.NEXT_PUBLIC_AUTH_COOKIE_NAME || 'odoo_auth'
  );
  
  // Redirect logic
  if (!authToken && !isPublicPath) {
    // Redirect to login if trying to access protected route without auth
    const url = new URL('/login', request.url);
    url.searchParams.set('callbackUrl', encodeURI(request.url));
    return NextResponse.redirect(url);
  }
  
  if (authToken && pathname === '/login') {
    // Redirect to dashboard if already logged in and trying to access login page
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }
  
  return NextResponse.next();
}

/**
 * Configure which paths the middleware runs on
 */
export const config = {
  // Match all request paths except for static files, api routes, etc.
  matcher: [
    /*
     * Match all paths except for:
     * 1. /api routes
     * 2. /_next (Next.js internals)
     * 3. /_static (inside /public)
     * 4. /_vercel (Vercel internals)
     * 5. /favicon.ico, /sitemap.xml, /robots.txt (static files)
     */
    '/((?!api|_next|_static|_vercel|favicon.ico|sitemap.xml|robots.txt).*)',
  ],
};