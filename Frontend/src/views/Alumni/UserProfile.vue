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

      <!-- Profile Content Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left Column - About & Contact (2/3) -->
        <div class="lg:col-span-2 space-y-6">
          <!-- About Section -->
          <UserAboutSection 
            :user="user" 
            :profile="profile"
          />
        </div>

        <!-- Right Column - Suggestions (1/3) -->
        <div class="lg:col-span-1 space-y-6">
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
import UserAboutSection from '@/components/user-profile/UserAboutSection.vue'
import UserSuggestionsWidget from '@/components/user-profile/UserSuggestionsWidget.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// State
const loading = ref(true)
const user = ref(null)
const profile = ref(null)
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

    // Fetch user profile by username
    const response = await api.get(`/auth/enhanced-profile/username/${userIdentifier.value}/`)
    
    // Debug: Log the API response structure
    console.log('UserProfile API response:', response.data)
    
    // The API returns the user data directly, with profile nested inside
    user.value = response.data
    profile.value = response.data.profile
    connections.value = response.data.connections_count || 0
    
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
      }
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