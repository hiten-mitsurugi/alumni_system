<template>
  <div class="bg-white rounded-3xl shadow-xl border-2 border-blue-100 mb-8 overflow-hidden">
    <div class="bg-gradient-to-r from-blue-500 to-blue-600 px-8 py-6">
      <h2 class="text-2xl font-bold text-white flex items-center">
        <svg class="w-8 h-8 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
        </svg>
        Share Your Thoughts
      </h2>
      <p class="text-blue-100 text-lg mt-1">Connect with your fellow alumni and share what's on your mind</p>
    </div>
    
    <div class="p-8">
      <div class="flex items-start space-x-6">
        <img 
          :src="userProfilePicture || '/default-avatar.png'"
          alt="Your Profile"
          class="w-16 h-16 rounded-full object-cover border-4 border-blue-200 shadow-lg"
        />
        <div class="flex-1">
          <!-- Title Input -->
          <input
            v-model="localTitle"
            type="text"
            placeholder="Add a compelling title (optional)..."
            class="w-full p-4 text-xl border-2 border-slate-300 rounded-2xl mb-4 focus:ring-4 focus:ring-blue-300 focus:border-blue-500 shadow-md"
          />
          
          <!-- Content Textarea -->
          <textarea
            v-model="localContent"
            placeholder="What would you like to share with your alumni community?"
            rows="4"
            class="w-full p-4 text-lg border-2 border-slate-300 rounded-2xl resize-none focus:ring-4 focus:ring-blue-300 focus:border-blue-500 shadow-md"
          ></textarea>
          
          <!-- File Preview -->
          <div v-if="selectedFiles.length > 0" class="mt-6">
            <div class="flex items-center justify-between mb-4">
              <h4 class="text-lg font-bold text-slate-700">
                📎 {{ selectedFiles.length }} file{{ selectedFiles.length > 1 ? 's' : '' }} selected
              </h4>
              <button
                @click="clearAllFiles"
                class="text-red-500 hover:text-red-700 font-medium text-sm underline"
              >
                Clear all
              </button>
            </div>
            
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              <div
                v-for="(file, index) in selectedFiles"
                :key="index"
                class="relative group bg-white rounded-2xl shadow-lg border-2 border-slate-200 overflow-hidden hover:shadow-xl transition-all duration-300"
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
                  <svg class="w-16 h-16 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z"/>
                  </svg>
                </div>
                
                <!-- Other file types -->
                <div v-else class="aspect-square bg-gradient-to-br from-blue-100 to-purple-100 flex flex-col items-center justify-center p-4">
                  <svg class="w-12 h-12 text-slate-500 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  <span class="text-xs text-slate-600 font-medium">{{ file.type.split('/')[1]?.toUpperCase() || 'FILE' }}</span>
                </div>
                
                <!-- File info overlay -->
                <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-3">
                  <p class="text-white text-xs font-medium truncate">{{ file.name }}</p>
                  <p class="text-white/70 text-xs">{{ formatFileSize(file.size) }}</p>
                </div>
                
                <!-- Remove button -->
                <button
                  @click="removeFile(index)"
                  class="absolute -top-2 -right-2 bg-red-500 hover:bg-red-600 text-white rounded-full w-8 h-8 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300 shadow-lg text-sm font-bold z-10"
                >
                  ×
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Post Actions -->
      <div class="flex items-center justify-between mt-8 pt-6 border-t-2 border-slate-200">
        <div class="flex items-center space-x-6">
          <!-- File Upload -->
          <label class="flex items-center space-x-3 text-slate-700 hover:text-blue-700 cursor-pointer bg-slate-100 hover:bg-blue-100 px-4 py-3 rounded-2xl transition-all duration-300 shadow-md">
            <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span class="text-lg font-semibold">
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
            class="text-lg font-semibold border-2 border-slate-300 rounded-2xl px-4 py-3 focus:ring-4 focus:ring-blue-300 focus:border-blue-500 bg-white shadow-md"
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
            'px-8 py-4 rounded-2xl font-bold text-xl transition-all duration-300 shadow-xl transform',
            localContent.trim() && !isPosting
              ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 hover:scale-105 hover:shadow-2xl'
              : 'bg-slate-300 text-slate-500 cursor-not-allowed'
          ]"
        >
          <span v-if="isPosting" class="flex items-center">
            <svg class="animate-spin -ml-1 mr-3 h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Sharing...
          </span>
          <span v-else class="flex items-center">
            <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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

const createPost = () => {
  if (!localContent.value.trim()) return
  
  const postData = {
    title: localTitle.value,
    content: localContent.value,
    category: localCategory.value,
    files: selectedFiles.value
  }
  
  emit('create-post', postData)
  
  // Clear form after successful creation
  clearForm()
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
