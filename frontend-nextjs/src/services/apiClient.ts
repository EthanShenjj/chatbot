import { getAuthToken } from '@/stores/authStore';
import { getApiBaseUrl } from '@/config/environment';

/**
 * Make an authenticated API request with automatic token inclusion
 */
export async function fetchWithAuth(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getAuthToken();
  
  const headers = new Headers(options.headers);
  
  // Add authorization header if token exists
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  
  // Add content-type if not already set and body exists
  // Don't set Content-Type for FormData - browser will set it with boundary
  if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  
  const response = await fetch(`${getApiBaseUrl()}${endpoint}`, {
    ...options,
    headers,
  });
  
  // Handle 401 unauthorized - token might be expired
  if (response.status === 401) {
    // Could trigger logout here if needed
    throw new Error('Unauthorized - please login again');
  }
  
  return response;
}

/**
 * Helper for GET requests
 */
export async function get(endpoint: string): Promise<Response> {
  return fetchWithAuth(endpoint, { method: 'GET' });
}

/**
 * Helper for POST requests
 */
export async function post(endpoint: string, data?: unknown): Promise<Response> {
  return fetchWithAuth(endpoint, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * Helper for PUT requests
 */
export async function put(endpoint: string, data?: unknown): Promise<Response> {
  return fetchWithAuth(endpoint, {
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * Helper for DELETE requests
 */
export async function del(endpoint: string): Promise<Response> {
  return fetchWithAuth(endpoint, { method: 'DELETE' });
}