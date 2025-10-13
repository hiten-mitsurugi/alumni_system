<template>
  <div class="bg-white rounded-lg p-4 border border-gray-200 hover:shadow-md transition-shadow duration-200">
    <div class="flex items-start space-x-3">
      <div class="flex-shrink-0">
        <div class="bg-gray-50 p-2 rounded-lg">
          <svg class="w-5 h-5" :class="iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="icon"></path>
          </svg>
        </div>
      </div>
      <div class="flex-1 min-w-0">
        <div class="text-sm font-medium text-gray-500 mb-1">{{ label }}</div>
        <div class="text-base text-gray-900 font-medium break-words">{{ value }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  icon: {
    type: String,
    required: true
  },
  label: {
    type: String,
    required: true
  },
  value: {
    type: String,
    required: true
  },
  iconColor: {
    type: String,
    default: 'text-gray-600'
  }
})
</script>

<style scoped>
/* Additional styles if needed */
</style>