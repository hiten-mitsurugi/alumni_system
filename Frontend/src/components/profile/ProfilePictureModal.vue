<template>
  <div class="fixed inset-0 bg-black/50 bg-opacity-50b backdrop-blur-sm flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h2 class="text-xl font-semibold text-gray-900">Update Profile Picture</h2>
        <button 
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="p-6">
        <!-- Upload Area -->
        <div 
          @click="triggerFileInput"
          @drop.prevent="handleDrop"
          @dragover.prevent
          @dragenter.prevent="handleDragEnter"
          @dragleave.prevent="handleDragLeave"
          class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-orange-500 transition-colors"
          :class="{ 'border-orange-500 bg-orange-50': dragOver }"
        >
          <div v-if="!selectedFile">
            <svg class="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            <p class="text-gray-600 mb-2">
              <span class="font-medium">Click to upload</span> or drag and drop
            </p>
            <p class="text-sm text-gray-500">
              PNG, JPG, GIF up to 10MB
            </p>
          </div>
          
          <!-- Preview -->
          <div v-else class="space-y-4">
            <img 
              :src="previewUrl" 
              alt="Profile picture preview"
              class="w-32 h-32 mx-auto object-cover rounded-full border-4 border-orange-500"
            />
            <div class="text-sm text-gray-600">
              {{ selectedFile.name }}
              <span class="text-gray-400">
                ({{ formatFileSize(selectedFile.size) }})
              </span>
            </div>
            <button 
              @click.stop="clearSelection"
              class="text-red-600 hover:text-red-700 text-sm font-medium"
            >
              Remove
            </button>
          </div>
        </div>

        <!-- Hidden file input -->
        <input 
          ref="fileInput"
          type="file"
          accept="image/*"
          @change="handleFileSelect"
          class="hidden"
        />

        <!-- Recommended dimensions -->
        <div class="mt-4 p-3 bg-blue-50 rounded-lg">
          <p class="text-sm text-blue-800">
            <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            Recommended: Square image (400 x 400 pixels) for best quality
          </p>
        </div>

        <!-- Error message -->
        <div v-if="error" class="mt-4 p-3 bg-red-50 rounded-lg">
          <p class="text-sm text-red-800">
            {{ error }}
          </p>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end space-x-3 p-6 border-t border-gray-200">
        <button 
          @click="$emit('close')"
          class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Cancel
        </button>
        <button 
          @click="saveProfilePicture"
          :disabled="!selectedFile || uploading"
          class="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors disabled:opacity-50"
        >
          <span v-if="uploading" class="animate-spin mr-2">⟳</span>
          {{ uploading ? 'Uploading...' : 'Save Photo' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'

const emit = defineEmits(['close', 'save'])

const fileInput = ref(null)
const selectedFile = ref(null)
const previewUrl = ref(null)
const dragOver = ref(false)
const uploading = ref(false)
const error = ref('')

const maxFileSize = 10 * 1024 * 1024 // 10MB
const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    processFile(file)
  }
}

const handleDrop = (event) => {
  dragOver.value = false
  const file = event.dataTransfer.files[0]
  if (file) {
    processFile(file)
  }
}

const handleDragEnter = () => {
  dragOver.value = true
}

const handleDragLeave = () => {
  dragOver.value = false
}

const processFile = (file) => {
  error.value = ''
  
  // Validate file type
  if (!allowedTypes.includes(file.type)) {
    error.value = 'Please select a valid image file (PNG, JPG, GIF)'
    return
  }
  
  // Validate file size
  if (file.size > maxFileSize) {
    error.value = 'File size must be less than 10MB'
    return
  }
  
  selectedFile.value = file
  
  // Create preview URL
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
  previewUrl.value = URL.createObjectURL(file)
}

const clearSelection = () => {
  selectedFile.value = null
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = null
  }
  error.value = ''
  
  // Clear file input
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const saveProfilePicture = async () => {
  if (!selectedFile.value) return
  
  try {
    uploading.value = true
    emit('save', selectedFile.value)
  } catch (error) {
    console.error('Error saving profile picture:', error)
    error.value = 'Failed to upload profile picture. Please try again.'
  } finally {
    uploading.value = false
  }
}

// Cleanup on unmount
const cleanup = () => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
}

onUnmounted(cleanup)
</script>
