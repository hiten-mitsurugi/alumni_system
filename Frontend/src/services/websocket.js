import { useAuthStore } from '@/stores/auth';

export class WebSocketService {
  constructor() {
    this.sockets = new Map(); // Store multiple WebSocket connections
    this.listeners = new Map(); // Store listeners per connection
    this.authStore = useAuthStore();
    this.reconnectAttempts = new Map();
    this.maxReconnectAttempts = 5;
  }

  connect(endpoint = 'notifications') {
    if (!this.authStore.token) {
      console.error('No JWT token available for WebSocket connection');
      return;
    }

    const wsUrl = `ws://localhost:8000/ws/${endpoint}/?token=${this.authStore.token}`;
    if (this.sockets.has(endpoint)) {
      return; // Avoid duplicate connections
    }

    const socket = new WebSocket(wsUrl);
    this.sockets.set(endpoint, socket);

    socket.onopen = () => {
      console.log(`WebSocket connected to ${endpoint}`);
      this.reconnectAttempts.delete(endpoint);
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const listeners = this.listeners.get(endpoint) || [];
      listeners.forEach((listener) => listener(data));
    };

    socket.onclose = () => {
      console.log(`WebSocket disconnected from ${endpoint}, attempting to reconnect...`);
      this.sockets.delete(endpoint);
      this.reconnect(endpoint);
    };

    socket.onerror = (error) => {
      console.error(`WebSocket error on ${endpoint}:`, error);
    };
  }

  reconnect(endpoint, attempt = 0) {
    if (attempt >= this.maxReconnectAttempts) {
      console.error(`Max reconnect attempts reached for ${endpoint}`);
      return;
    }
    const delay = Math.min(1000 * Math.pow(2, attempt), 10000); // Exponential backoff up to 10s
    setTimeout(() => this.connect(endpoint), delay);
    this.reconnectAttempts.set(endpoint, attempt + 1);
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
    }
  }

  getSocket(endpoint) {
    return this.sockets.get(endpoint);
  }
}

export const websocketService = new WebSocketService();