import { ref, computed, watch } from 'vue'

/**
 * Main settings composable that manages overall settings state and navigation
 * Follows COPILOT_INSTRUCTIONS for modularization and separation of concerns
 */
export function useSettings() {
  // Active section state
  const activeSection = ref('profile')
  
  // Sidebar state
  const sidebarExpanded = ref(false)
  const hoverDisabled = ref(false)
  
  // Loading states
  const isLoading = ref(false)
  
  // Notification state
  const notification = ref({
    show: false,
    type: 'success', // 'success', 'error', 'warning', 'info'
    title: '',
    message: ''
  })

  // Settings sections configuration
  const sections = [
    { 
      id: 'profile', 
      label: 'Profile Settings', 
      icon: 'User',
      description: 'Manage your personal information and profile picture'
    },
    { 
      id: 'account', 
      label: 'Account & Security', 
      icon: 'Shield',
      description: 'Update password, enable 2FA, and manage security settings'
    },
    { 
      id: 'appearance', 
      label: 'Appearance', 
      icon: 'Palette',
      description: 'Customize theme and visual preferences'
    },
    { 
      id: 'privacy', 
      label: 'Privacy Settings', 
      icon: 'Lock',
      description: 'Control your privacy and visibility settings'
    },
    { 
      id: 'notifications', 
      label: 'Notifications', 
      icon: 'Bell',
      description: 'Manage notification preferences'
    }
  ]

  // Computed properties
  const currentSection = computed(() => 
    sections.find(section => section.id === activeSection.value)
  )

  // Methods
  const setActiveSection = (sectionId) => {
    if (sections.find(section => section.id === sectionId)) {
      activeSection.value = sectionId
    }
  }

  const toggleSidebar = () => {
    sidebarExpanded.value = false
    hoverDisabled.value = true
    // Re-enable hover after animation
    setTimeout(() => {
      hoverDisabled.value = false
    }, 500)
  }

  const expandSidebar = () => {
    if (!hoverDisabled.value) {
      sidebarExpanded.value = true
    }
  }

  // Notification management
  const showNotification = (type, title, message, autoHide = true) => {
    notification.value = {
      show: true,
      type,
      title,
      message
    }

    if (autoHide) {
      setTimeout(() => {
        hideNotification()
      }, 5000)
    }
  }

  const hideNotification = () => {
    notification.value.show = false
  }

  const showSuccess = (title, message) => {
    showNotification('success', title, message)
  }

  const showError = (title, message) => {
    showNotification('error', title, message)
  }

  const showWarning = (title, message) => {
    showNotification('warning', title, message)
  }

  const showInfo = (title, message) => {
    showNotification('info', title, message)
  }

  // Alias methods for compatibility
  const showSuccessMessage = showSuccess
  const showErrorMessage = showError

  // Loading state management
  const setLoading = (loading) => {
    isLoading.value = loading
  }

  // Settings validation
  const validateSettings = (settingsData, requiredFields = []) => {
    const errors = []
    
    for (const field of requiredFields) {
      if (!settingsData[field] || settingsData[field].toString().trim() === '') {
        errors.push(`${field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} is required`)
      }
    }
    
    return {
      isValid: errors.length === 0,
      errors
    }
  }

  // Export reactive state and methods
  return {
    // State
    activeSection,
    sidebarExpanded,
    hoverDisabled,
    isLoading,
    notification,
    sections,
    
    // Computed
    currentSection,
    
    // Methods
    setActiveSection,
    toggleSidebar,
    expandSidebar,
    showNotification,
    hideNotification,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showSuccessMessage,
    showErrorMessage,
    setLoading,
    validateSettings
  }
}