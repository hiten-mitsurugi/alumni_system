<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-4xl mx-auto">
      <!-- Page Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">People you may know</h1>
            <p class="text-gray-600 mt-2">Connect with fellow alumni and expand your network</p>
          </div>
          <router-link 
            to="/alumni/my-profile"
            class="text-green-600 hover:text-green-700 font-medium"
          >
            ← Back to Profile
          </router-link>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="i in 6" :key="i" class="bg-white rounded-lg shadow-lg p-6 animate-pulse">
          <div class="flex flex-col items-center">
            <div class="w-20 h-20 bg-gray-300 rounded-full mb-4"></div>
            <div class="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
            <div class="h-3 bg-gray-300 rounded w-1/2 mb-4"></div>
            <div class="h-8 bg-gray-300 rounded w-20"></div>
          </div>
        </div>
      </div>

      <!-- Suggestions Grid -->
      <div v-else-if="suggestions.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="person in suggestions" 
          :key="person.id"
          class="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow"
        >
          <div class="flex flex-col items-center text-center">
            <!-- Profile Picture -->
            <div 
              @click="viewProfile(person)"
              class="cursor-pointer mb-4"
            >
              <img 
                :src="person.profile_picture || '/default-avatar.png'" 
                :alt="`${person.first_name} ${person.last_name}`"
                class="w-20 h-20 rounded-full object-cover hover:ring-4 hover:ring-green-500 transition-all"
              />
            </div>
            
            <!-- Person Info -->
            <div 
              @click="viewProfile(person)"
              class="cursor-pointer mb-4"
            >
              <h3 class="text-lg font-semibold text-gray-900 hover:text-green-600 transition-colors">
                {{ person.first_name }} {{ person.last_name }}
              </h3>
              <p class="text-sm text-gray-600 mb-2">
                {{ person.profile?.headline || person.profile?.present_occupation || 'Alumni' }}
              </p>
              <p v-if="person.profile?.location" class="text-xs text-gray-500 mb-2">
                📍 {{ person.profile.location }}
              </p>
              <p v-if="person.mutual_connections > 0" class="text-xs text-gray-500">
                {{ person.mutual_connections }} mutual connection{{ person.mutual_connections !== 1 ? 's' : '' }}
              </p>
            </div>
            
            <!-- Action Buttons -->
            <div class="flex space-x-2 w-full">
              <button 
                @click="connect(person)"
                :disabled="person.connecting"
                class="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 text-sm font-medium"
              >
                <span v-if="person.connecting" class="animate-spin mr-2">⟳</span>
                Connect
              </button>
              <button 
                @click="viewProfile(person)"
                class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
              >
                View
              </button>
            </div>

            <!-- Additional Info -->
            <div v-if="person.profile?.program_graduated" class="mt-3 text-xs text-gray-500">
              {{ person.profile.program_graduated }} • Class of {{ person.profile.graduation_year }}
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <svg class="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
        </svg>
        <h3 class="text-lg font-medium text-gray-900 mb-2">No suggestions available</h3>
        <p class="text-gray-600">Check back later for new connection suggestions.</p>
      </div>

      <!-- Load More Button -->
      <div v-if="hasMore && !loading" class="text-center mt-8">
        <button 
          @click="loadMore"
          :disabled="loadingMore"
          class="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
        >
          <span v-if="loadingMore" class="animate-spin mr-2">⟳</span>
          Load More
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()

const loading = ref(true)
const loadingMore = ref(false)
const suggestions = ref([])
const hasMore = ref(true)
const currentPage = ref(1)

const fetchSuggestions = async (page = 1) => {
  try {
    if (page === 1) {
      loading.value = true
    } else {
      loadingMore.value = true
    }
    
    const response = await api.get(`/suggested-connections/?page=${page}`)
    const data = response.data
    
    if (page === 1) {
      suggestions.value = data.results || data || []
    } else {
      suggestions.value = [...suggestions.value, ...(data.results || data || [])]
    }
    
    hasMore.value = !!data.next
    currentPage.value = page
  } catch (error) {
    console.error('Error fetching suggestions:', error)
    if (page === 1) {
      suggestions.value = []
    }
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const viewProfile = (person) => {
  router.push({
    name: 'AlumniProfile',
    params: { userId: person.id }
  })
}

const connect = async (person) => {
  try {
    person.connecting = true
    
    await api.post(`/follow/${person.id}/`)
    
    // Remove from suggestions after successful connection
    suggestions.value = suggestions.value.filter(p => p.id !== person.id)
  } catch (error) {
    console.error('Error connecting:', error)
    // Show error message to user
    alert('Failed to connect. Please try again.')
  } finally {
    person.connecting = false
  }
}

const loadMore = () => {
  fetchSuggestions(currentPage.value + 1)
}

onMounted(() => {
  fetchSuggestions()
})
</script>
