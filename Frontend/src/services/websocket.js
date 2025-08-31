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
      console.log(`WebSocket disconnected from ${endpoint} (code: ${event.code})`);
      this.sockets.delete(endpoint);
      
      // Handle authentication failures - stop reconnecting immediately
      if (event.code === 403 || event.code === 4001 || event.code === 1002) {
        console.warn(`WebSocket authentication failed on ${endpoint} (code: ${event.code})`);
        console.warn('Authentication error detected - stopping all reconnection attempts');
        
        // Clear all reconnection attempts for this endpoint
        this.reconnectAttempts.delete(endpoint);
        
        // Don't force logout immediately - just stop reconnecting
        console.log('Stopping WebSocket reconnection due to authentication failure');
        return;
      }
      
      // Only reconnect on unexpected disconnections (not authentication errors)
      if (event.code === 1006) { // Network disconnection
        console.log(`Network disconnection detected on ${endpoint}, attempting to reconnect...`);
        this.reconnect(endpoint);
      } else {
        console.log(`WebSocket closed with code ${event.code}, not reconnecting`);
        this.reconnectAttempts.delete(endpoint);
      }
    };

    socket.onerror = (error) => {
      console.error(`WebSocket error on ${endpoint}:`, error);
      
      // For authentication errors, stop reconnecting immediately
      console.log(`WebSocket error detected on ${endpoint}, will handle in onclose`);
    };
  }

  async reconnect(endpoint, attempt = 0) {
    // Don't reconnect if we're not authenticated
    const authStore = this.getAuthStore();
    if (!authStore.token) {
      console.log(`No auth token available, skipping reconnect for ${endpoint}`);
      return;
    }

    const currentAttempt = this.reconnectAttempts.get(endpoint) || 0;
    if (currentAttempt >= this.maxReconnectAttempts) {
      console.error(`Max reconnect attempts reached for ${endpoint}`);
      console.warn('Consider checking if the user exists in the database or if the JWT token is valid');
      this.reconnectAttempts.delete(endpoint);
      return;
    }
    
    const delay = Math.min(1000 * Math.pow(2, currentAttempt), 10000);
    console.log(`Reconnecting to ${endpoint} in ${delay}ms (attempt ${currentAttempt + 1})`);
    
    setTimeout(async () => {
      this.reconnectAttempts.set(endpoint, currentAttempt + 1);
      await this.connect(endpoint);
    }, delay);
  }

  addListener(endpointOrListener, listener = null) {
    // Backward compatibility: if only one argument, assume it's a listener for 'notifications'
    if (typeof endpointOrListener === 'function' && listener === null) {
      const endpoint = 'notifications';
      listener = endpointOrListener;
      if (!this.listeners.has(endpoint)) {
        this.listeners.set(endpoint, []);
      }
      this.listeners.get(endpoint).push(listener);
      console.log(`Added listener to ${endpoint} (backward compatibility mode)`);
    } else {
      // New format: addListener(endpoint, listener)
      const endpoint = endpointOrListener;
      if (!this.listeners.has(endpoint)) {
        this.listeners.set(endpoint, []);
      }
      this.listeners.get(endpoint).push(listener);
      console.log(`Added listener to ${endpoint}`);
    }
  }

  removeListener(endpointOrListener, listener = null) {
    // Backward compatibility: if only one argument, assume it's a listener for 'notifications'
    if (typeof endpointOrListener === 'function' && listener === null) {
      const endpoint = 'notifications';
      listener = endpointOrListener;
      if (this.listeners.has(endpoint)) {
        this.listeners.set(endpoint, this.listeners.get(endpoint).filter((l) => l !== listener));
        console.log(`Removed listener from ${endpoint} (backward compatibility mode)`);
      }
    } else {
      // New format: removeListener(endpoint, listener)
      const endpoint = endpointOrListener;
      if (this.listeners.has(endpoint)) {
        this.listeners.set(endpoint, this.listeners.get(endpoint).filter((l) => l !== listener));
        console.log(`Removed listener from ${endpoint}`);
      }
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

  disconnectAll() {
    console.log('Disconnecting all WebSocket connections');
    for (const [endpoint, socket] of this.sockets.entries()) {
      socket.close();
    }
    this.sockets.clear();
    this.listeners.clear();
    this.reconnectAttempts.clear();
  }

  getSocket(endpoint) {
    return this.sockets.get(endpoint);
  }
}

export const websocketService = new WebSocketService();