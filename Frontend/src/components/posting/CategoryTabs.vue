<template>
  <div class="flex flex-wrap gap-2 mt-4 justify-start">
    <button
      v-for="category in categories"
      :key="category.value"
      @click="$emit('category-change', category.value)"
      :class="[
        'px-4 py-2 rounded-full text-sm font-semibold transition-all duration-200 whitespace-nowrap border-none',
        activeTab === category.value
          ? (themeStore.isAdminDark() 
              ? 'bg-blue-500 text-white shadow-md' 
              : 'bg-blue-600 text-white shadow-md')
          : (themeStore.isAdminDark()
              ? 'bg-gray-800 text-gray-300 hover:bg-gray-700 hover:text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:text-blue-700')
      ]"
    >
      <span>{{ category.label }}</span>
    </button>
  </div>
</template>

<script setup>
import { useThemeStore } from '@/stores/theme'

// Theme store
const themeStore = useThemeStore()

// Props
const props = defineProps({
  categories: {
    type: Array,
    required: true
  },
  activeTab: {
    type: String,
    required: true
  }
})

// Emits
const emit = defineEmits(['category-change'])
</script>

<style scoped>
/* Custom scrollbar for category tabs */
.overflow-x-auto::-webkit-scrollbar {
  height: 6px;
}

.overflow-x-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Smooth transitions for all interactive elements */
.transition-all {
  transition: all 0.3s ease;
}

/* Enhanced hover effects */
button:hover:not(:disabled) {
  transform: translateY(-1px);
}

/* Focus states for accessibility */
button:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}
</style>
