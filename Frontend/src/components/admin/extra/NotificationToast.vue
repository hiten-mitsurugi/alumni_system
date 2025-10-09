<template>
  <div v-if="notifications.length" class="fixed top-4 right-4 z-50 space-y-2">
    <div
      v-for="(notification, index) in notifications"
      :key="index"
      class="bg-blue-600 text-white p-4 rounded-lg shadow-md flex items-center justify-between max-w-sm"
    >
      <span>{{ notification.message }}</span>
      <button @click="removeNotification(index)" class="text-white hover:text-gray-200">
        &times;
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { websocketService } from '@/services/websocket';

const notifications = ref([]);

const addNotification = (data) => {
  notifications.value.push({ message: data.message });
  setTimeout(() => {
    notifications.value.shift();
  }, 5000); // Auto-dismiss after 5 seconds
};

const removeNotification = (index) => {
  notifications.value.splice(index, 1);
};

onMounted(() => {
  websocketService.addListener(addNotification);
  websocketService.connect();
});

onUnmounted(() => {
  websocketService.removeListener(addNotification);
});
</script>