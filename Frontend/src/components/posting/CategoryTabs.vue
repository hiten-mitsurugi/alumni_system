<template>
  <div class="flex flex-wrap gap-3 mt-6 justify-center">
    <button
      v-for="category in categories"
      :key="category.value"
      @click="$emit('category-change', category.value)"
      :class="[
        'flex items-center space-x-3 px-6 py-4 rounded-2xl text-lg font-semibold transition-all duration-300 whitespace-nowrap min-w-fit shadow-md',
        activeTab === category.value
          ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white transform scale-105 shadow-xl'
          : 'bg-white text-slate-700 hover:bg-blue-50 hover:text-blue-700 hover:shadow-lg'
      ]"
    >
      <span class="text-2xl">{{ category.icon }}</span>
      <span>{{ category.label }}</span>
    </button>
  </div>
</template>

<script setup>
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
