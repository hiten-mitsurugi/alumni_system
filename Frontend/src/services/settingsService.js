import apiClient from './api'

/**
 * Settings Service
 * Handles all settings-related API calls
 * Follows COPILOT_INSTRUCTIONS for modular service separation
 */
class SettingsService {
  constructor() {
    this.baseURL = '/auth'
  }

  // Profile management endpoints
  async getProfile() {
    try {
      const response = await apiClient.get(`${this.baseURL}/profile/`)
      return response.data
    } catch (error) {
      console.error('Failed to fetch profile:', error)
      throw this.handleError(error)
    }
  }

  async updateProfile(profileData) {
    try {
      console.log('Sending profile data to backend:', profileData)
      const response = await apiClient.put(`${this.baseURL}/profile/`, profileData)
      return response.data
    } catch (error) {
      console.error('Failed to update profile:', error)
      console.error('Backend error response:', error.response?.data)
      throw this.handleError(error)
    }
  }

  async updateProfilePartial(profileData) {
    try {
      const response = await apiClient.patch(`${this.baseURL}/profile/`, profileData)
      return response.data
    } catch (error) {
      console.error('Failed to update profile:', error)
      throw this.handleError(error)
    }
  }

  // Enhanced profile endpoints
  async getEnhancedProfile(userId = null, username = null) {
    try {
      let url = `${this.baseURL}/enhanced-profile/`
      
      if (username) {
        url = `${this.baseURL}/enhanced-profile/username/${username}/`
      } else if (userId) {
        url = `${this.baseURL}/enhanced-profile/${userId}/`
      }

      const response = await apiClient.get(url)
      return response.data
    } catch (error) {
      console.error('Failed to fetch enhanced profile:', error)
      throw this.handleError(error)
    }
  }

  async updateEnhancedProfile(profileData) {
    try {
      const response = await apiClient.patch(`${this.baseURL}/enhanced-profile/`, profileData)
      return response.data
    } catch (error) {
      console.error('Failed to update enhanced profile:', error)
      throw this.handleError(error)
    }
  }

  // Profile picture management
  async uploadProfilePicture(file) {
    try {
      const formData = new FormData()
      formData.append('profile_picture', file)

      const response = await apiClient.patch(`${this.baseURL}/enhanced-profile/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response.data
    } catch (error) {
      console.error('Failed to upload profile picture:', error)
      throw this.handleError(error)
    }
  }

  async uploadCoverPhoto(file) {
    try {
      const formData = new FormData()
      formData.append('cover_photo', file)

      const response = await apiClient.patch(`${this.baseURL}/enhanced-profile/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response.data
    } catch (error) {
      console.error('Failed to upload cover photo:', error)
      throw this.handleError(error)
    }
  }

  // Password management endpoints
  async changePassword(passwordData) {
    try {
      const response = await apiClient.post(`${this.baseURL}/settings/password-change/`, passwordData)
      return response.data
    } catch (error) {
      console.error('Failed to change password:', error)
      throw this.handleError(error)
    }
  }

  async validateCurrentPassword(password) {
    try {
      const response = await apiClient.post(`${this.baseURL}/validate-password/`, {
        password
      })
      return response.data
    } catch (error) {
      console.error('Failed to validate password:', error)
      throw this.handleError(error)
    }
  }

  // Two-factor authentication endpoints
  async enable2FA() {
    try {
      const response = await apiClient.post(`${this.baseURL}/2fa/enable/`)
      return response.data
    } catch (error) {
      console.error('Failed to enable 2FA:', error)
      throw this.handleError(error)
    }
  }

  async disable2FA() {
    try {
      const response = await apiClient.post(`${this.baseURL}/2fa/disable/`)
      return response.data
    } catch (error) {
      console.error('Failed to disable 2FA:', error)
      throw this.handleError(error)
    }
  }

  async verify2FASetup(verificationData) {
    try {
      const response = await apiClient.post(`${this.baseURL}/2fa/verify-setup/`, verificationData)
      return response.data
    } catch (error) {
      console.error('Failed to verify 2FA setup:', error)
      throw this.handleError(error)
    }
  }

  async get2FABackupCodes() {
    try {
      const response = await apiClient.get(`${this.baseURL}/2fa/backup-codes/`)
      return response.data
    } catch (error) {
      console.error('Failed to get backup codes:', error)
      throw this.handleError(error)
    }
  }

  async regenerate2FABackupCodes() {
    try {
      const response = await apiClient.post(`${this.baseURL}/2fa/regenerate-backup-codes/`)
      return response.data
    } catch (error) {
      console.error('Failed to regenerate backup codes:', error)
      throw this.handleError(error)
    }
  }

  // Security settings endpoints
  async getSecuritySettings() {
    try {
      const response = await apiClient.get(`${this.baseURL}/security-settings/`)
      return response.data
    } catch (error) {
      console.error('Failed to fetch security settings:', error)
      throw this.handleError(error)
    }
  }

  async updateSecuritySettings(settings) {
    try {
      const response = await apiClient.put(`${this.baseURL}/security-settings/`, settings)
      return response.data
    } catch (error) {
      console.error('Failed to update security settings:', error)
      throw this.handleError(error)
    }
  }

  // Session management endpoints
  async getActiveSessions() {
    try {
      const response = await apiClient.get(`${this.baseURL}/sessions/`)
      return response.data
    } catch (error) {
      console.error('Failed to fetch active sessions:', error)
      throw this.handleError(error)
    }
  }

  async terminateSession(sessionId) {
    try {
      const response = await apiClient.delete(`${this.baseURL}/sessions/${sessionId}/`)
      return response.data
    } catch (error) {
      console.error('Failed to terminate session:', error)
      throw this.handleError(error)
    }
  }

  async terminateAllOtherSessions() {
    try {
      const response = await apiClient.post(`${this.baseURL}/sessions/terminate-others/`)
      return response.data
    } catch (error) {
      console.error('Failed to terminate other sessions:', error)
      throw this.handleError(error)
    }
  }

  // Privacy settings endpoints
  async getPrivacySettings() {
    try {
      const response = await apiClient.get(`${this.baseURL}/privacy-settings/`)
      return response.data
    } catch (error) {
      console.error('Failed to fetch privacy settings:', error)
      throw this.handleError(error)
    }
  }

  async updatePrivacySettings(settings) {
    try {
      const response = await apiClient.put(`${this.baseURL}/privacy-settings/`, settings)
      return response.data
    } catch (error) {
      console.error('Failed to update privacy settings:', error)
      throw this.handleError(error)
    }
  }

  // Notification settings endpoints
  async getNotificationSettings() {
    try {
      const response = await apiClient.get(`${this.baseURL}/notification-settings/`)
      return response.data
    } catch (error) {
      console.error('Failed to fetch notification settings:', error)
      throw this.handleError(error)
    }
  }

  async updateNotificationSettings(settings) {
    try {
      const response = await apiClient.put(`${this.baseURL}/notification-settings/`, settings)
      return response.data
    } catch (error) {
      console.error('Failed to update notification settings:', error)
      throw this.handleError(error)
    }
  }

  // Account management endpoints
  async deactivateAccount(reason = '') {
    try {
      const response = await apiClient.post(`${this.baseURL}/deactivate-account/`, { reason })
      return response.data
    } catch (error) {
      console.error('Failed to deactivate account:', error)
      throw this.handleError(error)
    }
  }

  async deleteAccount(password, reason = '') {
    try {
      const response = await apiClient.post(`${this.baseURL}/delete-account/`, { 
        password, 
        reason 
      })
      return response.data
    } catch (error) {
      console.error('Failed to delete account:', error)
      throw this.handleError(error)
    }
  }

  async exportAccountData() {
    try {
      const response = await apiClient.get(`${this.baseURL}/export-data/`, {
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      console.error('Failed to export account data:', error)
      throw this.handleError(error)
    }
  }

  // Email management endpoints
  async changeEmail(newEmail, password) {
    try {
      const response = await apiClient.post(`${this.baseURL}/change-email/`, {
        email: newEmail,
        password
      })
      return response.data
    } catch (error) {
      console.error('Failed to change email:', error)
      throw this.handleError(error)
    }
  }

  async verifyEmailChange(token) {
    try {
      const response = await apiClient.post(`${this.baseURL}/verify-email-change/`, { token })
      return response.data
    } catch (error) {
      console.error('Failed to verify email change:', error)
      throw this.handleError(error)
    }
  }

  async resendEmailVerification() {
    try {
      const response = await apiClient.post(`${this.baseURL}/resend-verification/`)
      return response.data
    } catch (error) {
      console.error('Failed to resend email verification:', error)
      throw this.handleError(error)
    }
  }

  // Login history endpoints
  async getLoginHistory(page = 1, limit = 20) {
    try {
      const response = await apiClient.get(`${this.baseURL}/login-history/`, {
        params: { page, limit }
      })
      return response.data
    } catch (error) {
      console.error('Failed to fetch login history:', error)
      throw this.handleError(error)
    }
  }

  // Audit log endpoints
  async getAuditLog(page = 1, limit = 20, type = null) {
    try {
      const params = { page, limit }
      if (type) params.type = type

      const response = await apiClient.get(`${this.baseURL}/audit-log/`, { params })
      return response.data
    } catch (error) {
      console.error('Failed to fetch audit log:', error)
      throw this.handleError(error)
    }
  }

  // Connected apps endpoints
  async getConnectedApps() {
    try {
      const response = await apiClient.get(`${this.baseURL}/connected-apps/`)
      return response.data
    } catch (error) {
      console.error('Failed to fetch connected apps:', error)
      throw this.handleError(error)
    }
  }

  async revokeAppAccess(appId) {
    try {
      const response = await apiClient.delete(`${this.baseURL}/connected-apps/${appId}/`)
      return response.data
    } catch (error) {
      console.error('Failed to revoke app access:', error)
      throw this.handleError(error)
    }
  }

  // Error handling helper
  handleError(error) {
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.message || 
                        error.response?.data?.error ||
                        error.message || 
                        'An unexpected error occurred'

    const errorCode = error.response?.status || 'UNKNOWN'
    
    return {
      message: errorMessage,
      code: errorCode,
      details: error.response?.data || {},
      originalError: error
    }
  }

  // Utility methods
  async validateProfileData(profileData) {
    // Client-side validation before sending to API
    const errors = {}

    if (profileData.first_name && profileData.first_name.length < 2) {
      errors.first_name = 'First name must be at least 2 characters'
    }

    if (profileData.last_name && profileData.last_name.length < 2) {
      errors.last_name = 'Last name must be at least 2 characters'
    }

    if (profileData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(profileData.email)) {
      errors.email = 'Please enter a valid email address'
    }

    if (profileData.contact_number && !/^[\+]?[1-9][\d]{0,15}$/.test(profileData.contact_number)) {
      errors.contact_number = 'Please enter a valid phone number'
    }

    if (profileData.profile?.website && 
        profileData.profile.website && 
        !/^https?:\/\/.+/.test(profileData.profile.website)) {
      errors.website = 'Website must start with http:// or https://'
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    }
  }
}

// Create singleton instance
const settingsService = new SettingsService()
export { settingsService }