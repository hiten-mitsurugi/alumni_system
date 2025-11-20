<template>
  <div :class="[
    'rounded-lg shadow-lg p-6 transition-colors duration-200',
    themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white'
  ]">
    <h3 :class="[
      'text-lg font-semibold mb-4',
      themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
    ]">People you may know</h3>
    
    <div v-if="loading" class="space-y-4">
      <div v-for="i in 3" :key="i" class="animate-pulse">
        <div class="flex items-center space-x-3">
          <div :class="[
            'w-12 h-12 rounded-full',
            themeStore.isDarkMode ? 'bg-gray-600' : 'bg-gray-300'
          ]"></div>
          <div class="flex-1">
            <div :class="[
              'h-4 rounded w-3/4 mb-2',
              themeStore.isDarkMode ? 'bg-gray-600' : 'bg-gray-300'
            ]"></div>
            <div :class="[
              'h-3 rounded w-1/2',
              themeStore.isDarkMode ? 'bg-gray-600' : 'bg-gray-300'
            ]"></div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="suggestions.length > 0" class="space-y-4">
      <div 
        v-for="person in suggestions" 
        :key="person.id"
        :class="[
          'flex items-center space-x-3 p-3 rounded-lg transition-colors',
          themeStore.isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50'
        ]"
      >
        <!-- Profile Picture - Clickable -->
        <div 
          @click="viewProfile(person)"
          class="cursor-pointer"
        >
          <img 
            :src="person.profile_picture || '/default-avatar.png'" 
            :alt="`${person.first_name} ${person.last_name}`"
            class="w-12 h-12 rounded-full object-cover hover:ring-2 hover:ring-green-500 transition-all"
          />
        </div>
        
        <!-- Person Info - Clickable -->
        <div 
          @click="viewProfile(person)"
          class="flex-1 min-w-0 cursor-pointer"
        >
          <p :class="[
            'text-sm font-medium truncate transition-colors',
            themeStore.isDarkMode 
              ? 'text-white hover:text-green-400' 
              : 'text-gray-900 hover:text-green-600'
          ]">
            {{ person.first_name }} {{ person.last_name }}
          </p>
          <p :class="[
            'text-xs truncate',
            themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
          ]">
            {{ person.profile?.headline || person.profile?.present_occupation || 'Alumni' }}
          </p>
          <p v-if="person.mutual_connections > 0" :class="[
            'text-xs',
            themeStore.isDarkMode ? 'text-gray-500' : 'text-gray-400'
          ]">
            {{ person.mutual_connections }} mutual connection{{ person.mutual_connections !== 1 ? 's' : '' }}
          </p>
        </div>
        
        <!-- Connect Button -->
        <button 
          @click.stop="connect(person)"
          :disabled="person.connecting"
          class="px-3 py-1 text-xs bg-orange-600 text-white rounded-full hover:bg-orange-700 transition-colors disabled:opacity-50"
        >
          <span v-if="person.connecting" class="animate-spin mr-1">⟳</span>
          Connect
        </button>
      </div>
      
      <!-- View All Button -->
      <div :class="[
        'pt-3 border-t',
        themeStore.isDarkMode ? 'border-gray-700' : 'border-gray-200'
      ]">
        <router-link 
          to="/alumni/network/suggestions"
          :class="[
            'block text-center text-sm font-medium',
            themeStore.isDarkMode 
              ? 'text-orange-400 hover:text-orange-300' 
              : 'text-orange-600 hover:text-orange-700'
          ]"
        >
          View all suggestions
        </router-link>
      </div>
    </div>

    <div v-else class="text-center py-6">
      <svg :class="[
        'w-12 h-12 mx-auto mb-3',
        themeStore.isDarkMode ? 'text-gray-500' : 'text-gray-400'
      ]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
      </svg>
      <p :class="[
        'text-sm',
        themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
      ]">No suggestions available</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import api from '@/services/api'

const emit = defineEmits(['connect'])
const router = useRouter()
const themeStore = useThemeStore()

const loading = ref(true)
const suggestions = ref([])

const fetchSuggestions = async () => {
  try {
    loading.value = true
    const response = await api.get('/auth/suggested-connections/')
    suggestions.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Error fetching suggestions:', error)
    suggestions.value = []
  } finally {
    loading.value = false
  }
}

const viewProfile = (person) => {
  // Debug: Log the person data
  console.log('Clicked person data:', person)
  
  // Use the person's username for clean URLs
  console.log('Navigating to username:', person.username)
  
  // Navigate to the person's profile using their username
  router.push({
    name: 'AlumniProfile',
    params: { userIdentifier: person.username }
  })
}

const connect = async (person) => {
  try {
    person.connecting = true
    
    // Try the follow endpoint
    await api.post(`/auth/follow/${person.id}/`)
    
    // Remove from suggestions after successful connection
    suggestions.value = suggestions.value.filter(p => p.id !== person.id)
    
    emit('connect', person.id)
  } catch (error) {
    console.error('Error connecting:', error)
    
    // Show user-friendly error message
    let errorMessage = 'Failed to connect. Please try again.'
    
    if (error.response?.status === 500) {
      errorMessage = 'Server error. The connection feature may not be fully configured yet.'
    } else if (error.response?.status === 404) {
      errorMessage = 'User not found or connection endpoint not available.'
    } else if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail
    }
    
    alert(errorMessage)
  } finally {
    person.connecting = false
  }
}

onMounted(() => {
  fetchSuggestions()
})
</script>
