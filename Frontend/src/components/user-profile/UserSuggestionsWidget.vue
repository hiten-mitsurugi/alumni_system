<template>
  <div class="p-6 transition-colors duration-200 bg-white rounded-lg shadow-lg dark:bg-gray-800">
    <h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-white">People you may know</h3>

    <div v-if="loading" class="space-y-4">
      <div v-for="i in 3" :key="i" class="animate-pulse">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-gray-300 rounded-full dark:bg-gray-600"></div>
          <div class="flex-1">
            <div class="w-3/4 h-3 mb-2 bg-gray-300 rounded dark:bg-gray-600"></div>
            <div class="w-1/2 h-2 bg-gray-300 rounded dark:bg-gray-600"></div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="suggestions.length > 0" class="space-y-3">
      <div
        v-for="person in suggestions"
        :key="person.id"
        class="flex items-center p-2 space-x-3 transition-colors rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
      >
        <!-- Profile Picture - Clickable -->
        <div
          @click="viewProfile(person)"
          class="cursor-pointer"
        >
          <img
            :src="person.profile_picture || '/default-avatar.png'"
            :alt="`${person.first_name} ${person.last_name}`"
            class="object-cover w-10 h-10 transition-all rounded-full hover:ring-2 hover:ring-green-500"
          />
        </div>

        <!-- Person Info - Clickable -->
        <div
          @click="viewProfile(person)"
          class="flex-1 min-w-0 cursor-pointer"
        >
          <p class="text-sm font-medium text-gray-900 truncate transition-colors dark:text-white hover:text-green-600 dark:hover:text-green-400">
            {{ person.first_name }} {{ person.last_name }}
          </p>
          <p class="text-xs text-gray-500 truncate dark:text-gray-400">
            {{ person.profile?.headline || person.profile?.present_occupation || 'Alumni' }}
          </p>
        </div>

        <!-- Connect Button -->
        <button
          @click.stop="connect(person)"
          :disabled="person.connecting"
          class="px-2 py-1 text-xs text-white transition-colors bg-green-600 rounded-full hover:bg-green-700 disabled:opacity-50"
        >
          <span v-if="person.connecting" class="mr-1 animate-spin">⟳</span>
          Connect
        </button>
      </div>

      <!-- View All Button -->
      <div class="pt-3 border-t border-gray-200 dark:border-gray-700">
        <router-link
          to="/alumni/network/suggestions"
          class="block text-sm font-medium text-center text-green-600 hover:text-green-700 dark:text-green-400 dark:hover:text-green-300"
        >
          View all suggestions
        </router-link>
      </div>
    </div>

    <div v-else class="py-4 text-center">
      <svg class="w-8 h-8 mx-auto mb-2 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
      </svg>
      <p class="text-sm text-gray-500 dark:text-gray-400">No suggestions available</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const emit = defineEmits(['connect'])
const router = useRouter()

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
  console.log('Clicked person data:', person)
  console.log('Navigating to username:', person.username)

  router.push({
    name: 'AlumniProfile',
    params: { userIdentifier: person.username }
  })
}

const connect = async (person) => {
  try {
    person.connecting = true

    await api.post(`/auth/follow/${person.id}/`)

    suggestions.value = suggestions.value.filter(p => p.id !== person.id)

    emit('connect', person.id)
  } catch (error) {
    console.error('Error connecting:', error)

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
