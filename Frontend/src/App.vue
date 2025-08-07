<script setup>
import { RouterView } from 'vue-router';
import { onMounted, onUnmounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { websocketService } from '@/services/websocket';

const authStore = useAuthStore();

// Global status update handler
const handleGlobalStatusUpdate = (data) => {
  console.log('App.vue: Received global status update:', data);
  // Emit a global event that other components can listen to
  window.dispatchEvent(new CustomEvent('user-status-update', { detail: data }));
};

onMounted(() => {
  // Check authentication and connect to global notifications
  const connectIfAuthenticated = () => {
    try {
      if (authStore.token) {
        console.log('App.vue: Connecting to global notifications for status updates');
        websocketService.connect('notifications');
        websocketService.addListener('notifications', handleGlobalStatusUpdate);
      }
    } catch (error) {
      console.error('App.vue: Error accessing auth store:', error);
    }
  };
  
  // Initial connection with a small delay to ensure Pinia is ready
  setTimeout(connectIfAuthenticated, 100);
  
  // Watch for authentication changes
  const checkAuthInterval = setInterval(() => {
    try {
      const hasToken = !!authStore.token;
      const isConnected = websocketService.getSocket('notifications')?.readyState === WebSocket.OPEN;
      
      if (hasToken && !isConnected) {
        console.log('App.vue: User authenticated but not connected to notifications, connecting...');
        websocketService.connect('notifications');
        websocketService.addListener('notifications', handleGlobalStatusUpdate);
      } else if (!hasToken && isConnected) {
        console.log('App.vue: User not authenticated but connected to notifications, disconnecting...');
        websocketService.removeListener('notifications', handleGlobalStatusUpdate);
        websocketService.disconnect('notifications');
      }
    } catch (error) {
      console.error('App.vue: Error in auth check interval:', error);
    }
  }, 1000);
  
  // Store interval for cleanup
  window.authCheckInterval = checkAuthInterval;
});

onUnmounted(() => {
  // Clean up global WebSocket connection
  websocketService.removeListener('notifications', handleGlobalStatusUpdate);
  websocketService.disconnect('notifications');
  
  // Clean up auth check interval
  if (window.authCheckInterval) {
    clearInterval(window.authCheckInterval);
  }
});
</script>

<template>
  <RouterView />
</template>