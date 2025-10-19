import { useAuthStore } from '@/stores/auth';

// Dynamic WebSocket URL that adapts to any environment and IP changes
const getWebSocketBaseURL = () => {
  // Allow override via environment variable for production
  if (import.meta.env.VITE_WS_BASE_URL) {
    return import.meta.env.VITE_WS_BASE_URL;
  }
  
  // Auto-detect based on current location (works with any IP)
  const { protocol, hostname } = window.location;
  const wsProtocol = protocol === 'https:' ? 'wss:' : 'ws:';
  return `${wsProtocol}//${hostname}:8000/ws`;
};

export class WebSocketService {
  constructor() {
    this.sockets = new Map();
    this.listeners = new Map();
    this.reconnectAttempts = new Map();
    this.maxReconnectAttempts = 3;
    this.heartbeatIntervals = new Map(); // Store heartbeat intervals
    this.heartbeatInterval = 30000; // Send heartbeat every 30 seconds
  }

  getAuthStore() {
    // Lazy initialization of auth store to avoid Pinia timing issues
    return useAuthStore();
  }

  sendHeartbeat(endpoint) {
    const socket = this.sockets.get(endpoint);
    if (socket && socket.readyState === WebSocket.OPEN) {
      const heartbeat = {
        type: 'heartbeat',
        timestamp: new Date().toISOString()
      };
      socket.send(JSON.stringify(heartbeat));
      console.log(`Sent heartbeat to ${endpoint}`);
    }
  }

  startHeartbeat(endpoint) {
    // Clear any existing heartbeat for this endpoint
    this.stopHeartbeat(endpoint);
    
    // Start new heartbeat
    const intervalId = setInterval(() => {
      this.sendHeartbeat(endpoint);
    }, this.heartbeatInterval);
    
    this.heartbeatIntervals.set(endpoint, intervalId);
    console.log(`Started heartbeat for ${endpoint}`);
  }

  stopHeartbeat(endpoint) {
    const intervalId = this.heartbeatIntervals.get(endpoint);
    if (intervalId) {
      clearInterval(intervalId);
      this.heartbeatIntervals.delete(endpoint);
      console.log(`Stopped heartbeat for ${endpoint}`);
    }
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

    const wsUrl = `${getWebSocketBaseURL()}/${endpoint}/?token=${authStore.token}`;
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
      
      // Start heartbeat to keep connection alive and status accurate
      // Temporarily disabled to test connection stability
      // this.startHeartbeat(endpoint);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log(`WebSocket service: Received message on ${endpoint}:`, data);
        
        // Handle heartbeat acknowledgments
        if (data.type === 'heartbeat_ack') {
          console.log(`Received heartbeat ack from ${endpoint}`);
          return;
        }
        
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
      
      // Stop heartbeat when connection closes
      this.stopHeartbeat(endpoint);
      
      
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
        // Add delay before reconnecting to prevent rapid reconnection loops
        setTimeout(() => {
          this.reconnect(endpoint);
        }, 2000);
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

  async reconnect(endpoint, _attempt = 0) {
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
      // Stop heartbeat before closing
      this.stopHeartbeat(endpoint);
      socket.close();
      this.sockets.delete(endpoint);
      this.listeners.delete(endpoint);
      this.reconnectAttempts.delete(endpoint);
    }
  }

  disconnectAll() {
    console.log('Disconnecting all WebSocket connections');
    for (const [endpoint, socket] of this.sockets.entries()) {
      // Stop all heartbeats
      this.stopHeartbeat(endpoint);
      socket.close();
    }
    this.sockets.clear();
    this.listeners.clear();
    this.reconnectAttempts.clear();
    this.heartbeatIntervals.clear();
  }

  getSocket(endpoint) {
    return this.sockets.get(endpoint);
  }
}

export const websocketService = new WebSocketService();