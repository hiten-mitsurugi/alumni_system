import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // State
  const isDarkMode = ref(false)

  // Initialize theme from localStorage (no system preference fallback)
  const initializeTheme = () => {
    const savedTheme = localStorage.getItem('theme')
    
    // Sync reactive state with localStorage
    isDarkMode.value = savedTheme === 'dark'
    
    console.log('🔄 Initializing theme store', {
      savedTheme,
      isDarkMode: isDarkMode.value
    })
    
    // Don't apply theme here - HTML script and interval already handle it
    // Just ensure reactive state is correct
  }

  // Apply theme to document
  const applyTheme = () => {
    console.log('⚡ Applying theme, isDarkMode:', isDarkMode.value)
    if (isDarkMode.value) {
      document.documentElement.classList.add('dark')
      document.body.classList.add('dark')
      console.log('✅ Added dark class')
    } else {
      document.documentElement.classList.remove('dark')
      document.body.classList.remove('dark')
      console.log('✅ Removed dark class')
    }
  }

  // Toggle theme
  const toggleTheme = () => {
    console.log('🔄 Toggle theme clicked, current state:', isDarkMode.value)
    
    // Toggle the reactive state
    isDarkMode.value = !isDarkMode.value
    
    // Persist to localStorage immediately
    localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
    
    console.log('✅ Theme toggled to:', isDarkMode.value ? 'dark' : 'light')
    
    // Apply theme immediately (watcher might not trigger in some cases)
    applyTheme()
  }

  // Set specific theme
  const setTheme = (theme) => {
    isDarkMode.value = theme === 'dark'
    localStorage.setItem('theme', theme)
    applyTheme()
  }

  // Admin-scoped theme (admin-only UI)
  // values: 'light' | 'dark' | 'auto' | 'system'
  const adminThemeMode = ref('auto')

  // Time-based switching for auto mode
  const isNightTime = () => {
    const now = new Date()
    const hour = now.getHours()
    // Night mode from 6 PM (18:00) to 6 AM (06:00)
    return hour >= 18 || hour < 6
  }

  const isAdminDark = () => {
    if (adminThemeMode.value === 'dark') return true
    if (adminThemeMode.value === 'light') return false
    // auto mode: time-based switching (6pm-6am = dark, 6am-6pm = light)
    return isNightTime()
  }

  const setAdminTheme = (mode) => {
    if (!mode) return
    if (['light', 'dark', 'auto'].indexOf(mode) === -1) return
    adminThemeMode.value = mode
    try { localStorage.setItem('adminTheme', mode) } catch (e) {}
  }

  const initializeAdminTheme = () => {
    try {
      const saved = localStorage.getItem('adminTheme')
      if (saved === 'light' || saved === 'dark' || saved === 'auto') {
        adminThemeMode.value = saved
      } else {
        // If saved was 'system' or any invalid value, default to 'auto'
        adminThemeMode.value = 'auto'
        localStorage.setItem('adminTheme', 'auto') // Update localStorage to remove old 'system' setting
      }
    } catch (e) {
      adminThemeMode.value = 'auto'
    }
    // ensure the admin class is applied immediately after initialization
    applyAdminClass()
  }

  // Auto-update timer for time-based switching
  let timeUpdateInterval = null

  const startTimeBasedUpdates = () => {
    // Only start if using auto mode
    if (adminThemeMode.value === 'auto') {
      // Check every minute for time changes
      timeUpdateInterval = setInterval(() => {
        if (adminThemeMode.value === 'auto') {
          applyAdminClass()
        }
      }, 60000) // 1 minute
    }
  }

  const stopTimeBasedUpdates = () => {
    if (timeUpdateInterval) {
      clearInterval(timeUpdateInterval)
      timeUpdateInterval = null
    }
  }

  // apply or remove the admin-dark class on the root element so Tailwind's dark variants scoped to .admin-dark work
  const applyAdminClass = () => {
    try {
      const root = document.documentElement
      if (isAdminDark()) {
        root.classList.add('admin-dark')
      } else {
        root.classList.remove('admin-dark')
      }
    } catch (e) {}
  }

  // watch for adminThemeMode changes and apply class automatically
  try {
    // lazy import: watch may be used safely
    const { watch: watchAdmin } = require('vue')
    watchAdmin && watchAdmin(adminThemeMode, (newMode) => {
      applyAdminClass()
      try { 
        localStorage.setItem('adminTheme', newMode) 
        
        // Start/stop time-based updates based on mode
        stopTimeBasedUpdates()
        if (newMode === 'auto') {
          startTimeBasedUpdates()
        }
      } catch (e) {}
    })
  } catch (e) {
    // fallback: do nothing
  }

    // Watch for changes to the isDarkMode state and apply theme
  watch(isDarkMode, (newValue) => {
    console.log('🔄 Theme changed via reactive state:', newValue)
    applyTheme()
  }, { immediate: false }) // Don't run on initial setup

  return {
    isDarkMode,
    initializeTheme,
    toggleTheme,
    setTheme,
    applyTheme,
    // admin-scoped theme API
    adminThemeMode,
    isAdminDark,
    setAdminTheme,
    initializeAdminTheme,
    startTimeBasedUpdates,
    stopTimeBasedUpdates,
    isNightTime
  }
})
