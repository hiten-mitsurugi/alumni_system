import { useAuthStore } from '@/stores/auth';

export class WebSocketService {
  constructor() {
    this.socket = null;
    this.listeners = [];
    this.authStore = useAuthStore();
  }

  connect() {
    if (!this.authStore.token) {
      console.error('No JWT token available for WebSocket connection');
      return;
    }

    const wsUrl = `ws://localhost:8000/ws/notifications/?token=${this.authStore.token}`;
    this.socket = new WebSocket(wsUrl);

    this.socket.onopen = () => {
      console.log('WebSocket connected');
    };

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.listeners.forEach((listener) => listener(data));
    };

    this.socket.onclose = () => {
      console.log('WebSocket disconnected, attempting to reconnect...');
      setTimeout(() => this.connect(), 3000);
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  addListener(listener) {
    this.listeners.push(listener);
  }

  removeListener(listener) {
    this.listeners = this.listeners.filter((l) => l !== listener);
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

export const websocketService = new WebSocketService();