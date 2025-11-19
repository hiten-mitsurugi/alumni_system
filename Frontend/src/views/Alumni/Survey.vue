<script setup>
import { ref, onMounted, computed } from 'vue'
import { 
  CheckCircle, 
  Clock, 
  FileText, 
  ChevronLeft, 
  ChevronRight,
  Send,
  AlertCircle,
  BarChart3
} from 'lucide-vue-next'
import surveyService from '@/services/surveyService'
import { useThemeStore } from '@/stores/theme'

// Theme store
const themeStore = useThemeStore()

// Reactive data
const loading = ref(true)
const currentFormIndex = ref(null) // null = show form cards, number = show form
const currentCategoryIndex = ref(null) // which category within the form
const surveyData = ref([]) // Array of forms with their categories
const responses = ref({})
const progress = ref(null)
const submitting = ref(false)
const showResults = ref(false)
const showCardGrid = ref(true) // Toggle between card grid and form view

// Computed properties
const currentForm = computed(() => {
  if (currentFormIndex.value === null) return null
  return surveyData.value[currentFormIndex.value] || null
})

const currentCategory = computed(() => {
  if (!currentForm.value || currentCategoryIndex.value === null) return null
  return currentForm.value.categories[currentCategoryIndex.value] || null
})

// Get answered questions count for a form
const getFormProgress = (formIndex) => {
  const form = surveyData.value[formIndex]
  if (!form || !form.categories || !Array.isArray(form.categories)) {
    return { answered: 0, total: 0, percentage: 0 }
  }
  
  let totalQuestions = 0
  let answeredQuestions = 0
  
  form.categories.forEach(cat => {
    if (cat && cat.questions && Array.isArray(cat.questions)) {
      totalQuestions += cat.questions.length
      answeredQuestions += cat.questions.filter(q => {
        const response = responses.value[q.id]
        return response !== undefined && response !== '' && response !== null
      }).length
    }
  })
  
  return {
    answered: answeredQuestions,
    total: totalQuestions,
    percentage: totalQuestions > 0 ? Math.round((answeredQuestions / totalQuestions) * 100) : 0
  }
}

// Get form status
const getFormStatus = (formIndex) => {
  const progress = getFormProgress(formIndex)
  if (progress.answered === 0) return 'not-started'
  if (progress.answered === progress.total) return 'complete'
  return 'in-progress'
}

// Get category progress within current form
const getCategoryProgress = (categoryIndex) => {
  if (!currentForm.value || !currentForm.value.categories || !Array.isArray(currentForm.value.categories)) {
    return { answered: 0, total: 0, percentage: 0 }
  }
  
  const category = currentForm.value.categories[categoryIndex]
  if (!category || !category.questions || !Array.isArray(category.questions)) {
    return { answered: 0, total: 0, percentage: 0 }
  }
  
  const totalQuestions = category.questions.length
  const answeredQuestions = category.questions.filter(q => {
    const response = responses.value[q.id]
    return response !== undefined && response !== '' && response !== null
  }).length
  
  return {
    answered: answeredQuestions,
    total: totalQuestions,
    percentage: totalQuestions > 0 ? Math.round((answeredQuestions / totalQuestions) * 100) : 0
  }
}

// Get category status
const getCategoryStatus = (categoryIndex) => {
  const progress = getCategoryProgress(categoryIndex)
  if (progress.answered === 0) return 'not-started'
  if (progress.answered === progress.total) return 'complete'
  return 'in-progress'
}

const currentQuestions = computed(() => {
  return currentCategory.value?.questions || []
})

const totalCategories = computed(() => {
  return currentForm.value?.categories.length || 0
})

const canGoNext = computed(() => {
  if (!currentCategory.value) return false
  
  // Check if all required questions in current category are answered
  const requiredQuestions = currentQuestions.value.filter(q => q.is_required)
  return requiredQuestions.every(q => responses.value[q.id] !== undefined && responses.value[q.id] !== '')
})

const isLastCategory = computed(() => {
  return currentCategoryIndex.value === totalCategories.value - 1
})

const overallProgress = computed(() => {
  let totalQuestions = 0
  let answeredQuestions = 0
  
  if (Array.isArray(surveyData.value)) {
    surveyData.value.forEach(form => {
      if (form && form.categories && Array.isArray(form.categories)) {
        form.categories.forEach(category => {
          if (category && category.questions && Array.isArray(category.questions)) {
            totalQuestions += category.questions.length
            answeredQuestions += category.questions.filter(q => {
              return responses.value[q.id] !== undefined && responses.value[q.id] !== '' && responses.value[q.id] !== null
            }).length
          }
        })
      }
    })
  }
  
  return totalQuestions > 0 ? Math.round((answeredQuestions / totalQuestions) * 100) : 0
})

// Load survey data
const loadSurveyData = async () => {
  try {
    const response = await surveyService.getActiveSurveyQuestions()
    console.log('📋 Survey data received from backend:', response.data)
    console.log('📊 Data structure:', JSON.stringify(response.data, null, 2))
    surveyData.value = response.data
  } catch (error) {
    console.error('Error loading survey questions:', error)
  }
}

const loadProgress = async () => {
  try {
    const response = await surveyService.getSurveyProgress()
    progress.value = response.data
  } catch (error) {
    console.error('Error loading progress:', error)
  }
}

const loadExistingResponses = async () => {
  try {
    const response = await surveyService.getMyResponses()
    const existingResponses = {}
    
    response.data.forEach(responseItem => {
      if (responseItem.response_data) {
        existingResponses[responseItem.question.id] = responseItem.response_data.value || responseItem.response_data
      }
    })
    
    responses.value = existingResponses
  } catch (error) {
    console.error('Error loading existing responses:', error)
  }
}

// Navigation
const openForm = (formIndex) => {
  currentFormIndex.value = formIndex
  currentCategoryIndex.value = 0 // Start with first category
  showCardGrid.value = false
}

const closeForm = () => {
  currentFormIndex.value = null
  currentCategoryIndex.value = null
  showCardGrid.value = true
}

const goToCategory = (index) => {
  if (currentForm.value && index >= 0 && index < currentForm.value.categories.length) {
    currentCategoryIndex.value = index
  }
}

const nextCategory = () => {
  if (!isLastCategory.value) {
    currentCategoryIndex.value++
  }
}

const previousCategory = () => {
  if (currentCategoryIndex.value > 0) {
    currentCategoryIndex.value--
  }
}

// Response handling
const updateResponse = (questionId, value) => {
  // Validate question ID before storing
  if (questionId === null || questionId === undefined || questionId === '' || isNaN(parseInt(questionId))) {
    console.warn('⚠️ Invalid question ID in updateResponse:', questionId, 'value:', value)
    return
  }
  responses.value[questionId] = value
}

// Get response value for display
const getResponseValue = (questionId) => {
  return responses.value[questionId] || ''
}

const handleCheckboxChange = (questionId, option, checked) => {
  let currentValue = getResponseValue(questionId)
  
  if (!Array.isArray(currentValue)) {
    currentValue = []
  }
  
  if (checked) {
    if (!currentValue.includes(option)) {
      currentValue.push(option)
    }
  } else {
    const index = currentValue.indexOf(option)
    if (index > -1) {
      currentValue.splice(index, 1)
    }
  }
  
  updateResponse(questionId, currentValue)
}

// Submit survey
const submitSurvey = async () => {
  submitting.value = true
  
  try {
    // Prepare response data (filter out empty responses and invalid question IDs)
    const responseData = {
      responses: Object.entries(responses.value)
        .filter(([questionId, value]) => {
          // Filter out empty, null, or undefined values
          if (value === null || value === undefined || value === '') {
            console.warn('⚠️ Filtering out empty value for question:', questionId)
            return false
          }
          // Filter out invalid question IDs (must be a valid number)
          if (questionId === null || questionId === undefined || questionId === 'null' || questionId === 'undefined') {
            console.warn('⚠️ Filtering out null/undefined question ID:', questionId, 'with value:', value)
            return false
          }
          const parsedId = parseInt(questionId)
          if (isNaN(parsedId) || parsedId <= 0) {
            console.warn('⚠️ Filtering out invalid question ID:', questionId, 'parsed as:', parsedId, 'with value:', value)
            return false
          }
          return true
        })
        .map(([questionId, value]) => ({
          question_id: parseInt(questionId),
          response_data: value
        }))
    }
    
    // Check if we have any responses to submit
    if (responseData.responses.length === 0) {
      alert('Please answer at least one question before submitting.')
      return
    }
    
    console.log('� Raw Object.entries(responses.value):', Object.entries(responses.value))
    console.log('�🚀 Submitting survey data:', JSON.stringify(responseData, null, 2))
    console.log('📋 Current responses:', responses.value)
    
    await surveyService.submitSurveyResponse(responseData)
    showResults.value = true
    await loadProgress() // Refresh progress
  } catch (error) {
    console.error('Error submitting survey:', error)
    console.error('❌ Error response:', error.response?.data)
    console.error('❌ Error status:', error.response?.status)
    console.error('❌ Full error:', error)
    alert(`Error submitting survey: ${error.response?.data?.message || error.message}. Please try again.`)
  } finally {
    submitting.value = false
  }
}

// Question type renderers
const renderTextInput = (question) => {
  return {
    type: 'input',
    inputType: question.question_type === 'email' ? 'email' : 
               question.question_type === 'number' ? 'number' : 'text',
    placeholder: question.placeholder_text || `Enter your ${question.question_text.toLowerCase()}`
  }
}

const renderTextarea = (question) => {
  return {
    type: 'textarea',
    placeholder: question.placeholder_text || 'Enter your response...',
    rows: 4
  }
}

const renderSelect = (question) => {
  return {
    type: 'select',
    options: question.get_options_list ? question.get_options_list() : (question.options || [])
  }
}

const renderRadio = (question) => {
  return {
    type: 'radio',
    options: question.get_options_list ? question.get_options_list() : (question.options || [])
  }
}

const renderCheckbox = (question) => {
  return {
    type: 'checkbox',
    options: question.get_options_list ? question.get_options_list() : (question.options || [])
  }
}

const renderRating = (question) => {
  return {
    type: 'rating',
    min: question.min_value || 1,
    max: question.max_value || 5
  }
}

const renderYesNo = (question) => {
  return {
    type: 'radio',
    options: ['Yes', 'No']
  }
}

const renderDate = (question) => {
  return {
    type: 'input',
    inputType: 'date'
  }
}

// Get question config for rendering
const getQuestionConfig = (question) => {
  switch (question.question_type) {
    case 'text':
    case 'email':
    case 'number':
      return renderTextInput(question)
    case 'textarea':
      return renderTextarea(question)
    case 'select':
      return renderSelect(question)
    case 'radio':
      return renderRadio(question)
    case 'checkbox':
      return renderCheckbox(question)
    case 'rating':
      return renderRating(question)
    case 'yes_no':
      return renderYesNo(question)
    case 'date':
      return renderDate(question)
    default:
      return renderTextInput(question)
  }
}

// Initialize
onMounted(async () => {
  await Promise.all([
    loadSurveyData(),
    loadProgress(),
    loadExistingResponses()
  ])
  loading.value = false
})
</script>

<template>
  <div :class="themeStore.isDarkMode ? 'min-h-screen bg-gray-900 py-8' : 'min-h-screen bg-gray-50 py-8'">
    <div class="max-w-7xl mx-auto px-4">
      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>

      <!-- Card Grid View - Show Forms -->
      <div v-else-if="showCardGrid && surveyData.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="(form, formIndex) in surveyData"
          :key="form?.template?.id || formIndex"
          @click="openForm(formIndex)"
          :class="[
            'cursor-pointer rounded-lg shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden',
            themeStore.isDarkMode ? 'bg-gray-800 hover:bg-gray-750 border border-gray-700' : 'bg-white hover:border-blue-300 border border-gray-200'
          ]"
        >
          <!-- Card Header -->
          <div :class="[
            'p-4 border-b',
            getFormStatus(formIndex) === 'complete' ? 'bg-green-50 border-green-200' :
            getFormStatus(formIndex) === 'in-progress' ? 'bg-yellow-50 border-yellow-200' :
            themeStore.isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-orange-100 border-gray-200'
          ]">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <h3 :class="[
                  'font-semibold text-lg mb-1',
                  themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                ]">
                  {{ form?.template?.name || 'Untitled Form' }}
                </h3>
                <p :class="[
                  'text-sm',
                  themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'
                ]">
                  {{ form?.categories?.length || 0 }} section{{ (form?.categories?.length || 0) !== 1 ? 's' : '' }}
                </p>
              </div>
              
              <!-- Status Badge -->
              <div :class="[
                'flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium',
                getFormStatus(formIndex) === 'complete' ? 'bg-green-100 text-green-700' :
                getFormStatus(formIndex) === 'in-progress' ? 'bg-yellow-100 text-yellow-700' :
                'bg-gray-100 text-gray-600'
              ]">
                <CheckCircle v-if="getFormStatus(formIndex) === 'complete'" class="w-3 h-3" />
                <Clock v-else-if="getFormStatus(formIndex) === 'in-progress'" class="w-3 h-3" />
                <FileText v-else class="w-3 h-3" />
                <span class="capitalize">{{ getFormStatus(formIndex).replace('-', ' ') }}</span>
              </div>
            </div>
          </div>
          
          <!-- Card Body -->
          <div class="p-4">
            <p v-if="form?.template?.description" :class="[
              'text-sm mb-4 line-clamp-3',
              themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
            ]">
              {{ form.template.description }}
            </p>
            
            <!-- Progress Bar -->
            <div class="space-y-2">
              <div class="flex items-center justify-between text-sm">
                <span :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'">Progress</span>
                <span :class="[
                  'font-medium',
                  getFormProgress(formIndex).percentage === 100 ? 'text-green-600' :
                  getFormProgress(formIndex).percentage > 0 ? 'text-yellow-600' :
                  themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
                ]">
                  {{ getFormProgress(formIndex).answered }}/{{ getFormProgress(formIndex).total }}
                </span>
              </div>
              
              <div :class="[
                'w-full rounded-full h-2',
                themeStore.isDarkMode ? 'bg-gray-700' : 'bg-gray-200'
              ]">
                <div
                  :class="[
                    'h-2 rounded-full transition-all duration-300',
                    getFormProgress(formIndex).percentage === 100 ? 'bg-green-500' :
                    getFormProgress(formIndex).percentage > 0 ? 'bg-yellow-500' :
                    'bg-blue-500'
                  ]"
                  :style="{ width: `${getFormProgress(formIndex).percentage}%` }"
                ></div>
              </div>
            </div>
          </div>
          
          <!-- Card Footer -->
          <div :class="[
            'px-4 py-3 border-t flex items-center justify-between',
            themeStore.isDarkMode ? 'bg-gray-750 border-gray-700' : 'bg-gray-50 border-gray-200'
          ]">
            <span :class="[
              'text-sm font-medium',
              themeStore.isDarkMode ? 'text-blue-400' : 'text-blue-600'
            ]">
              Click to {{ getFormStatus(formIndex) === 'not-started' ? 'start' : 'continue' }}
            </span>
            <ChevronRight :class="[
              'w-4 h-4',
              themeStore.isDarkMode ? 'text-blue-400' : 'text-blue-600'
            ]" />
          </div>
        </div>
      </div>

      <!-- Survey Complete -->
      <div v-else-if="showResults" :class="themeStore.isDarkMode ? 'bg-gray-800 rounded-lg shadow-md p-8 text-center' : 'bg-white rounded-lg shadow-md p-8 text-center'">
        <CheckCircle class="w-16 h-16 text-green-600 mx-auto mb-4" />
        <h2 :class="themeStore.isDarkMode ? 'text-2xl font-bold text-white mb-2' : 'text-2xl font-bold text-gray-900 mb-2'">Survey Completed!</h2>
        <p :class="themeStore.isDarkMode ? 'text-gray-300 mb-6' : 'text-gray-600 mb-6'">
          Thank you for taking the time to complete the Alumni Tracer Survey. 
          Your responses will help improve our programs and services.
        </p>
        
        <div v-if="progress" :class="themeStore.isDarkMode ? 'bg-gray-700 rounded-lg p-4 mb-6' : 'bg-gray-50 rounded-lg p-4 mb-6'">
          <h3 :class="themeStore.isDarkMode ? 'font-semibold text-white mb-2' : 'font-semibold text-gray-900 mb-2'">Your Survey Statistics</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'">Questions Answered:</span>
              <span class="font-semibold ml-2">{{ progress.answered_questions }}/{{ progress.total_questions }}</span>
            </div>
            <div>
              <span :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'">Completion Rate:</span>
              <span class="font-semibold ml-2">{{ progress.progress_percentage }}%</span>
            </div>
            <div>
              <span :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'">Status:</span>
              <span :class="[
                'font-semibold ml-2',
                progress.is_complete ? 'text-green-600' : 'text-yellow-600'
              ]">
                {{ progress.is_complete ? 'Complete' : 'In Progress' }}
              </span>
            </div>
          </div>
        </div>
        
        <button
          @click="$router.push('/alumni')"
          class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Return to Dashboard
        </button>
      </div>

      <!-- Survey Questions -->
      <div v-else-if="currentForm && currentCategory" class="max-w-3xl mx-auto">
        <div :class="themeStore.isDarkMode ? 'bg-gray-800 rounded-lg shadow-md' : 'bg-white rounded-lg shadow-md'">
          <!-- Back to Forms Button -->
          <div class="p-4 border-b" :class="themeStore.isDarkMode ? 'border-gray-700' : 'border-gray-200'">
            <button
              @click="closeForm"
              :class="[
                'flex items-center gap-2 px-4 py-2 rounded-lg transition-colors',
                themeStore.isDarkMode 
                  ? 'bg-gray-700 text-gray-200 hover:bg-gray-600' 
                  : 'bg-orange-600 text-white hover:bg-orange-700'
              ]"
            >
              <ChevronLeft class="w-4 h-4" />
              Back to Forms
            </button>
          </div>
        
        <!-- Form & Category Header -->
        <div :class="themeStore.isDarkMode ? 'bg-gray-700 p-6 border-b border-gray-600' : 'bg-orange-100 p-6 border-b'">
          <div class="mb-2">
            <span :class="[
              'text-sm font-medium px-2 py-1 rounded',
              themeStore.isDarkMode ? 'bg-gray-600 text-gray-300' : 'bg-orange-200 text-orange-800'
            ]">
              {{ currentForm?.template?.name || 'Survey Form' }}
            </span>
          </div>
          <h2 :class="themeStore.isDarkMode ? 'text-xl font-bold text-white' : 'text-xl font-bold text-gray-900'">{{ currentCategory?.category?.name || 'Section' }}</h2>
          <p v-if="currentCategory?.category?.description" :class="themeStore.isDarkMode ? 'text-gray-300 mt-2' : 'text-gray-600 mt-2'">
            {{ currentCategory.category.description }}
          </p>
          <div :class="themeStore.isDarkMode ? 'mt-4 text-sm text-gray-400' : 'mt-4 text-sm text-gray-600'">
            Section {{ currentCategoryIndex + 1 }} of {{ totalCategories }} • 
            {{ currentQuestions.length }} questions
          </div>
        </div>

        <!-- Questions -->
        <div class="p-6 space-y-8">
          <div
            v-for="question in currentQuestions"
            :key="question.id"
            :class="themeStore.isDarkMode ? 'border-b border-gray-700 pb-8 last:border-b-0' : 'border-b border-gray-100 pb-8 last:border-b-0'"
          >
            <div class="mb-4">
              <label :class="themeStore.isDarkMode ? 'block text-lg font-medium text-white mb-2' : 'block text-lg font-medium text-gray-900 mb-2'">
                {{ question.question_text }}
                <span v-if="question.is_required" class="text-red-500">*</span>
              </label>
              <p v-if="question.help_text" :class="themeStore.isDarkMode ? 'text-sm text-gray-400 mb-3' : 'text-sm text-gray-600 mb-3'">
                {{ question.help_text }}
              </p>
            </div>

            <!-- Text Input -->
            <template v-if="getQuestionConfig(question).type === 'input'">
              <input
                :type="getQuestionConfig(question).inputType"
                :placeholder="getQuestionConfig(question).placeholder"
                :value="getResponseValue(question.id)"
                @input="updateResponse(question.id, $event.target.value)"
                :class="themeStore.isDarkMode 
                  ? 'w-full px-4 py-3 border border-gray-600 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent' 
                  : 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'"
                :required="question.is_required"
              />
            </template>

            <!-- Textarea -->
            <template v-else-if="getQuestionConfig(question).type === 'textarea'">
              <textarea
                :placeholder="getQuestionConfig(question).placeholder"
                :rows="getQuestionConfig(question).rows"
                :value="getResponseValue(question.id)"
                @input="updateResponse(question.id, $event.target.value)"
                :class="themeStore.isDarkMode 
                  ? 'w-full px-4 py-3 border border-gray-600 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent' 
                  : 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'"
                :required="question.is_required"
              ></textarea>
            </template>

            <!-- Select -->
            <template v-else-if="getQuestionConfig(question).type === 'select'">
              <select
                :value="getResponseValue(question.id)"
                @change="updateResponse(question.id, $event.target.value)"
                :class="themeStore.isDarkMode 
                  ? 'w-full px-4 py-3 border border-gray-600 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent' 
                  : 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'"
                :required="question.is_required"
              >
                <option value="">Please select an option</option>
                <option
                  v-for="option in getQuestionConfig(question).options"
                  :key="option"
                  :value="option"
                >
                  {{ option }}
                </option>
              </select>
            </template>

            <!-- Radio -->
            <template v-else-if="getQuestionConfig(question).type === 'radio'">
              <div class="space-y-3">
                <label
                  v-for="option in getQuestionConfig(question).options"
                  :key="option"
                  class="flex items-center gap-3 cursor-pointer"
                >
                  <input
                    type="radio"
                    :name="`question_${question.id}`"
                    :value="option"
                    :checked="getResponseValue(question.id) === option"
                    @change="updateResponse(question.id, option)"
                    class="w-4 h-4 text-blue-600 focus:ring-blue-500"
                  />
                  <span :class="themeStore.isDarkMode ? 'text-gray-200' : 'text-gray-900'">{{ option }}</span>
                </label>
              </div>
            </template>

            <!-- Checkbox -->
            <template v-else-if="getQuestionConfig(question).type === 'checkbox'">
              <div class="space-y-3">
                <label
                  v-for="option in getQuestionConfig(question).options"
                  :key="option"
                  class="flex items-center gap-3 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    :value="option"
                    :checked="Array.isArray(getResponseValue(question.id)) ? getResponseValue(question.id).includes(option) : false"
                    @change="handleCheckboxChange(question.id, option, $event.target.checked)"
                    class="w-4 h-4 text-blue-600 focus:ring-blue-500"
                  />
                  <span :class="themeStore.isDarkMode ? 'text-gray-200' : 'text-gray-900'">{{ option }}</span>
                </label>
              </div>
            </template>

            <!-- Rating -->
            <template v-else-if="getQuestionConfig(question).type === 'rating'">
              <div class="flex items-center gap-2">
                <span :class="themeStore.isDarkMode ? 'text-sm text-gray-400' : 'text-sm text-gray-600'">{{ getQuestionConfig(question).min }}</span>
                <div class="flex gap-1">
                  <button
                    v-for="rating in Array.from({length: getQuestionConfig(question).max - getQuestionConfig(question).min + 1}, (_, i) => i + getQuestionConfig(question).min)"
                    :key="rating"
                    @click="updateResponse(question.id, rating)"
                    :class="[
                      'w-10 h-10 rounded-full border-2 transition-colors',
                      getResponseValue(question.id) === rating
                        ? 'bg-blue-600 border-blue-600 text-white'
                        : (themeStore.isDarkMode 
                          ? 'border-gray-600 text-gray-400 hover:border-blue-400' 
                          : 'border-gray-300 text-gray-600 hover:border-blue-400')
                    ]"
                  >
                    {{ rating }}
                  </button>
                </div>
                <span :class="themeStore.isDarkMode ? 'text-sm text-gray-400' : 'text-sm text-gray-600'">{{ getQuestionConfig(question).max }}</span>
              </div>
            </template>
          </div>
        </div>

        <!-- Navigation -->
        <div :class="themeStore.isDarkMode ? 'bg-gray-700 px-6 py-4 flex justify-between items-center' : 'bg-gray-50 px-6 py-4 flex justify-between items-center'">
          <button
            @click="previousCategory"
            :disabled="currentCategoryIndex === 0"
            :class="[
              'flex items-center gap-2 px-4 py-2 rounded-lg transition-colors',
              currentCategoryIndex === 0
                ? (themeStore.isDarkMode ? 'bg-gray-800 text-gray-600 cursor-not-allowed' : 'bg-gray-100 text-gray-400 cursor-not-allowed')
                : (themeStore.isDarkMode ? 'bg-gray-600 text-gray-200 hover:bg-gray-500' : 'bg-gray-200 text-gray-700 hover:bg-gray-300')
            ]"
          >
            <ChevronLeft class="w-4 h-4" />
            Previous
          </button>

          <div :class="themeStore.isDarkMode ? 'text-sm text-gray-300' : 'text-sm text-gray-600'">
            {{ currentCategoryIndex + 1 }} of {{ totalCategories }}
          </div>

          <button
            v-if="!isLastCategory"
            @click="nextCategory"
            :disabled="!canGoNext"
            :class="[
              'flex items-center gap-2 px-4 py-2 rounded-lg transition-colors',
              canGoNext
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : (themeStore.isDarkMode ? 'bg-gray-800 text-gray-600 cursor-not-allowed' : 'bg-gray-100 text-gray-400 cursor-not-allowed')
            ]"
          >
            Next
            <ChevronRight class="w-4 h-4" />
          </button>

          <button
            v-else
            @click="submitSurvey"
            :disabled="submitting || !canGoNext"
            :class="[
              'flex items-center gap-2 px-6 py-2 rounded-lg transition-colors',
              canGoNext && !submitting
                ? 'bg-green-600 text-white hover:bg-green-700'
                : (themeStore.isDarkMode ? 'bg-gray-800 text-gray-600 cursor-not-allowed' : 'bg-gray-100 text-gray-400 cursor-not-allowed')
            ]"
          >
            <Send class="w-4 h-4" />
            {{ submitting ? 'Submitting...' : 'Submit Survey' }}
          </button>
        </div>
        </div>
      </div>

      <!-- No Survey Data -->
      <div v-else-if="!loading && surveyData.length === 0" :class="themeStore.isDarkMode ? 'bg-gray-800 rounded-lg shadow-md p-8 text-center' : 'bg-white rounded-lg shadow-md p-8 text-center'">
        <AlertCircle class="w-16 h-16 text-yellow-600 mx-auto mb-4" />
        <h2 :class="themeStore.isDarkMode ? 'text-2xl font-bold text-white mb-2' : 'text-2xl font-bold text-gray-900 mb-2'">No Survey Available</h2>
        <p :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'">
          There are currently no active surveys available. Please check back later.
        </p>
      </div>
    </div>
  </div>
</template>
