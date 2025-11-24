<script setup>
import { RouterView } from 'vue-router';
import { onMounted, onUnmounted, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useThemeStore } from '@/stores/theme';
import { useRoute } from 'vue-router';
import { websocketService } from '@/services/websocket';
import GlobalLoading from '@/components/common/GlobalLoading.vue';
import { useUiStore } from '@/stores/ui';
import AIChatbot from '@/components/AIChat/AIChatbot.vue';

const authStore = useAuthStore();
const themeStore = useThemeStore();
const ui = useUiStore();
const route = useRoute();

// Check if current route should be excluded from theme
const isPublicRoute = computed(() => {
  const publicRoutes = ['/login', '/register', '/forgot-password'];
  return publicRoutes.includes(route.path);
});

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
  <div :class="[
    'min-h-screen transition-colors duration-200',
    isPublicRoute 
      ? 'bg-gray-50' 
      : themeStore.isDarkMode 
        ? 'bg-gray-900' 
        : 'bg-gray-50'
  ]">
    <RouterView />
    <GlobalLoading v-if="ui.isLoading" :message="ui.message" />
    
    <!-- AI Chatbot - Show only when user is authenticated -->
    <AIChatbot v-if="authStore.token" />
  </div>
</template>