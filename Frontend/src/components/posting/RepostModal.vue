<template>
  <div v-if="isVisible" 
       class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
       @click="closeModal">
    <div
      class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto"
      @click.stop
    >
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
          Repost to your profile
        </h3>
        <button 
          @click="closeModal"
          class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Original Post Preview -->
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
          <div class="flex items-center space-x-3 mb-2">
            <img 
              :src="originalPost.user?.profile_picture || '/default-avatar.png'" 
              :alt="originalPost.user?.first_name"
              class="w-8 h-8 rounded-full object-cover"
            />
            <div>
              <p class="font-medium text-sm text-gray-900 dark:text-white">
                {{ originalPost.user?.first_name }} {{ originalPost.user?.last_name }}
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                {{ formatTimeAgo(originalPost.created_at) }}
              </p>
            </div>
          </div>
          <p class="text-sm text-gray-800 dark:text-gray-200 line-clamp-3">
            {{ originalPost.content }}
          </p>
        </div>
      </div>

      <!-- Repost Form -->
      <div class="p-4">
        <!-- Optional Text -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Add your thoughts (optional)
          </label>
          <textarea
            v-model="repostText"
            rows="3"
            placeholder="What do you think about this post?"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 dark:bg-gray-700 dark:text-white resize-none"
            :maxlength="280"
          ></textarea>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 text-right">
            {{ repostText.length }}/280
          </p>
        </div>

        <!-- Privacy Selection -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Who can see this repost?
          </label>
          <div class="space-y-2">
            <label v-for="option in privacyOptions" 
                   :key="option.value"
                   class="flex items-center space-x-3 cursor-pointer">
              <input
                type="radio"
                :value="option.value"
                v-model="selectedVisibility"
                class="h-4 w-4 text-orange-500 focus:ring-orange-500 border-gray-300 dark:border-gray-600"
              />
              <div class="flex items-center space-x-2">
                <svg v-if="option.value === 'public'" class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-18 0m18 0a9 9 0 00-18 0m18 0H3m18 0v0a9 9 0 00-9 9 9 9 0 01-9-9m18 0V9a9 9 0 00-9-9 9 9 0 01-9 9"></path>
                </svg>
                <svg v-else-if="option.value === 'alumni_only'" class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-2.25"></path>
                </svg>
                <svg v-else class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                </svg>
                <div>
                  <p class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ option.label }}
                  </p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">
                    {{ option.description }}
                  </p>
                </div>
              </div>
            </label>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex space-x-3">
          <button
            @click="closeModal"
            class="flex-1 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="handleRepost"
            :disabled="isLoading"
            class="flex-1 px-4 py-2 text-sm font-medium text-white bg-orange-500 border border-transparent rounded-md hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          >
            <svg v-if="isLoading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isLoading ? 'Reposting...' : 'Repost' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { postsService } from '@/services/postsService'

// Props
const props = defineProps({
  isVisible: {
    type: Boolean,
    required: true
  },
  originalPost: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['close', 'reposted'])

// State
const repostText = ref('')
const selectedVisibility = ref('public')
const isLoading = ref(false)

// Privacy options
const privacyOptions = [
  {
    value: 'public',
    label: 'Public',
    description: 'Anyone can see this repost'
  },
  {
    value: 'alumni_only',
    label: 'Alumni Only',
    description: 'Only alumni members can see this'
  },
  {
    value: 'admin_only',
    label: 'Only Me',
    description: 'Only you can see this repost'
  }
]

// Methods
const closeModal = () => {
  repostText.value = ''
  selectedVisibility.value = 'public'
  emit('close')
}

const handleRepost = async () => {
  if (isLoading.value) return
  
  try {
    isLoading.value = true
    
    const response = await postsService.repostPost(
      props.originalPost.id,
      repostText.value,
      selectedVisibility.value
    )
    
    emit('reposted', {
      originalPost: props.originalPost,
      repost: response.repost,
      visibility: selectedVisibility.value,
      message: response.message
    })
    
    closeModal()
  } catch (error) {
    console.error('Error reposting:', error)
    // You can add a toast notification here
    alert(error.response?.data?.error || 'Failed to repost. Please try again.')
  } finally {
    isLoading.value = false
  }
}

const formatTimeAgo = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`
  return date.toLocaleDateString()
}
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>