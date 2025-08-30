<template>
  <div class="min-h-screen bg-gray-50">
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
                  {{ profile?.headline || profile?.present_occupation || 'Alumni' }}
                </p>
                <div class="flex items-center text-gray-500 mt-2">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  </svg>
                  {{ profile?.location || profile?.present_address || 'Location not specified' }}
                </div>
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
            :is-own-profile="isOwnProfile"
            @add="addEducation"
            @edit="editEducation"
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
          
          <!-- Contact Info -->
          <ContactInfoWidget :profile="profile" :user="user" />
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

// Reactive data
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const followLoading = ref(false)
const showEditModal = ref(false)
const showCoverModal = ref(false)

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
  
  // If no userIdentifier, it's own profile
  if (!userIdentifier) {
    return true
  }
  
  // If we have a resolved user ID, compare it with current user
  if (resolvedUserId.value) {
    return resolvedUserId.value === authStore.user?.id
  }
  
  // If userIdentifier is a number and matches current user ID, it's own profile
  if (!isNaN(userIdentifier) && userIdentifier == authStore.user?.id) {
    return true
  }
  
  // If userIdentifier is a name, check if it matches current user's name
  if (authStore.user && isNaN(userIdentifier)) {
    const currentUserName = (authStore.user.first_name + authStore.user.last_name).toLowerCase().replace(/\s+/g, '')
    return currentUserName === userIdentifier.toLowerCase()
  }
  
  return false
})

const profileUserId = computed(() => {
  return route.params.userIdentifier || authStore.user?.id
})

// Methods
const fetchProfile = async () => {
  try {
    loading.value = true
    
    let userId = route.params.userIdentifier || authStore.user?.id
    console.log('fetchProfile called with userIdentifier:', route.params.userIdentifier)
    console.log('Initial userId:', userId)
    
    // If userIdentifier is not a number, resolve it to user ID
    if (userId && isNaN(userId)) {
      console.log('Resolving name to ID:', userId)
      try {
        const response = await api.get(`/alumni/by-name/${userId}/`)
        userId = response.data.id
        console.log('Resolved to userId:', userId)
      } catch (error) {
        console.error('Error resolving user name:', error)
        // Fallback to current user
        userId = authStore.user?.id
        console.log('Fallback to current user ID:', userId)
      }
    }
    
    // Set the resolved user ID for isOwnProfile computation
    resolvedUserId.value = parseInt(userId)
    
    console.log('Final userId for API call:', userId)
    console.log('isOwnProfile after resolution:', isOwnProfile.value)
    console.log('Current user ID:', authStore.user?.id)
    console.log('Resolved user ID:', resolvedUserId.value)
    
    const endpoint = (userId === authStore.user?.id)
      ? '/enhanced-profile/' 
      : `/enhanced-profile/${userId}/`
    
    console.log('Fetching from endpoint:', endpoint)
    
    const response = await api.get(endpoint)
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
      await api.delete(`/follow/${profileUserId.value}/`)
      isFollowing.value = false
    } else {
      await api.post(`/follow/${profileUserId.value}/`)
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
        await api.patch('/enhanced-profile/', formData, {
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
    await api.patch('/enhanced-profile/', profileData)
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
    
    await api.patch('/enhanced-profile/', formData, {
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

const addEducation = () => {
  // Implement add education
}

const editEducation = (education) => {
  // Implement edit education
}

const deleteEducation = (educationId) => {
  // Implement delete education
}

const addExperience = () => {
  // Implement add experience
}

const editExperience = (experience) => {
  // Implement edit experience
}

const deleteExperience = (experienceId) => {
  // Implement delete experience
}

const addSkill = () => {
  // Implement add skill
}

const editSkill = (skill) => {
  // Implement edit skill
}

const deleteSkill = (skillId) => {
  // Implement delete skill
}

const addAchievement = () => {
  // Implement add achievement
}

const editAchievement = (achievement) => {
  // Implement edit achievement
}

const deleteAchievement = (achievementId) => {
  // Implement delete achievement
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
