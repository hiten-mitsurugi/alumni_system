<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Alumni Tracer Survey</h1>
        <p class="mt-2 text-gray-600">Help us improve our programs by sharing your experiences and feedback</p>
      </div>

      <!-- Already Submitted Notice -->
      <div v-if="hasSubmitted" class="bg-orange-50 border border-orange-200 rounded-lg p-6 text-center">
        <div class="mx-auto w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mb-4">
          <svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
        </div>
        <h3 class="text-lg font-medium text-green-900 mb-2">Survey Already Completed</h3>
        <p class="text-green-700">Thank you for your participation! You have already submitted your responses to this survey.</p>
        <p class="text-sm text-orange-600 mt-2">If you need to update your responses, please contact the administration.</p>
      </div>

      <!-- Loading State -->
      <div v-else-if="loading" class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6">
        <div class="flex">
          <svg class="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
          </svg>
          <div>
            <h3 class="text-red-800 font-medium">Error Loading Survey</h3>
            <p class="text-red-700 mt-1">{{ error }}</p>
          </div>
        </div>
      </div>

      <!-- Survey Form -->
      <form v-else @submit.prevent="handleSubmit" class="space-y-8">
        <!-- Progress Bar -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-gray-700">Progress</span>
            <span class="text-sm text-gray-600">{{ completedQuestions }}/{{ totalQuestions }} completed</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              class="bg-blue-600 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${progressPercentage}%` }"
            ></div>
          </div>
        </div>

        <!-- Survey Categories -->
        <div
          v-for="category in categorizedQuestions"
          :key="category.id"
          class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
        >
          <!-- Category Header -->
          <div class="bg-gray-50 px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-medium text-gray-900">{{ category.name }}</h2>
            <p v-if="category.description" class="text-sm text-gray-600 mt-1">{{ category.description }}</p>
          </div>

          <!-- Category Questions -->
          <div class="p-6 space-y-6">
            <div
              v-for="question in category.questions"
              :key="question.id"
              class="space-y-3"
            >
              <!-- Question Label -->
              <label class="block text-sm font-medium text-gray-900">
                {{ question.question_text }}
                <span v-if="question.is_required" class="text-red-500">*</span>
              </label>

              <!-- Help Text -->
              <p v-if="question.help_text" class="text-sm text-gray-600">{{ question.help_text }}</p>

              <!-- Question Input Based on Type -->
              <!-- Text Input -->
              <input
                v-if="question.question_type === 'text'"
                v-model="responses[question.id]"
                type="text"
                :placeholder="question.placeholder_text"
                :maxlength="question.max_length"
                :required="question.is_required"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors[question.id] }"
              />

              <!-- Textarea -->
              <textarea
                v-else-if="question.question_type === 'textarea'"
                v-model="responses[question.id]"
                rows="4"
                :placeholder="question.placeholder_text"
                :maxlength="question.max_length"
                :required="question.is_required"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors[question.id] }"
              ></textarea>

              <!-- Number Input -->
              <input
                v-else-if="question.question_type === 'number'"
                v-model.number="responses[question.id]"
                type="number"
                :min="question.min_value"
                :max="question.max_value"
                :placeholder="question.placeholder_text"
                :required="question.is_required"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors[question.id] }"
              />

              <!-- Email Input -->
              <input
                v-else-if="question.question_type === 'email'"
                v-model="responses[question.id]"
                type="email"
                :placeholder="question.placeholder_text"
                :required="question.is_required"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors[question.id] }"
              />

              <!-- Phone Input -->
              <input
                v-else-if="question.question_type === 'phone'"
                v-model="responses[question.id]"
                type="tel"
                :placeholder="question.placeholder_text"
                :required="question.is_required"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors[question.id] }"
              />

              <!-- URL Input -->
              <input
                v-else-if="question.question_type === 'url'"
                v-model="responses[question.id]"
                type="url"
                :placeholder="question.placeholder_text"
                :required="question.is_required"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors[question.id] }"
              />

              <!-- Date Input -->
              <input
                v-else-if="question.question_type === 'date'"
                v-model="responses[question.id]"
                type="date"
                :required="question.is_required"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors[question.id] }"
              />

              <!-- Radio Buttons -->
              <div
                v-else-if="question.question_type === 'radio'"
                class="space-y-2"
              >
                <div
                  v-for="option in question.options"
                  :key="option"
                  class="flex items-center"
                >
                  <input
                    :id="`${question.id}_${option}`"
                    v-model="responses[question.id]"
                    type="radio"
                    :value="option"
                    :name="`question_${question.id}`"
                    :required="question.is_required"
                    class="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                  />
                  <label
                    :for="`${question.id}_${option}`"
                    class="ml-2 text-sm text-gray-700"
                  >
                    {{ option }}
                  </label>
                </div>
              </div>

              <!-- Checkboxes -->
              <div
                v-else-if="question.question_type === 'checkbox'"
                class="space-y-2"
              >
                <div
                  v-for="option in question.options"
                  :key="option"
                  class="flex items-center"
                >
                  <input
                    :id="`${question.id}_${option}`"
                    v-model="responses[question.id]"
                    type="checkbox"
                    :value="option"
                    class="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label
                    :for="`${question.id}_${option}`"
                    class="ml-2 text-sm text-gray-700"
                  >
                    {{ option }}
                  </label>
                </div>
              </div>

              <!-- Select Dropdown -->
              <select
                v-else-if="question.question_type === 'select'"
                v-model="responses[question.id]"
                :required="question.is_required"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors[question.id] }"
              >
                <option value="">Select an option</option>
                <option
                  v-for="option in question.options"
                  :key="option"
                  :value="option"
                >
                  {{ option }}
                </option>
              </select>

              <!-- Rating Scale -->
              <div
                v-else-if="question.question_type === 'rating'"
                class="space-y-3"
              >
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-600">{{ question.min_value }}</span>
                  <span class="text-sm text-gray-600">{{ question.max_value }}</span>
                </div>
                <div class="flex items-center space-x-2">
                  <div
                    v-for="rating in getRatingRange(question)"
                    :key="rating"
                    class="flex flex-col items-center"
                  >
                    <input
                      :id="`${question.id}_${rating}`"
                      v-model.number="responses[question.id]"
                      type="radio"
                      :value="rating"
                      :name="`question_${question.id}`"
                      :required="question.is_required"
                      class="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                    />
                    <label
                      :for="`${question.id}_${rating}`"
                      class="text-sm text-gray-700 mt-1"
                    >
                      {{ rating }}
                    </label>
                  </div>
                </div>
                <div v-if="responses[question.id]" class="text-center">
                  <span class="text-sm font-medium text-blue-600">
                    Selected: {{ responses[question.id] }}
                  </span>
                </div>
              </div>

              <!-- Yes/No -->
              <div
                v-else-if="question.question_type === 'yes_no'"
                class="flex items-center space-x-6"
              >
                <div class="flex items-center">
                  <input
                    :id="`${question.id}_yes`"
                    v-model="responses[question.id]"
                    type="radio"
                    :value="true"
                    :name="`question_${question.id}`"
                    :required="question.is_required"
                    class="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                  />
                  <label
                    :for="`${question.id}_yes`"
                    class="ml-2 text-sm text-gray-700"
                  >
                    Yes
                  </label>
                </div>
                <div class="flex items-center">
                  <input
                    :id="`${question.id}_no`"
                    v-model="responses[question.id]"
                    type="radio"
                    :value="false"
                    :name="`question_${question.id}`"
                    :required="question.is_required"
                    class="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                  />
                  <label
                    :for="`${question.id}_no`"
                    class="ml-2 text-sm text-gray-700"
                  >
                    No
                  </label>
                </div>
              </div>

              <!-- Error Message -->
              <p v-if="errors[question.id]" class="text-sm text-red-600">{{ errors[question.id] }}</p>
            </div>
          </div>
        </div>

        <!-- Submit Section -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <!-- Submit Error -->
          <div v-if="submitError" class="bg-red-50 border border-red-200 rounded-md p-3 mb-4">
            <p class="text-sm text-red-800">{{ submitError }}</p>
          </div>

          <!-- Submit Button -->
          <div class="flex justify-end">
            <button
              type="submit"
              :disabled="submitting"
              class="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <svg
                v-if="submitting"
                class="animate-spin h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                ></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              {{ submitting ? 'Submitting...' : 'Submit Survey' }}
            </button>
          </div>

          <p class="text-xs text-gray-500 mt-3 text-center">
            Your responses are confidential and will be used to improve our programs.
          </p>
        </div>
      </form>

      <!-- Success Modal -->
      <div
        v-if="showSuccessModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6 text-center">
          <div class="mx-auto w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mb-4">
            <svg class="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Survey Submitted Successfully!</h3>
          <p class="text-gray-600 mb-6">Thank you for your valuable feedback. Your responses have been recorded.</p>
          <button
            @click="showSuccessModal = false"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { surveyService } from '@/services/surveyService'

export default {
  name: 'AlumniSurvey',
  setup() {
    const loading = ref(false)
    const submitting = ref(false)
    const error = ref(null)
    const submitError = ref(null)
    const hasSubmitted = ref(false)
    const showSuccessModal = ref(false)
    
    const questions = ref([])
    const responses = ref({})
    const errors = ref({})

    // Group questions by category
    const categorizedQuestions = computed(() => {
      const categories = {}
      
      questions.value.forEach(question => {
        if (!categories[question.category.id]) {
          categories[question.category.id] = {
            id: question.category.id,
            name: question.category.name,
            description: question.category.description,
            order: question.category.order,
            questions: []
          }
        }
        categories[question.category.id].questions.push(question)
      })
      
      // Sort categories by order and questions within categories by order
      return Object.values(categories)
        .sort((a, b) => a.order - b.order)
        .map(category => ({
          ...category,
          questions: category.questions.sort((a, b) => a.order - b.order)
        }))
    })

    // Progress tracking
    const totalQuestions = computed(() => questions.value.length)
    
    const completedQuestions = computed(() => {
      return Object.keys(responses.value).filter(questionId => {
        const value = responses.value[questionId]
        return value !== null && value !== undefined && value !== '' && 
               (Array.isArray(value) ? value.length > 0 : true)
      }).length
    })
    
    const progressPercentage = computed(() => {
      return totalQuestions.value > 0 ? (completedQuestions.value / totalQuestions.value) * 100 : 0
    })

    // Initialize responses for checkbox questions
    const initializeResponses = () => {
      questions.value.forEach(question => {
        if (question.question_type === 'checkbox') {
          responses.value[question.id] = []
        }
      })
    }

    // Get rating range for rating questions
    const getRatingRange = (question) => {
      const range = []
      for (let i = question.min_value; i <= question.max_value; i++) {
        range.push(i)
      }
      return range
    }

    // Load survey questions
    const loadSurveyQuestions = async () => {
      try {
        loading.value = true
        error.value = null
        
        // Check if user has already submitted
        const statusResponse = await surveyService.checkResponseStatus()
        if (statusResponse.data.has_submitted) {
          hasSubmitted.value = true
          return
        }
        
        // Load questions
        const response = await surveyService.getActiveSurveyQuestions()
        questions.value = response.data
        initializeResponses()
        
      } catch (err) {
        error.value = 'Failed to load survey questions. Please try again later.'
        console.error('Error loading survey:', err)
      } finally {
        loading.value = false
      }
    }

    // Validate form
    const validateForm = () => {
      errors.value = {}
      let isValid = true

      questions.value.forEach(question => {
        if (question.is_required) {
          const value = responses.value[question.id]
          
          if (value === null || value === undefined || value === '' || 
              (Array.isArray(value) && value.length === 0)) {
            errors.value[question.id] = 'This field is required'
            isValid = false
          }
        }
        
        // Type-specific validation
        if (question.question_type === 'email' && responses.value[question.id]) {
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
          if (!emailRegex.test(responses.value[question.id])) {
            errors.value[question.id] = 'Please enter a valid email address'
            isValid = false
          }
        }
        
        if (question.question_type === 'number' && responses.value[question.id] !== null && responses.value[question.id] !== undefined && responses.value[question.id] !== '') {
          const value = parseFloat(responses.value[question.id])
          if (question.min_value !== null && value < question.min_value) {
            errors.value[question.id] = `Value must be at least ${question.min_value}`
            isValid = false
          }
          if (question.max_value !== null && value > question.max_value) {
            errors.value[question.id] = `Value must be at most ${question.max_value}`
            isValid = false
          }
        }
      })

      return isValid
    }

    // Submit survey
    const handleSubmit = async () => {
      if (!validateForm()) {
        // Scroll to first error
        const firstErrorElement = document.querySelector('.border-red-500')
        if (firstErrorElement) {
          firstErrorElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
        return
      }

      try {
        submitting.value = true
        submitError.value = null

        // Prepare submission data
        const submissionData = {
          responses: { ...responses.value }
        }

        await surveyService.submitSurveyResponse(submissionData)
        
        showSuccessModal.value = true
        hasSubmitted.value = true
        
      } catch (err) {
        if (err.response?.data) {
          const errorData = err.response.data
          if (typeof errorData === 'object' && errorData.responses) {
            // Handle field-specific errors
            Object.keys(errorData.responses).forEach(questionId => {
              errors.value[questionId] = errorData.responses[questionId]
            })
          } else {
            submitError.value = errorData.detail || errorData.message || 'Failed to submit survey'
          }
        } else {
          submitError.value = 'Network error. Please check your connection and try again.'
        }
        console.error('Error submitting survey:', err)
      } finally {
        submitting.value = false
      }
    }

    // Initialize
    onMounted(() => {
      loadSurveyQuestions()
    })

    return {
      loading,
      submitting,
      error,
      submitError,
      hasSubmitted,
      showSuccessModal,
      questions,
      responses,
      errors,
      categorizedQuestions,
      totalQuestions,
      completedQuestions,
      progressPercentage,
      getRatingRange,
      handleSubmit
    }
  }
}
</script>

<style scoped>
/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Form focus styles */
input:focus,
textarea:focus,
select:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Progress bar animation */
.transition-all {
  transition: all 0.3s ease-in-out;
}

/* Rating scale styling */
input[type="radio"] + label {
  cursor: pointer;
}

input[type="radio"]:checked + label {
  font-weight: 600;
  color: #2563eb;
}
</style>
