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
            ]">{{ user.connections_count || 0 }}</p>
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
            ]">{{ user.posts_count || 0 }}</p>
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
          @click="$emit('edit-profile')"
          :class="[
            'w-full px-3 py-2 text-sm font-medium transition-colors rounded-lg',
            themeStore.isDarkMode 
              ? 'text-gray-300 bg-gray-700 hover:bg-gray-600' 
              : 'text-gray-700 bg-gray-100 hover:bg-gray-200'
          ]"
        >
          Edit Profile
        </button>
        <button
          @click="$emit('view-profile')"
          :class="[
            'w-full px-3 py-2 text-sm font-medium transition-colors rounded-lg',
            themeStore.isDarkMode 
              ? 'text-green-400 bg-gray-700 hover:bg-gray-600' 
              : 'text-green-600 bg-blue-50 hover:bg-blue-100'
          ]"
        >
          View Profile
        </button>
      </div>

      <!-- Quick Links -->
      <div :class="[
        'pt-3 mt-4 border-t',
        themeStore.isDarkMode ? 'border-gray-700' : 'border-gray-100'
      ]">
        <h4 :class="[
          'mb-2 text-xs font-semibold tracking-wider uppercase',
          themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
        ]">Quick Links</h4>
        <div class="space-y-1">
          <a href="#" :class="[
            'flex items-center text-sm transition-colors',
            themeStore.isDarkMode 
              ? 'text-gray-300 hover:text-green-400' 
              : 'text-gray-600 hover:text-green-600'
          ]">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            My Network
          </a>
          <a href="#" :class="[
            'flex items-center text-sm transition-colors',
            themeStore.isDarkMode 
              ? 'text-gray-300 hover:text-green-400' 
              : 'text-gray-600 hover:text-green-600'
          ]">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Analytics
          </a>
          <a href="#" :class="[
            'flex items-center text-sm transition-colors',
            themeStore.isDarkMode 
              ? 'text-gray-300 hover:text-green-400' 
              : 'text-gray-600 hover:text-green-600'
          ]">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3a4 4 0 118 0v4m-4 8l2-2m0 0l2-2m-2 2l-2-2m2 2v4" />
            </svg>
            Events
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import api from '@/services/api'

const authStore = useAuthStore()
const themeStore = useThemeStore()

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

  // Construct profile picture URL like in navbar
  const pic = userData.value.profile_picture
  const profilePictureUrl = pic
    ? (pic.startsWith('http') ? pic : `http://127.0.0.1:8000${pic}`)
    : '/default-avatar.png'

  // Construct cover photo URL similarly
  const coverPic = profileData.value?.cover_photo
  const coverPhotoUrl = coverPic
    ? (coverPic.startsWith('http') ? coverPic : `http://127.0.0.1:8000${coverPic}`)
    : null

  return {
    full_name: fullName || 'Alumni Member',
    profile_picture: profilePictureUrl,
    cover_photo: coverPhotoUrl,
    title: profileData.value?.headline || profileData.value?.present_occupation || 'Alumni Member',
    location: profileData.value?.location || profileData.value?.present_address || 'Location not specified',
    connections_count: profileData.value?.connections_count || 0,
    posts_count: 0 // Will be updated if needed
  }
})

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

  } catch (error) {
    console.error('Error fetching user data:', error)
    // Final fallback to auth store data
    userData.value = authStore.user
    profileData.value = null
  } finally {
    loading.value = false
  }
}

// Emits
defineEmits(['edit-profile', 'view-profile'])

// Lifecycle
onMounted(() => {
  fetchUserData()
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
