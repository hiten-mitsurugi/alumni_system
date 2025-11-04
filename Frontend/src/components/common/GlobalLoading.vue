<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-white/80 backdrop-blur-sm">
    <div class="flex flex-col items-center">
      <img v-if="showLogo" src="@/assets/logo3-removebg-preview.png" alt="Logo" class="h-20 w-auto mb-6 animate-bounce" />
      <div class="loader mb-4"></div>
      <span class="text-xl font-semibold text-gray-700">{{ message }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  message: { type: String, default: 'Loading...' },
  showLogo: { type: Boolean, default: true }
});
</script>

<style scoped>
.loader {
  border: 6px solid rgba(0,0,0,0.06);
  border-top: 6px solid #38bdf8;
  border-radius: 50%;
  width: 56px;
  height: 56px;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
