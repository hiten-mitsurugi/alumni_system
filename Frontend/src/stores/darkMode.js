import { ref, watch } from 'vue'
import { defineStore } from 'pinia'

export const useDarkModeStore = defineStore('darkMode', () => {
  const isDarkMode = ref(false)

  // Initialize from localStorage
  const initializeDarkMode = () => {
    const saved = localStorage.getItem('darkMode')
    isDarkMode.value = saved === 'true'
    applyDarkMode()
  }

  // Apply dark mode to document
  const applyDarkMode = () => {
    console.log('🌙 STORE: Applying dark mode:', isDarkMode.value)
    if (isDarkMode.value) {
      document.documentElement.classList.add('dark')
      console.log('🌙 STORE: Added dark class to document')
    } else {
      document.documentElement.classList.remove('dark')
      console.log('🌙 STORE: Removed dark class from document')
    }
    console.log('🌙 STORE: Document classes:', document.documentElement.className)
  }

  // Toggle dark mode
  const toggleDarkMode = () => {
    console.log('🌙 STORE: Toggle clicked! Current isDarkMode:', isDarkMode.value)
    isDarkMode.value = !isDarkMode.value
    console.log('🌙 STORE: New isDarkMode value:', isDarkMode.value)
    localStorage.setItem('darkMode', isDarkMode.value.toString())
    console.log('🌙 STORE: Saved to localStorage:', localStorage.getItem('darkMode'))
    applyDarkMode()
  }

  // Watch for changes and apply them
  watch(isDarkMode, applyDarkMode)

  return {
    isDarkMode,
    toggleDarkMode,
    initializeDarkMode
  }
})
