<template>
  <div 
    v-if="visible" 
    class="fixed bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50 min-w-48 context-menu"
    :style="{ top: position.y + 'px', left: position.x + 'px' }"
    @click.stop
  >
    <!-- Pin/Unpin -->
    <button 
      @click="handleAction('pin')"
      class="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-3 transition-colors"
      :class="message.is_pinned ? 'text-amber-700' : 'text-gray-700'"
    >
      <svg class="w-4 h-4" :class="message.is_pinned ? 'text-amber-600' : 'text-amber-500'" fill="currentColor" viewBox="0 0 24 24">
        <path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
      </svg>
      <span>{{ message.is_pinned ? 'Unpin Message' : 'Pin Message' }}</span>
    </button>

    <!-- Bump -->
    <button 
      @click="handleAction('bump')"
      class="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-3 text-gray-700 transition-colors"
    >
      <svg class="w-4 h-4 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M7 11l5-5m0 0l5 5m-5-5v12" />
      </svg>
      <span>Bump Message</span>
    </button>

    <!-- Forward -->
    <button 
      @click="handleAction('forward')"
      class="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-3 text-gray-700 transition-colors"
    >
      <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M13 5l7 7-7 7M5 5l7 7-7 7" />
      </svg>
      <span>Forward</span>
    </button>

    <!-- Copy -->
    <button 
      @click="handleAction('copy')"
      class="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-3 text-gray-700 transition-colors"
    >
      <svg class="w-4 h-4 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
      </svg>
      <span>Copy</span>
    </button>

    <!-- Edit (only for own messages) -->
    <button 
      v-if="canEdit"
      @click="handleAction('edit')"
      class="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-3 text-gray-700 transition-colors"
    >
      <svg class="w-4 h-4 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
      </svg>
      <span>Edit</span>
    </button>

    <!-- Divider -->
    <div v-if="canEdit || canDelete" class="border-t border-gray-200 my-1"></div>

    <!-- Delete (only for own messages) -->
    <button 
      v-if="canDelete"
      @click="handleAction('delete')"
      class="w-full px-4 py-2 text-left hover:bg-red-50 flex items-center gap-3 text-red-600 transition-colors"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
      </svg>
      <span>Delete</span>
    </button>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  position: {
    type: Object,
    default: () => ({ x: 0, y: 0 })
  },
  message: {
    type: Object,
    required: true
  },
  currentUser: {
    type: Object,
    default: () => ({ id: null })
  }
})

// Emits
const emit = defineEmits(['action', 'close'])

// Close menu when clicking outside
const handleClickOutside = (event) => {
  if (props.visible && !event.target.closest('.context-menu')) {
    emit('close')
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Computed
const canEdit = computed(() => {
  return props.message.sender?.id === props.currentUser?.id
})

const canDelete = computed(() => {
  return props.message.sender?.id === props.currentUser?.id
})

// Methods
const handleAction = (action) => {
  console.log('MessageContextMenu: Handling action:', action, 'for message:', props.message.id)
  
  // Emit the action with message data
  emit('action', {
    action,
    message: props.message
  })
  
  // Close the menu
  emit('close')
}
</script>

<style scoped>
/* Add smooth transitions for menu items */
button {
  transition: all 0.15s ease-in-out;
}

/* Ensure menu appears above other elements */
.z-50 {
  z-index: 50;
}

/* Subtle shadow for better visibility */
.shadow-lg {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}
</style>
