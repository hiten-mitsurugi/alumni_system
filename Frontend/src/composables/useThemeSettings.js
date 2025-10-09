import { ref, computed, watch } from 'vue'
import { useThemeStore } from '@/stores/theme'

/**
 * Theme and appearance settings composable
 * Manages theme switching, appearance preferences, and UI customization
 * Follows COPILOT_INSTRUCTIONS for modular theme logic separation
 */
export function useThemeSettings() {
  const themeStore = useThemeStore()
  
  // Appearance settings state
  const appearanceSettings = ref({
    theme: 'light', // 'light', 'dark', 'auto'
    colorScheme: 'blue', // 'blue', 'green', 'purple', 'red'
    fontSize: 'medium', // 'small', 'medium', 'large'
    compactMode: false,
    highContrast: false,
    reducedMotion: false,
    sidebarPosition: 'left', // 'left', 'right'
    showAnimations: true,
    borderRadius: 'medium' // 'none', 'small', 'medium', 'large'
  })

  // System theme detection
  const systemTheme = ref('light')
  const prefersDarkMode = ref(false)

  // Theme options
  const themeOptions = [
    {
      id: 'light',
      name: 'Light Mode',
      description: 'Clean and bright interface',
      preview: {
        background: 'bg-white',
        surface: 'bg-gray-50',
        text: 'text-gray-900',
        accent: 'bg-blue-500'
      }
    },
    {
      id: 'dark',
      name: 'Dark Mode',
      description: 'Easy on the eyes in low light',
      preview: {
        background: 'bg-gray-900',
        surface: 'bg-gray-800',
        text: 'text-white',
        accent: 'bg-blue-400'
      }
    },
    {
      id: 'auto',
      name: 'System Default',
      description: 'Matches your device settings',
      preview: {
        background: 'bg-gradient-to-br from-gray-100 to-gray-900',
        surface: 'bg-gradient-to-br from-gray-50 to-gray-800',
        text: 'text-gray-700',
        accent: 'bg-blue-500'
      }
    }
  ]

  // Color scheme options
  const colorSchemeOptions = [
    { id: 'blue', name: 'Blue', color: 'bg-blue-500', description: 'Professional and trustworthy' },
    { id: 'green', name: 'Green', color: 'bg-green-500', description: 'Natural and calming' },
    { id: 'purple', name: 'Purple', color: 'bg-purple-500', description: 'Creative and modern' },
    { id: 'red', name: 'Red', color: 'bg-red-500', description: 'Bold and energetic' },
    { id: 'orange', name: 'Orange', color: 'bg-orange-500', description: 'Warm and friendly' },
    { id: 'teal', name: 'Teal', color: 'bg-teal-500', description: 'Fresh and balanced' }
  ]

  // Font size options
  const fontSizeOptions = [
    { id: 'small', name: 'Small', description: 'More content visible', class: 'text-sm' },
    { id: 'medium', name: 'Medium', description: 'Balanced readability', class: 'text-base' },
    { id: 'large', name: 'Large', description: 'Easier to read', class: 'text-lg' }
  ]

  // Border radius options
  const borderRadiusOptions = [
    { id: 'none', name: 'Sharp', description: 'No rounded corners', class: 'rounded-none' },
    { id: 'small', name: 'Subtle', description: 'Slightly rounded', class: 'rounded-sm' },
    { id: 'medium', name: 'Balanced', description: 'Moderately rounded', class: 'rounded-md' },
    { id: 'large', name: 'Soft', description: 'Highly rounded', class: 'rounded-lg' }
  ]

  // Computed properties
  const currentThemeOption = computed(() => 
    themeOptions.find(option => option.id === appearanceSettings.value.theme) || themeOptions[0]
  )

  const currentColorScheme = computed(() => 
    colorSchemeOptions.find(scheme => scheme.id === appearanceSettings.value.colorScheme) || colorSchemeOptions[0]
  )

  const currentFontSize = computed(() => 
    fontSizeOptions.find(size => size.id === appearanceSettings.value.fontSize) || fontSizeOptions[1]
  )

  const effectiveTheme = computed(() => {
    if (appearanceSettings.value.theme === 'auto') {
      return systemTheme.value
    }
    return appearanceSettings.value.theme
  })

  const isDarkMode = computed(() => effectiveTheme.value === 'dark')

  // System theme detection
  const detectSystemTheme = () => {
    if (typeof window !== 'undefined') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      prefersDarkMode.value = mediaQuery.matches
      systemTheme.value = mediaQuery.matches ? 'dark' : 'light'
      
      // Listen for system theme changes
      mediaQuery.addEventListener('change', (e) => {
        prefersDarkMode.value = e.matches
        systemTheme.value = e.matches ? 'dark' : 'light'
      })
    }
  }

  // Theme management methods
  const setTheme = (theme) => {
    if (themeOptions.find(option => option.id === theme)) {
      appearanceSettings.value.theme = theme
      applyTheme()
      saveToStorage()
    }
  }

  const setColorScheme = (scheme) => {
    if (colorSchemeOptions.find(option => option.id === scheme)) {
      appearanceSettings.value.colorScheme = scheme
      applyColorScheme()
      saveToStorage()
    }
  }

  const setFontSize = (size) => {
    if (fontSizeOptions.find(option => option.id === size)) {
      appearanceSettings.value.fontSize = size
      applyFontSize()
      saveToStorage()
    }
  }

  const setBorderRadius = (radius) => {
    if (borderRadiusOptions.find(option => option.id === radius)) {
      appearanceSettings.value.borderRadius = radius
      applyBorderRadius()
      saveToStorage()
    }
  }

  const toggleCompactMode = () => {
    appearanceSettings.value.compactMode = !appearanceSettings.value.compactMode
    applyCompactMode()
    saveToStorage()
  }

  const toggleHighContrast = () => {
    appearanceSettings.value.highContrast = !appearanceSettings.value.highContrast
    applyHighContrast()
    saveToStorage()
  }

  const toggleReducedMotion = () => {
    appearanceSettings.value.reducedMotion = !appearanceSettings.value.reducedMotion
    applyReducedMotion()
    saveToStorage()
  }

  const toggleAnimations = () => {
    appearanceSettings.value.showAnimations = !appearanceSettings.value.showAnimations
    applyAnimations()
    saveToStorage()
  }

  // Application methods
  const applyTheme = () => {
    const theme = effectiveTheme.value
    themeStore.setTheme(theme)
    
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('dark', theme === 'dark')
      document.documentElement.setAttribute('data-theme', theme)
    }
  }

  const applyColorScheme = () => {
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-color-scheme', appearanceSettings.value.colorScheme)
    }
  }

  const applyFontSize = () => {
    if (typeof document !== 'undefined') {
      const fontSizeMap = {
        small: '14px',
        medium: '16px',
        large: '18px'
      }
      document.documentElement.style.fontSize = fontSizeMap[appearanceSettings.value.fontSize]
      document.documentElement.setAttribute('data-font-size', appearanceSettings.value.fontSize)
    }
  }

  const applyBorderRadius = () => {
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-border-radius', appearanceSettings.value.borderRadius)
    }
  }

  const applyCompactMode = () => {
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('compact-mode', appearanceSettings.value.compactMode)
    }
  }

  const applyHighContrast = () => {
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('high-contrast', appearanceSettings.value.highContrast)
    }
  }

  const applyReducedMotion = () => {
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('reduced-motion', appearanceSettings.value.reducedMotion)
    }
  }

  const applyAnimations = () => {
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('no-animations', !appearanceSettings.value.showAnimations)
    }
  }

  const applyAllSettings = () => {
    applyTheme()
    applyColorScheme()
    applyFontSize()
    applyBorderRadius()
    applyCompactMode()
    applyHighContrast()
    applyReducedMotion()
    applyAnimations()
  }

  // Storage methods
  const saveToStorage = () => {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('appearanceSettings', JSON.stringify(appearanceSettings.value))
    }
  }

  const loadFromStorage = () => {
    if (typeof localStorage !== 'undefined') {
      const saved = localStorage.getItem('appearanceSettings')
      if (saved) {
        try {
          const parsed = JSON.parse(saved)
          appearanceSettings.value = { ...appearanceSettings.value, ...parsed }
        } catch (error) {
          console.warn('Failed to parse appearance settings from storage:', error)
        }
      }
    }
  }

  // Reset methods
  const resetToDefaults = () => {
    appearanceSettings.value = {
      theme: 'light',
      colorScheme: 'blue',
      fontSize: 'medium',
      compactMode: false,
      highContrast: false,
      reducedMotion: false,
      sidebarPosition: 'left',
      showAnimations: true,
      borderRadius: 'medium'
    }
    applyAllSettings()
    saveToStorage()
  }

  // Accessibility helpers
  const getAccessibilityRecommendations = () => {
    const recommendations = []
    
    if (!appearanceSettings.value.highContrast) {
      recommendations.push({
        type: 'contrast',
        message: 'Consider enabling high contrast mode for better readability',
        action: () => toggleHighContrast()
      })
    }
    
    if (appearanceSettings.value.fontSize === 'small') {
      recommendations.push({
        type: 'font-size',
        message: 'Larger font sizes can improve readability',
        action: () => setFontSize('medium')
      })
    }
    
    if (appearanceSettings.value.showAnimations && appearanceSettings.value.reducedMotion === false) {
      recommendations.push({
        type: 'motion',
        message: 'Disable animations if you experience motion sensitivity',
        action: () => toggleReducedMotion()
      })
    }
    
    return recommendations
  }

  // Initialize
  const initialize = () => {
    detectSystemTheme()
    loadFromStorage()
    applyAllSettings()
  }

  // Watch for system theme changes when auto theme is selected
  watch(
    () => [systemTheme.value, appearanceSettings.value.theme],
    () => {
      if (appearanceSettings.value.theme === 'auto') {
        applyTheme()
      }
    }
  )

  return {
    // State
    appearanceSettings,
    systemTheme,
    prefersDarkMode,
    themeOptions,
    colorSchemeOptions,
    fontSizeOptions,
    borderRadiusOptions,
    
    // Computed
    currentThemeOption,
    currentColorScheme,
    currentFontSize,
    effectiveTheme,
    isDarkMode,
    
    // Methods
    setTheme,
    setColorScheme,
    setFontSize,
    setBorderRadius,
    toggleCompactMode,
    toggleHighContrast,
    toggleReducedMotion,
    toggleAnimations,
    applyAllSettings,
    resetToDefaults,
    getAccessibilityRecommendations,
    initialize,
    
    // Storage
    saveToStorage,
    loadFromStorage
  }
}