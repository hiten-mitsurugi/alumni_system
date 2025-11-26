import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';

export const useNotificationsStore = defineStore('notifications', () => {
  // State
  const items = ref([]);
  const isLoading = ref(false);
  const wsConnected = ref(false);
  const ws = ref(null);
  const isInitialized = ref(false);

  // Computed
  const unreadNotifications = computed(() => 
    items.value.filter(n => !n.read_at)
  );

  // Computed unread count (reactive based on items)
  const unreadCount = computed(() => {
    const count = items.value.filter(n => !n.read_at).length;
    console.log('🔢 Computing unreadCount:', count, 'from', items.value.length, 'total notifications');
    return count;
  });

  // Actions
  async function fetchNotifications(filters = {}) {
    isLoading.value = true;
    try {
      const token = localStorage.getItem('access_token');
      const params = new URLSearchParams();
      
      if (filters.read !== undefined) params.append('read', filters.read);
      if (filters.type) params.append('type', filters.type);
      
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
      const response = await axios.get(
        `${apiBaseUrl}/api/notifications/?${params}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      items.value = response.data.results || response.data;
      console.log('📥 Fetched notifications:', items.value.length, 'total, unread count will be computed automatically');
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    } finally {
      isLoading.value = false;
    }
  }

  async function markAsRead(notificationId) {
    try {
      const token = localStorage.getItem('access_token');
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
      await axios.patch(
        `${apiBaseUrl}/api/notifications/${notificationId}/mark_as_read/`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      // Update local state
      const notification = items.value.find(n => n.id === notificationId);
      if (notification && !notification.read_at) {
        notification.read_at = new Date().toISOString();
        console.log('✅ Marked notification as read, unread count will update automatically');
      }
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  }

  async function markAllAsRead() {
    try {
      const token = localStorage.getItem('access_token');
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
      await axios.post(
        `${apiBaseUrl}/api/notifications/mark_all_read/`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      // Update local state
      items.value.forEach(n => {
        if (!n.read_at) {
          n.read_at = new Date().toISOString();
        }
      });
      console.log('✅ Marked all notifications as read, unread count will update automatically');
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
    }
  }

  function connectWebSocket() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.warn('No auth token, cannot connect notifications WebSocket');
      return;
    }

    // Close existing connection if any
    if (ws.value) {
      ws.value.close();
    }

    // Connect to WebSocket with auth token using dynamic URL
    const wsBaseUrl = import.meta.env.VITE_API_BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://');
    const wsUrl = `${wsBaseUrl}/ws/notifications/?token=${token}`;
    console.log('🌐 Connecting to notifications WebSocket:', wsUrl);
    ws.value = new WebSocket(wsUrl);

    ws.value.onopen = () => {
      console.log('✅ Notifications WebSocket connected');
      wsConnected.value = true;
    };

    ws.value.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      console.log('📨 RAW WebSocket message received:', event.data);
      console.log('📨 Parsed data:', data);
      console.log('📨 Message type:', data.type);
      
      // Handle notification messages (both formats)
      if ((data.type === 'notification' || data.type === 'notification.message') && data.notification) {
        console.log('🔔 NEW NOTIFICATION RECEIVED!');
        console.log('   Title:', data.notification.title);
        console.log('   Message:', data.notification.message);
        console.log('   Actor:', data.notification.actor_name);
        console.log('   Avatar:', data.notification.actor_avatar);
        console.log('   Current unread count BEFORE:', unreadCount.value);
        
        // Prepend new notification to list IMMEDIATELY
        items.value.unshift(data.notification);
        
        console.log('   New unread count AFTER:', unreadCount.value);
        console.log('   Total notifications in store:', items.value.length);
        console.log('✅ Notification added to store successfully!');
      } else if (data.type === 'connection_established') {
        console.log('✅ Connection established:', data.message);
      } else {
        console.log('⚠️ Unknown message type or missing notification data:', data);
      }
    };

    ws.value.onerror = (error) => {
      console.error('❌ Notifications WebSocket error:', error);
      wsConnected.value = false;
    };

    ws.value.onclose = () => {
      console.log('🔌 Notifications WebSocket disconnected');
      wsConnected.value = false;
      
      // Auto-reconnect after 3 seconds
      setTimeout(() => {
        if (localStorage.getItem('access_token')) {
          console.log('🔄 Attempting to reconnect notifications WebSocket...');
          connectWebSocket();
        }
      }, 3000);
    };
  }

  function disconnectWebSocket() {
    if (ws.value) {
      ws.value.close();
      ws.value = null;
      wsConnected.value = false;
    }
  }

  function reset() {
    items.value = [];
    isLoading.value = false;
    isInitialized.value = false;
    disconnectWebSocket();
  }

  // Initialize store (fetch initial data and connect WebSocket)
  async function initialize() {
    if (isInitialized.value) {
      console.log('🔔 Notifications store already initialized');
      return;
    }

    console.log('🔔 Initializing notifications store...');
    try {
      await fetchNotifications();
      connectWebSocket();
      isInitialized.value = true;
      console.log('✅ Notifications store initialized');
    } catch (error) {
      console.error('❌ Failed to initialize notifications store:', error);
    }
  }

  return {
    // State
    items,
    unreadCount,
    isLoading,
    wsConnected,
    isInitialized,
    
    // Computed
    unreadNotifications,
    
    // Actions
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    connectWebSocket,
    disconnectWebSocket,
    initialize,
    reset
  };
});
