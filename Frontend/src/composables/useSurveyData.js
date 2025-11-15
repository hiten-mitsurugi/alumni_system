import { ref } from 'vue'
import surveyService from '@/services/surveyService'

export function useSurveyData() {
  const loading = ref(true)
  const categories = ref([])
  const questions = ref([])
  const analytics = ref(null)

  const loadCategories = async () => {
    try {
      loading.value = true
      const response = await surveyService.getCategories()
      categories.value = response.data
    } catch (error) {
      console.error('Error loading categories:', error)
    } finally {
      loading.value = false
    }
  }

  const loadQuestions = async (categoryId = null) => {
    try {
      const response = await surveyService.getQuestions(categoryId)
      questions.value = response.data
    } catch (error) {
      console.error('Error loading questions:', error)
    }
  }

  const loadAnalytics = async () => {
    try {
      const response = await surveyService.getAnalytics()
      analytics.value = response.data
    } catch (error) {
      console.error('Error loading analytics:', error)
    }
  }

  const deleteCategory = async (id) => {
    if (confirm('Are you sure you want to delete this category and all its questions?')) {
      try {
        const categoryIndex = categories.value.findIndex(cat => cat.id === id)
        const removedCategory = categories.value[categoryIndex]
        if (categoryIndex !== -1) {
          categories.value.splice(categoryIndex, 1)
        }
        
        await surveyService.deleteCategory(id)
        await loadCategories()
      } catch (error) {
        console.error('Error deleting category:', error)
        if (removedCategory && categoryIndex !== -1) {
          categories.value.splice(categoryIndex, 0, removedCategory)
        }
      }
    }
  }

  const deleteQuestion = async (id, selectedCategoryId = null) => {
    if (confirm('Are you sure you want to delete this question and all its responses?')) {
      try {
        const questionIndex = questions.value.findIndex(q => q.id === id)
        const removedQuestion = questions.value[questionIndex]
        if (questionIndex !== -1) {
          questions.value.splice(questionIndex, 1)
        }
        
        await surveyService.deleteQuestion(id)
        await loadQuestions(selectedCategoryId)
        await loadCategories()
      } catch (error) {
        console.error('Error deleting question:', error)
        if (removedQuestion && questionIndex !== -1) {
          questions.value.splice(questionIndex, 0, removedQuestion)
        }
      }
    }
  }

  const getQuestionCountByCategory = (categoryId) => {
    return questions.value.filter(q => q.category === categoryId).length
  }

  const getResponseCountByCategory = (categoryId) => {
    const categoryQuestionIds = questions.value
      .filter(q => q.category === categoryId)
      .map(q => q.id)
    return 0 // Will be populated from analytics data when available
  }

  return {
    loading,
    categories,
    questions,
    analytics,
    loadCategories,
    loadQuestions,
    loadAnalytics,
    deleteCategory,
    deleteQuestion,
    getQuestionCountByCategory,
    getResponseCountByCategory
  }
}
