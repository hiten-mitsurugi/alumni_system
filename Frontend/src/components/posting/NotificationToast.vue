<template>
  <div class="fixed top-6 right-6 z-50 space-y-4">
    <div
      v-for="notification in notifications.slice(0, 3)"
      :key="notification.id"
      :class="[
        'max-w-sm bg-white border-2 rounded-2xl shadow-2xl p-6 transition-all duration-500 transform',
        notification.type === 'success' ? 'border-green-400 bg-green-50' : 
        notification.type === 'error' ? 'border-red-400 bg-red-50' : 'border-blue-400 bg-blue-50'
      ]"
    >
      <div class="flex justify-between items-start">
        <div class="flex-1">
          <div class="flex items-center mb-2">
            <span v-if="notification.type === 'success'" class="text-2xl mr-3">✅</span>
            <span v-else-if="notification.type === 'error'" class="text-2xl mr-3">❌</span>
            <span v-else class="text-2xl mr-3">📢</span>
            <span class="font-bold text-lg" :class="notification.type === 'success' ? 'text-green-800' : notification.type === 'error' ? 'text-red-800' : 'text-blue-800'">
              {{ notification.type === 'success' ? 'Success!' : notification.type === 'error' ? 'Error' : 'Notification' }}
            </span>
          </div>
          <p class="text-lg text-slate-800 font-medium mb-2">{{ notification.message }}</p>
          <p class="text-sm text-slate-500 font-medium">{{ formatTimeAgo(notification.timestamp) }}</p>
        </div>
        <button
          @click="$emit('dismiss', notification.id)"
          class="text-slate-400 hover:text-slate-600 ml-4 p-2 rounded-full hover:bg-slate-200 transition-colors text-xl font-bold"
        >
          ×
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
// Props
const props = defineProps({
  notifications: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['dismiss'])

// Methods
const formatTimeAgo = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInSeconds = Math.floor((now - date) / 1000)
  
  if (diffInSeconds < 60) return 'Just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`
  
  return date.toLocaleDateString()
}
</script>

<style scoped>
/* Enhanced card shadows */
.shadow-2xl {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

/* Smooth transitions for all interactive elements */
.transition-all {
  transition: all 0.3s ease;
}

.transition-colors {
  transition: all 0.3s ease;
}

/* Animation for notifications */
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.fixed.top-6.right-6 > div {
  animation: slideInRight 0.3s ease-out;
}
</style>
