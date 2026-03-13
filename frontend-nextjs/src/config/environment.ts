/**
 * Environment configuration validation and management
 */

interface EnvironmentConfig {
  apiBaseUrl: string;
  nodeEnv: string;
}

/**
 * Validates and returns the environment configuration
 */
export function getEnvironmentConfig(): EnvironmentConfig {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';
  const nodeEnv = process.env.NODE_ENV || 'development';

  // Validate API base URL format
  if (!apiBaseUrl.startsWith('http://') && !apiBaseUrl.startsWith('https://')) {
    throw new Error('Invalid NEXT_PUBLIC_API_BASE_URL format. Must start with http:// or https://');
  }

  // Remove trailing slash if present
  const normalizedApiBaseUrl = apiBaseUrl.replace(/\/$/, '');

  return {
    apiBaseUrl: normalizedApiBaseUrl,
    nodeEnv,
  };
}

/**
 * Get the API base URL
 */
export function getApiBaseUrl(): string {
  return getEnvironmentConfig().apiBaseUrl;
}

/**
 * Check if running in development mode
 */
export function isDevelopment(): boolean {
  return getEnvironmentConfig().nodeEnv === 'development';
}