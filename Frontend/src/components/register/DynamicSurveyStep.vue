<template>
  <div>
    <!-- Category Header -->
    <div class="mb-6">
      <h4 class="text-lg font-semibold text-gray-800 mb-2">{{ category.name }}</h4>
      <p v-if="category.description" class="text-sm text-gray-600">{{ category.description }}</p>
    </div>

    <!-- Questions Grid - Single column layout -->
    <div class="space-y-4">
      <div
        v-for="question in props.questions"
        :key="question.id"
        v-show="getQuestionVisibility[question.id]"
      >
        <!-- Question Label -->
        <label class="block text-sm font-medium text-gray-700">
          {{ question.question_text }}
          <span v-if="question.is_required" class="text-red-500">*</span>
        </label>

        <!-- Help Text -->
        <p v-if="question.help_text" class="text-xs text-gray-600 mb-1">{{ question.help_text }}</p>

        <!-- Question Input Based on Type -->
        <div>
          <!-- Text Input -->
          <input
            v-if="question.question_type === 'text'"
            v-model="localResponses[question.id]"
            type="text"
            :placeholder="question.placeholder_text"
            :maxlength="question.max_length"
            :required="question.is_required"
            class="mt-1 w-full border rounded-md p-2"
            :class="{ 'border-red-500': errors[question.id] }"
          />

          <!-- Textarea -->
          <textarea
            v-else-if="question.question_type === 'textarea'"
            v-model="localResponses[question.id]"
            rows="3"
            :placeholder="question.placeholder_text"
            :maxlength="question.max_length"
            :required="question.is_required"
            class="mt-1 w-full border rounded-md p-2"
            :class="{ 'border-red-500': errors[question.id] }"
          ></textarea>

          <!-- Number Input -->
          <input
            v-else-if="question.question_type === 'number'"
            v-model.number="localResponses[question.id]"
            type="number"
            :min="question.min_value"
            :max="question.max_value"
            :placeholder="question.placeholder_text"
            :required="question.is_required"
            class="mt-1 w-full border rounded-md p-2"
            :class="{ 'border-red-500': errors[question.id] }"
          />

          <!-- Year Input -->
          <select
            v-else-if="question.question_type === 'year'"
            v-model.number="localResponses[question.id]"
            :required="question.is_required"
            class="mt-1 w-full border rounded-md p-2"
            :class="{ 'border-red-500': errors[question.id] }"
          >
            <option :value="null">{{ question.placeholder_text || 'Select a year' }}</option>
            <option 
              v-for="year in generateYearRange(question.min_value || 1950, question.max_value || (new Date().getFullYear() + 1))" 
              :key="year" 
              :value="year"
            >
              {{ year }}
            </option>
          </select>

          <!-- Email Input -->
          <input
            v-else-if="question.question_type === 'email'"
            v-model="localResponses[question.id]"
            type="email"
            :placeholder="question.placeholder_text"
            :required="question.is_required"
            class="mt-1 w-full border rounded-md p-2"
            :class="{ 'border-red-500': errors[question.id] }"
          />

          <!-- Date Input -->
          <input
            v-else-if="question.question_type === 'date'"
            v-model="localResponses[question.id]"
            type="date"
            :required="question.is_required"
            class="mt-1 w-full border rounded-md p-2"
            :class="{ 'border-red-500': errors[question.id] }"
          />

          <!-- Radio Buttons -->
          <div
            v-else-if="question.question_type === 'radio'"
            class="mt-1 space-y-2"
          >
            <div
              v-for="option in question.options"
              :key="option"
              class="flex items-center"
            >
              <input
                :id="`${question.id}_${option}`"
                v-model="localResponses[question.id]"
                type="radio"
                :value="option"
                :name="`question_${question.id}`"
                :required="question.is_required"
                class="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500 mr-2"
              />
              <label
                :for="`${question.id}_${option}`"
                class="text-sm text-gray-700 cursor-pointer"
              >
                {{ option }}
              </label>
            </div>
          </div>

          <!-- Checkboxes -->
          <div
            v-else-if="question.question_type === 'checkbox'"
            class="mt-1 space-y-2"
          >
            <div
              v-for="option in question.options"
              :key="option"
              class="flex items-center"
            >
              <input
                :id="`${question.id}_${option}`"
                v-model="localResponses[question.id]"
                type="checkbox"
                :value="option"
                class="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 mr-2"
              />
              <label
                :for="`${question.id}_${option}`"
                class="text-sm text-gray-700 cursor-pointer"
              >
                {{ option }}
              </label>
            </div>
          </div>

          <!-- Select Dropdown -->
          <select
            v-else-if="question.question_type === 'select'"
            v-model="localResponses[question.id]"
            :required="question.is_required"
            class="mt-1 w-full border rounded-md p-2"
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
            class="mt-2"
          >
            <!-- Labels for min and max -->
            <div class="flex items-center justify-between text-xs text-gray-500 mb-3">
              <span class="font-medium">{{ question.min_value }} - Low</span>
              <span class="font-medium">{{ question.max_value }} - High</span>
            </div>
            
            <!-- Rating options -->
            <div class="flex items-center justify-start gap-2 flex-wrap">
              <div
                v-for="rating in getRatingRange(question)"
                :key="rating"
                class="flex flex-col items-center gap-1"
              >
                <input
                  :id="`${question.id}_${rating}`"
                  v-model.number="localResponses[question.id]"
                  type="radio"
                  :value="rating"
                  :name="`question_${question.id}`"
                  :required="question.is_required"
                  class="h-5 w-5 text-orange-600 border-gray-300 focus:ring-orange-500 cursor-pointer"
                />
                <label
                  :for="`${question.id}_${rating}`"
                  class="text-sm font-medium text-gray-700 cursor-pointer text-center w-8"
                >
                  {{ rating }}
                </label>
              </div>
            </div>
          </div>

          <!-- Yes/No -->
          <div
            v-else-if="question.question_type === 'yes_no'"
            class="mt-1 flex items-center space-x-6"
          >
            <div class="flex items-center">
              <input
                :id="`${question.id}_yes`"
                v-model="localResponses[question.id]"
                type="radio"
                :value="true"
                :name="`question_${question.id}`"
                :required="question.is_required"
                class="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500 mr-2"
              />
              <label
                :for="`${question.id}_yes`"
                class="text-sm text-gray-700 cursor-pointer"
              >
                Yes
              </label>
            </div>
            <div class="flex items-center">
              <input
                :id="`${question.id}_no`"
                v-model="localResponses[question.id]"
                type="radio"
                :value="false"
                :name="`question_${question.id}`"
                :required="question.is_required"
                class="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500 mr-2"
              />
              <label
                :for="`${question.id}_no`"
                class="text-sm text-gray-700 cursor-pointer"
              >
                No
              </label>
            </div>
          </div>

          <!-- File Upload -->
          <input
            v-else-if="question.question_type === 'file'"
            type="file"
            :required="question.is_required"
            class="mt-1 w-full border rounded-md p-2"
            :class="{ 'border-red-500': errors[question.id] }"
            @change="handleFileUpload(question.id, $event)"
          />
        </div>

        <!-- Error Message -->
        <p v-if="errors[question.id]" class="text-sm text-red-600 mt-1">{{ errors[question.id] }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, reactive, watch, computed } from 'vue'

const props = defineProps({
  category: {
    type: Object,
    required: true
  },
  questions: {
    type: Array,
    required: true
  },
  responses: {
    type: Object,
    default: () => ({})
  },
  errors: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:responses'])

// Helper function to generate year range for year questions
const generateYearRange = (minYear, maxYear) => {
  const years = []
  for (let year = maxYear; year >= minYear; year--) {
    years.push(year)
  }
  return years
}

// Initialize local responses
const localResponses = reactive({ ...props.responses })

// Force reactivity by watching props.responses changes
watch(
  () => props.responses,
  (newResponses) => {
    Object.assign(localResponses, newResponses)
  },
  { deep: true, immediate: true }
)

// Create a computed property for question visibility that reacts to response changes
const getQuestionVisibility = computed(() => {
  const visibility = {}
  props.questions.forEach(question => {
    // Always show questions without dependencies
    if (!question.depends_on_question_id || !question.depends_on_value) {
      visibility[question.id] = true
      return
    }
    
    // Get the parent question response
    const parentResponse = localResponses[question.depends_on_question_id]
    
    // Hide if no response yet
    if (parentResponse === undefined || parentResponse === null || parentResponse === '') {
      visibility[question.id] = false
      return
    }
    
    // Handle boolean to string conversion for yes/no questions
    let normalizedResponse = parentResponse
    let normalizedRequiredValue = question.depends_on_value
    
    // Convert boolean responses to Yes/No strings for comparison
    if (typeof parentResponse === 'boolean') {
      normalizedResponse = parentResponse ? 'Yes' : 'No'
    }
    
    // Compare values
    const isVisible = String(normalizedResponse) === String(normalizedRequiredValue)
    visibility[question.id] = isVisible
    
    // Debug log
    console.log(`Question "${question.question_text}" visibility:`, {
      questionId: question.id,
      dependsOn: question.depends_on_question_id,
      requiredValue: normalizedRequiredValue,
      actualResponse: normalizedResponse,
      originalResponse: parentResponse,
      isVisible: isVisible
    })
  })
  return visibility
})

// Simple function to check if question should be visible
const isQuestionVisible = (question) => {
  return getQuestionVisibility.value[question.id] || false
}

// Initialize checkbox arrays and clear conditional question responses
props.questions.forEach(question => {
  if (question.question_type === 'checkbox' && !localResponses[question.id]) {
    localResponses[question.id] = []
  }
  
  // Clear responses for conditional questions that shouldn't be visible initially
  if (question.depends_on_question_id && question.depends_on_value) {
    const dependentResponse = localResponses[question.depends_on_question_id]
    
    // Normalize the response for comparison
    let normalizedResponse = dependentResponse
    if (typeof dependentResponse === 'boolean') {
      normalizedResponse = dependentResponse ? 'Yes' : 'No'
    }
    
    if (!dependentResponse || String(normalizedResponse) !== String(question.depends_on_value)) {
      // Clear the response if the condition is not met
      if (question.question_type === 'checkbox') {
        localResponses[question.id] = []
      } else {
        delete localResponses[question.id]
      }
    }
  }
})

// Watch for changes and emit to parent
watch(
  localResponses,
  (newResponses) => {
    console.log('🔄 Local responses changed:', newResponses)
    emit('update:responses', { ...newResponses })
  },
  { deep: true }
)

// Separate watcher for conditional question cleanup - only when dependency changes
watch(
  () => {
    // Create an object of just the dependency values to watch
    const dependencies = {}
    props.questions.forEach(question => {
      if (question.depends_on_question_id) {
        dependencies[question.depends_on_question_id] = localResponses[question.depends_on_question_id]
      }
    })
    return dependencies
  },
  (newDependencies, oldDependencies) => {
    // Only clear responses when a parent question's value actually changes
    props.questions.forEach(question => {
      if (question.depends_on_question_id && question.depends_on_value) {
        const oldValue = oldDependencies?.[question.depends_on_question_id]
        const newValue = newDependencies[question.depends_on_question_id]
        
        // Only clear if the parent value actually changed
        if (oldValue !== newValue) {
          const dependentResponse = newValue
          
          // Normalize the response for comparison
          let normalizedResponse = dependentResponse
          if (typeof dependentResponse === 'boolean') {
            normalizedResponse = dependentResponse ? 'Yes' : 'No'
          }
          
          const requiredValue = String(question.depends_on_value)
          const responseStr = String(normalizedResponse || '')
          
          console.log(`🔍 Checking conditional question "${question.question_text}":`, {
            dependentResponse,
            normalizedResponse,
            requiredValue,
            responseStr,
            matches: responseStr === requiredValue
          })
          
          // Clear response if condition is not met
          if (!dependentResponse || responseStr !== requiredValue) {
            if (question.question_type === 'checkbox') {
              localResponses[question.id] = []
            } else {
              delete localResponses[question.id]
            }
          }
        }
      }
    })
  },
  { deep: true }
)

// Watch for visibility changes and clear hidden question responses
watch(
  getQuestionVisibility,
  (newVisibility, oldVisibility) => {
    props.questions.forEach(question => {
      // If question became hidden, clear its response
      if (oldVisibility && oldVisibility[question.id] && !newVisibility[question.id]) {
        if (question.question_type === 'checkbox') {
          localResponses[question.id] = []
        } else {
          delete localResponses[question.id]
        }
      }
    })
  },
  { deep: true }
)

// Helper function for rating ranges
const getRatingRange = (question) => {
  const range = []
  for (let i = question.min_value; i <= question.max_value; i++) {
    range.push(i)
  }
  return range
}

// Handle file upload
const handleFileUpload = (questionId, event) => {
  const file = event.target.files[0]
  if (file) {
    // For now, just store the file name
    // In a real implementation, you'd upload the file to server
    localResponses[questionId] = file.name
  }
}

// Watch for external responses changes
watch(
  () => props.responses,
  (newResponses) => {
    Object.assign(localResponses, newResponses)
  },
  { deep: true }
)
</script>
