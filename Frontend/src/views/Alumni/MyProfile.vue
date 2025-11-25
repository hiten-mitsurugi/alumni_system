<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import api from '@/services/api'

// Component imports
import ProfileAboutSection from '@/components/profile/ProfileAboutSection.vue'
import ProfileContactSection from '@/components/profile/ProfileContactSection.vue'
import ProfileEducationSection from '@/components/profile/ProfileEducationSection.vue'
import ProfileExperienceSection from '@/components/profile/ProfileExperienceSection.vue'
import ProfileSkillsSection from '@/components/profile/ProfileSkillsSection.vue'
import ProfileMembershipsSection from '@/components/profile/ProfileMembershipsSection.vue'
import ProfileRecognitionsSection from '@/components/profile/ProfileRecognitionsSection.vue'
import ProfileTrainingsSection from '@/components/profile/ProfileTrainingsSection.vue'
import ProfilePublicationsSection from '@/components/profile/ProfilePublicationsSection.vue'
import ProfileCareerEnhancementSection from '@/components/profile/ProfileCareerEnhancementSection.vue'

import ProfileAchievementsSection from '@/components/profile/ProfileAchievementsSection.vue'
import SuggestedConnectionsWidget from '@/components/profile/SuggestedConnectionsWidget.vue'
import EditProfileModal from '@/components/profile/EditProfileModal.vue'
import CoverPhotoModal from '@/components/profile/CoverPhotoModal.vue'
import ProfilePictureModal from '@/components/profile/ProfilePictureModal.vue'
import EducationModal from '@/components/profile/EducationModal.vue'
import ExperienceModal from '@/components/profile/ExperienceModal.vue'
import SkillModal from '@/components/profile/SkillModal.vue'
import AchievementModal from '@/components/profile/AchievementModal.vue'
import MembershipModal from '@/components/profile/MembershipModal.vue'
import RecognitionModal from '@/components/profile/RecognitionModal.vue'
import TrainingModal from '@/components/profile/TrainingModal.vue'
import PublicationModal from '@/components/profile/PublicationModal.vue'
import CareerEnhancementModal from '@/components/profile/CareerEnhancementModal.vue'

// Tab components
import PostsTab from '@/components/profile/tabs/PostsTab.vue'

// Reactive data
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const loading = ref(false)
const followLoading = ref(false)
const showEditModal = ref(false)
const showCoverModal = ref(false)
const showProfilePictureModal = ref(false)

// Modal states for CRUD operations
const showEducationModal = ref(false)
const showExperienceModal = ref(false)
const showSkillModal = ref(false)
const showAchievementModal = ref(false)
const showMembershipModal = ref(false)
const showRecognitionModal = ref(false)
const showTrainingModal = ref(false)
const showPublicationModal = ref(false)
const showCareerEnhancementModal = ref(false)

// Selected items for editing
const selectedEducation = ref(null)
const selectedExperience = ref(null)
const selectedSkill = ref(null)
const selectedAchievement = ref(null)
const selectedMembership = ref(null)
const selectedRecognition = ref(null)
const selectedTraining = ref(null)
const selectedPublication = ref(null)
const selectedCareerEnhancement = ref(null)

const user = ref(null)
const profile = ref(null)
const education = ref([])
const workHistories = ref([])
const skills = ref([])
const achievements = ref([])
const memberships = ref([])
const recognitions = ref([])
const trainings = ref([])
const publications = ref([])
const careerEnhancement = ref({})

const isFollowing = ref(false)
const connectionsCount = ref(0)
const resolvedUserId = ref(null) // Track the resolved user ID

// Tab state
const activeTab = ref('about') // Default to about tab

// Computed properties
const isOwnProfile = computed(() => {
  const userIdentifier = route.params.userIdentifier

  // If no userIdentifier in route, it's own profile
  if (!userIdentifier) {
    return true
  }

  // Check if userIdentifier matches current user's username
  if (authStore.user && userIdentifier === authStore.user.username) {
    return true
  }

  return false
})

const profileUserId = computed(() => {
  return route.params.userIdentifier || authStore.user?.id
})

// Computed properties to derive profile info from detailed sections
const currentEducation = computed(() => {
  if (!education.value || education.value.length === 0) return null

  // Find current education (is_current = true) or most recent one
  const current = education.value.find(edu => edu.is_current)
  if (current) return current

  // If no current, get the most recent one by end_date or start_date
  const sorted = [...education.value].sort((a, b) => {
    const dateA = new Date(a.end_date || a.start_date || '1900-01-01')
    const dateB = new Date(b.end_date || b.start_date || '1900-01-01')
    return dateB - dateA
  })

  return sorted[0]
})

const currentJob = computed(() => {
  if (!workHistories.value || workHistories.value.length === 0) return null

  // Find current job (job_type = 'current_job') or most recent one
  const current = workHistories.value.find(work => work.job_type === 'current_job')
  if (current) return current

  // If no current job, get the most recent one by end_date or start_date
  const sorted = [...workHistories.value].sort((a, b) => {
    const dateA = new Date(a.end_date || a.start_date || '1900-01-01')
    const dateB = new Date(b.end_date || b.start_date || '1900-01-01')
    return dateB - dateA
  })

  return sorted[0]
})

const displayHeadline = computed(() => {
  // Priority: Profile headline > Current job title > Current education > Default
  if (profile.value?.headline) {
    return profile.value.headline
  }

  if (currentJob.value) {
    return `${currentJob.value.occupation} at ${currentJob.value.employing_agency}`
  }

  if (currentEducation.value) {
    const degree = currentEducation.value.degree_type?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Student'
    const field = currentEducation.value.field_of_study ? ` in ${currentEducation.value.field_of_study}` : ''
    return `${degree}${field}`
  }

  return 'Alumni'
})

const displayEducationInfo = computed(() => {
  if (currentEducation.value) {
    const degree = currentEducation.value.degree_type?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || ''
    const field = currentEducation.value.field_of_study || ''
    const institution = currentEducation.value.institution || ''

    if (degree && field && institution) {
      return `${degree} in ${field} from ${institution}`
    } else if (degree && institution) {
      return `${degree} from ${institution}`
    } else if (institution) {
      return institution
    }
  }

  // Fallback to user basic info if available
  if (user.value?.program && user.value?.year_graduated) {
    return `${user.value.program} (Class of ${user.value.year_graduated})`
  }

  return null
})

// Profile picture URL with cache-busting (same logic as AlumniNavbar)
const BASE_URL = `${window.location.protocol}//${window.location.hostname}:8000`

const profilePictureUrl = computed(() => {
  const pic = user.value?.profile_picture
  console.log('🖼️ profilePictureUrl computed - user.value:', user.value)
  console.log('🖼️ profilePictureUrl computed - pic value:', pic)

  if (!pic) {
    console.log('🖼️ No profile_picture, returning default')
    return '/default-avatar.png'
  }

  const baseUrl = pic.startsWith('http') ? pic : `${BASE_URL}${pic}`
  const cacheBuster = `?t=${Date.now()}`
  const finalUrl = `${baseUrl}${cacheBuster}`

  console.log('🖼️ Profile picture URL:', {
    original: pic,
    baseUrl,
    finalUrl
  })

  return finalUrl
})

// Methods
const fetchProfile = async () => {
  try {
    loading.value = true

    let userIdentifier = route.params.userIdentifier
    console.log('fetchProfile called with userIdentifier:', userIdentifier)

    let userId = null

    if (!userIdentifier) {
      // No userIdentifier, use current user
      userId = authStore.user?.id
      console.log('No userIdentifier, using current user ID:', userId)
    } else if (!isNaN(userIdentifier)) {
      // userIdentifier is a number (ID)
      userId = parseInt(userIdentifier)
      console.log('userIdentifier is ID:', userId)
    } else {
      // userIdentifier is a username, need to resolve to ID
      console.log('userIdentifier is username, resolving:', userIdentifier)
      try {
        // For now, let's find the user by username in the suggested connections or use a direct lookup
        const response = await api.get(`/auth/alumni/by-name/${userIdentifier}/`)
        userId = response.data.id
        console.log('Resolved username to ID:', userId)
      } catch (error) {
        console.error('Error resolving username:', error)
        // Fallback: try to get the user by username directly
        try {
          const usersResponse = await api.get('/auth/users/')
          const user = usersResponse.data.find(u => u.username === userIdentifier)
          if (user) {
            userId = user.id
            console.log('Found user by username search:', userId)
          } else {
            throw new Error('User not found')
          }
        } catch (fallbackError) {
          console.error('Fallback username resolution failed:', fallbackError)
          userId = authStore.user?.id // Ultimate fallback to current user
          console.log('Ultimate fallback to current user ID:', userId)
        }
      }
    }

    // Set the resolved user ID for isOwnProfile computation
    resolvedUserId.value = userId

    console.log('Final userId for API call:', userId)
    console.log('isOwnProfile after resolution:', isOwnProfile.value)

    // Use ID-based API endpoint (reliable)
    const endpoint = (userId === authStore.user?.id)
      ? '/enhanced-profile/'
      : `/enhanced-profile/${userId}/`

    console.log('Fetching from endpoint:', endpoint)

    const response = await api.get(`/auth${endpoint}`)
    const data = response.data

    console.log('Profile data received:', data.first_name, data.last_name)
    console.log('🖼️ API Response full data keys:', Object.keys(data))
    console.log('🖼️ API Response profile_picture:', data.profile_picture)
    console.log('🖼️ API Response profile object:', data.profile)

    user.value = data
    profile.value = data.profile

    console.log('🖼️ After assignment - user.value.profile_picture:', user.value.profile_picture)

    // Load privacy settings and apply to data
    await loadPrivacySettings()

    // Add privacy settings to each item
    education.value = (data.education || []).map(edu => ({
      ...edu,
      visibility: getItemPrivacy('education', edu.id) || 'connections_only'
    }))

    workHistories.value = (data.work_histories || []).map(work => ({
      ...work,
      visibility: getItemPrivacy('experience', work.id) || 'connections_only'
    }))

    achievements.value = (data.achievements || []).map(achievement => ({
      ...achievement,
      visibility: getItemPrivacy('achievement', achievement.id) || 'connections_only'
    }))

    memberships.value = (data.memberships || []).map(membership => ({
      ...membership,
      visibility: getItemPrivacy('membership', membership.id) || 'connections_only'
    }))

    recognitions.value = (data.recognitions || []).map(recognition => ({
      ...recognition,
      visibility: getItemPrivacy('recognition', recognition.id) || 'connections_only'
    }))

    trainings.value = (data.trainings || []).map(training => ({
      ...training,
      visibility: getItemPrivacy('training', training.id) || 'connections_only'
    }))

    publications.value = (data.publications || []).map(publication => ({
      ...publication,
      visibility: getItemPrivacy('publication', publication.id) || 'connections_only'
    }))

    // Map backend response fields to careerEnhancement structure
    careerEnhancement.value = {
      certificates: data.certificates || [],
      cseStatus: data.cse_status || null
    }

    // Load user skills separately
    await loadUserSkills()

    // Set social data
    if (profile.value) {
      connectionsCount.value = profile.value.connections_count || 0
      isFollowing.value = profile.value.is_following || false
    }
  } catch (error) {
    console.error('Error fetching profile:', error)
  } finally {
    loading.value = false
  }
}

// Load user skills from the new UserSkill API
const loadUserSkills = async () => {
  try {
    const endpoint = isOwnProfile.value ? '/user-skills/' : `/user-skills/user/${profileUserId.value}/`
    const response = await api.get(`/auth${endpoint}`)

    // Apply privacy settings to each skill
    skills.value = (response.data || []).map(skill => ({
      ...skill,
      visibility: getItemPrivacy('skill', skill.id) || 'connections_only'
    }))
  } catch (error) {
    console.error('Error loading user skills:', error)
    skills.value = []
  }
}

const toggleFollow = async () => {
  try {
    followLoading.value = true

    if (isFollowing.value) {
      await api.delete(`/auth/follow/${profileUserId.value}/`)
      isFollowing.value = false
    } else {
      await api.post(`/auth/follow/${profileUserId.value}/`)
      isFollowing.value = true
    }

    // Refresh connections count
    await fetchProfile()
  } catch (error) {
    console.error('Error toggling follow:', error)
  } finally {
    followLoading.value = false
  }
}

const openMessage = () => {
  // Navigate to messaging with this user
  router.push({
    name: 'AlumniMessaging',
    query: { userId: profileUserId.value }
  })
}

const editProfile = () => {
  showEditModal.value = true
}

const editCoverPhoto = () => {
  showCoverModal.value = true
}

const editProfilePicture = () => {
  showProfilePictureModal.value = true
}

const updateProfile = async (profileData) => {
  try {
    await api.patch('/auth/enhanced-profile/', profileData)
    await fetchProfile()
    showEditModal.value = false
  } catch (error) {
    console.error('Error updating profile:', error)
  }
}

const updateCoverPhoto = async (file) => {
  try {
    const formData = new FormData()
    formData.append('cover_photo', file)

    await api.patch('/auth/enhanced-profile/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    await fetchProfile()
    showCoverModal.value = false
  } catch (error) {
    console.error('Error updating cover photo:', error)
  }
}

const updateProfilePicture = async (file) => {
  try {
    const formData = new FormData()
    formData.append('profile_picture', file)

    await api.patch('/auth/enhanced-profile/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    await fetchProfile()
    showProfilePictureModal.value = false
  } catch (error) {
    console.error('Error updating profile picture:', error)
  }
}

// Education CRUD handlers
const addEducation = () => {
  selectedEducation.value = null
  showEducationModal.value = true
}

const editEducation = (education) => {
  selectedEducation.value = education
  showEducationModal.value = true
}

const deleteEducation = async (educationId) => {
  if (!confirm('Are you sure you want to delete this education record?')) {
    return
  }

  try {
    await api.delete(`/auth/education/${educationId}/`)
    await fetchProfile() // Refresh data
  } catch (error) {
    console.error('Error deleting education:', error)
    alert('Failed to delete education record')
  }
}

const closeEducationModal = () => {
  showEducationModal.value = false
  selectedEducation.value = null
}

const saveEducation = async (educationData) => {
  try {
    console.log('🔍 Saving education data:', educationData)
    console.log('🔍 API endpoint:', selectedEducation.value ? `/auth/education/${selectedEducation.value.id}/` : '/auth/education/')

    if (selectedEducation.value) {
      // Update existing education
      const response = await api.put(`/auth/education/${selectedEducation.value.id}/`, educationData)
      console.log('✅ Update response:', response.data)
    } else {
      // Create new education
      const response = await api.post('/auth/education/', educationData)
      console.log('✅ Create response:', response.data)
    }

    closeEducationModal()
    await fetchProfile() // Refresh data
  } catch (error) {
    console.error('❌ Error saving education:', error)
    console.error('❌ Error details:', error.response?.data)
    console.error('❌ Error status:', error.response?.status)
    alert('Failed to save education record: ' + (error.response?.data?.detail || error.message))
  }
}

// Experience CRUD handlers
const addExperience = () => {
  selectedExperience.value = null
  showExperienceModal.value = true
}

const editExperience = (experience) => {
  selectedExperience.value = experience
  showExperienceModal.value = true
}

const deleteExperience = async (experienceId) => {
  if (!confirm('Are you sure you want to delete this work experience?')) {
    return
  }

  try {
    await api.delete(`/auth/work-history/${experienceId}/`)
    await fetchProfile() // Refresh data
  } catch (error) {
    console.error('Error deleting experience:', error)
    alert('Failed to delete work experience')
  }
}

const closeExperienceModal = () => {
  showExperienceModal.value = false
  selectedExperience.value = null
}

const saveExperience = async (experienceData) => {
  try {
    if (selectedExperience.value) {
      // Update existing experience
      await api.put(`/auth/work-history/${selectedExperience.value.id}/`, experienceData)
    } else {
      // Create new experience
      await api.post('/auth/work-history/', experienceData)
    }

    closeExperienceModal()
    await fetchProfile() // Refresh data
  } catch (error) {
    console.error('Error saving experience:', error)
    alert('Failed to save work experience')
  }
}

// Skill CRUD handlers
const addSkill = () => {
  selectedSkill.value = null
  showSkillModal.value = true
}

const editSkill = (skill) => {
  selectedSkill.value = skill
  showSkillModal.value = true
}

const deleteSkill = async (skillId) => {
  if (!confirm('Are you sure you want to remove this skill?')) {
    return
  }

  try {
    await api.delete(`/auth/user-skills/${skillId}/`)
    await loadUserSkills() // Reload skills after deletion
    alert('Skill removed successfully!')
  } catch (error) {
    console.error('Error deleting skill:', error)
    alert('Failed to delete skill')
  }
}

const closeSkillModal = () => {
  showSkillModal.value = false
  selectedSkill.value = null
}

const saveSkill = async (skillData) => {
  try {
    if (selectedSkill.value) {
      // Update existing skill
      await api.put(`/auth/user-skills/${selectedSkill.value.id}/`, skillData)
    } else {
      // Create new skill
      await api.post('/auth/user-skills/', skillData)
    }

    closeSkillModal()
    await loadUserSkills() // Refresh skills data
    alert('Skill saved successfully!')
  } catch (error) {
    console.error('Error saving skill:', error)
    alert('Failed to save skill')
  }
}

// Achievement CRUD handlers
const addAchievement = () => {
  selectedAchievement.value = null
  showAchievementModal.value = true
}

const editAchievement = (achievement) => {
  selectedAchievement.value = achievement
  showAchievementModal.value = true
}

const deleteAchievement = async (achievementId) => {
  if (!confirm('Are you sure you want to delete this achievement?')) {
    return
  }

  try {
    await api.delete(`/auth/achievements/${achievementId}/`)
    await fetchProfile() // Refresh data
  } catch (error) {
    console.error('Error deleting achievement:', error)
    alert('Failed to delete achievement')
  }
}

const closeAchievementModal = () => {
  showAchievementModal.value = false
  selectedAchievement.value = null
}

const saveAchievement = async (achievementData) => {
  try {
    console.log('🔍 Raw achievementData received:', achievementData)

    const formData = new FormData()

    // Add all fields to FormData with proper handling
    Object.keys(achievementData).forEach(key => {
      const value = achievementData[key]
      console.log(`🔍 Processing field: ${key} = ${value} (type: ${typeof value})`)

      // Always add critical fields (type, url, is_featured) even if empty
      const criticalFields = ['type', 'url', 'is_featured']

      if (value !== null && value !== undefined) {
        // Handle file uploads
        if (key === 'attachment' && value instanceof File) {
          formData.append(key, value)
          console.log(`📎 Added file: ${key} = ${value.name}`)
        }
        // Handle other fields
        else if (key !== 'attachment') {
          const stringValue = String(value)
          formData.append(key, stringValue)
          console.log(`📝 Added field: ${key} = "${stringValue}"`)
        }
      } else {
        // For critical fields, send empty string instead of skipping
        if (criticalFields.includes(key)) {
          formData.append(key, '')
          console.log(`📝 Added empty critical field: ${key} = ""`)
        } else {
          console.log(`⚠️ Skipped null/undefined field: ${key}`)
        }
      }
    })

    // Log all FormData entries
    console.log('📤 FormData entries:')
    for (let [key, value] of formData.entries()) {
      console.log(`  ${key}: ${value}`)
    }

    let response
    if (selectedAchievement.value) {
      // Update existing achievement
      console.log(`🔄 Updating achievement ID: ${selectedAchievement.value.id}`)
      response = await api.put(`/auth/achievements/${selectedAchievement.value.id}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      console.log('✅ Update API response:', response.data)
    } else {
      // Create new achievement
      console.log('🆕 Creating new achievement via API')
      response = await api.post('/auth/achievements/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      console.log('✅ Create API response:', response.data)
    }

    // Show success message
    const action = selectedAchievement.value ? 'updated' : 'created'
    console.log(`Achievement ${action} successfully:`, response.data)

    closeAchievementModal()
    await fetchProfile() // Refresh data to show changes

  } catch (error) {
    console.error('Error saving achievement:', error)

    // More specific error handling
    if (error.response?.status === 400) {
      alert('Please check all fields and try again. Make sure required fields are filled.')
    } else if (error.response?.status === 413) {
      alert('File size too large. Please upload a smaller file.')
    } else {
      alert('Failed to save achievement. Please try again.')
    }
  }
}

// Privacy settings state and functions
const privacySettings = ref({})

const loadPrivacySettings = async () => {
  try {
    console.log('🔐 Loading privacy settings...')
    const response = await api.get('/auth/profile/field-update/')

    // Convert array to lookup object
    privacySettings.value = {}
    response.data.forEach(setting => {
      privacySettings.value[setting.field_name] = setting.visibility
    })

    console.log('🔐 Privacy settings loaded:', privacySettings.value)
  } catch (error) {
    console.error('❌ Failed to load privacy settings:', error)
    privacySettings.value = {}
  }
}

const getItemPrivacy = (itemType, itemId) => {
  const fieldName = `${itemType}_${itemId}`
  return privacySettings.value[fieldName] || 'connections_only'
}

// Privacy handlers for individual items
const handleEducationVisibilityChange = async (educationId, newVisibility) => {
  console.log('🎯 handleEducationVisibilityChange called:', { educationId, newVisibility })
  try {
    // Use the existing field-update endpoint with a specific naming convention
    console.log('📤 Sending privacy update request...')
    const response = await api.post('/auth/profile/field-update/', {
      field_name: `education_${educationId}`,
      visibility: newVisibility
    })

    // Update both local state and privacy settings cache
    const edu = education.value.find(e => e.id === educationId)
    if (edu) {
      edu.visibility = newVisibility
      console.log('🔄 Updated local education visibility:', edu)
    }

    // Update privacy settings cache
    privacySettings.value[`education_${educationId}`] = newVisibility

    console.log('✅ Education privacy updated:', response.data)
  } catch (error) {
    console.error('❌ Failed to update education privacy:', error)
    alert('Failed to update privacy setting. Please try again.')
  }
}

const handleExperienceVisibilityChange = async (experienceId, newVisibility) => {
  console.log('🎯 handleExperienceVisibilityChange called:', { experienceId, newVisibility })
  try {
    console.log('📤 Sending experience privacy update request...')
    const response = await api.post('/auth/profile/field-update/', {
      field_name: `experience_${experienceId}`,
      visibility: newVisibility
    })

    // Update both local state and privacy settings cache
    const exp = workHistories.value.find(w => w.id === experienceId)
    if (exp) {
      exp.visibility = newVisibility
      console.log('🔄 Updated local experience visibility:', exp)
    }

    // Update privacy settings cache
    privacySettings.value[`experience_${experienceId}`] = newVisibility

    console.log('✅ Experience privacy updated:', response.data)
  } catch (error) {
    console.error('❌ Failed to update experience privacy:', error)
    alert('Failed to update privacy setting. Please try again.')
  }
}

const handleSkillVisibilityChange = async (skillId, newVisibility) => {
  console.log('🎯 handleSkillVisibilityChange called:', { skillId, newVisibility })
  try {
    console.log('📤 Sending skill privacy update request...')
    const response = await api.post('/auth/profile/field-update/', {
      field_name: `skill_${skillId}`,
      visibility: newVisibility
    })

    // Update both local state and privacy settings cache
    const skill = skills.value.find(s => s.id === skillId)
    if (skill) {
      skill.visibility = newVisibility
      console.log('🔄 Updated local skill visibility:', skill)
    }

    // Update privacy settings cache
    privacySettings.value[`skill_${skillId}`] = newVisibility

    console.log('✅ Skill privacy updated:', response.data)
  } catch (error) {
    console.error('❌ Failed to update skill privacy:', error)
    alert('Failed to update privacy setting. Please try again.')
  }
}

const handleAchievementVisibilityChange = async (achievementId, newVisibility) => {
  console.log('🎯 handleAchievementVisibilityChange called:', { achievementId, newVisibility })
  try {
    console.log('📤 Sending achievement privacy update request...')
    const response = await api.post('/auth/profile/field-update/', {
      field_name: `achievement_${achievementId}`,
      visibility: newVisibility
    })

    // Update both local state and privacy settings cache
    const achievement = achievements.value.find(a => a.id === achievementId)
    if (achievement) {
      achievement.visibility = newVisibility
      console.log('🔄 Updated local achievement visibility:', achievement)
    }

    // Update privacy settings cache
    privacySettings.value[`achievement_${achievementId}`] = newVisibility

    console.log('✅ Achievement privacy updated:', response.data)
  } catch (error) {
    console.error('❌ Failed to update achievement privacy:', error)
    alert('Failed to update privacy setting. Please try again.')
  }
}

const handleConnect = () => {
  // Handle connection from suggested connections
}

// Membership handlers
const addMembership = () => {
  selectedMembership.value = null
  showMembershipModal.value = true
}

const editMembership = (membership) => {
  selectedMembership.value = membership
  showMembershipModal.value = true
}

const deleteMembership = async (membershipId) => {
  if (!confirm('Are you sure you want to delete this membership?')) {
    return
  }

  try {
    await api.delete(`/auth/memberships/${membershipId}/`)
    
    // Remove from local state
    memberships.value = memberships.value.filter(m => m.id !== membershipId)
    console.log('Membership deleted:', membershipId)
  } catch (error) {
    console.error('Error deleting membership:', error)
    alert('Failed to delete membership')
  }
}

const closeMembershipModal = () => {
  showMembershipModal.value = false
  selectedMembership.value = null
}

const saveMembership = async (membershipData) => {
  try {
    if (selectedMembership.value) {
      // Update existing membership
      await api.put(`/auth/memberships/${selectedMembership.value.id}/`, membershipData)
    } else {
      // Create new membership
      await api.post('/auth/memberships/', membershipData)
    }
    
    closeMembershipModal()
    await fetchProfile() // Refresh to get updated memberships with privacy settings
  } catch (error) {
    console.error('Error saving membership:', error)
    alert('Failed to save membership')
  }
}

const handleMembershipVisibilityChange = async (data) => {
  console.log('Membership visibility change:', data)
  // TODO: Implement visibility change API call
}

// Recognition handlers
const addRecognition = () => {
  selectedRecognition.value = null
  showRecognitionModal.value = true
}

const editRecognition = (recognition) => {
  selectedRecognition.value = recognition
  showRecognitionModal.value = true
}

const deleteRecognition = async (recognitionId) => {
  if (!confirm('Are you sure you want to delete this recognition?')) {
    return
  }

  try {
    await api.delete(`/auth/recognitions/${recognitionId}/`)
    
    // Remove from local state
    recognitions.value = recognitions.value.filter(r => r.id !== recognitionId)
    console.log('Recognition deleted:', recognitionId)
  } catch (error) {
    console.error('Error deleting recognition:', error)
    alert('Failed to delete recognition')
  }
}

const closeRecognitionModal = () => {
  showRecognitionModal.value = false
  selectedRecognition.value = null
}

const saveRecognition = async (recognitionData) => {
  try {
    if (selectedRecognition.value) {
      // Update existing recognition
      await api.put(`/auth/recognitions/${selectedRecognition.value.id}/`, recognitionData)
    } else {
      // Create new recognition
      await api.post('/auth/recognitions/', recognitionData)
    }
    
    closeRecognitionModal()
    await fetchProfile() // Refresh to get updated recognitions
  } catch (error) {
    console.error('Error saving recognition:', error)
    console.error('Error response:', error.response?.data)
    alert('Failed to save recognition: ' + (error.response?.data?.detail || error.message))
  }
}

const handleRecognitionVisibilityChange = (data) => {
  console.log('Recognition visibility change:', data)
}

// Training handlers
const addTraining = () => {
  selectedTraining.value = null
  showTrainingModal.value = true
}

const editTraining = (training) => {
  selectedTraining.value = training
  showTrainingModal.value = true
}

const deleteTraining = async (trainingId) => {
  if (!confirm('Are you sure you want to delete this training?')) {
    return
  }

  try {
    await api.delete(`/auth/trainings/${trainingId}/`)
    
    // Remove from local state
    trainings.value = trainings.value.filter(t => t.id !== trainingId)
    console.log('Training deleted:', trainingId)
  } catch (error) {
    console.error('Error deleting training:', error)
    alert('Failed to delete training')
  }
}

const closeTrainingModal = () => {
  showTrainingModal.value = false
  selectedTraining.value = null
}

const saveTraining = async (trainingData) => {
  try {
    let response
    if (selectedTraining.value) {
      // Update existing training
      response = await api.put(`/auth/trainings/${selectedTraining.value.id}/`, trainingData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      const index = trainings.value.findIndex(t => t.id === selectedTraining.value.id)
      if (index !== -1) {
        trainings.value[index] = response.data
      }
    } else {
      // Create new training
      response = await api.post('/auth/trainings/', trainingData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      trainings.value.push(response.data)
    }
    
    closeTrainingModal()
    console.log('Training saved:', response.data)
  } catch (error) {
    console.error('Error saving training:', error)
    alert('Failed to save training')
  }
}

const handleTrainingVisibilityChange = (data) => {
  console.log('Training visibility change:', data)
}

// Publication handlers
const addPublication = () => {
  selectedPublication.value = null
  showPublicationModal.value = true
}

const editPublication = (publication) => {
  selectedPublication.value = publication
  showPublicationModal.value = true
}

const deletePublication = async (publicationId) => {
  if (!confirm('Are you sure you want to delete this publication?')) {
    return
  }

  try {
    await api.delete(`/auth/publications/${publicationId}/`)
    
    // Remove from local state
    publications.value = publications.value.filter(p => p.id !== publicationId)
    console.log('Publication deleted:', publicationId)
  } catch (error) {
    console.error('Error deleting publication:', error)
    alert('Failed to delete publication')
  }
}

const closePublicationModal = () => {
  showPublicationModal.value = false
  selectedPublication.value = null
}

const savePublication = async (publicationData) => {
  try {
    // Transform frontend data to match backend PublicationSerializer
    const backendData = {
      title: publicationData.title,
      publication_type: publicationData.publication_type || 'journal',
      // Combine co_authors array into single authors string
      authors: publicationData.co_authors && publicationData.co_authors.length > 0
        ? publicationData.co_authors.join(', ')
        : 'Unknown',
      // Convert year_published (number) to date_published (YYYY-MM-DD)
      date_published: publicationData.year_published 
        ? `${publicationData.year_published}-01-01`
        : new Date().toISOString().split('T')[0],
      // Map place_of_publication to publisher
      publisher: publicationData.place_of_publication || null,
      url: publicationData.url || null,
      doi: publicationData.doi || null
      // Note: journal_name, volume, issue, pages, authors_type are not in backend model
    }

    console.log('📝 Saving publication with data:', backendData)

    let response
    if (selectedPublication.value) {
      // Update existing publication
      response = await api.put(`/auth/publications/${selectedPublication.value.id}/`, backendData)
      const index = publications.value.findIndex(p => p.id === selectedPublication.value.id)
      if (index !== -1) {
        publications.value[index] = response.data
      }
    } else {
      // Create new publication
      response = await api.post('/auth/publications/', backendData)
      publications.value.push(response.data)
    }
    
    closePublicationModal()
    console.log('✅ Publication saved successfully:', response.data)
  } catch (error) {
    console.error('❌ Error saving publication:', error)
    console.error('❌ Error response data:', error.response?.data)
    console.error('❌ Error status:', error.response?.status)
    
    // Show detailed error message
    let errorMessage = 'Failed to save publication'
    if (error.response?.data) {
      if (typeof error.response.data === 'object') {
        // DRF validation errors
        const errors = Object.entries(error.response.data)
          .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
          .join('\n')
        errorMessage += ':\n' + errors
      } else {
        errorMessage += ': ' + error.response.data
      }
    }
    alert(errorMessage)
  }
}

const handlePublicationVisibilityChange = (data) => {
  console.log('Publication visibility change:', data)
}

// Career Enhancement handlers
const addCareerEnhancement = () => {
  selectedCareerEnhancement.value = null
  showCareerEnhancementModal.value = true
}

const editCertificate = (certificate) => {
  // For editing certificates, we open the career enhancement modal with the full data
  // The certificate parameter is the specific certificate to edit
  selectedCareerEnhancement.value = careerEnhancement.value
  showCareerEnhancementModal.value = true
  
  // Log for debugging - certificate contains the specific certificate data
  console.log('Editing certificate:', certificate)
}

const deleteCertificate = async (certificateId) => {
  if (!confirm('Are you sure you want to delete this certificate?')) {
    return
  }

  try {
    await api.delete(`/auth/certificates/${certificateId}/`)
    
    // Remove from local state
    if (careerEnhancement.value.certificates) {
      careerEnhancement.value.certificates = careerEnhancement.value.certificates.filter(c => c.id !== certificateId)
    }
    console.log('Certificate deleted:', certificateId)
  } catch (error) {
    console.error('Error deleting certificate:', error)
    alert('Failed to delete certificate')
  }
}

const editCSE = () => {
  selectedCareerEnhancement.value = careerEnhancement.value
  showCareerEnhancementModal.value = true
}

const closeCareerEnhancementModal = () => {
  showCareerEnhancementModal.value = false
  selectedCareerEnhancement.value = null
}

const saveCareerEnhancement = async (careerEnhancementData) => {
  try {
    // Handle certificates
    if (careerEnhancementData.certificates) {
      const certificates = Array.isArray(careerEnhancementData.certificates) 
        ? careerEnhancementData.certificates 
        : [careerEnhancementData.certificates]
      
      for (const cert of certificates) {
        const formData = new FormData()
        
        if (cert.certificate_type) formData.append('certificate_type', cert.certificate_type)
        if (cert.certificate_number) formData.append('certificate_number', cert.certificate_number)
        if (cert.issuing_body) formData.append('issuing_body', cert.issuing_body)
        if (cert.date_issued) formData.append('date_issued', cert.date_issued)
        if (cert.expiry_date) formData.append('expiry_date', cert.expiry_date)
        if (cert.certificate_file instanceof File) {
          formData.append('certificate_file', cert.certificate_file)
        }
        
        if (cert.id) {
          // Update existing
          const response = await api.put(`/auth/certificates/${cert.id}/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
          // Update in local state
          const index = careerEnhancement.value.certificates.findIndex(c => c.id === cert.id)
          if (index !== -1) {
            careerEnhancement.value.certificates[index] = response.data
          }
        } else {
          // Create new
          const response = await api.post('/auth/certificates/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
          if (!careerEnhancement.value.certificates) {
            careerEnhancement.value.certificates = []
          }
          careerEnhancement.value.certificates.push(response.data)
        }
      }
    }
    
    // Handle CSE status
    if (careerEnhancementData.cseStatus) {
      const statusData = {
        status: careerEnhancementData.cseStatus.status,
        current_position: careerEnhancementData.cseStatus.current_position,
        current_company: careerEnhancementData.cseStatus.current_company,
        industry: careerEnhancementData.cseStatus.industry,
        start_date: careerEnhancementData.cseStatus.start_date,
        end_date: careerEnhancementData.cseStatus.end_date,
        is_current: careerEnhancementData.cseStatus.is_current
      }
      
      const response = await api.put('/auth/cse-status/', statusData)
      careerEnhancement.value.cseStatus = response.data
    }
    
    closeCareerEnhancementModal()
    console.log('Career enhancement saved:', careerEnhancementData)
  } catch (error) {
    console.error('Error saving career enhancement:', error)
    alert('Failed to save career enhancement')
  }
}

const handleCareerEnhancementVisibilityChange = (data) => {
  console.log('Career enhancement visibility change:', data)
}

// Lifecycle
onMounted(() => {
  fetchProfile()
})

// Watch for route changes to update profile
watch(() => route.params.userIdentifier, () => {
  // Reset resolved user ID when route changes
  resolvedUserId.value = null
  fetchProfile()
}, { immediate: false })
</script>

<template>
  <div :class="[
    'min-h-screen transition-colors duration-200',
    themeStore.isDarkMode ? 'bg-gray-900' : 'bg-white'
  ]">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center h-64">
      <div class="w-12 h-12 border-b-2 border-green-600 rounded-full animate-spin"></div>
    </div>

    <!-- Main Profile Content -->
    <div v-else class="max-w-6xl p-4 mx-auto">
      <!-- Profile Header Section -->
      <div :class="[
        'rounded-lg shadow-lg overflow-hidden mb-6 transition-colors duration-200',
        themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white'
      ]">
        <!-- Cover Photo -->
        <div class="relative h-48 bg-gradient-to-r from-green-400 to-blue-500">
          <img
            v-if="profile?.cover_photo"
            :src="profile.cover_photo"
            alt="Cover Photo"
            class="object-cover w-full h-full"
          />
          <div
            v-if="isOwnProfile"
            :class="[
              'absolute top-4 right-4 rounded-full p-2 cursor-pointer transition-colors',
              themeStore.isDarkMode
                ? 'bg-gray-700 hover:bg-gray-600'
                : 'bg-white hover:bg-gray-100'
            ]"
            @click="editCoverPhoto"
          >
            <svg :class="[
              'w-5 h-5',
              themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
            ]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
          </div>
        </div>

        <!-- Profile Info -->
        <div class="relative px-6 pb-6">
          <!-- Profile Picture -->
          <div class="absolute -top-16 left-6">
            <div class="relative">
              <img
                :src="profilePictureUrl"
                alt="Profile Picture"
                :class="[
                  'w-32 h-32 rounded-full border-4 shadow-lg object-cover',
                  themeStore.isDarkMode ? 'border-gray-800' : 'border-white'
                ]"
              />
              <div
                v-if="isOwnProfile"
                class="absolute p-2 transition-colors bg-orange-500 rounded-full cursor-pointer bottom-2 right-2 hover:bg-orange-600"
                @click="editProfilePicture"
              >
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
              </div>
            </div>
          </div>

          <!-- Name and Basic Info -->
          <div class="pt-20">
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between">
              <div>
                <h1 :class="[
                  'text-3xl font-bold',
                  themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                ]">
                  {{ user?.first_name }} {{ user?.middle_name }} {{ user?.last_name }}
                </h1>
                <p :class="[
                  'text-lg mt-1',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">
                  {{ displayHeadline }}
                </p>

                <!-- Education Info (derived from Education section) -->
                <div v-if="displayEducationInfo" :class="[
                  'flex items-center mt-2',
                  themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
                ]">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                  </svg>
                  {{ displayEducationInfo }}
                </div>

                <!-- Location -->
                <div :class="[
                  'flex items-center mt-2',
                  themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
                ]">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  </svg>
                  {{ profile?.location || profile?.present_address || 'Location not specified' }}
                </div>

                <!-- Connections -->
                <div :class="[
                  'flex items-center mt-1',
                  themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
                ]">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                  </svg>
                  {{ connectionsCount }} connections
                </div>
              </div>

              <!-- Action Buttons -->
              <div v-if="!isOwnProfile" class="flex mt-4 space-x-3 lg:mt-0">
                <button
                  @click="toggleFollow"
                  :disabled="followLoading"
                  :class="[
                    'px-6 py-2 rounded-lg font-medium transition-colors',
                    isFollowing
                      ? themeStore.isDarkMode
                        ? 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      : 'bg-orange-500 text-white hover:bg-orange-600'
                  ]"
                >
                  <span v-if="followLoading" class="mr-2 animate-spin">⟳</span>
                  {{ isFollowing ? 'Following' : 'Follow' }}
                </button>
                <button
                  @click="openMessage"
                  class="px-6 py-2 font-medium text-white transition-colors bg-orange-600 rounded-lg hover:bg-orange-700"
                >
                  Message
                </button>
              </div>

              <!-- Edit Profile Button for own profile -->
              <div v-else class="mt-4 lg:mt-0">
                <button
                  @click="editProfile"
                  class="px-6 py-2 font-medium text-white transition-colors bg-orange-500 rounded-lg hover:bg-orange-600"
                >
                  Edit Profile
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab Navigation -->
      <div :class="[
        'border-b shadow-sm transition-colors duration-200',
        themeStore.isDarkMode
          ? 'bg-gray-800 border-gray-700'
          : 'bg-white border-gray-200'
      ]">
        <div class="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
          <nav class="flex space-x-8">
            <button
              @click="activeTab = 'about'"
              :class="[
                'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                activeTab === 'about'
                  ? 'border-orange-500 ' + (themeStore.isDarkMode ? 'text-orange-400' : 'text-orange-600')
                  : 'border-transparent ' + (themeStore.isDarkMode
                      ? 'text-gray-400 hover:text-gray-200 hover:border-gray-600'
                      : 'text-gray-500 hover:text-gray-700 hover:border-gray-300')
              ]"
            >
              About
            </button>
            <button
              @click="activeTab = 'posts'"
              :class="[
                'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                activeTab === 'posts'
                  ? 'border-orange-500 ' + (themeStore.isDarkMode ? 'text-orange-400' : 'text-orange-600')
                  : 'border-transparent ' + (themeStore.isDarkMode
                      ? 'text-gray-400 hover:text-gray-200 hover:border-gray-600'
                      : 'text-gray-500 hover:text-gray-700 hover:border-gray-300')
              ]"
            >
              Posts
            </button>
          </nav>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <!-- Left Column - Profile Sections -->
        <div class="space-y-6 lg:col-span-2">

          <!-- About Tab Content -->
          <div v-show="activeTab === 'about'" class="space-y-6">
            <!-- About Section -->
            <ProfileAboutSection
              :profile="profile"
              :is-own-profile="isOwnProfile"
              @profile-updated="fetchProfile"
            />

            <!-- Contact Information Section -->
            <ProfileContactSection
              :profile="profile"
              :is-own-profile="isOwnProfile"
              @profile-updated="fetchProfile"
            />

            <!-- Education Section -->
            <ProfileEducationSection
              :education="education"
              :profile="profile"
              :user="user"
              :is-own-profile="isOwnProfile"
              @add="addEducation"
              @edit="editEducation"
              @edit-profile="editProfile"
              @delete="deleteEducation"
              @education-visibility-changed="handleEducationVisibilityChange"
            />

            <!-- Experience Section -->
            <ProfileExperienceSection
              :workHistories="workHistories"
              :is-own-profile="isOwnProfile"
              @add="addExperience"
              @edit="editExperience"
              @delete="deleteExperience"
              @experience-visibility-changed="handleExperienceVisibilityChange"
            />

            <!-- Skills Section -->
            <ProfileSkillsSection
              :skills="skills"
              :is-own-profile="isOwnProfile"
              @add="addSkill"
              @edit="editSkill"
              @delete="deleteSkill"
              @skill-visibility-changed="handleSkillVisibilityChange"
            />

            <!-- Achievements Section -->
            <ProfileAchievementsSection
              :achievements="achievements"
              :is-own-profile="isOwnProfile"
              @add="addAchievement"
              @edit="editAchievement"
              @delete="deleteAchievement"
              @toggle-visibility="handleAchievementVisibilityChange"
            />

            <!-- Memberships Section -->
            <ProfileMembershipsSection
              :memberships="memberships"
              :is-own-profile="isOwnProfile"
              @add="addMembership"
              @edit="editMembership"
              @delete="deleteMembership"
              @visibility-changed="handleMembershipVisibilityChange"
            />

            <!-- Non-Academic Recognitions Section -->
            <ProfileRecognitionsSection
              :recognitions="recognitions"
              :is-own-profile="isOwnProfile"
              @add="addRecognition"
              @edit="editRecognition"
              @delete="deleteRecognition"
              @visibility-changed="handleRecognitionVisibilityChange"
            />

            <!-- Trainings Section -->
            <ProfileTrainingsSection
              :trainings="trainings"
              :is-own-profile="isOwnProfile"
              @add="addTraining"
              @edit="editTraining"
              @delete="deleteTraining"
              @visibility-changed="handleTrainingVisibilityChange"
            />

            <!-- Publications Section -->
            <ProfilePublicationsSection
              :publications="publications"
              :is-own-profile="isOwnProfile"
              @add="addPublication"
              @edit="editPublication"
              @delete="deletePublication"
              @visibility-changed="handlePublicationVisibilityChange"
            />

            <!-- Career Enhancement Section -->
            <ProfileCareerEnhancementSection
              :career-enhancement="careerEnhancement"
              :is-own-profile="isOwnProfile"
              @add="addCareerEnhancement"
              @edit-certificate="editCertificate"
              @delete-certificate="deleteCertificate"
              @edit-cse="editCSE"
              @visibility-changed="handleCareerEnhancementVisibilityChange"
            />
          </div>

          <!-- Posts Tab Content -->
          <div v-show="activeTab === 'posts'">
            <PostsTab :user-id="resolvedUserId" />
          </div>

        </div>

        <!-- Right Column - Sidebar -->
        <div class="space-y-6">
          <!-- People You May Know -->
          <SuggestedConnectionsWidget @connect="handleConnect" />
        </div>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <EditProfileModal
      v-if="showEditModal"
      :profile="profile"
      @close="showEditModal = false"
      @save="updateProfile"
    />

    <!-- Cover Photo Upload Modal -->
    <CoverPhotoModal
      v-if="showCoverModal"
      @close="showCoverModal = false"
      @save="updateCoverPhoto"
    />

    <!-- Profile Picture Upload Modal -->
    <ProfilePictureModal
      v-if="showProfilePictureModal"
      @close="showProfilePictureModal = false"
      @save="updateProfilePicture"
    />

    <!-- Education Modal -->
    <EducationModal
      v-if="showEducationModal"
      :education="selectedEducation"
      @close="closeEducationModal"
      @save="saveEducation"
    />

    <!-- Experience Modal -->
    <ExperienceModal
      v-if="showExperienceModal"
      :experience="selectedExperience"
      @close="closeExperienceModal"
      @save="saveExperience"
    />

    <!-- Skill Modal -->
    <SkillModal
      v-if="showSkillModal"
      :skill="selectedSkill"
      @close="closeSkillModal"
      @save="saveSkill"
    />

    <!-- Achievement Modal -->
    <AchievementModal
      v-if="showAchievementModal"
      :achievement="selectedAchievement"
      @close="closeAchievementModal"
      @save="saveAchievement"
    />

    <!-- Membership Modal -->
    <MembershipModal
      v-if="showMembershipModal"
      :membership="selectedMembership"
      @close="closeMembershipModal"
      @save="saveMembership"
    />

    <!-- Recognition Modal -->
    <RecognitionModal
      v-if="showRecognitionModal"
      :recognition="selectedRecognition"
      @close="closeRecognitionModal"
      @save="saveRecognition"
    />

    <!-- Training Modal -->
    <TrainingModal
      v-if="showTrainingModal"
      :training="selectedTraining"
      @close="closeTrainingModal"
      @save="saveTraining"
    />

    <!-- Publication Modal -->
    <PublicationModal
      v-if="showPublicationModal"
      :publication="selectedPublication"
      @close="closePublicationModal"
      @save="savePublication"
    />

    <!-- Career Enhancement Modal -->
    <CareerEnhancementModal
      v-if="showCareerEnhancementModal"
      :career-enhancement="selectedCareerEnhancement"
      @close="closeCareerEnhancementModal"
      @save="saveCareerEnhancement"
    />
  </div>
</template>



<style scoped>
/* Custom styles if needed */
</style>
