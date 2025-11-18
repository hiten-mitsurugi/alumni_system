import { ref } from 'vue'
import surveyService from '@/services/surveyService'

export function useQuestions() {
  const questions = ref([])
  const loading = ref(false)
  const error = ref(null)

  const loadQuestions = async (categoryId = null) => {
    loading.value = true
    error.value = null
    try {
      const response = await surveyService.getQuestions(categoryId)
      questions.value = response.data
    } catch (err) {
      error.value = err.message
      console.error('Error loading questions:', err)
    } finally {
      loading.value = false
    }
  }

  const createQuestion = async (questionData) => {
    loading.value = true
    error.value = null
    try {
      const response = await surveyService.createQuestion(questionData)
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Error creating question:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  const updateQuestion = async (questionId, questionData) => {
    loading.value = true
    error.value = null
    try {
      const response = await surveyService.updateQuestion(questionId, questionData)
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Error updating question:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  const deleteQuestion = async (questionId) => {
    loading.value = true
    error.value = null
    try {
      await surveyService.deleteQuestion(questionId)
      return true
    } catch (err) {
      error.value = err.message
      console.error('Error deleting question:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    questions,
    loading,
    error,
    loadQuestions,
    createQuestion,
    updateQuestion,
    deleteQuestion
  }
}
