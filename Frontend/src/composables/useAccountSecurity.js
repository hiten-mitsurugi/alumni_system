import { ref, computed } from 'vue'
import { settingsService } from '@/services/settingsService'
import { useAuthStore } from '@/stores/auth'

/**
 * Account security composable
 * Handles password changes, 2FA, and security settings
 * Follows COPILOT_INSTRUCTIONS for modular security logic separation
 */
export function useAccountSecurity() {
  const authStore = useAuthStore()
  
  // Password form state
  const passwordForm = ref({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })

  // Security settings state
  const securitySettings = ref({
    twoFactorEnabled: false,
    loginNotifications: true,
    securityAlerts: true,
    sessionTimeout: 30, // minutes
    allowedDevices: []
  })

  // Visibility toggles for password fields
  const passwordVisibility = ref({
    current: false,
    new: false,
    confirm: false
  })

  // Loading states
  const isChangingPassword = ref(false)
  const isEnabling2FA = ref(false)
  const isUpdatingSecuritySettings = ref(false)

  // Validation state
  const passwordErrors = ref({})
  const securityErrors = ref({})

  // Password strength computation
  const passwordStrength = computed(() => {
    const password = passwordForm.value.newPassword
    if (!password) return { score: 0, label: '', color: 'gray' }

    let score = 0
    const checks = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      numbers: /\d/.test(password),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    }

    score = Object.values(checks).filter(Boolean).length

    const levels = [
      { score: 0, label: 'Very Weak', color: 'red' },
      { score: 1, label: 'Weak', color: 'orange' },
      { score: 2, label: 'Fair', color: 'yellow' },
      { score: 3, label: 'Good', color: 'blue' },
      { score: 4, label: 'Strong', color: 'green' },
      { score: 5, label: 'Very Strong', color: 'green' }
    ]

    return levels[score] || levels[0]
  })

  // Password validation rules
  const validatePassword = () => {
    const errors = {}
    const { currentPassword, newPassword, confirmPassword } = passwordForm.value

    // Current password validation
    if (!currentPassword) {
      errors.currentPassword = 'Current password is required'
    }

    // New password validation
    if (!newPassword) {
      errors.newPassword = 'New password is required'
    } else {
      if (newPassword.length < 8) {
        errors.newPassword = 'Password must be at least 8 characters long'
      } else if (newPassword === currentPassword) {
        errors.newPassword = 'New password must be different from current password'
      } else if (passwordStrength.value.score < 3) {
        errors.newPassword = 'Password is too weak. Please use a stronger password'
      }
    }

    // Confirm password validation
    if (!confirmPassword) {
      errors.confirmPassword = 'Please confirm your password'
    } else if (newPassword !== confirmPassword) {
      errors.confirmPassword = 'Passwords do not match'
    }

    passwordErrors.value = errors
    return Object.keys(errors).length === 0
  }

  // Security settings validation
  const validateSecuritySettings = () => {
    const errors = {}
    const { sessionTimeout } = securitySettings.value

    if (sessionTimeout < 5) {
      errors.sessionTimeout = 'Session timeout must be at least 5 minutes'
    } else if (sessionTimeout > 480) {
      errors.sessionTimeout = 'Session timeout cannot exceed 8 hours'
    }

    securityErrors.value = errors
    return Object.keys(errors).length === 0
  }

  // Password management methods
  const changePassword = async () => {
    if (!validatePassword()) {
      throw new Error('Please fix the validation errors')
    }

    try {
      isChangingPassword.value = true

      const passwordData = {
        current_password: passwordForm.value.currentPassword,
        new_password: passwordForm.value.newPassword,
        confirm_password: passwordForm.value.confirmPassword
      }

      await settingsService.changePassword(passwordData)
      
      // Clear form after successful change
      resetPasswordForm()
      
      return { success: true }
    } catch (error) {
      throw error
    } finally {
      isChangingPassword.value = false
    }
  }

  const resetPasswordForm = () => {
    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
    passwordErrors.value = {}
    passwordVisibility.value = {
      current: false,
      new: false,
      confirm: false
    }
  }

  // Two-factor authentication methods
  const toggle2FA = async () => {
    try {
      isEnabling2FA.value = true

      if (securitySettings.value.twoFactorEnabled) {
        // Disable 2FA
        await settingsService.disable2FA()
        securitySettings.value.twoFactorEnabled = false
        return { success: true, message: 'Two-factor authentication disabled' }
      } else {
        // Enable 2FA - this would typically return setup instructions
        const result = await settingsService.enable2FA()
        securitySettings.value.twoFactorEnabled = true
        return { 
          success: true, 
          message: 'Two-factor authentication enabled',
          qrCode: result.qr_code,
          backupCodes: result.backup_codes
        }
      }
    } catch (error) {
      throw error
    } finally {
      isEnabling2FA.value = false
    }
  }

  const verify2FASetup = async (verificationCode) => {
    try {
      const result = await settingsService.verify2FASetup({ code: verificationCode })
      if (result.success) {
        securitySettings.value.twoFactorEnabled = true
      }
      return result
    } catch (error) {
      throw error
    }
  }

  // Security settings management
  const updateSecuritySettings = async () => {
    if (!validateSecuritySettings()) {
      throw new Error('Please fix the validation errors')
    }

    try {
      isUpdatingSecuritySettings.value = true

      await settingsService.updateSecuritySettings(securitySettings.value)
      return { success: true }
    } catch (error) {
      throw error
    } finally {
      isUpdatingSecuritySettings.value = false
    }
  }

  const loadSecuritySettings = async () => {
    try {
      const settings = await settingsService.getSecuritySettings()
      securitySettings.value = {
        ...securitySettings.value,
        ...settings
      }
      return settings
    } catch (error) {
      console.error('Failed to load security settings:', error)
      throw error
    }
  }

  // Session management
  const getActiveSessions = async () => {
    try {
      const sessions = await settingsService.getActiveSessions()
      return sessions
    } catch (error) {
      console.error('Failed to load active sessions:', error)
      throw error
    }
  }

  const terminateSession = async (sessionId) => {
    try {
      await settingsService.terminateSession(sessionId)
      return { success: true }
    } catch (error) {
      throw error
    }
  }

  const terminateAllOtherSessions = async () => {
    try {
      await settingsService.terminateAllOtherSessions()
      return { success: true }
    } catch (error) {
      throw error
    }
  }

  // Password visibility toggles
  const togglePasswordVisibility = (field) => {
    passwordVisibility.value[field] = !passwordVisibility.value[field]
  }

  // Utility methods
  const generateStrongPassword = () => {
    const length = 12
    const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-='
    let password = ''
    
    // Ensure at least one character from each required set
    password += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[Math.floor(Math.random() * 26)]
    password += 'abcdefghijklmnopqrstuvwxyz'[Math.floor(Math.random() * 26)]
    password += '0123456789'[Math.floor(Math.random() * 10)]
    password += '!@#$%^&*()_+-='[Math.floor(Math.random() * 14)]
    
    // Fill the rest randomly
    for (let i = password.length; i < length; i++) {
      password += charset[Math.floor(Math.random() * charset.length)]
    }
    
    // Shuffle the password
    return password.split('').sort(() => Math.random() - 0.5).join('')
  }

  const checkPasswordCompromised = async (password) => {
    try {
      // This would check against a database of compromised passwords
      // For now, we'll just check against common passwords
      const commonPasswords = [
        'password', '123456', 'password123', 'admin', 'qwerty',
        'letmein', 'welcome', 'monkey', '1234567890', 'password1'
      ]
      
      return {
        isCompromised: commonPasswords.includes(password.toLowerCase()),
        message: commonPasswords.includes(password.toLowerCase()) 
          ? 'This password has been found in data breaches and should not be used'
          : 'Password appears to be secure'
      }
    } catch (error) {
      return { isCompromised: false, message: 'Unable to check password security' }
    }
  }

  return {
    // State
    passwordForm,
    securitySettings,
    passwordVisibility,
    isChangingPassword,
    isEnabling2FA,
    isUpdatingSecuritySettings,
    passwordErrors,
    securityErrors,
    
    // Computed
    passwordStrength,
    
    // Methods
    validatePassword,
    validateSecuritySettings,
    changePassword,
    resetPasswordForm,
    toggle2FA,
    verify2FASetup,
    updateSecuritySettings,
    loadSecuritySettings,
    getActiveSessions,
    terminateSession,
    terminateAllOtherSessions,
    togglePasswordVisibility,
    generateStrongPassword,
    checkPasswordCompromised
  }
}