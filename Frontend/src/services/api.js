// services/api.js
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const api = axios.create({
  baseURL: 'http://localhost:8000/api', // Django backend API base URL
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    const token = authStore.token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for 401/403 handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !error.config._retry) {
      // Handle 401 errors (authentication failures)
      error.config._retry = true;
      const authStore = useAuthStore();
      const refreshSuccess = await authStore.tryRefreshToken();
      if (refreshSuccess) {
        // Use the updated token from the store
        error.config.headers.Authorization = `Bearer ${authStore.token}`;
        return api(error.config); // Retry with new token
      } else {
        authStore.logout();
        window.location.href = '/login';
      }
    } else if (error.response?.status === 403 && !error.config._retry) {
      // Handle 403 errors - check if it's actually an auth issue
      const errorMessage = error.response?.data?.error || error.response?.data?.detail || '';
      const isAuthError = errorMessage.toLowerCase().includes('token') || 
                         errorMessage.toLowerCase().includes('authentication') ||
                         errorMessage.toLowerCase().includes('credential') ||
                         errorMessage.toLowerCase().includes('signature') ||
                         errorMessage.toLowerCase().includes('expired');
      
      if (isAuthError) {
        // Only try refresh for actual auth-related 403 errors
        error.config._retry = true;
        const authStore = useAuthStore();
        const refreshSuccess = await authStore.tryRefreshToken();
        if (refreshSuccess) {
          // Use the updated token from the store
          error.config.headers.Authorization = `Bearer ${authStore.token}`;
          return api(error.config); // Retry with new token
        } else {
          authStore.logout();
          window.location.href = '/login';
        }
      }
      // For non-auth 403 errors (like blocking), just pass the error through
      // Don't try to refresh token or logout
    }
    return Promise.reject(error);
  }
);

// Add support for file uploads
api.upload = (url, formData, config = {}) => {
  return api.post(url, formData, {
    ...config,
    headers: {
      ...config.headers,
      'Content-Type': 'multipart/form-data',
    },
  });
};

export default api;