import { ref } from 'vue'
import surveyService from '@/services/surveyService'

export function useSurveyManagementLogic() {
  // State
  const loading = ref(true)
  const activeTab = ref('categories')
  const categories = ref([])
  const questions = ref([])
  const analytics = ref(null)

  // Question types constant
  const questionTypes = [
    { value: 'text', label: 'Short Text', hasOptions: false },
    { value: 'textarea', label: 'Long Text', hasOptions: false },
    { value: 'number', label: 'Number', hasOptions: false },
    { value: 'email', label: 'Email', hasOptions: false },
    { value: 'date', label: 'Date', hasOptions: false },
    { value: 'radio', label: 'Single Choice', hasOptions: true },
    { value: 'checkbox', label: 'Multiple Choice', hasOptions: true },
    { value: 'select', label: 'Dropdown', hasOptions: true },
    { value: 'rating', label: 'Rating Scale', hasOptions: false },
    { value: 'yes_no', label: 'Yes/No', hasOptions: false }
  ]

  // Load all categories
  const loadCategories = async () => {
    try {
      const response = await surveyService.getCategories()
      categories.value = response.data
    } catch (error) {
      console.error('Error loading categories:', error)
    }
  }

  // Load all questions (optionally filter by category)
  const loadQuestions = async (categoryId = null) => {
    try {
      const response = await surveyService.getQuestions(categoryId)
      questions.value = response.data
    } catch (error) {
      console.error('Error loading questions:', error)
    }
  }

  // Load analytics data
  const loadAnalytics = async () => {
    try {
      const response = await surveyService.getAnalytics()
      analytics.value = response.data
    } catch (error) {
      console.error('Error loading analytics:', error)
    }
  }

  return {
    loading,
    activeTab,
    categories,
    questions,
    analytics,
    questionTypes,
    loadCategories,
    loadQuestions,
    loadAnalytics
  }
}
