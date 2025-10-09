import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { settingsService } from '@/services/settingsService'


export function useProfile() {
  const authStore = useAuthStore()
  
  // Profile form state
  const profileForm = ref({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    bio: '',
    location: '',
    website: '',
    birthDate: null,
    profilePicture: null,
    coverPhoto: null,
    // Social links
    linkedinUrl: '',
    twitterUrl: '',
    facebookUrl: '',
    instagramUrl: '',
    // Employment info
    presentOccupation: '',
    employingAgency: '',
    // Privacy settings
    isPublic: true,
    showEmail: false,
    showPhone: false,
    allowContact: true,
    allowMessaging: true
  })

  // Loading and validation states
  const isUpdatingProfile = ref(false)
  const isUploadingPicture = ref(false)
  const profileErrors = ref({})
  const profilePicturePreview = ref(null)

  // Computed properties
  const user = computed(() => authStore.user || {})
  const hasProfileChanges = ref(false)

  // Validation rules
  const validationRules = {
    firstName: {
      required: true,
      minLength: 2,
      maxLength: 50
    },
    lastName: {
      required: true,
      minLength: 2,
      maxLength: 50
    },
    email: {
      required: true,
      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    },
    phone: {
      pattern: /^[\+]?[0-9][0-9\-\s]{8,20}$/
    },
    bio: {
      maxLength: 500
    },
    website: {
      pattern: /^https?:\/\/.+/
    }
  }

  // Initialize form data from user
  const initializeProfile = () => {
    if (user.value && user.value.profile) {
      const userProfile = user.value.profile
      profileForm.value = {
        firstName: user.value.first_name || '',
        lastName: user.value.last_name || '',
        email: user.value.email || '',
        phone: user.value.contact_number || '',
        bio: userProfile.bio || '',
        location: userProfile.location || '',
        website: userProfile.website || '',
        birthDate: userProfile.birth_date || null,
        profilePicture: null,
        coverPhoto: null,
        // Social links
        linkedinUrl: userProfile.linkedin_url || '',
        twitterUrl: userProfile.twitter_url || '',
        facebookUrl: userProfile.facebook_url || '',
        instagramUrl: userProfile.instagram_url || '',
        // Employment info
        presentOccupation: userProfile.present_occupation || '',
        employingAgency: userProfile.employing_agency || '',
        // Privacy settings
        isPublic: userProfile.is_public !== undefined ? userProfile.is_public : true,
        showEmail: userProfile.show_email || false,
        showPhone: userProfile.show_phone || false,
        allowContact: userProfile.allow_contact !== undefined ? userProfile.allow_contact : true,
        allowMessaging: userProfile.allow_messaging !== undefined ? userProfile.allow_messaging : true
      }
      hasProfileChanges.value = false
    }
  }

  // Validation functions
  const validateField = (fieldName, value) => {
    const rule = validationRules[fieldName]
    if (!rule) return null

    if (rule.required && (!value || value.toString().trim() === '')) {
      return `${fieldName.replace(/([A-Z])/g, ' $1').toLowerCase()} is required`
    }

    if (rule.minLength && value && value.length < rule.minLength) {
      return `${fieldName.replace(/([A-Z])/g, ' $1').toLowerCase()} must be at least ${rule.minLength} characters`
    }

    if (rule.maxLength && value && value.length > rule.maxLength) {
      return `${fieldName.replace(/([A-Z])/g, ' $1').toLowerCase()} must not exceed ${rule.maxLength} characters`
    }

    if (rule.pattern && value && !rule.pattern.test(value)) {
      if (fieldName === 'email') {
        return 'Please enter a valid email address'
      }
      if (fieldName === 'phone') {
        return 'Please enter a valid phone number'
      }
      if (fieldName === 'website') {
        return 'Website must start with http:// or https://'
      }
      return `Invalid ${fieldName.replace(/([A-Z])/g, ' $1').toLowerCase()} format`
    }

    return null
  }

  const validateProfile = () => {
    const errors = {}
    
    Object.keys(validationRules).forEach(field => {
      const error = validateField(field, profileForm.value[field])
      if (error) {
        errors[field] = error
      }
    })

    profileErrors.value = errors
    return Object.keys(errors).length === 0
  }

  // Profile picture handling
  const handleProfilePictureChange = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    // Validate file
    const validation = validateProfilePicture(file)
    if (!validation.isValid) {
      throw new Error(validation.error)
    }

    try {
      isUploadingPicture.value = true
      
      // Create preview
      const reader = new FileReader()
      reader.onload = (e) => {
        profilePicturePreview.value = e.target.result
      }
      reader.readAsDataURL(file)

        // Upload profile picture
      const result = await settingsService.uploadProfilePicture(file)
      profileForm.value.profilePicture = file
      
      // Update the user's profile picture in auth store so UI updates immediately
      if (result.profile_picture && authStore.user) {
        authStore.user.profile_picture = result.profile_picture
        authStore.setUser(authStore.user)
      }
      
      return result
    } catch (error) {
      profilePicturePreview.value = null
      throw error
    } finally {
      isUploadingPicture.value = false
    }
  }

  const validateProfilePicture = (file) => {
    // Check file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      return {
        isValid: false,
        error: 'File size must be less than 5MB'
      }
    }

    // Check file type
    if (!file.type.startsWith('image/')) {
      return {
        isValid: false,
        error: 'Please select an image file'
      }
    }

    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      return {
        isValid: false,
        error: 'Please select a JPEG, PNG, GIF, or WebP image'
      }
    }

    return { isValid: true }
  }

  // Profile update functions
  const saveProfile = async () => {
    if (!validateProfile()) {
      throw new Error('Please fix the validation errors before saving')
    }

    try {
      isUpdatingProfile.value = true

      // Prepare profile data for API
      const profileData = {
        first_name: profileForm.value.firstName,
        last_name: profileForm.value.lastName,
        email: profileForm.value.email,
        contact_number: profileForm.value.phone,
        profile: {
          bio: profileForm.value.bio,
          location: profileForm.value.location,
          website: profileForm.value.website,
          birth_date: profileForm.value.birthDate,
          linkedin_url: profileForm.value.linkedinUrl,
          twitter_url: profileForm.value.twitterUrl,
          facebook_url: profileForm.value.facebookUrl,
          instagram_url: profileForm.value.instagramUrl,
          present_occupation: profileForm.value.presentOccupation,
          employing_agency: profileForm.value.employingAgency,
          is_public: profileForm.value.isPublic,
          show_email: profileForm.value.showEmail,
          show_phone: profileForm.value.showPhone,
          allow_contact: profileForm.value.allowContact,
          allow_messaging: profileForm.value.allowMessaging
        }
      }

      const result = await settingsService.updateProfile(profileData)
      
      // Update auth store with new data
      await authStore.fetchUser()
      // Re-initialize form with updated user data
      initializeProfile()
      hasProfileChanges.value = false
      
      return result
    } catch (error) {
      throw error
    } finally {
      isUpdatingProfile.value = false
    }
  }

  const resetProfileForm = () => {
    initializeProfile()
    profileErrors.value = {}
    profilePicturePreview.value = null
    hasProfileChanges.value = false
  }

  // Helper function to get profile picture URL
  const getProfilePictureUrl = (profilePicturePath) => {
    if (!profilePicturePath) {
      return '/default-avatar.png'
    }

    // If it's already a full URL, return as is
    if (profilePicturePath.startsWith('http')) {
      return profilePicturePath
    }

    // If it starts with /, it's a relative path from backend
    if (profilePicturePath.startsWith('/')) {
      return `${import.meta.env.VITE_API_BASE_URL}${profilePicturePath}`
    }

    // Otherwise, assume it's a media file
    return `${import.meta.env.VITE_API_BASE_URL}/media/${profilePicturePath}`
  }

  // Watch for form changes to track unsaved changes
  const watchFormChanges = () => {
    // This would be implemented with watchers on profileForm
    // For now, we'll set it manually when fields change
  }

  // Initialize on mount
  onMounted(() => {
    initializeProfile()
  })

  return {
    // State
    profileForm,
    isUpdatingProfile,
    isUploadingPicture,
    profileErrors,
    profilePicturePreview,
    hasProfileChanges,
    
    // Computed
    user,
    
    // Methods
    initializeProfile,
    validateField,
    validateProfile,
    handleProfilePictureChange,
    validateProfilePicture,
    saveProfile,
    resetProfileForm,
    getProfilePictureUrl,
    watchFormChanges
  }
}