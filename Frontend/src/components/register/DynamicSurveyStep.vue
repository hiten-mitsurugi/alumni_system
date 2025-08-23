<template>
  <div>
    <!-- Category Header -->
    <div class="mb-6">
      <h4 class="text-lg font-semibold text-gray-800 mb-2">{{ category.name }}</h4>
      <p v-if="category.description" class="text-sm text-gray-600">{{ category.description }}</p>
    </div>

    <!-- Questions -->
    <div class="space-y-6">
      <div
        v-for="question in props.questions"
        :key="question.id"
        v-show="isQuestionVisible(question)"
        class="space-y-3"
      >
        <!-- Question Label -->
        <label class="block text-sm font-medium text-gray-700">
          {{ question.question_text }}
          <span v-if="question.is_required" class="text-red-500">*</span>
        </label>

        <!-- Help Text -->
        <p v-if="question.help_text" class="text-sm text-gray-600">{{ question.help_text }}</p>

        <!-- Question Input Based on Type -->
        <div class="mt-2">
          <!-- Text Input -->
          <input
            v-if="question.question_type === 'text'"
            v-model="localResponses[question.id]"
            type="text"
            :placeholder="question.placeholder_text"
            :maxlength="question.max_length"
            :required="question.is_required"
            class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            :class="{ 'border-red-500': errors[question.id] }"
          />

          <!-- Textarea -->
          <textarea
            v-else-if="question.question_type === 'textarea'"
            v-model="localResponses[question.id]"
            rows="4"
            :placeholder="question.placeholder_text"
            :maxlength="question.max_length"
            :required="question.is_required"
            class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
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
            class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            :class="{ 'border-red-500': errors[question.id] }"
          />

          <!-- Email Input -->
          <input
            v-else-if="question.question_type === 'email'"
            v-model="localResponses[question.id]"
            type="email"
            :placeholder="question.placeholder_text"
            :required="question.is_required"
            class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            :class="{ 'border-red-500': errors[question.id] }"
          />

          <!-- Date Input -->
          <input
            v-else-if="question.question_type === 'date'"
            v-model="localResponses[question.id]"
            type="date"
            :required="question.is_required"
            class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
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
            class="space-y-2"
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
            class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
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
            <div class="flex items-center justify-between text-sm text-gray-600">
              <span>{{ question.min_value }}</span>
              <span>{{ question.max_value }}</span>
            </div>
            <div class="flex items-center space-x-2">
              <div
                v-for="rating in getRatingRange(question)"
                :key="rating"
                class="flex flex-col items-center"
              >
                <input
                  :id="`${question.id}_${rating}`"
                  v-model.number="localResponses[question.id]"
                  type="radio"
                  :value="rating"
                  :name="`question_${question.id}`"
                  :required="question.is_required"
                  class="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                />
                <label
                  :for="`${question.id}_${rating}`"
                  class="text-sm text-gray-700 mt-1 cursor-pointer"
                >
                  {{ rating }}
                </label>
              </div>
            </div>
            <div v-if="localResponses[question.id]" class="text-center">
              <span class="text-sm font-medium text-blue-600">
                Selected: {{ localResponses[question.id] }}
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
        </div>

        <!-- Error Message -->
        <p v-if="errors[question.id]" class="text-sm text-red-600">{{ errors[question.id] }}</p>
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

// Simple function to check if question should be visible
const isQuestionVisible = (question) => {
  // Always show questions without dependencies
  if (!question.depends_on_question_id || !question.depends_on_value) {
    return true
  }
  
  // Get the parent question response
  const parentResponse = localResponses[question.depends_on_question_id]
  
  // Hide if no response yet
  if (parentResponse === undefined || parentResponse === null) {
    return false
  }
  
  // Simple string comparison like the static components
  return String(parentResponse) === String(question.depends_on_value)
}

// Initialize checkbox arrays and clear conditional question responses
props.questions.forEach(question => {
  if (question.question_type === 'checkbox' && !localResponses[question.id]) {
    localResponses[question.id] = []
  }
  
  // Clear responses for conditional questions that shouldn't be visible initially
  if (question.depends_on_question_id && question.depends_on_value) {
    const dependentResponse = localResponses[question.depends_on_question_id]
    if (!dependentResponse || String(dependentResponse) !== question.depends_on_value) {
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
    // Clear conditional question responses when parent question changes
    props.questions.forEach(question => {
      if (question.depends_on_question_id && question.depends_on_value) {
        const dependentResponse = newResponses[question.depends_on_question_id]
        const requiredValue = String(question.depends_on_value)
        const responseStr = String(dependentResponse || '')
        
        // Clear response if condition is not met
        if (!dependentResponse || responseStr !== requiredValue) {
          if (question.question_type === 'checkbox') {
            newResponses[question.id] = []
          } else {
            delete newResponses[question.id]
          }
        }
      }
    })
    
    emit('update:responses', { ...newResponses })
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

// Watch for external responses changes
watch(
  () => props.responses,
  (newResponses) => {
    Object.assign(localResponses, newResponses)
  },
  { deep: true }
)
</script>
