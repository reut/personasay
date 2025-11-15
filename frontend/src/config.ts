// Configuration file for PersonaSay
// In production, these values should be set via environment variables
export type AppConfig = {
  openai: { apiKey: string };
  api: { baseUrl: string; endpoints: { chat: string; summary: string } };
};

// Get configuration from environment variables or use defaults
const getEnvVar = (key: string, defaultValue: string): string => {
  if (typeof import.meta !== 'undefined' && import.meta.env) {
    return import.meta.env[key] || defaultValue;
  }
  return defaultValue;
};

export const config: AppConfig = {
  // OpenAI API Configuration
  // NOTE: API key is stored on backend only for security
  openai: {
    apiKey: '' // Not used - backend handles API key
  },
  // API Endpoints
  api: {
    baseUrl: getEnvVar('VITE_API_BASE_URL', 'http://localhost:8000'),
    endpoints: {
      chat: '/chat',
      summary: '/summary'
    }
  }
};