import { useAuthStore } from '@/stores/auth';

export class WebSocketService {
  constructor() {
    this.sockets = new Map();
    this.listeners = new Map();
    this.reconnectAttempts = new Map();
    this.maxReconnectAttempts = 5;
  }

  getAuthStore() {
    // Lazy initialization of auth store to avoid Pinia timing issues
    return useAuthStore();
  }

  async connect(endpoint = 'notifications') {
    const authStore = this.getAuthStore();
    
    if (!authStore.token) {
      try {
        await authStore.tryRefreshToken();
        if (!authStore.token) {
          console.error('No JWT token available after refresh attempt');
          return;
        }
      } catch (error) {
        console.error('Token refresh failed:', error);
        return;
      }
    }

    const wsUrl = `ws://localhost:8000/ws/${endpoint}/?token=${authStore.token}`;
    if (this.sockets.has(endpoint)) {
      const socket = this.sockets.get(endpoint);
      if (socket.readyState === WebSocket.OPEN) {
        console.log(`WebSocket already connected to ${endpoint}`);
        return;
      }
      this.sockets.delete(endpoint);
    }

    const socket = new WebSocket(wsUrl);
    this.sockets.set(endpoint, socket);

    socket.onopen = () => {
      console.log(`WebSocket connected to ${endpoint}`);
      console.log(`WebSocket service: Active listeners for ${endpoint}:`, this.listeners.get(endpoint) || []);
      this.reconnectAttempts.delete(endpoint);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log(`WebSocket service: Received message on ${endpoint}:`, data);
        const listeners = this.listeners.get(endpoint) || [];
        console.log(`WebSocket service: Found ${listeners.length} listeners for ${endpoint}`);
        listeners.forEach((listener) => {
          console.log(`WebSocket service: Calling listener with data:`, data);
          listener(data);
        });
      } catch (error) {
        console.error(`Error parsing WebSocket message on ${endpoint}:`, error);
      }
    };

    socket.onclose = (event) => {
      console.log(`WebSocket disconnected from ${endpoint} (code: ${event.code}), attempting to reconnect...`);
      this.sockets.delete(endpoint);
      this.reconnect(endpoint);
    };

    socket.onerror = (error) => {
      console.error(`WebSocket error on ${endpoint}:`, error);
    };
  }

  async reconnect(endpoint, attempt = 0) {
    if (attempt >= this.maxReconnectAttempts) {
      console.error(`Max reconnect attempts reached for ${endpoint}`);
      return;
    }
    const delay = Math.min(1000 * Math.pow(2, attempt), 10000);
    console.log(`Reconnecting to ${endpoint} in ${delay}ms (attempt ${attempt + 1})`);
    setTimeout(async () => {
      await this.connect(endpoint);
      this.reconnectAttempts.set(endpoint, attempt + 1);
    }, delay);
  }

  addListener(endpoint, listener) {
    if (!this.listeners.has(endpoint)) {
      this.listeners.set(endpoint, []);
    }
    this.listeners.get(endpoint).push(listener);
  }

  removeListener(endpoint, listener) {
    if (this.listeners.has(endpoint)) {
      this.listeners.set(endpoint, this.listeners.get(endpoint).filter((l) => l !== listener));
    }
  }

  disconnect(endpoint) {
    const socket = this.sockets.get(endpoint);
    if (socket) {
      socket.close();
      this.sockets.delete(endpoint);
      this.listeners.delete(endpoint);
      this.reconnectAttempts.delete(endpoint);
    }
  }

  getSocket(endpoint) {
    return this.sockets.get(endpoint);
  }
}

export const websocketService = new WebSocketService();