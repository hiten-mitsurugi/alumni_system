<script setup>
/*
  NOTE: "category" == "section"

  - The backend model and API use the name `SurveyCategory` and expect
    payload keys like `category` (an integer id). Example create payload:
      { "category": 3, "question_text": "...", ... }

  - The frontend UI uses the friendlier term "section" for the same
    concept. This component accepts `selectedCategoryId` (the id of the
    currently-selected section) and writes it into `form.category` so the
    backend receives the expected field.

  - If you prefer developer-facing names like `selectedSectionId`, it's
    fine to rename props/variables in the UI for clarity, but map them to
    `category` in the request payload when calling the API.

  - Keep this comment in place to avoid confusion between UI wording and
    the API/model naming.
*/

import { ref, computed, watch } from 'vue'
import { X, Plus, Trash2 } from 'lucide-vue-next'
import surveyService from '@/services/surveyService'
import { useThemeStore } from '@/stores/theme'

const props = defineProps({
  question: {
    type: Object,
    default: null
  },
  selectedCategoryId: {
    type: Number,
    default: null
  },
  categories: {
    type: Array,
    default: () => []
  },
  questions: {
    type: Array,
    default: () => []
  },
  questionsLength: {
    type: Number,
    default: 0
  },
  isDragging: Boolean,
  draggedModal: String,
  modalPosition: {
    type: Object,
    default: () => ({ x: 0, y: 0 })
  }
})

const emit = defineEmits(['close', 'save', 'startDrag', 'resetPosition'])

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isAdminDark?.())

const form = ref({
  id: null,
  category: null,
  question_text: '',
  question_type: 'text',
  options: [],
  is_required: true,
  order: 0,
  is_active: true,
  placeholder_text: '',
  help_text: '',
  min_value: null,
  max_value: null,
  max_length: null,
  depends_on_question: null,
  depends_on_value: ''
})

const questionTypes = [
  { value: 'text', label: 'Short Text', hasOptions: false },
  { value: 'textarea', label: 'Long Text', hasOptions: false },
  { value: 'number', label: 'Number', hasOptions: false },
  { value: 'year', label: 'Year (YYYY)', hasOptions: false },
  { value: 'email', label: 'Email', hasOptions: false },
  { value: 'date', label: 'Date', hasOptions: false },
  { value: 'radio', label: 'Single Choice', hasOptions: true },
  { value: 'checkbox', label: 'Multiple Choice', hasOptions: true },
  { value: 'select', label: 'Dropdown', hasOptions: true },
  { value: 'rating', label: 'Rating Scale', hasOptions: false },
  { value: 'yes_no', label: 'Yes/No', hasOptions: false }
]

const availableQuestions = computed(() => {
  const available = props.questions.filter(q => {
    if (q.id === form.value.id) return false
    if (q.question_type === 'yes_no') return true
    if (q.question_type === 'radio' && q.options && Array.isArray(q.options)) {
      const options = q.options.map(opt => opt.toLowerCase().trim())
      return options.includes('yes') && options.includes('no') && options.length === 2
    }
    return false
  })
  
  // Debug: Log available questions for conditional logic
  console.log('🔍 Available questions for conditional logic:', available.map(q => ({
    id: q.id,
    text: q.question_text?.substring(0, 40),
    type: q.question_type
  })))
  
  return available
})

// Generate year options (current year down to 1950)
const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  const startYear = 1950
  const years = []
  for (let year = currentYear + 1; year >= startYear; year--) {
    years.push(year)
  }
  return years
})

// Default max year for new year questions
const defaultMaxYear = computed(() => new Date().getFullYear() + 1)

// Initialize form
const initializeForm = () => {
  if (props.question) {
    const questionData = {
      ...props.question,
      options: props.question.options ? [...props.question.options] : [],
      category: props.question.category || props.selectedCategoryId,
      depends_on_question: props.question.depends_on_question || null,
      depends_on_value: props.question.depends_on_value || ''
    }
    
    console.log('🔄 Initializing form with question:', {
      id: questionData.id,
      text: questionData.question_text?.substring(0, 40),
      depends_on_question: questionData.depends_on_question,
      depends_on_value: questionData.depends_on_value
    })
    
    form.value = questionData
  } else {
    form.value = {
      id: null,
      category: props.selectedCategoryId,
      question_text: '',
      question_type: 'text',
      options: [],
      is_required: true,
      order: props.questionsLength,
      is_active: true,
      placeholder_text: '',
      help_text: '',
      min_value: null,
      max_value: null,
      max_length: null,
      depends_on_question: null,
      depends_on_value: ''
    }
    console.log('🆕 Initializing new question form')
  }
}

initializeForm()

// Watch for question prop changes (when editing different questions)
watch(() => props.question, (newQuestion) => {
  initializeForm()
}, { deep: true })

// Watch for selectedCategoryId changes when creating new questions
watch(() => props.selectedCategoryId, (newCategoryId) => {
  if (!props.question && newCategoryId) {
    form.value.category = newCategoryId
  }
})

const addOption = () => {
  if (form.value && form.value.options) {
    form.value.options.push('')
  }
}

const removeOption = (index) => {
  if (form.value && form.value.options) {
    form.value.options.splice(index, 1)
  }
}

const saveQuestion = async () => {
  try {
    // Prepare payload - clean up conditional logic if not set
    const payload = {
      ...form.value,
      // If no depends_on_question, clear depends_on_value
      depends_on_value: form.value.depends_on_question ? form.value.depends_on_value : ''
    }
    
    console.log('📤 Sending question data:', payload)
    
    if (form.value.id) {
      await surveyService.updateQuestion(form.value.id, payload)
    } else {
      await surveyService.createQuestion(payload)
    }
    emit('save')
    emit('close')
  } catch (error) {
    console.error('Error saving question:', error)
    console.error('Error response data:', error.response?.data)
    if (error.response?.status === 400) {
      const errorData = error.response.data
      
      // Log all validation errors
      console.error('Validation errors:', errorData)
      
      // Check for specific field errors
      if (errorData.question_type) {
        alert(`Question Type Error: ${Array.isArray(errorData.question_type) ? errorData.question_type[0] : errorData.question_type}`)
      } else if (errorData.category && Array.isArray(errorData.category)) {
        alert(errorData.category[0])
      } else if (typeof errorData.category === 'string') {
        alert(errorData.category)
      } else if (errorData.non_field_errors) {
        alert(errorData.non_field_errors[0])
      } else {
        alert('Failed to save question. Please check your input and try again.')
      }
    } else {
      alert('An error occurred while saving the question. Please try again.')
    }
  }
}
</script>

<template>
  <div
    class="fixed inset-0 overflow-y-auto h-full w-full flex items-center justify-center p-4"
    style="z-index: 1100;"
    @click.stop="emit('close')"
  >
    <div 
      :class="[
        'draggable-modal relative rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden',
        isDark ? 'bg-gray-800' : 'bg-white',
        isDragging && draggedModal === 'question' ? 'dragging' : ''
      ]"
      data-modal="question"
      @click.stop
      :style="{ transform: `translate(${modalPosition.x}px, ${modalPosition.y}px)` }"
    >
      <div 
        :class="[
          'bg-gradient-to-r from-orange-600 to-orange-500 p-6 select-none flex items-center justify-between',
          isDragging && draggedModal === 'question' ? 'cursor-grabbing' : 'cursor-move'
        ]"
        @mousedown="emit('startDrag', $event, 'question')"
      >
        <div>
          <h3 class="text-xl font-bold text-white flex items-center gap-2">
            {{ question ? 'Edit Question' : 'Create New Question' }}
          </h3>
          <p class="text-orange-100 text-sm mt-1">
            {{ question ? 'Update question details' : 'Add a new survey question' }}
          </p>
        </div>
        <button
          @click="emit('resetPosition', 'question')"
          class="text-orange-200 hover:text-white p-1 rounded transition-colors"
          title="Reset position"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
      
      <form @submit.prevent="saveQuestion" class="p-6 space-y-6 max-h-[calc(90vh-120px)] overflow-y-auto">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="md:col-span-2">
            <label :class="['block text-sm font-semibold mb-2', isDark ? 'text-gray-300' : 'text-slate-700']">Question Text *</label>
            <textarea
              v-model="form.question_text"
              required
              rows="3"
              placeholder="Enter your survey question"
              :class="[
                'w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors resize-none',
                isDark ? 'bg-gray-700 border-gray-600 text-white' : 'border-slate-300'
              ]"
            ></textarea>
          </div>
          
          <div class="md:col-span-2">
            <label :class="['block text-sm font-semibold mb-2', isDark ? 'text-gray-300' : 'text-slate-700']">Question Type *</label>
            <select
              v-model="form.question_type"
              required
              :class="[
                'w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors',
                isDark ? 'bg-gray-700 border-gray-600 text-white' : 'border-slate-300'
              ]"
            >
              <option v-for="type in questionTypes" :key="type.value" :value="type.value">
                {{ type.label }}
              </option>
            </select>
          </div>
          
          <div>
            <label :class="['block text-sm font-semibold mb-2', isDark ? 'text-gray-300' : 'text-slate-700']">Section*</label>
            <select
              v-model="form.category"
              required
              :class="[
                'w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors',
                isDark ? 'bg-gray-700 border-gray-600 text-white' : 'border-slate-300'
              ]"
            >
              <option :value="null">Select a Section</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>

          <div>
            <label :class="['block text-sm font-semibold mb-2', isDark ? 'text-gray-300' : 'text-slate-700']">Display Order</label>
            <input
              v-model.number="form.order"
              type="number"
              min="0"
              :class="[
                'w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors',
                isDark ? 'bg-gray-700 border-gray-600 text-white' : 'border-slate-300'
              ]"
            />
          </div>
        </div>
        
        <!-- Options for choice questions -->
        <div v-if="questionTypes.find(t => t.value === form.question_type)?.hasOptions" :class="['p-4 rounded-lg', isDark ? 'bg-gray-700' : 'bg-slate-50']">
          <label :class="['block text-sm font-semibold mb-3', isDark ? 'text-gray-300' : 'text-slate-700']">Answer Options *</label>
          <div class="space-y-3">
            <div v-for="(option, index) in form.options" :key="index" class="flex gap-2">
              <input
                v-model="form.options[index]"
                type="text"
                :placeholder="`Option ${index + 1}`"
                required
                :class="[
                  'flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500',
                  isDark ? 'bg-gray-600 border-gray-500 text-white' : 'border-slate-300'
                ]"
              />
              <button
                type="button"
                @click="removeOption(index)"
                :class="[
                  'p-2 rounded-lg transition-colors',
                  isDark ? 'bg-gray-600 text-red-400 hover:bg-gray-500' : 'bg-red-50 text-red-600 hover:bg-red-100'
                ]"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
            <button
              type="button"
              @click="addOption"
              :class="[
                'w-full px-4 py-2 border-2 border-dashed rounded-lg transition-colors flex items-center justify-center gap-2',
                isDark ? 'border-gray-600 text-gray-400 hover:border-gray-500 hover:text-gray-300' : 'border-slate-300 text-slate-600 hover:border-slate-400 hover:text-slate-700'
              ]"
            >
              <Plus class="w-4 h-4" />
              Add Option
            </button>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label :class="['block text-sm font-semibold mb-2', isDark ? 'text-gray-300' : 'text-slate-700']">Placeholder Text</label>
            <input
              v-model="form.placeholder_text"
              type="text"
              :class="[
                'w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors',
                isDark ? 'bg-gray-700 border-gray-600 text-white' : 'border-slate-300'
              ]"
            />
          </div>

          <div>
            <label :class="['block text-sm font-semibold mb-2', isDark ? 'text-gray-300' : 'text-slate-700']">Help Text</label>
            <input
              v-model="form.help_text"
              type="text"
              :class="[
                'w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors',
                isDark ? 'bg-gray-700 border-gray-600 text-white' : 'border-slate-300'
              ]"
            />
          </div>
        </div>

        <!-- Year Range Section -->
        <div v-if="form.question_type === 'year'" :class="['grid grid-cols-1 md:grid-cols-2 gap-6 p-4 rounded-lg border', isDark ? 'bg-gray-700 border-gray-600' : 'bg-green-50 border-green-200']">
          <div>
            <label :class="['block text-sm font-semibold mb-2', isDark ? 'text-gray-300' : 'text-green-900']">Minimum Year</label>
            <select
              v-model.number="form.min_value"
              :class="[
                'w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors',
                isDark ? 'bg-gray-600 border-gray-500 text-white' : 'border-green-300 bg-white'
              ]"
            >
              <option :value="null">No minimum</option>
              <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}</option>
            </select>
          </div>

          <div>
            <label :class="['block text-sm font-semibold mb-2', isDark ? 'text-gray-300' : 'text-green-900']">Maximum Year</label>
            <select
              v-model.number="form.max_value"
              :class="[
                'w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors',
                isDark ? 'bg-gray-600 border-gray-500 text-white' : 'border-green-300 bg-white'
              ]"
            >
              <option :value="null">Use current year + 1 ({{ defaultMaxYear }})</option>
              <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}</option>
            </select>
          </div>
        </div>

        <!-- Rating Scale Min/Max Section -->
        <div v-if="form.question_type === 'rating'" :class="['grid grid-cols-1 md:grid-cols-2 gap-6 p-4 rounded-lg border', isDark ? 'bg-gray-700 border-gray-600' : 'bg-indigo-50 border-indigo-200']">
          <div>
            <label :class="['block text-sm font-semibold mb-2', isDark ? 'text-gray-300' : 'text-indigo-900']">Minimum Value</label>
            <input
              v-model.number="form.min_value"
              type="number"
              placeholder="e.g., 1"
              :class="[
                'w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors',
                isDark ? 'bg-gray-600 border-gray-500 text-white' : 'border-indigo-300 bg-white'
              ]"
            />
          </div>

          <div>
            <label :class="['block text-sm font-semibold mb-2', isDark ? 'text-gray-300' : 'text-indigo-900']">Maximum Value</label>
            <input
              v-model.number="form.max_value"
              type="number"
              placeholder="e.g., 5"
              :class="[
                'w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors',
                isDark ? 'bg-gray-600 border-gray-500 text-white' : 'border-indigo-300 bg-white'
              ]"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Conditional Logic Section -->
          <div :class="['space-y-4 p-4 rounded-lg border', isDark ? 'bg-gray-700 border-gray-600' : 'bg-orange-50 border-orange-200']">
            <h4 :class="['font-semibold text-sm', isDark ? 'text-gray-300' : 'text-orange-900']">Conditional Logic</h4>
            <div>
              <label :class="['block text-xs font-medium mb-2', isDark ? 'text-gray-400' : 'text-orange-700']">Show this question only if:</label>
              <select
                v-model="form.depends_on_question"
                :class="[
                  'w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500',
                  isDark ? 'bg-gray-600 border-gray-500 text-white' : 'border-orange-300 bg-white'
                ]"
              >
                <option :value="null">No condition (always show)</option>
                <option v-for="q in availableQuestions" :key="q.id" :value="q.id">
                  {{ q.question_text.substring(0, 50) }}{{ q.question_text.length > 50 ? '...' : '' }}
                </option>
              </select>
            </div>
            <div v-if="form.depends_on_question">
              <label :class="['block text-xs font-medium mb-2', isDark ? 'text-gray-400' : 'text-orange-700']">Answer is:</label>
              <select
                v-model="form.depends_on_value"
                :class="[
                  'w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500',
                  isDark ? 'bg-gray-600 border-gray-500 text-white' : 'border-orange-300 bg-white'
                ]"
              >
                <option value="Yes">Yes</option>
                <option value="No">No</option>
              </select>
            </div>
          </div>
        </div>
        
        <div :class="['flex items-center gap-6 p-4 rounded-lg', isDark ? 'bg-gray-700' : 'bg-slate-50']">
          <div class="flex items-center">
            <input
              v-model="form.is_required"
              type="checkbox"
              id="is_required"
              class="h-4 w-4 text-orange-600 focus:ring-orange-500 border-slate-300 rounded cursor-pointer"
            />
            <label for="is_required" :class="['ml-3 block text-sm font-medium cursor-pointer', isDark ? 'text-gray-300' : 'text-slate-700']">
              Required Question
            </label>
          </div>
          
          <div class="flex items-center">
            <input
              v-model="form.is_active"
              type="checkbox"
              id="is_active_q"
              class="h-4 w-4 text-orange-600 focus:ring-orange-500 border-slate-300 rounded cursor-pointer"
            />
            <label for="is_active_q" :class="['ml-3 block text-sm font-medium cursor-pointer', isDark ? 'text-gray-300' : 'text-slate-700']">
              Active Question
            </label>
          </div>
        </div>
        
        <div :class="['flex justify-end gap-3 pt-6 border-t', isDark ? 'border-gray-700' : 'border-slate-200']">
          <button
            type="button"
            @click="emit('close')"
            :class="[
              'px-6 py-3 text-sm font-medium rounded-lg transition-colors cursor-pointer',
              isDark ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' : 'text-slate-700 bg-slate-100 hover:bg-slate-200'
            ]"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="px-6 py-3 text-sm font-medium text-white bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-600 rounded-lg transition-all duration-200 cursor-pointer shadow-md hover:shadow-lg"
          >
            {{ question ? 'Update Question' : 'Create Question' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
