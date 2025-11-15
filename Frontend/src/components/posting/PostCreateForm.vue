<template>
  <div
    :class="themeStore.isDarkMode ? 'bg-gray-900 border border-gray-800 rounded-lg md:rounded-xl lg:rounded-2xl shadow-md md:shadow-lg mb-4 md:mb-6 overflow-hidden' : 'bg-white border border-gray-100 rounded-lg md:rounded-xl lg:rounded-2xl shadow-md md:shadow-lg mb-4 md:mb-6 overflow-hidden'">
    <div :class="themeStore.isDarkMode ? 'bg-gray-800 border-b border-gray-700 px-3 md:px-4 lg:px-6 py-3 md:py-4' : 'bg-white border-b border-gray-100 px-3 md:px-4 lg:px-6 py-3 md:py-4'">
      <h2 :class="themeStore.isDarkMode ? 'text-base md:text-lg font-bold text-gray-100 flex items-center' : 'text-base md:text-lg font-bold text-gray-900 flex items-center'">
        <svg :class="themeStore.isDarkMode ? 'w-5 h-5 md:w-6 md:h-6 mr-2 text-gray-100' : 'w-5 h-5 md:w-6 md:h-6 mr-2 text-gray-900'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
        </svg>
        <span class="hidden sm:inline">Share Your Thoughts</span>
        <span class="sm:hidden">Share</span>
      </h2>
      <p :class="themeStore.isDarkMode ? 'text-gray-300 text-xs md:text-sm mt-1 hidden md:block' : 'text-gray-600 text-xs md:text-sm mt-1 hidden md:block'">Connect with your fellow alumni and share what's
        on your mind</p>
    </div>

    <div class="p-3 md:p-4 lg:p-6">
      <div class="flex items-start space-x-2 md:space-x-3 lg:space-x-4">
        <img :src="getProfilePictureUrl(userProfilePicture) || '/default-avatar.png'" alt="Your Profile"
          class="w-8 h-8 md:w-10 md:h-10 lg:w-12 lg:h-12 rounded-full object-cover border-2 border-gray-100 shadow-md flex-shrink-0" />
        <div class="flex-1 min-w-0">
          <!-- Title Input -->
          <input v-model="localTitle" type="text" placeholder="Add a title (optional)..."
            :class="themeStore.isDarkMode ? 'w-full p-2 md:p-3 text-sm md:text-base border border-gray-600 bg-gray-700 text-gray-100 placeholder-gray-400 rounded-lg md:rounded-xl mb-2 md:mb-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 shadow-sm' : 'w-full p-2 md:p-3 text-sm md:text-base border border-slate-300 rounded-lg md:rounded-xl mb-2 md:mb-3 focus:ring-2 focus:ring-blue-300 focus:border-blue-500 shadow-sm'" />

          <!-- Content with Mention Support -->
          <MentionTextarea
            v-model="localContent"
            @mention="handleMention"
            :placeholder="'What would you like to share? Use @ to mention alumni...'"
            :rows="3"
            :class="[
              'mb-3',
              themeStore.isDarkMode 
                ? 'bg-gray-700 border-gray-600' 
                : 'bg-white border-slate-300'
            ]"
          />

          <!-- Mentioned users display -->
          <div v-if="mentionedUsers.length > 0" class="mb-3">
            <p class="text-xs md:text-sm font-medium mb-2" :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
              Mentioning:
            </p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="user in mentionedUsers"
                :key="user.id"
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
              >
                @{{ user.username }}
              </span>
            </div>
          </div>

          <!-- File Preview -->
          <div v-if="selectedFiles.length > 0" class="mt-3 md:mt-4">
            <div class="flex items-center justify-between mb-2 md:mb-3">
              <h4 class="text-xs md:text-sm font-semibold text-slate-700">
                📎 {{ selectedFiles.length }} file{{ selectedFiles.length > 1 ? 's' : '' }} selected
              </h4>
              <button @click="clearAllFiles"
                class="text-red-700 hover:text-white hover:bg-red-700 border border-red-700 bg-white px-2 py-1 rounded font-medium text-xs transition-all duration-300">
                Clear all
              </button>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 md:gap-3">
              <div v-for="(file, index) in selectedFiles" :key="index"
                class="relative group bg-white rounded-lg shadow-md border border-slate-200 overflow-hidden hover:shadow-lg transition-all duration-300">
                <!-- Image preview -->
                <div v-if="file.type.startsWith('image/') && filePreviewUrls[index]" class="aspect-square">
                  <img :src="filePreviewUrls[index]" :alt="file.name" class="w-full h-full object-cover" />
                </div>

                <!-- Video preview -->
                <div v-else-if="file.type.startsWith('video/')"
                  class="aspect-square bg-slate-900 flex items-center justify-center">
                  <svg class="w-12 h-12 text-black" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                </div>

                <!-- Other file types -->
                <div v-else
                  class="aspect-square bg-gradient-to-br from-orange-100 to-purple-100 flex flex-col items-center justify-center p-2">
                  <svg class="w-8 h-8 text-slate-500 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  <span class="text-xs text-slate-600 font-medium">{{ file.type.split('/')[1]?.toUpperCase() || 'FILE'
                    }}</span>
                </div>

                <!-- File info overlay -->
                <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2">
                  <p class="text-black text-xs font-medium truncate">{{ file.name }}</p>
                  <p class="text-black/70 text-xs">{{ formatFileSize(file.size) }}</p>
                </div>

                <!-- Remove button -->
                <button @click="removeFile(index)"
                  class="absolute -top-1 -right-1 bg-red-700 hover:bg-red-800 active:bg-red-900 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300 shadow-md text-xs font-bold z-10 border border-red-800">
                  ×
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Post Actions -->
      <div
        class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-0 mt-4 md:mt-6 pt-3 md:pt-4 border-t border-slate-200">
        <div class="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-3 lg:gap-4">
          <!-- File Upload -->
          <label
            :class="['flex items-center space-x-2 cursor-pointer border-2 px-2 md:px-3 py-2 rounded-lg md:rounded-xl transition-all duration-300 shadow-sm text-xs md:text-sm w-full sm:w-auto justify-center sm:justify-start', isDark ? 'text-gray-300 hover:text-white border-gray-600 bg-gray-700 hover:bg-gray-600' : 'text-orange-600 hover:text-white border-orange-600 bg-white hover:bg-orange-600']">
            <svg class="w-4 h-4 md:w-5 md:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span class="font-medium">
              <span class="hidden sm:inline">📷</span>
              {{ selectedFiles.length > 0 ? `${selectedFiles.length} file${selectedFiles.length > 1 ? 's' : ''}` : 'Add Media' }}
            </span>
            <input type="file" multiple accept="image/*,video/*" @change="handleFileSelect" class="hidden" />
          </label>

          <!-- Category Selector -->
          <select v-model="localCategory"
            :class="['text-xs md:text-sm font-medium border-2 rounded-lg md:rounded-xl px-2 md:px-3 py-2 shadow-sm w-full sm:w-auto transition-all duration-300', isDark ? 'border-gray-600 bg-gray-700 hover:bg-gray-600 hover:text-white text-gray-300 focus:ring-2 focus:ring-gray-500 focus:border-gray-500' : 'border-orange-600 bg-white hover:bg-orange-600 hover:text-white text-orange-600 focus:ring-2 focus:ring-orange-600 focus:border-orange-600']">
            <option v-for="cat in categories.slice(1)" :key="cat.value" :value="cat.value">
              {{ cat.label }}
            </option>
          </select>
        </div>
        <button @click="createPost" :disabled="!localContent.trim() || isPosting" :class="[
          'px-4 md:px-6 py-2 rounded-lg md:rounded-xl font-medium text-sm md:text-base transition-all duration-300 shadow-md transform w-full sm:w-auto border-2',
          localContent.trim() && !isPosting
            ? (isDark ? 'border-gray-600 bg-gray-700 text-gray-300 hover:bg-gray-600 hover:text-white active:bg-gray-700 active:border-gray-700 hover:scale-105 hover:shadow-lg' : 'border-orange-600 bg-white text-orange-600 hover:bg-orange-600 hover:text-white active:bg-white active:border-orange-700 hover:scale-105 hover:shadow-lg')
            : 'border-slate-300 bg-slate-100 text-slate-500 cursor-not-allowed'
        ]">
          <span v-if="isPosting" class="flex items-center">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none"
              viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
              </path>
            </svg>
            Sharing...
          </span>

          <span v-else class="flex items-center">
            <!-- rotated rocket-style arrow -->
            <svg class="w-4 h-4 mr-1 transform rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
            Share Post
          </span>
        </button>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import MentionTextarea from '@/components/common/MentionTextarea.vue'
import { extractMentionsForBackend, convertMentionsForStorage } from '@/utils/mentionUtils'

// Theme store
const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isDarkMode || false)

// Props
defineProps({
  userProfilePicture: String,
  categories: {
    type: Array,
    required: true
  },
  isPosting: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['create-post'])

// Local state
const localTitle = ref('')
const localContent = ref('')
const localCategory = ref('discussion')
const selectedFiles = ref([])
const filePreviewUrls = ref([])
const mentionedUsers = ref([])

// Methods
const handleMention = (mentionData) => {
  const existingUser = mentionedUsers.value.find(u => u.id === mentionData.user.id)
  if (!existingUser) {
    mentionedUsers.value.push(mentionData.user)
  }
}
const handleFileSelect = (event) => {
  // Clean up previous URLs
  filePreviewUrls.value.forEach(url => {
    if (url) window.URL.revokeObjectURL(url)
  })
  filePreviewUrls.value = []

  const files = Array.from(event.target.files)
  selectedFiles.value = files

  // Create preview URLs for images
  files.forEach(file => {
    if (file.type.startsWith('image/')) {
      const url = window.URL.createObjectURL(file)
      filePreviewUrls.value.push(url)
    } else {
      filePreviewUrls.value.push(null)
    }
  })
}

const removeFile = (index) => {
  // Clean up the URL for the removed file
  if (filePreviewUrls.value[index]) {
    window.URL.revokeObjectURL(filePreviewUrls.value[index])
  }

  selectedFiles.value.splice(index, 1)
  filePreviewUrls.value.splice(index, 1)
}

const clearAllFiles = () => {
  // Clean up all preview URLs
  filePreviewUrls.value.forEach(url => {
    if (url) window.URL.revokeObjectURL(url)
  })

  selectedFiles.value = []
  filePreviewUrls.value = []
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getProfilePictureUrl = (profilePicture) => {
  if (!profilePicture) return null

  // If already a full URL, return as is
  if (profilePicture.startsWith('http://') || profilePicture.startsWith('https://')) {
    return profilePicture
  }

  // If relative path, prepend base URL
  const BASE_URL = 'http://127.0.0.1:8000'
  return profilePicture.startsWith('/') ? `${BASE_URL}${profilePicture}` : `${BASE_URL}/${profilePicture}`
}

const extractMentions = (content) => {
  // Use the utility function to extract mentions for backend processing
  return extractMentionsForBackend(content, mentionedUsers.value)
}

const createPost = () => {
  if (!localContent.value.trim()) return

  // Convert full name mentions to username mentions for backend storage
  const storageContent = convertMentionsForStorage(localContent.value, mentionedUsers.value)

  const postData = {
    title: localTitle.value,
    content: storageContent, // Send converted content to backend
    category: localCategory.value,
    files: selectedFiles.value,
    mentions: extractMentions(localContent.value) // Extract mentions for backend
  }

  emit('create-post', postData)

  // Don't clear form here - let parent component handle clearing after success
}

const clearForm = () => {
  localTitle.value = ''
  localContent.value = ''
  localCategory.value = 'discussion'
  mentionedUsers.value = []
  clearAllFiles()
}

// Cleanup on unmount
onUnmounted(() => {
  filePreviewUrls.value.forEach(url => {
    if (url) window.URL.revokeObjectURL(url)
  })
})

// Expose clearForm method for parent component
defineExpose({
  clearForm
})
</script>

<style scoped>
/* Focus states for accessibility */
input:focus,
textarea:focus,
select:focus,
button:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Enhanced hover effects */
button:hover:not(:disabled) {
  transform: translateY(-1px);
}

/* Smooth transitions for all interactive elements */
.transition-all {
  transition: all 0.3s ease;
}
</style>