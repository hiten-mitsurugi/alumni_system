<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-amber-50">
    <div class="flex flex-col items-center">
      <img src="@/assets/CCIS.png" alt="CCIS Logo" class="h-20 w-auto mb-8 animate-bounce" />
      <div class="loader mb-4"></div>
      <span class="text-xl font-semibold text-gray-700">Logging in...</span>
    </div>
  </div>
</template>

<script setup>
// No script needed for static loading
</script>

<style scoped>
.loader {
  border: 6px solid #f3f3f3;
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
