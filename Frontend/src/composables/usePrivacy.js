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

  // Section-Level Privacy State
  const sectionPrivacySettings = ref({})
  const privacyProfiles = ref([])
  const activePrivacyProfile = ref(null)

  /**
   * Load section-level privacy settings
   */
  const loadSectionPrivacySettings = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await privacyService.getSectionPrivacySettings()
      sectionPrivacySettings.value = response.section_settings || {}
      
      console.log('🔐 Section privacy settings loaded:', sectionPrivacySettings.value)
      
    } catch (err) {
      error.value = err.message || 'Failed to load section privacy settings'
      showToast('Failed to load section privacy settings', 'error')
      console.error('Section privacy settings load error:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * Update section-level privacy setting
   */
  const updateSectionPrivacySetting = async (section, visibility) => {
    try {
      const response = await privacyService.updateSectionPrivacySetting(section, visibility)
      
      // Update local state
      sectionPrivacySettings.value[section] = visibility
      
      showToast(`Section privacy updated for ${section}`, 'success')
      return response
      
    } catch (err) {
      error.value = err.message || 'Failed to update section privacy'
      showToast('Failed to update section privacy', 'error')
      console.error('Section privacy update error:', err)
      throw err
    }
  }

  /**
   * Bulk update section privacy settings
   */
  const bulkUpdateSectionPrivacy = async (sectionUpdates) => {
    try {
      const response = await privacyService.bulkUpdateSectionPrivacy(sectionUpdates)
      
      // Update local state
      Object.assign(sectionPrivacySettings.value, sectionUpdates)
      
      showToast(`Updated section privacy for ${Object.keys(sectionUpdates).length} sections`, 'success')
      return response
      
    } catch (err) {
      error.value = err.message || 'Failed to bulk update section privacy'
      showToast('Failed to bulk update section privacy', 'error')
      console.error('Bulk section privacy update error:', err)
      throw err
    }
  }

  /**
   * Load privacy profiles (templates)
   */
  const loadPrivacyProfiles = async () => {
    try {
      const response = await privacyService.getPrivacyProfiles()
      privacyProfiles.value = response.profiles || []
      activePrivacyProfile.value = response.active_profile || null
      
      console.log('🔐 Privacy profiles loaded:', privacyProfiles.value)
      
    } catch (err) {
      error.value = err.message || 'Failed to load privacy profiles'
      showToast('Failed to load privacy profiles', 'error')
      console.error('Privacy profiles load error:', err)
    }
  }

  /**
   * Create new privacy profile
   */
  const createPrivacyProfile = async (name, description, sectionSettings, isDefault = false) => {
    try {
      const response = await privacyService.createPrivacyProfile({
        name,
        description,
        section_settings: sectionSettings,
        is_default: isDefault
      })
      
      // Add to local state
      privacyProfiles.value.push(response.profile)
      
      showToast(`Privacy profile "${name}" created`, 'success')
      return response
      
    } catch (err) {
      error.value = err.message || 'Failed to create privacy profile'
      showToast('Failed to create privacy profile', 'error')
      console.error('Privacy profile creation error:', err)
      throw err
    }
  }

  /**
   * Apply privacy profile (template)
   */
  const applyPrivacyProfile = async (profileId) => {
    try {
      const response = await privacyService.applyPrivacyProfile(profileId)
      
      // Update local state
      sectionPrivacySettings.value = response.section_settings || {}
      activePrivacyProfile.value = profileId
      
      showToast('Privacy profile applied successfully', 'success')
      return response
      
    } catch (err) {
      error.value = err.message || 'Failed to apply privacy profile'
      showToast('Failed to apply privacy profile', 'error')
      console.error('Privacy profile application error:', err)
      throw err
    }
  }

  /**
   * Delete privacy profile
   */
  const deletePrivacyProfile = async (profileId) => {
    try {
      await privacyService.deletePrivacyProfile(profileId)
      
      // Remove from local state
      privacyProfiles.value = privacyProfiles.value.filter(p => p.id !== profileId)
      if (activePrivacyProfile.value === profileId) {
        activePrivacyProfile.value = null
      }
      
      showToast('Privacy profile deleted', 'success')
      
    } catch (err) {
      error.value = err.message || 'Failed to delete privacy profile'
      showToast('Failed to delete privacy profile', 'error')
      console.error('Privacy profile deletion error:', err)
      throw err
    }
  }

  /**
   * Get section privacy setting
   */
  const getSectionPrivacySetting = (section) => {
    return sectionPrivacySettings.value[section] || 'public'
  }

  /**
   * Check for privacy conflicts between field and section levels
   */
  const getPrivacyConflicts = () => {
    const conflicts = []
    
    Object.keys(privacySettings).forEach(section => {
      const sectionPrivacy = getSectionPrivacySetting(section)
      const sectionFields = fieldMappings[section] || []
      
      sectionFields.forEach(field => {
        const fieldPrivacy = getFieldPrivacy(field, section)
        
        if (fieldPrivacy !== sectionPrivacy) {
          conflicts.push({
            section,
            field,
            sectionPrivacy,
            fieldPrivacy,
            type: 'field_section_mismatch'
          })
        }
      })
    })
    
    return conflicts
  }

  /**
   * Resolve privacy conflicts by prioritizing section or field level
   */
  const resolvePrivacyConflicts = async (resolution = 'prioritize_section') => {
    const conflicts = getPrivacyConflicts()
    
    if (conflicts.length === 0) {
      showToast('No privacy conflicts to resolve', 'info')
      return
    }
    
    const updates = {}
    
    conflicts.forEach(conflict => {
      if (resolution === 'prioritize_section') {
        updates[conflict.field] = conflict.sectionPrivacy
      } else if (resolution === 'prioritize_field') {
        sectionPrivacySettings.value[conflict.section] = conflict.fieldPrivacy
      }
    })
    
    try {
      if (resolution === 'prioritize_section' && Object.keys(updates).length > 0) {
        await bulkUpdatePrivacy(updates)
      } else if (resolution === 'prioritize_field') {
        await bulkUpdateSectionPrivacy(sectionPrivacySettings.value)
      }
      
      showToast(`Resolved ${conflicts.length} privacy conflicts`, 'success')
      
    } catch (err) {
      error.value = err.message || 'Failed to resolve privacy conflicts'
      showToast('Failed to resolve privacy conflicts', 'error')
      console.error('Privacy conflict resolution error:', err)
      throw err
    }
  }

  /**
   * Get effective privacy level for a field (considering both field and section)
   */
  const getEffectivePrivacy = (fieldName, section = null) => {
    const fieldPrivacy = getFieldPrivacy(fieldName, section)
    const sectionPrivacy = getSectionPrivacySetting(section)
    
    // Return the more restrictive privacy level
    const privacyLevels = {
      'public': 0,
      'alumni_only': 1,
      'connections_only': 2,
      'private': 3
    }
    
    const fieldLevel = privacyLevels[fieldPrivacy] || 0
    const sectionLevel = privacyLevels[sectionPrivacy] || 0
    
    const effectiveLevel = Math.max(fieldLevel, sectionLevel)
    const effectivePrivacy = Object.keys(privacyLevels).find(key => privacyLevels[key] === effectiveLevel)
    
    return effectivePrivacy || 'public'
  }

  /**
   * Get section privacy statistics
   */
  const sectionPrivacyStats = computed(() => {
    const stats = {
      public: 0,
      alumni_only: 0,
      connections_only: 0,
      private: 0,
      total: Object.keys(sectionPrivacySettings.value).length
    }
    
    Object.values(sectionPrivacySettings.value).forEach(visibility => {
      if (stats[visibility] !== undefined) {
        stats[visibility]++
      }
    })
    
    return stats
  })

  return {
    // State
    privacySettings,
    loading,
    error,
    privacyOptions,
    fieldMappings,
    privacyStats,
    
    // Section-level state
    sectionPrivacySettings,
    privacyProfiles,
    activePrivacyProfile,
    sectionPrivacyStats,
    
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
    importPrivacySettings,
    
    // Section-level methods
    loadSectionPrivacySettings,
    updateSectionPrivacySetting,
    bulkUpdateSectionPrivacy,
    loadPrivacyProfiles,
    createPrivacyProfile,
    applyPrivacyProfile,
    deletePrivacyProfile,
    getSectionPrivacySetting,
    getPrivacyConflicts,
    resolvePrivacyConflicts,
    getEffectivePrivacy
  }
}