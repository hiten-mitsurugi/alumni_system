<template>
  <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
    <!-- Cover Photo -->
    <div class="h-16 bg-gradient-to-r from-green-500 to-green-600 relative">
      <img 
        v-if="user.cover_photo" 
        :src="user.cover_photo" 
        alt="Cover" 
        class="w-full h-full object-cover"
      >
    </div>
    
    <!-- Profile Section -->
    <div class="px-4 pb-4 relative">
      <!-- Profile Picture -->
      <div class="relative -mt-8 mb-4">
        <img 
          :src="user.profile_picture || '/default-avatar.png'" 
          :alt="user.full_name"
          class="w-16 h-16 rounded-full border-4 border-white object-cover mx-auto shadow-lg"
        >
      </div>
      
      <!-- User Info -->
      <div class="text-center">
        <h2 class="text-lg font-bold text-gray-900 mb-1">{{ user.full_name }}</h2>
        <p class="text-sm text-gray-600 mb-2">{{ user.title || 'Alumni Member' }}</p>
        <p class="text-xs text-gray-500 mb-3">{{ user.location || 'Location not specified' }}</p>
      </div>
      
      <!-- Stats -->
      <div class="border-t border-gray-100 pt-3">
        <div class="flex justify-between text-center">
          <div class="flex-1">
            <p class="text-sm font-semibold text-gray-900">{{ user.connections_count || 0 }}</p>
            <p class="text-xs text-gray-500">Connections</p>
          </div>
          <div class="flex-1 border-l border-gray-100">
            <p class="text-sm font-semibold text-gray-900">{{ user.posts_count || 0 }}</p>
            <p class="text-xs text-gray-500">Posts</p>
          </div>
        </div>
      </div>
      
      <!-- Action Buttons -->
      <div class="mt-4 space-y-2">
        <button
          @click="$emit('edit-profile')"
          class="w-full px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        >
          Edit Profile
        </button>
        <button
          @click="$emit('view-profile')"
          class="w-full px-3 py-2 text-sm font-medium text-green-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
        >
          View Profile
        </button>
      </div>
      
      <!-- Quick Links -->
      <div class="mt-4 pt-3 border-t border-gray-100">
        <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Quick Links</h4>
        <div class="space-y-1">
          <a href="#" class="flex items-center text-sm text-gray-600 hover:text-green-600 transition-colors">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            My Network
          </a>
          <a href="#" class="flex items-center text-sm text-gray-600 hover:text-green-600 transition-colors">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Analytics
          </a>
          <a href="#" class="flex items-center text-sm text-gray-600 hover:text-green-600 transition-colors">
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
import api from '@/services/api'

const authStore = useAuthStore()

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

  return {
    full_name: fullName || 'Alumni Member',
    profile_picture: profilePictureUrl,
    cover_photo: profileData.value?.cover_photo || null,
    title: profileData.value?.headline || profileData.value?.present_occupation || 'Alumni Member',
    location: profileData.value?.location || profileData.value?.present_address || 'Location not specified',
    connections_count: profileData.value?.connections_count || 0,
    posts_count: 0 // Will be updated if needed
  }
})

// Methods
const fetchUserData = async () => {
  try {
    loading.value = true
    
    // Try enhanced profile first, fallback to basic user endpoint
    try {
      const response = await api.get('/enhanced-profile/')
      const data = response.data
      userData.value = data
      profileData.value = data.profile
    } catch (enhancedError) {
      console.log('Enhanced profile failed, using basic user endpoint:', enhancedError.message)
      // Fallback to basic user endpoint that works
      const response = await api.get('/user/')
      userData.value = response.data
      profileData.value = response.data.profile || null
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
const emit = defineEmits(['edit-profile', 'view-profile'])

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
