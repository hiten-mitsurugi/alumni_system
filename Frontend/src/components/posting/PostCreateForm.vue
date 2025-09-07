<template>
  <div class="bg-white rounded-2xl shadow-lg border border-green-100 mb-6 overflow-hidden">
    <div class="bg-gradient-to-r from-green-500 to-green-600 px-6 py-4">
      <h2 class="text-lg font-bold text-white flex items-center">
        <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
        </svg>
        Share Your Thoughts
      </h2>
      <p class="text-green-100 text-sm mt-1">Connect with your fellow alumni and share what's on your mind</p>
    </div>
    
    <div class="p-6">
      <div class="flex items-start space-x-4">
        <img 
          :src="getProfilePictureUrl(userProfilePicture) || '/default-avatar.png'"
          alt="Your Profile"
          class="w-12 h-12 rounded-full object-cover border-2 border-green-200 shadow-md"
        />
        <div class="flex-1">
          <!-- Title Input -->
          <input
            v-model="localTitle"
            type="text"
            placeholder="Add a compelling title (optional)..."
            class="w-full p-3 text-base border border-slate-300 rounded-xl mb-3 focus:ring-2 focus:ring-green-300 focus:border-green-500 shadow-sm"
          />
          
          <!-- Content Textarea -->
          <textarea
            v-model="localContent"
            placeholder="What would you like to share with your alumni community?"
            rows="3"
            class="w-full p-3 text-base border border-slate-300 rounded-xl resize-none focus:ring-2 focus:ring-green-300 focus:border-green-500 shadow-sm"
          ></textarea>
          
          <!-- File Preview -->
          <div v-if="selectedFiles.length > 0" class="mt-4">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-semibold text-slate-700">
                📎 {{ selectedFiles.length }} file{{ selectedFiles.length > 1 ? 's' : '' }} selected
              </h4>
              <button
                @click="clearAllFiles"
                class="text-red-500 hover:text-red-700 font-medium text-xs underline"
              >
                Clear all
              </button>
            </div>
            
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              <div
                v-for="(file, index) in selectedFiles"
                :key="index"
                class="relative group bg-white rounded-lg shadow-md border border-slate-200 overflow-hidden hover:shadow-lg transition-all duration-300"
              >
                <!-- Image preview -->
                <div v-if="file.type.startsWith('image/') && filePreviewUrls[index]" class="aspect-square">
                  <img
                    :src="filePreviewUrls[index]"
                    :alt="file.name"
                    class="w-full h-full object-cover"
                  />
                </div>
                
                <!-- Video preview -->
                <div v-else-if="file.type.startsWith('video/')" class="aspect-square bg-slate-900 flex items-center justify-center">
                  <svg class="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z"/>
                  </svg>
                </div>
                
                <!-- Other file types -->
                <div v-else class="aspect-square bg-gradient-to-br from-green-100 to-purple-100 flex flex-col items-center justify-center p-2">
                  <svg class="w-8 h-8 text-slate-500 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  <span class="text-xs text-slate-600 font-medium">{{ file.type.split('/')[1]?.toUpperCase() || 'FILE' }}</span>
                </div>
                
                <!-- File info overlay -->
                <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2">
                  <p class="text-white text-xs font-medium truncate">{{ file.name }}</p>
                  <p class="text-white/70 text-xs">{{ formatFileSize(file.size) }}</p>
                </div>
                
                <!-- Remove button -->
                <button
                  @click="removeFile(index)"
                  class="absolute -top-1 -right-1 bg-red-500 hover:bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300 shadow-md text-xs font-bold z-10"
                >
                  ×
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Post Actions -->
      <div class="flex items-center justify-between mt-6 pt-4 border-t border-slate-200">
        <div class="flex items-center space-x-4">
          <!-- File Upload -->
          <label class="flex items-center space-x-2 text-slate-700 hover:text-green-700 cursor-pointer bg-slate-100 hover:bg-green-100 px-3 py-2 rounded-xl transition-all duration-300 shadow-sm">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span class="text-sm font-medium">
              📷 {{ selectedFiles.length > 0 ? `${selectedFiles.length} file${selectedFiles.length > 1 ? 's' : ''} selected` : 'Add Photos/Videos' }}
            </span>
            <input
              type="file"
              multiple
              accept="image/*,video/*"
              @change="handleFileSelect"
              class="hidden"
            />
          </label>
          
          <!-- Category Selector -->
          <select
            v-model="localCategory"
            class="text-sm font-medium border border-slate-300 rounded-xl px-3 py-2 focus:ring-2 focus:ring-green-300 focus:border-green-500 bg-white shadow-sm"
          >
            <option v-for="cat in categories.slice(1)" :key="cat.value" :value="cat.value">
              {{ cat.icon }} {{ cat.label }}
            </option>
          </select>
        </div>
        
        <button
          @click="createPost"
          :disabled="!localContent.trim() || isPosting"
          :class="[
            'px-6 py-2 rounded-xl font-medium text-base transition-all duration-300 shadow-md transform',
            localContent.trim() && !isPosting
              ? 'bg-gradient-to-r from-green-600 to-green-700 text-white hover:from-green-700 hover:to-green-800 hover:scale-105 hover:shadow-lg'
              : 'bg-slate-300 text-slate-500 cursor-not-allowed'
          ]"
        >
          <span v-if="isPosting" class="flex items-center">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Sharing...
          </span>
          <span v-else class="flex items-center">
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
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

// Props
const props = defineProps({
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

// Methods
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

const createPost = () => {
  if (!localContent.value.trim()) return
  
  const postData = {
    title: localTitle.value,
    content: localContent.value,
    category: localCategory.value,
    files: selectedFiles.value
  }
  
  emit('create-post', postData)
  
  // Don't clear form here - let parent component handle clearing after success
}

const clearForm = () => {
  localTitle.value = ''
  localContent.value = ''
  localCategory.value = 'discussion'
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
input:focus, textarea:focus, select:focus, button:focus {
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