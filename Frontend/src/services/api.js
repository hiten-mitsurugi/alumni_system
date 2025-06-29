// services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// Automatically add the access token to every request
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token'); // <-- FIXED HERE
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

export default api;
