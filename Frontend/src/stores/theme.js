import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // State
  const isDarkMode = ref(false)

  // Initialize theme from localStorage or system preference
  const initializeTheme = () => {
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      isDarkMode.value = savedTheme === 'dark'
    } else {
      // Check system preference
      isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    applyTheme()
  }

  // Apply theme to document
  const applyTheme = () => {
    if (isDarkMode.value) {
      document.documentElement.classList.add('dark')
      document.body.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
      document.body.classList.remove('dark')
    }
  }

  // Toggle theme
  const toggleTheme = () => {
    isDarkMode.value = !isDarkMode.value
    localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
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
    if (adminThemeMode.value === 'system') {
      // System mode: follow OS preference
      try {
        return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      } catch (e) {
        return false
      }
    }
    // auto mode: time-based switching (6pm-6am = dark, 6am-6pm = light)
    return isNightTime()
  }

  const setAdminTheme = (mode) => {
    if (!mode) return
    if (['light', 'dark', 'auto', 'system'].indexOf(mode) === -1) return
    adminThemeMode.value = mode
    try { localStorage.setItem('adminTheme', mode) } catch (e) {}
  }

  const initializeAdminTheme = () => {
    try {
      const saved = localStorage.getItem('adminTheme')
      if (saved === 'light' || saved === 'dark' || saved === 'auto' || saved === 'system') {
        adminThemeMode.value = saved
      } else {
        adminThemeMode.value = 'auto'
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

  // Watch for changes and apply them
  watch(isDarkMode, () => {
    applyTheme()
  })

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
