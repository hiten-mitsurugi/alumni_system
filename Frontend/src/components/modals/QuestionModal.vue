<template>
  <teleport to="body">
    <div
      v-if="show"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      @click.self="$emit('close')"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900">
              {{ isEditing ? 'Edit Question' : 'Create New Question' }}
            </h3>
            <button
              @click="$emit('close')"
              class="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="p-6 space-y-6">
          <!-- Category Selection -->
          <div>
            <label for="category" class="block text-sm font-medium text-gray-700 mb-1">
              Category *
            </label>
            <select
              id="category"
              v-model="form.category"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              :class="{ 'border-red-500': errors.category }"
            >
              <option value="">Select a category</option>
              <option
                v-for="category in categories"
                :key="category.id"
                :value="category.id"
              >
                {{ category.name }}
              </option>
            </select>
            <p v-if="errors.category" class="mt-1 text-sm text-red-600">{{ errors.category }}</p>
          </div>

          <!-- Question Text -->
          <div>
            <label for="question_text" class="block text-sm font-medium text-gray-700 mb-1">
              Question Text *
            </label>
            <textarea
              id="question_text"
              v-model="form.question_text"
              rows="3"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              :class="{ 'border-red-500': errors.question_text }"
              placeholder="Enter your question here..."
            ></textarea>
            <p v-if="errors.question_text" class="mt-1 text-sm text-red-600">{{ errors.question_text }}</p>
          </div>

          <!-- Question Type -->
          <div>
            <label for="question_type" class="block text-sm font-medium text-gray-700 mb-1">
              Question Type *
            </label>
            <select
              id="question_type"
              v-model="form.question_type"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              :class="{ 'border-red-500': errors.question_type }"
            >
              <option value="">Select question type</option>
              <option
                v-for="type in questionTypes"
                :key="type.value"
                :value="type.value"
              >
                {{ type.icon }} {{ type.label }}
              </option>
            </select>
            <p v-if="errors.question_type" class="mt-1 text-sm text-red-600">{{ errors.question_type }}</p>
          </div>

          <!-- Type-Specific Options -->
          <!-- Choice Options (Radio, Checkbox, Select) -->
          <div v-if="requiresOptions" class="space-y-3">
            <label class="block text-sm font-medium text-gray-700">
              Answer Options *
            </label>
            <div class="space-y-2">
              <div
                v-for="(option, index) in form.options"
                :key="index"
                class="flex items-center gap-2"
              >
                <input
                  v-model="form.options[index]"
                  type="text"
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  :placeholder="`Option ${index + 1}`"
                />
                <button
                  type="button"
                  @click="removeOption(index)"
                  class="text-red-600 hover:text-red-800 p-1"
                  :disabled="form.options.length <= 2"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                  </svg>
                </button>
              </div>
            </div>
            <button
              type="button"
              @click="addOption"
              class="text-blue-600 hover:text-blue-800 text-sm flex items-center gap-1"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
              </svg>
              Add Option
            </button>
            <p v-if="errors.options" class="text-sm text-red-600">{{ errors.options }}</p>
          </div>

          <!-- Rating Scale -->
          <div v-if="form.question_type === 'rating'" class="grid grid-cols-2 gap-4">
            <div>
              <label for="min_value" class="block text-sm font-medium text-gray-700 mb-1">
                Min Value *
              </label>
              <input
                id="min_value"
                v-model.number="form.min_value"
                type="number"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors.min_value }"
                placeholder="1"
              />
              <p v-if="errors.min_value" class="mt-1 text-sm text-red-600">{{ errors.min_value }}</p>
            </div>
            <div>
              <label for="max_value" class="block text-sm font-medium text-gray-700 mb-1">
                Max Value *
              </label>
              <input
                id="max_value"
                v-model.number="form.max_value"
                type="number"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors.max_value }"
                placeholder="5"
              />
              <p v-if="errors.max_value" class="mt-1 text-sm text-red-600">{{ errors.max_value }}</p>
            </div>
          </div>

          <!-- Number Range -->
          <div v-if="form.question_type === 'number'" class="grid grid-cols-2 gap-4">
            <div>
              <label for="number_min" class="block text-sm font-medium text-gray-700 mb-1">
                Min Value (Optional)
              </label>
              <input
                id="number_min"
                v-model.number="form.min_value"
                type="number"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label for="number_max" class="block text-sm font-medium text-gray-700 mb-1">
                Max Value (Optional)
              </label>
              <input
                id="number_max"
                v-model.number="form.max_value"
                type="number"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <!-- Text Length Limit -->
          <div v-if="['text', 'textarea'].includes(form.question_type)">
            <label for="max_length" class="block text-sm font-medium text-gray-700 mb-1">
              Maximum Characters (Optional)
            </label>
            <input
              id="max_length"
              v-model.number="form.max_length"
              type="number"
              min="1"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Leave empty for no limit"
            />
          </div>

          <!-- Additional Settings -->
          <div class="space-y-4">
            <!-- Placeholder Text -->
            <div>
              <label for="placeholder_text" class="block text-sm font-medium text-gray-700 mb-1">
                Placeholder Text (Optional)
              </label>
              <input
                id="placeholder_text"
                v-model="form.placeholder_text"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Enter your answer here..."
              />
            </div>

            <!-- Help Text -->
            <div>
              <label for="help_text" class="block text-sm font-medium text-gray-700 mb-1">
                Help Text (Optional)
              </label>
              <textarea
                id="help_text"
                v-model="form.help_text"
                rows="2"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Additional instructions or context for this question..."
              ></textarea>
            </div>

            <!-- Display Order -->
            <div>
              <label for="order" class="block text-sm font-medium text-gray-700 mb-1">
                Display Order *
              </label>
              <input
                id="order"
                v-model.number="form.order"
                type="number"
                min="1"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors.order }"
              />
              <p v-if="errors.order" class="mt-1 text-sm text-red-600">{{ errors.order }}</p>
              <p class="mt-1 text-xs text-gray-500">Lower numbers appear first within the category</p>
            </div>

            <!-- Checkboxes -->
            <div class="space-y-2">
              <div class="flex items-center">
                <input
                  id="is_required"
                  v-model="form.is_required"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label for="is_required" class="ml-2 block text-sm text-gray-700">
                  Required question (alumni must answer)
                </label>
              </div>

              <div class="flex items-center">
                <input
                  id="is_active"
                  v-model="form.is_active"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label for="is_active" class="ml-2 block text-sm text-gray-700">
                  Active (visible to alumni)
                </label>
              </div>
            </div>
          </div>

          <!-- Error Display -->
          <div v-if="submitError" class="bg-red-50 border border-red-200 rounded-md p-3">
            <p class="text-sm text-red-800">{{ submitError }}</p>
          </div>

          <!-- Actions -->
          <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              @click="$emit('close')"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <svg
                v-if="loading"
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
              {{ loading ? 'Saving...' : (isEditing ? 'Update Question' : 'Create Question') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </teleport>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { surveyService } from '@/services/surveyService'

export default {
  name: 'QuestionModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    question: {
      type: Object,
      default: null
    },
    categories: {
      type: Array,
      default: () => []
    },
    selectedCategory: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const loading = ref(false)
    const submitError = ref(null)
    const errors = ref({})
    const questionTypes = ref(surveyService.getQuestionTypes())
    
    const form = ref({
      category: '',
      question_text: '',
      question_type: '',
      options: ['', ''],
      is_required: false,
      min_value: null,
      max_value: null,
      max_length: null,
      placeholder_text: '',
      help_text: '',
      order: 1,
      is_active: true
    })

    const isEditing = computed(() => !!props.question)
    
    const requiresOptions = computed(() => {
      return ['radio', 'checkbox', 'select'].includes(form.value.question_type)
    })

    // Watch for question prop changes
    watch(
      () => props.question,
      (newQuestion) => {
        if (newQuestion) {
          form.value = {
            category: newQuestion.category || '',
            question_text: newQuestion.question_text || '',
            question_type: newQuestion.question_type || '',
            options: newQuestion.options ? [...newQuestion.options] : ['', ''],
            is_required: newQuestion.is_required || false,
            min_value: newQuestion.min_value || null,
            max_value: newQuestion.max_value || null,
            max_length: newQuestion.max_length || null,
            placeholder_text: newQuestion.placeholder_text || '',
            help_text: newQuestion.help_text || '',
            order: newQuestion.order || 1,
            is_active: newQuestion.is_active ?? true
          }
        } else {
          resetForm()
        }
      },
      { immediate: true }
    )

    // Watch for selected category
    watch(
      () => props.selectedCategory,
      (category) => {
        if (category && !props.question) {
          form.value.category = category.id
        }
      },
      { immediate: true }
    )

    // Watch show prop to reset form when modal opens
    watch(
      () => props.show,
      (show) => {
        if (show && !props.question) {
          resetForm()
          if (props.selectedCategory) {
            form.value.category = props.selectedCategory.id
          }
        }
        if (show) {
          errors.value = {}
          submitError.value = null
        }
      }
    )

    // Watch question type changes
    watch(
      () => form.value.question_type,
      (newType) => {
        // Reset type-specific fields when question type changes
        if (newType === 'rating') {
          form.value.min_value = 1
          form.value.max_value = 5
        } else if (!requiresOptions.value) {
          form.value.options = ['', '']
        }
        
        if (newType !== 'number' && newType !== 'rating') {
          form.value.min_value = null
          form.value.max_value = null
        }
        
        if (!['text', 'textarea'].includes(newType)) {
          form.value.max_length = null
        }
      }
    )

    const resetForm = () => {
      form.value = {
        category: '',
        question_text: '',
        question_type: '',
        options: ['', ''],
        is_required: false,
        min_value: null,
        max_value: null,
        max_length: null,
        placeholder_text: '',
        help_text: '',
        order: 1,
        is_active: true
      }
      errors.value = {}
      submitError.value = null
    }

    const addOption = () => {
      form.value.options.push('')
    }

    const removeOption = (index) => {
      if (form.value.options.length > 2) {
        form.value.options.splice(index, 1)
      }
    }

    const validateForm = () => {
      const validation = surveyService.validateQuestionData(form.value)
      errors.value = validation.errors
      return validation.isValid
    }

    const handleSubmit = async () => {
      if (!validateForm()) {
        return
      }

      try {
        loading.value = true
        submitError.value = null

        const questionData = { ...form.value }
        
        // Clean up options for non-choice questions
        if (!requiresOptions.value) {
          delete questionData.options
        } else {
          // Filter out empty options
          questionData.options = questionData.options.filter(opt => opt.trim())
        }

        // Clean up null values
        Object.keys(questionData).forEach(key => {
          if (questionData[key] === null || questionData[key] === '') {
            delete questionData[key]
          }
        })

        if (isEditing.value) {
          await surveyService.updateQuestion(props.question.id, questionData)
        } else {
          await surveyService.createQuestion(questionData)
        }

        emit('saved')
      } catch (error) {
        console.error('Error saving question:', error)
        
        if (error.response?.data) {
          const errorData = error.response.data
          
          if (typeof errorData === 'object') {
            errors.value = {}
            Object.keys(errorData).forEach(field => {
              if (field in form.value) {
                errors.value[field] = Array.isArray(errorData[field]) 
                  ? errorData[field][0] 
                  : errorData[field]
              } else {
                submitError.value = Array.isArray(errorData[field]) 
                  ? errorData[field][0] 
                  : errorData[field]
              }
            })
          } else {
            submitError.value = errorData.detail || errorData.message || 'Failed to save question'
          }
        } else {
          submitError.value = 'Network error. Please check your connection and try again.'
        }
      } finally {
        loading.value = false
      }
    }

    return {
      form,
      loading,
      submitError,
      errors,
      questionTypes,
      isEditing,
      requiresOptions,
      addOption,
      removeOption,
      handleSubmit
    }
  }
}
</script>
