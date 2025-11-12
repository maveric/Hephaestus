/**
 * API Configuration Utility
 * 
 * Centralized configuration for API endpoints.
 * Uses environment variables to determine the backend host.
 */

// Get API configuration from environment variables
const apiHost = import.meta.env.VITE_API_HOST || 'localhost';
const apiPort = import.meta.env.VITE_API_PORT || '8000';
const apiProtocol = import.meta.env.VITE_API_PROTOCOL || 'http';

/**
 * Get the base URL for API calls
 * @returns {string} The base API URL (e.g., "http://localhost:8000")
 */
export const getApiBaseUrl = (): string => {
  return `${apiProtocol}://${apiHost}:${apiPort}`;
};

/**
 * Get a full API URL for a given path
 * @param {string} path - The API path (e.g., "/api/workflows")
 * @returns {string} The full API URL
 */
export const getApiUrl = (path: string): string => {
  const baseUrl = getApiBaseUrl();
  // Ensure path starts with /
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${baseUrl}${normalizedPath}`;
};

/**
 * API configuration object
 */
export const apiConfig = {
  host: apiHost,
  port: apiPort,
  protocol: apiProtocol,
  baseUrl: getApiBaseUrl(),
};

export default apiConfig;
