/**
 * Privacy Service - Handle privacy-related API calls
 */
import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_BASE_URL = `${BASE_URL}/api/auth`

class PrivacyService {
  /**
   * Get all privacy settings for the current user
   */
  async getPrivacySettings() {
    try {
      const response = await axios.get(`${API_BASE_URL}/privacy/settings/`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })
      return response.data
    } catch (error) {
      console.error('Failed to fetch privacy settings:', error)
      throw error
    }
  }

  /**
   * Update privacy setting for a specific field
   * @param {string} fieldName - The field name to update
   * @param {string} visibility - The visibility level (public, alumni_only, connections_only, private)
   */
  async updateFieldPrivacy(fieldName, visibility) {
    try {
      const response = await axios.post(`${API_BASE_URL}/privacy/field-update/`, {
        field_name: fieldName,
        visibility: visibility
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      })
      return response.data
    } catch (error) {
      console.error('Failed to update field privacy:', error)
      throw error
    }
  }

  /**
   * Bulk update multiple privacy settings
   * @param {Object} settings - Object with field names as keys and visibility as values
   */
  async bulkUpdatePrivacy(settings) {
    try {
      const response = await axios.post(`${API_BASE_URL}/privacy/bulk-update/`, {
        settings: settings
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      })
      return response.data
    } catch (error) {
      console.error('Failed to bulk update privacy settings:', error)
      throw error
    }
  }

  /**
   * Update privacy settings for an entire section
   * @param {string} section - The section name (about, contact, education, etc.)
   * @param {string} visibility - The visibility level to apply to all fields in the section
   */
  async updateSectionPrivacy(section, visibility) {
    try {
      const response = await axios.post(`${API_BASE_URL}/privacy/section-update/`, {
        section: section,
        visibility: visibility
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      })
      return response.data
    } catch (error) {
      console.error('Failed to update section privacy:', error)
      throw error
    }
  }

  /**
   * Preview profile with different privacy settings
   * @param {Object} privacySettings - Temporary privacy settings to preview
   * @param {string} viewerType - Type of viewer (public, alumni_only, connections_only)
   */
  async previewPrivacy(privacySettings, viewerType = 'public') {
    try {
      const response = await axios.post(`${API_BASE_URL}/privacy/preview/`, {
        privacy_settings: privacySettings,
        viewer_type: viewerType
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      })
      return response.data
    } catch (error) {
      console.error('Failed to preview privacy settings:', error)
      throw error
    }
  }

  /**
   * Get privacy options with labels and descriptions
   */
  getPrivacyOptions() {
    return [
      {
        value: 'public',
        label: 'Everyone',
        description: 'Anyone can see this information',
        icon: 'globe'
      },
      {
        value: 'alumni_only',
        label: 'Alumni Only',
        description: 'Only verified alumni can see this',
        icon: 'users'
      },
      {
        value: 'connections_only',
        label: 'Connections Only',
        description: 'Only your connections can see this',
        icon: 'user-group'
      },
      {
        value: 'private',
        label: 'Only Me',
        description: 'Only you can see this information',
        icon: 'lock'
      }
    ]
  }

  /**
   * Get field mappings for different sections
   */
  getFieldMappings() {
    return {
      about: [
        'bio',
        'headline',
        'birth_date',
        'batch_year',
        'current_status'
      ],
      contact: [
        'email',
        'phone',
        'linkedin_profile',
        'github_profile',
        'website',
        'address_line_1',
        'address_line_2',
        'city',
        'state',
        'country',
        'postal_code'
      ],
      education: [
        'institution',
        'field_of_study',
        'degree_type',
        'start_date',
        'end_date',
        'grade',
        'activities',
        'description'
      ],
      experience: [
        'job_title',
        'company',
        'location',
        'start_date',
        'end_date',
        'description',
        'employment_type'
      ],
      skills: [
        'skill_name',
        'proficiency_level',
        'years_of_experience'
      ],
      achievements: [
        'title',
        'description',
        'date_achieved',
        'issuer',
        'credential_url'
      ]
    }
  }

  /**
   * Get privacy level color classes for UI
   */
  getPrivacyColorClasses(visibility) {
    const colorMap = {
      'public': 'text-green-600 bg-green-50 border-green-200',
      'alumni_only': 'text-blue-600 bg-blue-50 border-blue-200',
      'connections_only': 'text-purple-600 bg-purple-50 border-purple-200',
      'private': 'text-gray-600 bg-gray-50 border-gray-200'
    }
    return colorMap[visibility] || colorMap['public']
  }

  /**
   * Get privacy level icon name
   */
  getPrivacyIcon(visibility) {
    const iconMap = {
      'public': 'globe-alt',
      'alumni_only': 'user-group',
      'connections_only': 'users',
      'private': 'lock-closed'
    }
    return iconMap[visibility] || iconMap['public']
  }

  /**
   * Check if user can see field based on privacy setting and relationship
   * @param {string} visibility - Privacy setting of the field
   * @param {boolean} isOwner - Whether the viewer owns the profile
   * @param {boolean} isConnection - Whether the viewer is connected to the profile owner
   * @param {boolean} isAlumni - Whether the viewer is a verified alumni
   */
  canViewField(visibility, isOwner = false, isConnection = false, isAlumni = false) {
    // Owner can always see their own fields
    if (isOwner) return true

    switch (visibility) {
      case 'public':
        return true
      case 'alumni_only':
        return isAlumni
      case 'connections_only':
        return isConnection
      case 'private':
        return false
      default:
        return true // Default to public if unknown
    }
  }

}
