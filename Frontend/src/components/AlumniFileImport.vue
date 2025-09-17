<template>
  <div class="bg-white p-6 rounded-lg shadow-lg max-w-2xl mx-auto">
    <h2 class="text-2xl font-bold text-gray-800 mb-6">Import Alumni Data</h2>
    
    <!-- File Drop Zone -->
    <div
      @drop="handleDrop"
      @dragover="handleDragOver"
      @dragenter="handleDragEnter"
      @dragleave="handleDragLeave"
      :class="[
        'border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-200 cursor-pointer',
        isDragging ? 'border-green-500 bg-green-50' : 'border-gray-300 bg-gray-50',
        isUploading ? 'pointer-events-none opacity-50' : ''
      ]"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        @change="handleFileSelect"
        accept=".csv,.xlsx,.xls,.txt"
        class="hidden"
      />
      
      <div v-if="!selectedFile && !isUploading">
        <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
        </svg>
        <p class="text-lg text-gray-600 mb-2">Drag and drop your file here</p>
        <p class="text-sm text-gray-500 mb-4">or click to browse</p>
        <p class="text-xs text-gray-400">Supports CSV, Excel (.xlsx, .xls), and Text files</p>
        <p class="text-xs text-gray-400">Maximum file size: 10MB</p>
      </div>
      
      <div v-else-if="selectedFile && !isUploading" class="space-y-4">
        <svg class="mx-auto h-12 w-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <div>
          <p class="text-lg font-medium text-gray-800">{{ selectedFile.name }}</p>
          <p class="text-sm text-gray-500">{{ formatFileSize(selectedFile.size) }}</p>
        </div>
        <div class="flex justify-center space-x-4">
          <button
            @click.stop="uploadFile"
            class="px-6 py-2 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white rounded-lg transition-all duration-200"
          >
            Upload File
          </button>
          <button
            @click.stop="clearFile"
            class="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
          >
            Remove
          </button>
        </div>
      </div>
      
      <div v-else-if="isUploading" class="space-y-4">
        <div class="animate-spin mx-auto h-12 w-12 border-4 border-green-600 border-t-transparent rounded-full"></div>
        <p class="text-lg text-gray-600">Uploading and processing file...</p>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div 
            class="bg-green-600 h-2 rounded-full transition-all duration-300 ease-out"
            :style="{ width: uploadProgress + '%' }"
          ></div>
        </div>
        <p class="text-sm text-gray-500">{{ uploadProgress }}%</p>
      </div>
    </div>
    
    <!-- Upload Results -->
    <div v-if="uploadResult" class="mt-6 p-4 rounded-lg" :class="uploadResult.success_count > 0 ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'">
      <h3 class="text-lg font-semibold mb-3" :class="uploadResult.success_count > 0 ? 'text-green-800' : 'text-red-800'">
        Import Results
      </h3>
      
      <!-- Success Message -->
      <div v-if="uploadResult.success_count > 0 && uploadResult.error_count === 0" class="mb-4 p-3 bg-green-100 border border-green-300 rounded-lg">
        <div class="flex items-center">
          <svg class="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
          </svg>
          <span class="text-green-800 font-semibold">🎉 All records imported successfully!</span>
        </div>
        <p class="text-green-700 text-sm mt-1">{{ uploadResult.success_count }} alumni {{ uploadResult.success_count === 1 ? 'record has' : 'records have' }} been added to the directory.</p>
      </div>
      
      <!-- Partial Success Message -->
      <div v-else-if="uploadResult.success_count > 0 && uploadResult.error_count > 0" class="mb-4 p-3 bg-yellow-100 border border-yellow-300 rounded-lg">
        <div class="flex items-center">
          <svg class="w-5 h-5 text-yellow-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
          </svg>
          <span class="text-yellow-800 font-semibold">Partial import completed</span>
        </div>
        <p class="text-yellow-700 text-sm mt-1">{{ uploadResult.success_count }} records imported successfully, but {{ uploadResult.error_count }} {{ uploadResult.error_count === 1 ? 'error was' : 'errors were' }} encountered.</p>
      </div>
      
      <div class="grid grid-cols-2 gap-4 mb-4">
        <div class="text-center p-3 bg-white rounded-lg">
          <div class="text-2xl font-bold text-green-600">{{ uploadResult.success_count }}</div>
          <div class="text-sm text-gray-600">Successfully Imported</div>
        </div>
        <div class="text-center p-3 bg-white rounded-lg">
          <div class="text-2xl font-bold text-red-600">{{ uploadResult.error_count }}</div>
          <div class="text-sm text-gray-600">Errors</div>
        </div>
      </div>
      
      <div v-if="uploadResult.errors && uploadResult.errors.length > 0" class="space-y-2">
        <h4 class="font-semibold text-red-800">Errors encountered:</h4>
        <div class="max-h-40 overflow-y-auto space-y-1">
          <div
            v-for="(error, index) in uploadResult.errors"
            :key="index"
            class="text-sm text-red-700 bg-white p-2 rounded"
          >
            {{ error }}
          </div>
        </div>
        <p v-if="uploadResult.total_errors > uploadResult.errors.length" class="text-sm text-red-600">
          And {{ uploadResult.total_errors - uploadResult.errors.length }} more errors...
        </p>
      </div>
      
      <div class="flex justify-between items-center mt-4">
        <button
          @click="clearResults"
          class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
        >
          Clear Results
        </button>
        <button
          v-if="uploadResult.success_count > 0"
          @click="$emit('import-completed')"
          class="px-4 py-2 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white rounded-lg transition-all duration-200"
        >
          Refresh Alumni List
        </button>
      </div>
    </div>
    
    <!-- File Format Help -->
    <div class="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <h3 class="text-lg font-semibold text-blue-800 mb-2">Required File Format</h3>
      <p class="text-sm text-blue-700 mb-3">Your file must contain these columns (in any order):</p>
      <div class="grid grid-cols-2 gap-2 text-sm text-blue-700">
        <div>• first_name</div>
        <div>• last_name</div>
        <div>• birth_date (YYYY-MM-DD)</div>
        <div>• program</div>
        <div>• year_graduated</div>
        <div>• sex (male or female)</div>
        <div>• middle_name (optional)</div>
      </div>
      <div class="mt-3 p-2 bg-blue-100 rounded text-sm text-blue-800">
        <strong>Sex values must be exactly:</strong> "male" or "female"
      </div>
      <div class="mt-3 flex space-x-4">
        <a
          href="/sample_alumni.csv"
          download
          class="text-sm text-blue-600 hover:text-blue-800 underline"
        >
          Download CSV Sample
        </a>
        <a
          href="/sample_alumni.xlsx"
          download
          class="text-sm text-blue-600 hover:text-blue-800 underline"
        >
          Download Excel Sample
        </a>
        <a
          href="/sample_alumni.txt"
          download
          class="text-sm text-blue-600 hover:text-blue-800 underline"
        >
          Download TXT Sample
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

// Emit events
const emit = defineEmits(['import-completed'])

// Auth store
const authStore = useAuthStore()

// Reactive data
const isDragging = ref(false)
const selectedFile = ref(null)
const isUploading = ref(false)
const uploadProgress = ref(0)
const uploadResult = ref(null)
const fileInput = ref(null)

// Drag and drop handlers
const handleDragOver = (e) => {
  e.preventDefault()
}

const handleDragEnter = (e) => {
  e.preventDefault()
  isDragging.value = true
}

const handleDragLeave = (e) => {
  e.preventDefault()
  // Only set to false if we're leaving the drop zone completely
  if (!e.currentTarget.contains(e.relatedTarget)) {
    isDragging.value = false
  }
}

const handleDrop = (e) => {
  e.preventDefault()
  isDragging.value = false
  
  const files = e.dataTransfer.files
  if (files.length > 0) {
    handleFileSelection(files[0])
  }
}

// File selection handlers
const triggerFileInput = () => {
  if (!isUploading.value) {
    fileInput.value.click()
  }
}

const handleFileSelect = (e) => {
  const files = e.target.files
  if (files.length > 0) {
    handleFileSelection(files[0])
  }
}

const handleFileSelection = (file) => {
  // Validate file type
  const allowedTypes = ['.csv', '.xlsx', '.xls', '.txt']
  const fileExtension = '.' + file.name.split('.').pop().toLowerCase()
  
  if (!allowedTypes.includes(fileExtension)) {
    alert('Please select a CSV, Excel, or Text file.')
    return
  }
  
  // Validate file size (10MB)
  if (file.size > 10 * 1024 * 1024) {
    alert('File size must be less than 10MB.')
    return
  }
  
  selectedFile.value = file
  uploadResult.value = null
}

// File operations
const clearFile = () => {
  selectedFile.value = null
  uploadResult.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const clearResults = () => {
  uploadResult.value = null
}

const uploadFile = async () => {
  if (!selectedFile.value) return
  
  isUploading.value = true
  uploadProgress.value = 0
  
  // Simulate progress (since we can't get real progress from Django easily)
  const progressInterval = setInterval(() => {
    if (uploadProgress.value < 90) {
      uploadProgress.value += 10
    }
  }, 200)
  
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    const response = await api.post('alumni-directory/import/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    clearInterval(progressInterval)
    uploadProgress.value = 100
    
    setTimeout(() => {
      uploadResult.value = response.data
      isUploading.value = false
      selectedFile.value = null
      if (fileInput.value) {
        fileInput.value.value = ''
      }
    }, 500)
    
  } catch (error) {
    clearInterval(progressInterval)
    isUploading.value = false
    
    const errorMessage = error.response?.data?.error || 'Upload failed. Please try again.'
    uploadResult.value = {
      success_count: 0,
      error_count: 1,
      errors: [errorMessage],
      total_errors: 1
    }
    
    console.error('Upload error:', error)
    console.error('Error response:', error.response?.data)
  }
}

// Utility functions
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>

<style scoped>
/* Additional styles can be added here if needed */
</style>
