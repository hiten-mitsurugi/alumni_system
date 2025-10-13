<template>
  <div class="min-h-screen bg-amber-50">
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
    </div>

    <!-- Main Profile Content -->
    <div v-else class="max-w-6xl mx-auto p-4">
      <!-- Profile Header Section -->
      <div class="bg-white rounded-lg shadow-lg overflow-hidden mb-6">
        <!-- Cover Photo -->
        <div class="relative h-48 bg-gradient-to-r from-green-400 to-blue-500">
          <img 
            v-if="profile?.cover_photo" 
            :src="profile.cover_photo" 
            alt="Cover Photo"
            class="w-full h-full object-cover"
          />
          <div 
            v-if="isOwnProfile" 
            class="absolute top-4 right-4 bg-white rounded-full p-2 cursor-pointer hover:bg-gray-100"
            @click="editCoverPhoto"
          >
            <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                :src="user?.profile_picture || '/default-avatar.png'" 
                alt="Profile Picture"
                class="w-32 h-32 rounded-full border-4 border-white shadow-lg object-cover"
              />
              <div 
                v-if="isOwnProfile" 
                class="absolute bottom-2 right-2 bg-green-600 rounded-full p-2 cursor-pointer hover:bg-green-700"
                @click="editProfilePicture"
              >
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                </svg>
              </div>
            </div>
          </div>

          <!-- Name and Basic Info -->
          <div class="pt-20">
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between">
              <div>
                <h1 class="text-3xl font-bold text-gray-900">
                  {{ user?.first_name }} {{ user?.middle_name }} {{ user?.last_name }}
                </h1>
                <p class="text-lg text-gray-600 mt-1">
                  {{ displayHeadline }}
                </p>
                
                <!-- Education Info (derived from Education section) -->
                <div v-if="displayEducationInfo" class="flex items-center text-gray-500 mt-2">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                  </svg>
                  {{ displayEducationInfo }}
                </div>
                
                <!-- Location -->
                <div class="flex items-center text-gray-500 mt-2">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  </svg>
                  {{ profile?.location || profile?.present_address || 'Location not specified' }}
                </div>
                
                <!-- Connections -->
                <div class="flex items-center text-gray-500 mt-1">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                  </svg>
                  {{ connectionsCount }} connections
                </div>
              </div>

              <!-- Action Buttons -->
              <div v-if="!isOwnProfile" class="flex space-x-3 mt-4 lg:mt-0">
                <button 
                  @click="toggleFollow"
                  :disabled="followLoading"
                  class="px-6 py-2 rounded-lg font-medium transition-colors"
                  :class="isFollowing 
                    ? 'bg-gray-200 text-gray-700 hover:bg-gray-300' 
                    : 'bg-green-600 text-white hover:bg-green-700'"
                >
                  <span v-if="followLoading" class="animate-spin mr-2">⟳</span>
                  {{ isFollowing ? 'Following' : 'Follow' }}
                </button>
                <button 
                  @click="openMessage"
                  class="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
                >
                  Message
                </button>
              </div>
              
              <!-- Edit Profile Button for own profile -->
              <div v-else class="mt-4 lg:mt-0">
                <button 
                  @click="editProfile"
                  class="px-6 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors"
                >
                  Edit Profile
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left Column - Profile Sections -->
        <div class="lg:col-span-2 space-y-6">
          <!-- About Section -->
          <ProfileAboutSection 
            :profile="profile" 
            :is-own-profile="isOwnProfile"
            @edit="editAbout"
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
          />
          
          <!-- Experience Section -->
          <ProfileExperienceSection 
            :workHistories="workHistories" 
            :is-own-profile="isOwnProfile"
            @add="addExperience"
            @edit="editExperience"
            @delete="deleteExperience"
          />
          
          <!-- Skills Section -->
          <ProfileSkillsSection 
            :skills="skills" 
            :is-own-profile="isOwnProfile"
            @add="addSkill"
            @edit="editSkill"
            @delete="deleteSkill"
          />
          
          <!-- Achievements Section -->
          <ProfileAchievementsSection 
            :achievements="achievements" 
            :is-own-profile="isOwnProfile"
            @add="addAchievement"
            @edit="editAchievement"
            @delete="deleteAchievement"
          />
        </div>

        <!-- Right Column - Sidebar -->
        <div class="space-y-6">
          <!-- People You May Know -->
          <SuggestedConnectionsWidget @connect="handleConnect" />
          
          <!-- Recent Activity (if own profile) -->
          <RecentActivityWidget v-if="isOwnProfile" />
          
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

// Component imports
import ProfileAboutSection from '@/components/profile/ProfileAboutSection.vue'
import ProfileEducationSection from '@/components/profile/ProfileEducationSection.vue'
import ProfileExperienceSection from '@/components/profile/ProfileExperienceSection.vue'
import ProfileSkillsSection from '@/components/profile/ProfileSkillsSection.vue'
import ProfileAchievementsSection from '@/components/profile/ProfileAchievementsSection.vue'
import SuggestedConnectionsWidget from '@/components/profile/SuggestedConnectionsWidget.vue'
import RecentActivityWidget from '@/components/profile/RecentActivityWidget.vue'
import ContactInfoWidget from '@/components/profile/ContactInfoWidget.vue'
import EditProfileModal from '@/components/profile/EditProfileModal.vue'
import CoverPhotoModal from '@/components/profile/CoverPhotoModal.vue'
import EducationModal from '@/components/profile/EducationModal.vue'
import ExperienceModal from '@/components/profile/ExperienceModal.vue'
import SkillModal from '@/components/profile/SkillModal.vue'
import AchievementModal from '@/components/profile/AchievementModal.vue'

// Reactive data
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const followLoading = ref(false)
const showEditModal = ref(false)
const showCoverModal = ref(false)

// Modal states for CRUD operations
const showEducationModal = ref(false)
const showExperienceModal = ref(false)
const showSkillModal = ref(false)
const showAchievementModal = ref(false)

// Selected items for editing
const selectedEducation = ref(null)
const selectedExperience = ref(null)
const selectedSkill = ref(null)
const selectedAchievement = ref(null)

const user = ref(null)
const profile = ref(null)
const education = ref([])
const workHistories = ref([])
const skills = ref([])
const achievements = ref([])

const isFollowing = ref(false)
const connectionsCount = ref(0)
const resolvedUserId = ref(null) // Track the resolved user ID

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
    
    user.value = data
    profile.value = data.profile
    education.value = data.education || []
    workHistories.value = data.work_histories || []
    achievements.value = data.achievements || []
    
    // Extract skills from work histories
    skills.value = workHistories.value.reduce((acc, work) => {
      if (work.skills) {
        acc.push(...work.skills)
      }
      return acc
    }, [])
    
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
  // Implement profile picture upload
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (file) {
      const formData = new FormData()
      formData.append('profile_picture', file)
      
      try {
        await api.patch('/auth/enhanced-profile/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        await fetchProfile()
      } catch (error) {
        console.error('Error updating profile picture:', error)
      }
    }
  }
  input.click()
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

// Section handlers
const editAbout = () => {
  showEditModal.value = true
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
    if (selectedEducation.value) {
      // Update existing education
      await api.put(`/auth/education/${selectedEducation.value.id}/`, educationData)
    } else {
      // Create new education
      await api.post('/auth/education/', educationData)
    }
    
    closeEducationModal()
    await fetchProfile() // Refresh data
  } catch (error) {
    console.error('Error saving education:', error)
    alert('Failed to save education record')
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
    // For skills, we need to remove it from work histories or implement a user-skill relationship
    // Since skills are linked through work histories, we'll need to handle this differently
    console.log('Skill deletion needs to be implemented based on your data model')
    alert('Skill deletion functionality needs to be implemented')
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
    // Create the skill if it doesn't exist
    await api.post('/auth/skills/', skillData)
    
    closeSkillModal()
    await fetchProfile() // Refresh data
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
    if (selectedAchievement.value) {
      // Update existing achievement
      const formData = new FormData()
      Object.keys(achievementData).forEach(key => {
        if (achievementData[key] !== null && achievementData[key] !== undefined) {
          formData.append(key, achievementData[key])
        }
      })
      
      await api.put(`/auth/achievements/${selectedAchievement.value.id}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    } else {
      // Create new achievement
      const formData = new FormData()
      Object.keys(achievementData).forEach(key => {
        if (achievementData[key] !== null && achievementData[key] !== undefined) {
          formData.append(key, achievementData[key])
        }
      })
      
      await api.post('/auth/achievements/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    
    closeAchievementModal()
    await fetchProfile() // Refresh data
  } catch (error) {
    console.error('Error saving achievement:', error)
    alert('Failed to save achievement')
  }
}

const handleConnect = (userId) => {
  // Handle connection from suggested connections
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

<style scoped>
/* Custom styles if needed */
</style>
