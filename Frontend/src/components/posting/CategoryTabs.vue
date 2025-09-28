<template>
  <div class="flex space-x-1 mt-6 overflow-x-auto pb-0">
    <button
      v-for="category in categories"
      :key="category.value"
      @click="$emit('category-change', category.value)"
      :class="[
        'relative px-4 py-2 text-sm font-medium transition-all duration-300 whitespace-nowrap rounded-full focus:outline-none',
        activeTab === category.value
          ? 'bg-blue-600 text-white shadow-md'
          : 'text-gray-500 hover:text-blue-600 hover:bg-blue-50'
      ]"
    >
      <span>{{ category.label }}</span>
    </button>
  </div>
</template>

<script setup>
// Props
defineProps({
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
defineEmits(['category-change'])
</script>

<style scoped>
/* Custom scrollbar for category tabs */
.overflow-x-auto::-webkit-scrollbar {
  height: 4px;
}

.overflow-x-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 2px;
}

.overflow-x-auto::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}

/* Focus states for accessibility */
button:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Smooth transitions */
.transition-all {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
