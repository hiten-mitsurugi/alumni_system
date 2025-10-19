<template>
  <div 
    v-if="isVisible" 
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    @click.self="closeModal"
  >
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900">Report Post</h3>
        <button 
          @click="closeModal"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="p-6">
        <div class="mb-4">
          <h4 class="font-medium text-gray-900 mb-2">Why are you reporting this post?</h4>
          <p class="text-sm text-gray-600 mb-4">
            Help us understand what's wrong with this post. Your report will be reviewed by our moderation team.
          </p>
        </div>

        <!-- Report Reasons -->
        <div class="space-y-3 mb-4">
          <label 
            v-for="reason in reportReasons" 
            :key="reason.value"
            class="flex items-start space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
            :class="{ 'border-red-300 bg-red-50': selectedReason === reason.value }"
          >
            <input 
              type="radio" 
              :value="reason.value" 
              v-model="selectedReason"
              class="mt-1 text-red-600 focus:ring-red-500"
            />
            <div>
              <div class="font-medium text-gray-900">{{ reason.label }}</div>
              <div class="text-sm text-gray-600">{{ reason.description }}</div>
            </div>
          </label>
        </div>

        <!-- Additional Details -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Additional details (optional)
          </label>
          <textarea
            v-model="additionalDetails"
            placeholder="Provide any additional information that might help us understand the issue..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
            rows="4"
            maxlength="500"
          ></textarea>
          <div class="text-right text-xs text-gray-500 mt-1">
            {{ additionalDetails.length }}/500 characters
          </div>
        </div>

        <!-- Warning -->
        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <div class="flex">
            <svg class="w-5 h-5 text-yellow-400 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
            <div>
              <h4 class="text-sm font-medium text-yellow-800">Important</h4>
              <p class="text-sm text-yellow-700 mt-1">
                False reports may result in restrictions on your account. Please only report content that violates our community guidelines.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-end space-x-3 p-6 border-t border-gray-200 bg-gray-50">
        <button 
          @click="closeModal"
          class="px-4 py-2 text-gray-600 hover:text-gray-800 font-medium transition-colors"
        >
          Cancel
        </button>
        <button 
          @click="submitReport"
          :disabled="!selectedReason || isSubmitting"
          class="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors flex items-center"
        >
          <svg v-if="isSubmitting" class="w-4 h-4 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isSubmitting ? 'Submitting...' : 'Submit Report' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

// Props
const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  post: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['close', 'submit'])

// State
const selectedReason = ref('')
const additionalDetails = ref('')
const isSubmitting = ref(false)

// Report reasons
const reportReasons = [
  {
    value: 'inappropriate_content',
    label: 'Inappropriate Content',
    description: 'Contains offensive, harmful, or inappropriate material'
  },
  {
    value: 'spam',
    label: 'Spam',
    description: 'Repetitive, promotional, or unwanted content'
  },
  {
    value: 'harassment',
    label: 'Harassment or Bullying',
    description: 'Targeting or intimidating specific individuals'
  },
  {
    value: 'false_information',
    label: 'False Information',
    description: 'Contains misleading or factually incorrect information'
  },
  {
    value: 'privacy_violation',
    label: 'Privacy Violation',
    description: 'Shares personal information without consent'
  },
  {
    value: 'copyright',
    label: 'Copyright Infringement',
    description: 'Uses copyrighted material without permission'
  },
  {
    value: 'other',
    label: 'Other',
    description: 'Violates community guidelines in another way'
  }
]

// Methods
const closeModal = () => {
  emit('close')
  resetForm()
}

const resetForm = () => {
  selectedReason.value = ''
  additionalDetails.value = ''
  isSubmitting.value = false
}

const submitReport = async () => {
  if (!selectedReason.value) return

  isSubmitting.value = true

  try {
    const reportData = {
      reason: selectedReason.value,
      details: additionalDetails.value.trim(),
      reasonLabel: reportReasons.find(r => r.value === selectedReason.value)?.label
    }

    emit('submit', reportData)
    closeModal()
  } catch (error) {
    console.error('Error submitting report:', error)
    isSubmitting.value = false
  }
}

// Watch for modal visibility changes
watch(() => props.isVisible, (newValue) => {
  if (!newValue) {
    resetForm()
  }
})
</script>

<style scoped>
/* Custom scrollbar for textarea */
textarea::-webkit-scrollbar {
  width: 6px;
}

textarea::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

textarea::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

textarea::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Smooth transitions */
.transition-colors {
  transition: all 0.2s ease;
}

/* Loading animation */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>