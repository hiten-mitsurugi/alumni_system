<template>
  <div v-if="isVisible" class="relative">
    <!-- Backdrop to close menu -->
    <div 
      class="fixed inset-0 z-40" 
      @click="$emit('close')"
    ></div>
    
    <!-- Context Menu -->
    <div 
      :style="menuStyle"
      class="fixed z-50 bg-white border border-gray-200 rounded-lg shadow-lg py-2 min-w-[180px]"
    >
      <!-- Forward -->
      <button
        @click="handleAction('forward')"
        class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-3"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 10h-10a8 8 0 00-8 8v2m18-10l-6-6m6 6l-6 6" />
        </svg>
        Forward
      </button>

      <!-- Pin/Unpin -->
      <button
        @click="handleAction(message.isPinned ? 'unpin' : 'pin')"
        class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-3"
      >
        <svg v-if="!message.isPinned" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
        </svg>
        <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
          <path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
        </svg>
        {{ message.isPinned ? 'Unpin' : 'Pin' }}
      </button>

      <!-- Bump (available for all messages) -->
      <button
        @click="handleAction('bump')"
        class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-3"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11l5-5m0 0l5 5m-5-5v12" />
        </svg>
        Bump
      </button>

      <!-- Edit (only for own messages) -->
      <button
        v-if="isOwnMessage"
        @click="handleAction('edit')"
        class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-3"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
        Edit
      </button>

      <div class="border-t border-gray-200 my-1"></div>

      <!-- Copy -->
      <button
        @click="handleAction('copy')"
        class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-3"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
        Copy
      </button>

      <!-- Select -->
      <button
        @click="handleAction('select')"
        class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-3"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Select
      </button>

      <!-- Delete (only for own messages) -->
      <button
        v-if="isOwnMessage"
        @click="handleAction('delete')"
        class="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center gap-3"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
        Delete
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  message: {
    type: Object,
    required: true
  },
  position: {
    type: Object,
    default: () => ({ x: 0, y: 0 })
  },
  isOwnMessage: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'action'])

// Smart positioning to keep menu in viewport
const menuStyle = computed(() => {
  const menuWidth = 180
  const menuHeight = 320 // Approximate height
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight
  
  let x = props.position.x
  let y = props.position.y
  
  // Adjust horizontal position if menu would go off screen
  if (x + menuWidth > viewportWidth) {
    x = viewportWidth - menuWidth - 10
  }
  if (x < 10) {
    x = 10
  }
  
  // Adjust vertical position if menu would go off screen
  if (y + menuHeight > viewportHeight) {
    y = props.position.y - menuHeight - 10
  }
  if (y < 10) {
    y = 10
  }
  
  return {
    top: y + 'px',
    left: x + 'px'
  }
})

function handleAction(action) {
  console.log(`MessageContextMenu: ${action} action triggered for message ${props.message.id}`)
  emit('action', {
    action,
    message: props.message
  })
  emit('close')
}
</script>

<style scoped>
/* Smooth entrance animation */
.fixed {
  animation: contextMenuSlide 0.15s ease-out;
}

@keyframes contextMenuSlide {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
</style>
