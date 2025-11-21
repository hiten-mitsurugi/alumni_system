import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';

export const useNotificationsStore = defineStore('notifications', () => {
  // State
  const items = ref([]);
  const unreadCount = ref(0);
  const isLoading = ref(false);
  const wsConnected = ref(false);
  const ws = ref(null);

  // Computed
  const unreadNotifications = computed(() => 
    items.value.filter(n => !n.read_at)
  );

  // Actions
  async function fetchNotifications(filters = {}) {
    isLoading.value = true;
    try {
      const token = localStorage.getItem('access_token');
      const params = new URLSearchParams();
      
      if (filters.read !== undefined) params.append('read', filters.read);
      if (filters.type) params.append('type', filters.type);
      
      const response = await axios.get(
        `http://localhost:8000/api/notifications/?${params}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      items.value = response.data.results || response.data;
      await fetchUnreadCount();
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchUnreadCount() {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(
        'http://localhost:8000/api/notifications/unread_count/',
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      unreadCount.value = response.data.unread_count || 0;
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
    }
  }

  async function markAsRead(notificationId) {
    try {
      const token = localStorage.getItem('access_token');
      await axios.patch(
        `http://localhost:8000/api/notifications/${notificationId}/mark_as_read/`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      // Update local state
      const notification = items.value.find(n => n.id === notificationId);
      if (notification && !notification.read_at) {
        notification.read_at = new Date().toISOString();
        unreadCount.value = Math.max(0, unreadCount.value - 1);
      }
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  }

  async function markAllAsRead() {
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        'http://localhost:8000/api/notifications/mark_all_read/',
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
      unreadCount.value = 0;
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

    // Connect to WebSocket with auth token
    const wsUrl = `ws://localhost:8000/ws/notifications/?token=${token}`;
    ws.value = new WebSocket(wsUrl);

    ws.value.onopen = () => {
      console.log('✅ Notifications WebSocket connected');
      wsConnected.value = true;
    };

    ws.value.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      console.log('📨 WebSocket message received:', data.type);
      
      // Handle notification messages (both formats)
      if ((data.type === 'notification' || data.type === 'notification.message') && data.notification) {
        console.log('🔔 NEW NOTIFICATION:', data.notification.title);
        console.log('   Actor:', data.notification.actor_name);
        console.log('   Avatar:', data.notification.actor_avatar);
        
        // Prepend new notification to list IMMEDIATELY
        items.value.unshift(data.notification);
        
        // Increment unread count
        unreadCount.value++;
        
        console.log('✅ Notification added to store. Total:', items.value.length);
      } else if (data.type === 'connection_established') {
        console.log('✅ Connection established:', data.message);
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
    unreadCount.value = 0;
    isLoading.value = false;
    disconnectWebSocket();
  }

  return {
    // State
    items,
    unreadCount,
    isLoading,
    wsConnected,
    
    // Computed
    unreadNotifications,
    
    // Actions
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    connectWebSocket,
    disconnectWebSocket,
    reset
  };
});
