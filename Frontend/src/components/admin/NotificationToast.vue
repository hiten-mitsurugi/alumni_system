<template>
  <div v-if="notifications.length" class="fixed top-4 right-4 z-50 space-y-2">
    <div
      v-for="notification in notifications"
      :key="notification.id"
      class="bg-blue-600 text-white p-4 rounded-lg shadow-md flex items-center justify-between max-w-sm"
    >
      <span>{{ notification.message }}</span>
      <button @click="removeNotificationById(notification.id)" class="text-white hover:text-gray-200">
        &times;
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { websocketService } from '@/services/websocket';

const notifications = ref([]);
let idCounter = 0;

// Add notification with deduplication: ignore identical messages received within the last 5 seconds
const addNotification = (data) => {
  const message = data?.message || String(data || '');

  // Deduplicate recent identical messages
  const now = Date.now();
  const recentDuplicate = notifications.value.find(n => n.message === message && (now - n.timestamp) < 5000);
  if (recentDuplicate) return;

  const id = `${Date.now()}_${idCounter++}`;
  notifications.value.push({ id, message, timestamp: now });

  // Keep at most 5 toasts
  if (notifications.value.length > 5) {
    notifications.value.shift();
  }

  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    const idx = notifications.value.findIndex(n => n.id === id);
    if (idx !== -1) notifications.value.splice(idx, 1);
  }, 5000);
};

const removeNotificationById = (id) => {
  const idx = notifications.value.findIndex(n => n.id === id);
  if (idx !== -1) notifications.value.splice(idx, 1);
};

onMounted(() => {
  // Avoid registering duplicate listeners or reconnecting multiple times.
  const endpoint = 'notifications';
  const existingListeners = websocketService.listeners.get(endpoint) || [];
  const alreadyRegistered = existingListeners.includes(addNotification);
  if (!alreadyRegistered) {
    websocketService.addListener(addNotification);
  }

  // Only connect if not already connected
  const socket = websocketService.getSocket(endpoint);
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    websocketService.connect(endpoint);
  }
});

onUnmounted(() => {
  websocketService.removeListener(addNotification);
});
</script>