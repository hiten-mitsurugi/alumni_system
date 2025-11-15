<template>
  <div class="flex justify-center py-16">
    <div class="flex flex-col items-center">
      <div class="animate-spin rounded-full h-16 w-16 border-4 border-orange-200 border-t-orange-600"></div>
      <p class="mt-4 text-slate-600 font-medium">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: 'Loading survey data...'
  }
})
</script>
