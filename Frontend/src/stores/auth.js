import { defineStore } from 'pinia';
import api from '../services/api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || null,  // ✅ updated
    refreshToken: localStorage.getItem('refresh_token') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
    isRefreshing: false, // Add flag to prevent multiple refresh attempts
  }),

  actions: {
    setToken(access, refresh) {
      this.token = access;
      this.refreshToken = refresh;
      localStorage.setItem('access_token', access);       // ✅ updated
      localStorage.setItem('refresh_token', refresh);
    },

    setUser(user) {
      this.user = user;
      localStorage.setItem('user', JSON.stringify(user));
    },

    logout() {
      this.token = null;
      this.refreshToken = null;
      this.user = null;
      this.isRefreshing = false; // Reset refresh flag
      localStorage.removeItem('access_token');            // ✅ updated
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    },

    async logoutWithAPI() {
      console.log('=== AUTH STORE DEBUG: Starting logoutWithAPI ===');
      console.log('AUTH STORE DEBUG: Current refreshToken:', this.refreshToken ? 'exists' : 'null');
      console.log('AUTH STORE DEBUG: Current token:', this.token ? 'exists' : 'null');
      
      try {
        // Call backend logout API to set status to offline and broadcast
        if (this.refreshToken) {
          console.log('AUTH STORE DEBUG: Making POST request to /logout/');
          const response = await api.post('/logout/', {
            refresh: this.refreshToken
          });
          console.log('AUTH STORE DEBUG: Backend logout response:', response.status, response.data);
          console.log('AUTH STORE DEBUG: Backend logout successful - status set to offline and broadcasted');
        } else {
          console.log('AUTH STORE DEBUG: No refresh token available, skipping backend logout API call');
        }
      } catch (error) {
        console.error('AUTH STORE DEBUG: Backend logout failed:', error);
        console.error('AUTH STORE DEBUG: Error response:', error.response?.status, error.response?.data);
        // Continue with frontend logout even if backend fails
        // This ensures the user can always log out from the frontend
        // even if there are network issues
      }
      
      console.log('AUTH STORE DEBUG: Calling frontend logout to clear tokens');
      // Clear frontend state regardless of backend success/failure
      this.logout();
      console.log('AUTH STORE DEBUG: logoutWithAPI completed');
    },

    async fetchUser() {
      if (!this.token) return;

      try {
        const response = await api.get('/user/');
        this.setUser(response.data);
      } catch (error) {
        const response = error.response;
        const errData = response?.data;

        if (response?.status === 403 && errData?.code === 'token_not_valid') {
          const refreshed = await this.tryRefreshToken();
          if (refreshed) {
            try {
              const retry = await api.get('/user/');
              this.setUser(retry.data);
            } catch (err) {
              this.logout();
              console.error('Retry after refresh failed:', err);
            }
          } else {
            this.logout();
          }
        } else {
          console.error('Fetch user failed:', error);
        }
      }
    },

    async tryRefreshToken() {
      if (!this.refreshToken) {
        console.log('No refresh token available');
        return false;
      }

      // Prevent multiple simultaneous refresh attempts
      if (this.isRefreshing) {
        console.log('Token refresh already in progress');
        return false;
      }

      try {
        this.isRefreshing = true;
        console.log('Attempting to refresh token...');
        
        const response = await api.post('/token/refresh/', {
          refresh: this.refreshToken,
        });

        const newAccess = response.data.access;
        this.setToken(newAccess, this.refreshToken);
        console.log('Token refreshed successfully');
        return true;
      } catch (error) {
        console.error('Token refresh failed:', error);
        
        // If refresh fails, clear all tokens to prevent infinite loops
        if (error.response?.status === 401) {
          console.log('Refresh token is invalid, clearing all tokens');
          this.logout();
        }
        
        return false;
      } finally {
        this.isRefreshing = false;
      }
    },
  },
});
