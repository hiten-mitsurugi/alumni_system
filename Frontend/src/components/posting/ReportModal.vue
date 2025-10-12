<template>
  <!-- Invisible backdrop for click outside -->
  <div class="fixed inset-0 z-40" @click="$emit('close')"></div>
  
  <!-- Modal centered on screen -->
  <div class="fixed inset-0 flex items-center justify-center z-50 p-4 pointer-events-none">
    <!-- Modal container -->
    <div 
      :class="[
        'w-full max-w-md rounded-lg shadow-xl transform transition-all duration-200 ease-out border pointer-events-auto',
        themeStore.isAdminDark() 
          ? 'bg-gray-800 border-gray-600' 
          : 'bg-white border-gray-200'
      ]"
      @click.stop
    >
      <!-- Header -->
      <div :class="themeStore.isAdminDark()
        ? 'flex items-center justify-between p-6 border-b border-gray-600'
        : 'flex items-center justify-between p-6 border-b border-gray-200'"
      >
        <h3 :class="themeStore.isAdminDark() 
          ? 'text-lg font-semibold text-gray-100' 
          : 'text-lg font-semibold text-gray-900'"
        >
          Report Post
        </h3>
        <button 
          @click="$emit('close')"
          :class="themeStore.isAdminDark()
            ? 'text-gray-400 hover:text-gray-200 p-1 rounded-full hover:bg-gray-600'
            : 'text-gray-400 hover:text-gray-600 p-1 rounded-full hover:bg-gray-100'"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="submitReport" class="p-6">
        <div class="space-y-4">
          <!-- Reason selection -->
          <div>
            <label :class="themeStore.isAdminDark() 
              ? 'block text-sm font-medium text-gray-300 mb-2' 
              : 'block text-sm font-medium text-gray-700 mb-2'"
            >
              Why are you reporting this post?
            </label>
            <div class="space-y-2">
              <label 
                v-for="reason in reportReasons" 
                :key="reason.value"
                :class="themeStore.isAdminDark()
                  ? 'flex items-center p-3 border border-gray-600 rounded-lg cursor-pointer hover:bg-gray-700'
                  : 'flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50'"
              >
                <input 
                  type="radio" 
                  :value="reason.value" 
                  v-model="selectedReason"
                  :class="themeStore.isAdminDark()
                    ? 'text-blue-400 bg-gray-700 border-gray-600 focus:ring-blue-400'
                    : 'text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500'"
                  class="mr-3"
                />
                <div>
                  <div :class="themeStore.isAdminDark() 
                    ? 'text-sm font-medium text-gray-200' 
                    : 'text-sm font-medium text-gray-900'"
                  >
                    {{ reason.label }}
                  </div>
                  <div :class="themeStore.isAdminDark() 
                    ? 'text-xs text-gray-400' 
                    : 'text-xs text-gray-500'"
                  >
                    {{ reason.description }}
                  </div>
                </div>
              </label>
            </div>
          </div>

          <!-- Additional details -->
          <div>
            <label 
              for="details"
              :class="themeStore.isAdminDark() 
                ? 'block text-sm font-medium text-gray-300 mb-2' 
                : 'block text-sm font-medium text-gray-700 mb-2'"
            >
              Additional details (optional)
            </label>
            <textarea
              id="details"
              v-model="details"
              rows="3"
              :class="themeStore.isAdminDark()
                ? 'w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-gray-200 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                : 'w-full px-3 py-2 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent'"
              placeholder="Please provide any additional context..."
            ></textarea>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-end space-x-3 mt-6">
          <button
            type="button"
            @click="$emit('close')"
            :class="themeStore.isAdminDark()
              ? 'px-4 py-2 text-sm font-medium text-gray-300 bg-gray-700 border border-gray-600 rounded-lg hover:bg-gray-600'
              : 'px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200'"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="!selectedReason || loading"
            :class="themeStore.isAdminDark()
              ? 'px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed'
              : 'px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed'"
          >
            <span v-if="loading" class="flex items-center">
              <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
              Reporting...
            </span>
            <span v-else>Report Post</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { reportsService } from '@/services/reportsService'

// Stores
const themeStore = useThemeStore()

// Props & Emits
const props = defineProps({
  post: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'reported'])

// Refs
const selectedReason = ref('')
const details = ref('')
const loading = ref(false)

// Report reasons (must match backend choices)
const reportReasons = [
  {
    value: 'spam',
    label: 'Spam',
    description: 'Repetitive or unwanted content'
  },
  {
    value: 'inappropriate',
    label: 'Inappropriate Content',
    description: 'Offensive or unsuitable material'
  },
  {
    value: 'harassment',
    label: 'Harassment and Bullying',
    description: 'Targeting or intimidating behavior'
  },
  {
    value: 'false_information',
    label: 'False Information',
    description: 'Misleading or incorrect content'
  },
  {
    value: 'violence',
    label: 'Violence or Threats',
    description: 'Content promoting violence or threatening behavior'
  },
  {
    value: 'copyright',
    label: 'Copyright Infringement',
    description: 'Unauthorized use of copyrighted material'
  },
  {
    value: 'other',
    label: 'Other',
    description: 'Something else that violates community guidelines'
  }
]

// Methods
const submitReport = async () => {
  if (loading.value || !selectedReason.value) return

  loading.value = true
  try {
    const reportData = await reportsService.reportPost(props.post.id, {
      reason: selectedReason.value,
      details: details.value
    })

    // Show success message and close modal
    alert('✅ Report submitted successfully! Our team will review it shortly.')
    emit('reported', reportData)
    emit('close')
  } catch (error) {
    console.error('Error reporting post:', error)
    
    // Handle specific error messages
    if (error.response?.status === 400) {
      alert('❌ ' + (error.response.data.error || 'Unable to report this post'))
    } else {
      alert('❌ Failed to report post. Please try again.')
    }
  } finally {
    loading.value = false
  }
}
</script>