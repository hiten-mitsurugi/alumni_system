<template>
  <div :class="[
    'overflow-hidden transition-colors duration-200 border shadow-sm rounded-xl',
    themeStore.isDarkMode 
      ? 'bg-gray-800 border-gray-700' 
      : 'bg-white border-gray-200'
  ]">
    <!-- Cover Photo -->
    <div class="relative h-16 bg-gradient-to-r from-green-500 to-green-600">
      <img
        v-if="user.cover_photo"
        :src="user.cover_photo"
        alt="Cover"
        class="object-cover w-full h-full"
        @error="handleCoverPhotoError"
      >
    </div>

    <!-- Profile Section -->
    <div class="relative px-4 pb-4">
      <!-- Profile Picture -->
      <div class="relative mb-4 -mt-8">
        <img
          :src="user.profile_picture || '/default-avatar.png'"
          :alt="user.full_name"
          :class="[
            'object-cover w-16 h-16 mx-auto border-4 rounded-full shadow-lg',
            themeStore.isDarkMode ? 'border-gray-800' : 'border-white'
          ]"
        >
      </div>

      <!-- User Info -->
      <div class="text-center">
        <h2 :class="[
          'mb-1 text-lg font-bold',
          themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
        ]">{{ user.full_name }}</h2>
        <p :class="[
          'mb-2 text-sm',
          themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
        ]">{{ user.title || 'Alumni Member' }}</p>
        <p :class="[
          'mb-3 text-xs',
          themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
        ]">{{ user.location || 'Location not specified' }}</p>
      </div>

      <!-- Stats -->
      <div :class="[
        'pt-3 border-t',
        themeStore.isDarkMode ? 'border-gray-700' : 'border-gray-100'
      ]">
        <div class="flex justify-between text-center">
          <div class="flex-1">
            <p :class="[
              'text-sm font-semibold',
              themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
            ]">{{ user.connections_count }}</p>
            <p :class="[
              'text-xs',
              themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
            ]">Connections</p>
          </div>
          <div :class="[
            'flex-1 border-l',
            themeStore.isDarkMode ? 'border-gray-700' : 'border-gray-100'
          ]">
            <p :class="[
              'text-sm font-semibold',
              themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
            ]">{{ user.posts_count }}</p>
            <p :class="[
              'text-xs',
              themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
            ]">Posts</p>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="mt-4 space-y-2">
        <button
          @click="goToMyProfile"
          :class="[
            'w-full px-3 py-2 text-sm font-medium transition-colors rounded-lg',
            themeStore.isDarkMode 
              ? 'text-white bg-gray-700 hover:bg-gray-600' 
              : 'text-orange-700 bg-orange-100 hover:bg-orange-200'
          ]"
        >
          Edit Profile
        </button>
        <button
          @click="goToMyProfile"
          :class="[
            'w-full px-3 py-2 text-sm font-medium transition-colors rounded-lg',
            themeStore.isDarkMode 
              ? 'text-white bg-gray-700 hover:bg-gray-600' 
              : 'text-orange-700 bg-orange-100 hover:bg-orange-200'
          ]"
        >
          View Profile
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { getProfilePictureUrl, getCoverPhotoUrl } from '@/utils/imageUrl'
import api from '@/services/api'

const authStore = useAuthStore()
const themeStore = useThemeStore()
const router = useRouter()

// Reactive data
const loading = ref(true)
const userData = ref(null)
const profileData = ref(null)

// Computed user object that matches the template expectations
const user = computed(() => {
  if (!userData.value) {
    return {
      full_name: 'Loading...',
      profile_picture: '/default-avatar.png',
      cover_photo: null,
      title: 'Alumni Member',
      location: 'Location not specified',
      connections_count: 0,
      posts_count: 0
    }
  }

  // Build full name from individual name fields
  const firstName = userData.value.first_name || ''
  const middleName = userData.value.middle_name || ''
  const lastName = userData.value.last_name || ''
  const fullName = [firstName, middleName, lastName].filter(Boolean).join(' ')

  // Get profile picture and cover photo URLs using utility
  const profilePictureUrl = getProfilePictureUrl(userData.value.profile_picture)
  const coverPhotoUrl = getCoverPhotoUrl(profileData.value?.cover_photo)

  return {
    full_name: fullName || 'Alumni Member',
    profile_picture: profilePictureUrl,
    cover_photo: coverPhotoUrl,
    title: profileData.value?.headline || profileData.value?.present_occupation || 'Alumni Member',
    location: profileData.value?.location || profileData.value?.present_address || 'Location not specified',
    connections_count: userStats.value?.connections_count || profileData.value?.connections_count || 0,
    posts_count: userStats.value?.posts_count || profileData.value?.posts_count || 0
  }
})

// Add reactive stats data
const userStats = ref({ posts_count: 0, connections_count: 0 })

// Methods
const handleCoverPhotoError = (event) => {
  console.warn('Cover photo failed to load:', event.target.src)
  // Hide the image on error by setting its style to display: none
  event.target.style.display = 'none'
}

const fetchUserData = async () => {
  try {
    loading.value = true

    // Use auth store data directly for consistency and real-time updates
    userData.value = authStore.user
    profileData.value = authStore.user?.profile || null

    // If no user in store, try to fetch it
    if (!userData.value) {
      try {
        const response = await api.get('/auth/enhanced-profile/')
        const data = response.data
        userData.value = data
        profileData.value = data.profile
        // Update auth store with fresh data
        authStore.setUser(data)
      } catch (enhancedError) {
        console.log('Enhanced profile failed, using basic user endpoint:', enhancedError.message)
        // Fallback to basic user endpoint that works
        const response = await api.get('/auth/user/')
        userData.value = response.data
        profileData.value = response.data.profile || null
        // Update auth store with fresh data
        authStore.setUser(response.data)
      }
    }

    // Fetch real-time statistics
    await fetchUserStats()

  } catch (error) {
    console.error('Error fetching user data:', error)
    // Final fallback to auth store data
    userData.value = authStore.user
    profileData.value = null
  } finally {
    loading.value = false
  }
}

// New method to fetch user statistics
const fetchUserStats = async () => {
  try {
    console.log('🔍 ProfileCard: Fetching user statistics...')
    
    // Fetch enhanced profile to get connections count
    const enhancedResponse = await api.get('/auth/enhanced-profile/')
    console.log('🔍 Enhanced profile response:', enhancedResponse.data)
    
    const connections_count = enhancedResponse.data.profile?.connections_count || 0
    console.log('🔍 Connections count:', connections_count)
    
    // Get posts count from enhanced profile if available, otherwise try posts endpoint
    let posts_count = enhancedResponse.data.profile?.posts_count || 0
    console.log('🔍 Posts count from enhanced profile:', posts_count)
    
    // If no posts count from enhanced profile, try posts endpoint
    if (posts_count === 0) {
      try {
        const postsResponse = await api.get('/posts/')
        console.log('🔍 Posts endpoint response:', postsResponse.data)
        
        if (Array.isArray(postsResponse.data)) {
          // Filter posts by current user
          const userPosts = postsResponse.data.filter(post => post.user?.id === authStore.user?.id)
          posts_count = userPosts.length
        } else if (postsResponse.data.results) {
          // Paginated response
          const userPosts = postsResponse.data.results.filter(post => post.user?.id === authStore.user?.id)
          posts_count = userPosts.length
        }
        console.log('🔍 Calculated posts count:', posts_count)
      } catch (postsError) {
        console.warn('Could not fetch posts count:', postsError.message)
      }
    }
    
    // Update stats
    userStats.value = {
      connections_count,
      posts_count
    }
    
    console.log('🔍 Final userStats:', userStats.value)
    
    // Also update profile data if it exists
    if (profileData.value) {
      profileData.value.connections_count = connections_count
      profileData.value.posts_count = posts_count
    }
    
  } catch (error) {
    console.error('Error fetching user stats:', error)
  }
}

// Emits
// No emits needed - both buttons navigate directly

// Go to current user's profile
const goToMyProfile = () => {
  router.push({ name: 'AlumniMyProfile' })
}

// Lifecycle
onMounted(() => {
  fetchUserData()
})

// Watch auth store for user changes to update ProfileCard in real-time
watch(
  () => authStore.user,
  (newUser) => {
    if (newUser) {
      userData.value = newUser
      profileData.value = newUser.profile || null
      console.log('📱 ProfileCard: Auth store updated, refreshing user data')
    }
  },
  { deep: true, immediate: true }
)

// Method to refresh stats (can be called when posts are added/deleted)
const refreshStats = async () => {
  await fetchUserStats()
}

// Export the refresh method so parent components can call it
defineExpose({
  refreshStats
})
</script>

<style scoped>
/* Gradient backgrounds */
.bg-gradient-to-r {
  background-image: linear-gradient(to right, var(--tw-gradient-stops));
}

/* Shadow effects */
.shadow-lg {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.shadow-sm {
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

/* Smooth transitions */
.transition-colors {
  transition: all 0.2s ease;
}

/* Better hover effects */
@media (hover: hover) {
  .hover\:bg-gray-200:hover {
    background-color: #e5e7eb;
  }

  .hover\:bg-blue-100:hover {
    background-color: #dbeafe;
  }

  .hover\:text-blue-600:hover {
    color: #2563eb;
  }
}

/* Mobile optimizations */
@media (max-width: 768px) {
  /* Touch-friendly buttons */
  button, a {
    min-height: 44px;
    display: flex;
    align-items: center;
  }

  /* Compact spacing */
  .space-y-1 > :not([hidden]) ~ :not([hidden]) {
    margin-top: 0.25rem;
  }

  .space-y-2 > :not([hidden]) ~ :not([hidden]) {
    margin-top: 0.5rem;
  }
}

/* Profile picture positioning */
.relative {
  position: relative;
}

.-mt-8 {
  margin-top: -2rem;
}

/* Border styling */
.border-4 {
  border-width: 4px;
}

.border-white {
  border-color: #ffffff;
}

/* Text styling */
.uppercase {
  text-transform: uppercase;
}

.tracking-wider {
  letter-spacing: 0.05em;
}

/* Flexbox utilities */
.flex-1 {
  flex: 1 1 0%;
}

/* Object fit */
.object-cover {
  object-fit: cover;
}
</style>
