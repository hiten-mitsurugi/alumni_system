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
            </div>
          </div>

          <!-- User Info & Actions -->
          <div class="pt-20 flex justify-between items-start">
            <div class="flex-1">
              <h1 class="text-3xl font-bold text-gray-900 mb-2">
                {{ user?.first_name }} {{ user?.last_name }}
              </h1>
              
              <p v-if="profile?.headline" class="text-lg text-gray-600 mb-2">
                {{ profile.headline }}
              </p>
              
              <p v-if="profile?.present_occupation" class="text-gray-500 mb-2">
                {{ profile.present_occupation }}
              </p>
              
              <div class="flex items-center space-x-4 text-sm text-gray-500">
                <span v-if="user?.program">{{ user.program }}</span>
                <span v-if="user?.year_graduated">Class of {{ user.year_graduated }}</span>
                <span v-if="connections > 0">{{ connections }} connections</span>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex space-x-3">
              <button 
                @click="connectUser"
                :disabled="isConnecting"
                class="px-6 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50"
              >
                <span v-if="isConnecting" class="animate-spin mr-2">⟳</span>
                {{ isFollowing ? 'Following' : 'Connect' }}
              </button>
              
              <button 
                @click="sendMessage"
                class="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
              >
                Message
              </button>
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
            :is-own-profile="false"
            :user-id="user?.id"
            @profile-updated="fetchUserProfile"
          />
          
          <!-- Contact Information Section -->
          <ProfileContactSection 
            :profile="profile" 
            :is-own-profile="false"
            :user-id="user?.id"
            @profile-updated="fetchUserProfile"
          />
          
          <!-- Education Section -->
          <ProfileEducationSection 
            :education="education" 
            :profile="profile"
            :user="user"
            :is-own-profile="false"
            @add="() => {}"
            @edit="() => {}"
            @edit-profile="() => {}"
            @delete="() => {}"
          />
          
          <!-- Experience Section -->
          <ProfileExperienceSection 
            :workHistories="workHistories" 
            :is-own-profile="false"
            @add="() => {}"
            @edit="() => {}"
            @delete="() => {}"
          />
          
          <!-- Skills Section -->
          <ProfileSkillsSection 
            :skills="skills" 
            :is-own-profile="false"
            @add="() => {}"
            @edit="() => {}"
            @delete="() => {}"
          />
          
          <!-- Achievements Section -->
          <ProfileAchievementsSection 
            :achievements="achievements" 
            :is-own-profile="false"
            @add="() => {}"
            @edit="() => {}"
            @delete="() => {}"
          />
        </div>

        <!-- Right Column - Sidebar -->
        <div class="space-y-6">
          <!-- Suggestions Widget -->
          <UserSuggestionsWidget @connect="handleConnect" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

// Components
import ProfileAboutSection from '@/components/profile/ProfileAboutSection.vue'
import ProfileContactSection from '@/components/profile/ProfileContactSection.vue'
import ProfileEducationSection from '@/components/profile/ProfileEducationSection.vue'
import ProfileExperienceSection from '@/components/profile/ProfileExperienceSection.vue'
import ProfileSkillsSection from '@/components/profile/ProfileSkillsSection.vue'
import ProfileAchievementsSection from '@/components/profile/ProfileAchievementsSection.vue'
import UserSuggestionsWidget from '@/components/user-profile/UserSuggestionsWidget.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// State
const loading = ref(true)
const user = ref(null)
const profile = ref(null)
const education = ref([])
const workHistories = ref([])
const skills = ref([])
const achievements = ref([])
const connections = ref(0)
const isFollowing = ref(false)
const isConnecting = ref(false)

// Get user identifier from route
const userIdentifier = computed(() => route.params.userIdentifier)

// Fetch user profile data
const fetchUserProfile = async () => {
  try {
    loading.value = true
    
    if (!userIdentifier.value) {
      router.push({ name: 'AlumniHome' })
      return
    }

    // Fetch user profile by username using enhanced-profile endpoint
    const response = await api.get(`/auth/enhanced-profile/username/${userIdentifier.value}/`)
    
    // Debug: Log the API response structure
    console.log('UserProfile API response:', response.data)
    console.log('Available fields in response:', Object.keys(response.data))
    console.log('Skills data in response:', response.data.user_skills)
    console.log('Skills data type:', typeof response.data.user_skills)
    console.log('Skills data length:', response.data.user_skills?.length)
    
    // The API returns the user data directly, with profile nested inside
    const data = response.data
    user.value = data
    profile.value = data.profile
    education.value = data.education || []
    workHistories.value = data.work_histories || []
    achievements.value = data.achievements || []
    connections.value = data.connections_count || 0
    
    // Load user skills separately (like MyProfile does)
    await loadUserSkills()
    
    // Debug: Log the extracted data
    console.log('UserProfile extracted data:', {
      user: {
        name: user.value?.first_name + ' ' + user.value?.last_name,
        email: user.value?.email,
        fields: user.value ? Object.keys(user.value) : []
      },
      profile: {
        bio: profile.value?.bio,
        headline: profile.value?.headline,
        fields: profile.value ? Object.keys(profile.value) : []
      },
      education: education.value.length,
      workHistories: workHistories.value.length,
      achievements: achievements.value.length,
      skills: skills.value.length
    })
    
    // Check if already following
    await checkFollowingStatus()
    
  } catch (error) {
    console.error('Error fetching user profile:', error)
    if (error.response?.status === 404) {
      router.push({ name: 'AlumniHome' })
    }
  } finally {
    loading.value = false
  }
}

// Load user skills using the same approach as MyProfile
const loadUserSkills = async () => {
  try {
    if (!user.value) return
    
    // For UserProfile, we're viewing another user's profile, but the /auth/user-skills/ endpoint
    // only returns skills for the authenticated user. Since we can't get other users' skills directly,
    // we'll need to check if this is our own profile or implement a different approach.
    
    // Check if we're viewing our own profile
    const currentUserResponse = await api.get('/auth/user/')
    const currentUser = currentUserResponse.data
    
    if (currentUser.id === user.value.id) {
      // If viewing own profile, use the user-skills endpoint
      const response = await api.get('/auth/user-skills/')
      skills.value = response.data || []
    } else {
      // For other users' profiles, skills data should come from enhanced-profile
      // For now, we'll try to get it from the user_skills field if available
      skills.value = user.value.user_skills || []
    }
  } catch (error) {
    console.error('Error loading user skills:', error)
    skills.value = []
  }
}

// Check if current user is following this user
const checkFollowingStatus = async () => {
  try {
    if (!user.value) return
    
    const response = await api.get('/auth/connections/')
    const following = response.data.following || []
    isFollowing.value = following.some(f => f.id === user.value.id)
  } catch (error) {
    console.error('Error checking following status:', error)
  }
}

// Connect/Follow user
const connectUser = async () => {
  try {
    if (!user.value) return
    
    isConnecting.value = true
    
    if (isFollowing.value) {
      // Unfollow logic would go here
      console.log('Unfollow functionality not implemented yet')
    } else {
      await api.post(`/auth/follow/${user.value.id}/`)
      isFollowing.value = true
      connections.value += 1
    }
    
  } catch (error) {
    console.error('Error connecting user:', error)
  } finally {
    isConnecting.value = false
  }
}

// Send message to user
const sendMessage = () => {
  if (!user.value) return
  
  router.push({
    name: 'AlumniMessaging',
    query: { user: user.value.id }
  })
}

// Handle profile updates
const handleProfileUpdate = () => {
  fetchUserProfile()
}

// Handle connection from suggestions widget
const handleConnect = (userId) => {
  console.log('Connected to user:', userId)
  // Optionally refresh connections or show notification
}

// Watch for route changes
watch(userIdentifier, () => {
  if (userIdentifier.value) {
    fetchUserProfile()
  }
})

onMounted(() => {
  fetchUserProfile()
})
</script>