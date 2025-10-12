<template>
  <!-- Subtle backdrop overlay -->
  <div class="fixed inset-0 z-50 bg-black/20 backdrop-blur-[1px]" @click="$emit('cancel')">
    <!-- Logout-style positioned modal -->
    <div class="fixed top-4 right-4 max-w-sm w-full p-4" @click.stop>
    <div :class="[
      'rounded-xl shadow-2xl p-6 border backdrop-blur-sm animate-fade-in',
      themeStore.isAdminDark() 
        ? 'bg-gray-800/98 text-white border-gray-600' 
        : 'bg-white/98 text-gray-900 border-gray-300'
    ]">
      <!-- Header with Icon -->
      <div class="flex items-center mb-4">
        <div :class="[
          'flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center mr-3',
          themeStore.isAdminDark() ? 'bg-red-900/40' : 'bg-red-100'
        ]">
          <svg :class="[
            'w-5 h-5',
            themeStore.isAdminDark() ? 'text-red-400' : 'text-red-600'
          ]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </div>
        <h3 :class="[
          'text-lg font-semibold',
          themeStore.isAdminDark() ? 'text-white' : 'text-gray-900'
        ]">
          {{ title }}
        </h3>
      </div>
      
      <!-- Message -->
      <p :class="[
        'text-sm mb-6',
        themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-600'
      ]">
        {{ message }}
      </p>
      
      <!-- Actions -->
      <div class="flex space-x-3">
        <button
          @click="$emit('cancel')"
          :class="[
            'flex-1 px-4 py-2 text-sm font-medium rounded-lg transition-colors border',
            themeStore.isAdminDark() 
              ? 'bg-gray-700/80 text-gray-300 hover:bg-gray-600 border-gray-600'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border-gray-300'
          ]"
        >
          {{ cancelText || 'Cancel' }}
        </button>
        <button
          @click="$emit('confirm')"
          :class="[
            'flex-1 px-4 py-2 text-sm font-medium rounded-lg transition-colors border',
            confirmClass || 'bg-red-600 text-white hover:bg-red-700 border-red-600'
          ]"
        >
          {{ confirmText || 'Confirm' }}
        </button>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { useThemeStore } from '@/stores/theme'
import { onMounted, onUnmounted } from 'vue'

// Stores
const themeStore = useThemeStore()

// Props & Emits
defineProps({
  title: {
    type: String,
    required: true
  },
  message: {
    type: String,
    required: true
  },
  confirmText: {
    type: String,
    default: 'Confirm'
  },
  cancelText: {
    type: String,
    default: 'Cancel'
  },
  confirmClass: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['confirm', 'cancel'])

// Add escape key handler
const handleEscapeKey = (event) => {
  if (event.key === 'Escape') {
    emit('cancel')
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleEscapeKey)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscapeKey)
})
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.animate-fade-in {
  animation: fade-in 0.2s ease-out;
}
</style>