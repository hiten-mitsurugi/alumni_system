import { defineStore } from 'pinia';
import api from '../services/api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || null,  // ✅ updated
    refreshToken: localStorage.getItem('refresh_token') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
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
      localStorage.removeItem('access_token');            // ✅ updated
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
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
      if (!this.refreshToken) return false;

      try {
        const response = await api.post('/token/refresh/', {
          refresh: this.refreshToken,
        });

        const newAccess = response.data.access;
        this.setToken(newAccess, this.refreshToken);
        return true;
      } catch (error) {
        console.error('Token refresh failed:', error);
        return false;
      }
    },
  },
});
