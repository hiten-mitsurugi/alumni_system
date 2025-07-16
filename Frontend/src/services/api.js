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
    if ((error.response?.status === 401 || error.response?.status === 403) && !error.config._retry) {
      error.config._retry = true;
      const authStore = useAuthStore();
      const newToken = await authStore.tryRefreshToken(); // Use authStore's refresh method
      if (newToken) {
        error.config.headers.Authorization = `Bearer ${newToken}`;
        return api(error.config); // Retry with new token
      } else {
        authStore.logout();
        window.location.href = '/login';
      }
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