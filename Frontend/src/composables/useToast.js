/**
 * Toast Composable - Simple toast notifications
 */
import { ref, reactive } from 'vue'

const toasts = ref([])
let toastIdCounter = 0

export function useToast() {
  /**
   * Show a toast notification
   * @param {string} message - Toast message
   * @param {string} type - Toast type (success, error, warning, info)
   * @param {number} duration - Auto-dismiss duration in ms (0 = no auto-dismiss)
   */
  const showToast = (message, type = 'info', duration = 5000) => {
    const id = ++toastIdCounter
    const toast = {
      id,
      message,
      type,
      timestamp: Date.now()
    }
    
    toasts.value.push(toast)
    
    // Auto-remove toast after duration
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }
    
    return id
  }

  /**
   * Remove a toast by ID
   */
  const removeToast = (id) => {
    const index = toasts.value.findIndex(toast => toast.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }

  /**
   * Clear all toasts
   */
  const clearToasts = () => {
    toasts.value = []
  }

  /**
   * Show success toast
   */
  const showSuccess = (message, duration = 3000) => {
    return showToast(message, 'success', duration)
  }

  /**
   * Show error toast
   */
  const showError = (message, duration = 8000) => {
    return showToast(message, 'error', duration)
  }

  /**
   * Show warning toast
   */
  const showWarning = (message, duration = 5000) => {
    return showToast(message, 'warning', duration)
  }

  /**
   * Show info toast
   */
  const showInfo = (message, duration = 4000) => {
    return showToast(message, 'info', duration)
  }

  return {
    toasts,
    showToast,
    removeToast,
    clearToasts,
    showSuccess,
    showError,
    showWarning,
    showInfo
  }
}