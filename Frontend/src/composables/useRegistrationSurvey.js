import { ref } from 'vue'
import { surveyService } from '@/services/surveyService'

export function useRegistrationSurvey() {
  const loading = ref(false)
  const error = ref(null)
  const surveyCategories = ref([])
  const surveyResponses = ref({})
  const surveyErrors = ref({})

  // Load registration survey categories and questions
  const loadRegistrationSurvey = async () => {
    try {
      loading.value = true
      error.value = null

      // Load registration survey questions (public endpoint)
      const response = await surveyService.getRegistrationSurveyQuestions()
      surveyCategories.value = response.data || []

      // Initialize responses for checkbox questions
      initializeResponses()

    } catch (err) {
      error.value = 'Failed to load survey questions. Please try again later.'
      console.error('Error loading registration survey:', err)
    } finally {
      loading.value = false
    }
  }

  // Initialize responses for checkbox questions
  const initializeResponses = () => {
    surveyCategories.value.forEach(categoryData => {
      categoryData.questions?.forEach(question => {
        if (question.question_type === 'checkbox' && !surveyResponses.value[question.id]) {
          surveyResponses.value[question.id] = []
        }
      })
    })
  }

  // Update responses for a specific category
  const updateCategoryResponses = (categoryResponses) => {
    Object.assign(surveyResponses.value, categoryResponses)
  }

  // Validate required questions for a category
  const validateCategory = (categoryId) => {
    let isValid = true
    const errors = {}

    // Find the category data
    const categoryData = surveyCategories.value.find(cat => cat.category.id === categoryId)
    if (!categoryData) return true

    categoryData.questions?.forEach(question => {
      // Skip validation for questions that are not visible due to conditional logic
      if (!isQuestionVisible(question)) {
        return
      }

      if (question.is_required) {
        const value = surveyResponses.value[question.id]

        if (value === null || value === undefined || value === '' ||
            (Array.isArray(value) && value.length === 0)) {
          errors[question.id] = 'This field is required'
          isValid = false
        }
      }

      // Type-specific validation
      if (question.question_type === 'email' && surveyResponses.value[question.id]) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(surveyResponses.value[question.id])) {
          errors[question.id] = 'Please enter a valid email address'
          isValid = false
        }
      }

      if (question.question_type === 'number' && surveyResponses.value[question.id] !== null &&
          surveyResponses.value[question.id] !== undefined && surveyResponses.value[question.id] !== '') {
        const value = parseFloat(surveyResponses.value[question.id])
        if (question.min_value !== null && value < question.min_value) {
          errors[question.id] = `Value must be at least ${question.min_value}`
          isValid = false
        }
        if (question.max_value !== null && value > question.max_value) {
          errors[question.id] = `Value must be at most ${question.max_value}`
          isValid = false
        }
      }
    })

    surveyErrors.value = { ...surveyErrors.value, ...errors }
    return isValid
  }

  // Check if a question should be visible based on conditional logic
  const isQuestionVisible = (question) => {
    // Always show questions without dependencies
    if (!question.depends_on_question_id || !question.depends_on_value) {
      return true
    }

    // Get the parent question response
    const parentResponse = surveyResponses.value[question.depends_on_question_id]

    // Hide if no response yet
    if (parentResponse === undefined || parentResponse === null) {
      return false
    }

    // Parse the depends_on_value (it's stored as JSON string)
    let requiredValues = []
    try {
      requiredValues = JSON.parse(question.depends_on_value)
    } catch {
      // If not valid JSON, treat as single value
      requiredValues = [question.depends_on_value]
    }

    // For yes_no questions, handle boolean values
    if (typeof parentResponse === 'boolean') {
      return requiredValues.includes(parentResponse)
    }

    // For other types, convert to string for comparison
    return requiredValues.includes(String(parentResponse))
  }

  // Get survey responses in the format expected by backend
  const getSurveyResponsesForSubmission = () => {
    const responses = []

    Object.entries(surveyResponses.value).forEach(([questionId, responseData]) => {
      if (responseData !== null && responseData !== undefined && responseData !== '') {
        responses.push({
          question: parseInt(questionId),
          response_data: responseData
        })
      }
    })

    return responses
  }

  // Clear all survey data
  const clearSurveyData = () => {
    surveyCategories.value = []
    surveyResponses.value = {}
    surveyErrors.value = {}
  }

  return {
    loading,
    error,
    surveyCategories,
    surveyResponses,
    surveyErrors,
    loadRegistrationSurvey,
    updateCategoryResponses,
    validateCategory,
    getSurveyResponsesForSubmission,
    clearSurveyData,
    isQuestionVisible
  }
}
