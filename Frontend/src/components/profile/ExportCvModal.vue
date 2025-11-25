<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black/50 dark:bg-black/70 transition-opacity"
         @click="closeModal"></div>
    
    <!-- Modal -->
    <div :class="[
      'relative w-full max-w-md p-6 m-4 rounded-lg shadow-xl transition-all transform',
      themeStore.isDarkMode 
        ? 'bg-gray-800 border border-gray-700' 
        : 'bg-white border border-gray-200'
    ]">
      <!-- Header -->
      <div class="flex items-center justify-between mb-5">
        <div class="flex items-center gap-3">
          <div :class="[
            'p-2 rounded-lg',
            themeStore.isDarkMode ? 'bg-orange-900/30' : 'bg-orange-100'
          ]">
            <svg :class="[
              'w-6 h-6',
              themeStore.isDarkMode ? 'text-orange-400' : 'text-orange-600'
            ]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <h3 :class="[
              'text-lg font-semibold',
              themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
            ]">Export CV as PDF</h3>
            <p :class="[
              'text-sm',
              themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
            ]">Professional curriculum vitae</p>
          </div>
        </div>
        <button @click="closeModal" 
                :class="[
                  'p-2 rounded-lg transition-colors',
                  themeStore.isDarkMode 
                    ? 'hover:bg-gray-700 text-gray-400 hover:text-white' 
                    : 'hover:bg-gray-100 text-gray-500 hover:text-gray-700'
                ]">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Options -->
      <div class="mb-6 space-y-4">
        <!-- Include Profile Picture -->
        <div :class="[
          'flex items-center justify-between p-4 rounded-lg border',
          themeStore.isDarkMode 
            ? 'bg-gray-700/30 border-gray-600' 
            : 'bg-gray-50 border-gray-200'
        ]">
          <div class="flex-1">
            <label :class="[
              'font-medium cursor-pointer',
              themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
            ]" for="includePicture">
              Include Profile Picture
            </label>
            <p :class="[
              'text-sm mt-1',
              themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
            ]">
              Add your profile photo to the CV header
            </p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer ml-4">
            <input 
              type="checkbox"   
              id="includePicture"
              v-model="includePicture" 
              class="sr-only peer">
            <div class="w-11 h-6 bg-gray-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-orange-300 dark:peer-focus:ring-orange-800 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-orange-600"></div>
          </label>
        </div>

        <!-- PDF Info -->
        <div :class="[
          'flex items-start gap-3 p-3 rounded-lg',
          themeStore.isDarkMode ? 'bg-orange-900/20' : 'bg-orange-50'
        ]">
          <svg :class="[
            'w-5 h-5 mt-0.5 shrink-0',
            themeStore.isDarkMode ? 'text-orange-400' : 'text-orange-600'
          ]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <p :class="[
              'text-sm font-medium',
              themeStore.isDarkMode ? 'text-orange-300' : 'text-orange-800'
            ]">Professional PDF Format</p>
            <p :class="[
              'text-xs mt-1',
              themeStore.isDarkMode ? 'text-orange-400' : 'text-orange-700'
            ]">
              Your CV will be generated in A4 size with LinkedIn-inspired professional styling. Includes all sections: Education, Experience, Skills, Achievements, Publications, and more.
            </p>
          </div>
        </div>
      </div>

      <!-- Message Display -->
      <div v-if="message" :class="[
        'mb-4 p-3 rounded-lg text-sm',
        messageType === 'success' 
          ? themeStore.isDarkMode 
            ? 'bg-green-900/30 text-green-300 border border-green-800' 
            : 'bg-green-50 text-green-800 border border-green-200'
          : themeStore.isDarkMode 
            ? 'bg-red-900/30 text-red-300 border border-red-800' 
            : 'bg-red-50 text-red-800 border border-red-200'
      ]">
        {{ message }}
      </div>

      <!-- Actions -->
      <div class="flex gap-3">
        <button 
          @click="closeModal"
          :disabled="isGenerating"
          :class="[
            'flex-1 px-4 py-2.5 rounded-lg font-medium transition-colors',
            isGenerating 
              ? 'opacity-50 cursor-not-allowed' 
              : '',
            themeStore.isDarkMode 
              ? 'bg-gray-700 text-gray-200 hover:bg-gray-600' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]">
          Cancel
        </button>
        <button 
          @click="generateCV"
          :disabled="isGenerating"
          :class="[
            'flex-1 px-4 py-2.5 rounded-lg font-medium transition-colors flex items-center justify-center gap-2',
            isGenerating 
              ? 'bg-orange-400 cursor-not-allowed' 
              : 'bg-orange-600 hover:bg-orange-700',
            'text-white'
          ]">
          <svg v-if="isGenerating" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          <span>{{ isGenerating ? 'Generating PDF...' : 'Download CV' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'

const themeStore = useThemeStore()
const authStore = useAuthStore()

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'success'])

const includePicture = ref(true)
const isGenerating = ref(false)
const message = ref('')
const messageType = ref('success')

const BASE_URL = `${window.location.protocol}//${window.location.hostname}:8000`

function closeModal() {
  if (!isGenerating.value) {
    message.value = ''
    emit('close')
  }
}

async function generateCV() {
  isGenerating.value = true
  message.value = ''
  
  try {
    const response = await fetch(`${BASE_URL}/api/auth/profile/export-cv/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        include_picture: includePicture.value
      })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Failed to generate CV' }))
      throw new Error(errorData.error || errorData.detail || 'Failed to generate CV')
    }

    // Get the PDF blob
    const blob = await response.blob()
    
    // Create download link
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // Get filename from Content-Disposition header or use default
    const contentDisposition = response.headers.get('Content-Disposition')
    let filename = 'CV.pdf'
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/)
      if (filenameMatch) {
        filename = filenameMatch[1]
      }
    }
    
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    
    // Cleanup
    link.remove()
    window.URL.revokeObjectURL(url)

    // Show success message
    message.value = 'CV PDF downloaded successfully!'
    messageType.value = 'success'
    
    // Emit success event
    emit('success')
    
    // Close modal after short delay
    setTimeout(() => {
      closeModal()
    }, 1500)
    
  } catch (error) {
    console.error('Error generating CV:', error)
    message.value = error.message || 'Failed to generate CV. Please try again.'
    messageType.value = 'error'
  } finally {
    isGenerating.value = false
  }
}
</script>

<style scoped>
/* Ensure modal appears above other elements */
.fixed {
  z-index: 9999;
}

/* Smooth transitions */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* Toggle switch styling */
.peer:checked ~ div {
  background-color: #2563eb;
}

/* Dark mode toggle */
.dark .peer:checked ~ div {
  background-color: #3b82f6;
}
</style>
