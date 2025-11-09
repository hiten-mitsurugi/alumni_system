<template>
  <div class="p-4 space-y-4">
    <h2 class="text-2xl font-bold">Theme Debug Panel</h2>
    
    <!-- Theme Status -->
    <div class="p-4 border rounded-lg">
      <h3 class="font-semibold mb-2">Theme Status</h3>
      <p>isDarkMode: {{ themeStore.isDarkMode }}</p>
      <p>Document has 'dark' class: {{ documentHasDarkClass }}</p>
      <p>Body has 'dark' class: {{ bodyHasDarkClass }}</p>
      <p>localStorage theme: {{ localStorageTheme }}</p>
    </div>

    <!-- Color Test -->
    <div class="space-y-2">
      <h3 class="font-semibold">Color Tests</h3>
      <div class="p-4 bg-white dark:bg-slate-900 border dark:border-slate-700 rounded">
        <p class="text-gray-900 dark:text-slate-100">Primary background (white/slate-900)</p>
      </div>
      <div class="p-4 bg-gray-100 dark:bg-slate-800 border dark:border-slate-700 rounded">
        <p class="text-gray-800 dark:text-slate-200">Secondary background (gray-100/slate-800)</p>
      </div>
      <div class="p-4 bg-gray-200 dark:bg-slate-700 border dark:border-slate-600 rounded">
        <p class="text-gray-700 dark:text-slate-300">Tertiary background (gray-200/slate-700)</p>
      </div>
    </div>

    <!-- Controls -->
    <div class="space-x-2">
      <button 
        @click="themeStore.toggleTheme()"
        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Toggle Theme
      </button>
      <button 
        @click="forceApplyTheme"
        class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
      >
        Force Apply Theme
      </button>
      <button 
        @click="refreshStatus"
        class="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
      >
        Refresh Status
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

const documentHasDarkClass = ref(false)
const bodyHasDarkClass = ref(false)
const localStorageTheme = ref('')

const refreshStatus = () => {
  documentHasDarkClass.value = document.documentElement.classList.contains('dark')
  bodyHasDarkClass.value = document.body.classList.contains('dark')
  localStorageTheme.value = localStorage.getItem('theme') || 'none'
  
  console.log('Theme Debug Status:', {
    isDarkMode: themeStore.isDarkMode,
    documentHasDarkClass: documentHasDarkClass.value,
    bodyHasDarkClass: bodyHasDarkClass.value,
    localStorageTheme: localStorageTheme.value
  })
}

const forceApplyTheme = () => {
  console.log('Force applying theme...')
  themeStore.applyTheme()
  setTimeout(refreshStatus, 100)
}

onMounted(() => {
  refreshStatus()
  
  // Watch for changes
  setInterval(refreshStatus, 1000)
})
</script>