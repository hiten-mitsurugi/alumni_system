/**
 * Privacy Composable - Manage privacy state and operations
 */
import { ref, reactive, computed } from 'vue'
import privacyService from '@/services/privacyService'
import { useToast } from '@/composables/useToast'

export function usePrivacy() {
  const { showToast } = useToast()
  
  // Privacy state
  const privacySettings = reactive({
    about: {},
    contact: {},
    education: {},
    experience: {},
    skills: {},
    achievements: {}
  })
  
  const loading = ref(false)
  const error = ref(null)

  // Available privacy options
  const privacyOptions = privacyService.getPrivacyOptions()
  
  // Field mappings for sections
  const fieldMappings = privacyService.getFieldMappings()

  /**
   * Load privacy settings from the server
   */
  const loadPrivacySettings = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await privacyService.getPrivacySettings()
      
      // Update reactive privacy settings
      Object.keys(response.privacy_settings).forEach(section => {
        if (privacySettings[section]) {
          Object.assign(privacySettings[section], response.privacy_settings[section])
        }
      })
      
      console.log('🔐 Privacy settings loaded:', privacySettings)
      
    } catch (err) {
      error.value = err.message || 'Failed to load privacy settings'
      showToast('Failed to load privacy settings', 'error')
      console.error('Privacy settings load error:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * Update privacy setting for a specific field
   */
  const updateFieldPrivacy = async (fieldName, visibility, section = null) => {
    try {
      const response = await privacyService.updateFieldPrivacy(fieldName, visibility)
      
      // Update local state
      if (section && privacySettings[section]) {
        privacySettings[section][fieldName] = visibility
      } else {
        // Find which section this field belongs to
        for (const [sectionName, fields] of Object.entries(fieldMappings)) {
          if (fields.includes(fieldName) && privacySettings[sectionName]) {
            privacySettings[sectionName][fieldName] = visibility
            break
          }
        }
      }
      
      showToast(`Privacy updated for ${fieldName}`, 'success')
      return response
      
    } catch (err) {
      error.value = err.message || 'Failed to update privacy setting'
      showToast('Failed to update privacy setting', 'error')
      console.error('Privacy update error:', err)
      throw err
    }
  }

  /**
   * Update privacy settings for an entire section
   */
  const updateSectionPrivacy = async (section, visibility) => {
    try {
      const response = await privacyService.updateSectionPrivacy(section, visibility)
      
      // Update local state for all fields in the section
      if (privacySettings[section]) {
        const sectionFields = fieldMappings[section] || []
        sectionFields.forEach(field => {
          privacySettings[section][field] = visibility
        })
      }
      
      showToast(`Privacy updated for ${section} section`, 'success')
      return response
      
    } catch (err) {
      error.value = err.message || 'Failed to update section privacy'
      showToast('Failed to update section privacy', 'error')
      console.error('Section privacy update error:', err)
      throw err
    }
  }

  /**
   * Bulk update multiple privacy settings
   */
  const bulkUpdatePrivacy = async (updates) => {
    try {
      const response = await privacyService.bulkUpdatePrivacy(updates)
      
      // Update local state
      Object.entries(updates).forEach(([fieldName, visibility]) => {
        // Find which section this field belongs to
        for (const [sectionName, fields] of Object.entries(fieldMappings)) {
          if (fields.includes(fieldName) && privacySettings[sectionName]) {
            privacySettings[sectionName][fieldName] = visibility
            break
          }
        }
      })
      
      showToast(`Updated privacy for ${Object.keys(updates).length} fields`, 'success')
      return response
      
    } catch (err) {
      error.value = err.message || 'Failed to bulk update privacy'
      showToast('Failed to bulk update privacy settings', 'error')
      console.error('Bulk privacy update error:', err)
      throw err
    }
  }

  /**
   * Get privacy setting for a specific field
   */
  const getFieldPrivacy = (fieldName, section = null) => {
    if (section && privacySettings[section]) {
      return privacySettings[section][fieldName] || 'public'
    }
    
    // Search through all sections
    for (const [sectionName, fields] of Object.entries(fieldMappings)) {
      if (fields.includes(fieldName) && privacySettings[sectionName]) {
        return privacySettings[sectionName][fieldName] || 'public'
      }
    }
    
    return 'public' // Default
  }

  /**
   * Get all privacy settings for a section
   */
  const getSectionPrivacy = (section) => {
    return privacySettings[section] || {}
  }

  /**
   * Check if all fields in a section have the same privacy level
   */
  const getSectionUniformPrivacy = (section) => {
    const sectionSettings = privacySettings[section] || {}
    const sectionFields = fieldMappings[section] || []
    
    if (sectionFields.length === 0) return null
    
    const firstFieldPrivacy = sectionSettings[sectionFields[0]] || 'public'
    const isUniform = sectionFields.every(field => 
      (sectionSettings[field] || 'public') === firstFieldPrivacy
    )
    
    return isUniform ? firstFieldPrivacy : null
  }

  /**
   * Get privacy statistics
   */
  const privacyStats = computed(() => {
    const stats = {
      public: 0,
      alumni_only: 0,
      connections_only: 0,
      private: 0,
      total: 0
    }
    
    Object.values(privacySettings).forEach(sectionSettings => {
      Object.values(sectionSettings).forEach(visibility => {
        if (stats[visibility] !== undefined) {
          stats[visibility]++
        }
        stats.total++
      })
    })
    
    return stats
  })

  /**
   * Check if user can view a field based on privacy and relationship
   */
  const canViewField = (fieldName, isOwner = false, isConnection = false, isAlumni = false, section = null) => {
    const visibility = getFieldPrivacy(fieldName, section)
    return privacyService.canViewField(visibility, isOwner, isConnection, isAlumni)
  }

  /**
   * Get privacy color classes for UI
   */
  const getPrivacyColorClasses = (visibility) => {
    return privacyService.getPrivacyColorClasses(visibility)
  }

  /**
   * Get privacy icon name
   */
  const getPrivacyIcon = (visibility) => {
    return privacyService.getPrivacyIcon(visibility)
  }

  /**
   * Preview privacy changes
   */
  const previewPrivacy = async (tempSettings, viewerType = 'public') => {
    try {
      const response = await privacyService.previewPrivacy(tempSettings, viewerType)
      return response
    } catch (err) {
      error.value = err.message || 'Failed to preview privacy changes'
      console.error('Privacy preview error:', err)
      throw err
    }
  }

  /**
   * Reset privacy settings to defaults
   */
  const resetPrivacySettings = () => {
    Object.keys(privacySettings).forEach(section => {
      const sectionFields = fieldMappings[section] || []
      sectionFields.forEach(field => {
        privacySettings[section][field] = 'public'
      })
    })
  }

  /**
   * Export privacy settings for backup
   */
  const exportPrivacySettings = () => {
    return JSON.stringify(privacySettings, null, 2)
  }

  /**
   * Import privacy settings from backup
   */
  const importPrivacySettings = (settingsJson) => {
    try {
      const imported = JSON.parse(settingsJson)
      Object.keys(imported).forEach(section => {
        if (privacySettings[section]) {
          Object.assign(privacySettings[section], imported[section])
        }
      })
      return true
    } catch (err) {
      console.error('Failed to import privacy settings:', err)
      return false
    }
  }

  return {
    // State
    privacySettings,
    loading,
    error,
    privacyOptions,
    fieldMappings,
    privacyStats,
    
    // Methods
    loadPrivacySettings,
    updateFieldPrivacy,
    updateSectionPrivacy,
    bulkUpdatePrivacy,
    getFieldPrivacy,
    getSectionPrivacy,
    getSectionUniformPrivacy,
    canViewField,
    getPrivacyColorClasses,
    getPrivacyIcon,
    previewPrivacy,
    resetPrivacySettings,
    exportPrivacySettings,
    importPrivacySettings
  }
}