import { ref, computed } from 'vue'
import surveyService from '@/services/surveyService'

export function useQuestionManagement(questions, categories, selectedCategory) {
  // State
  const showQuestionModal = ref(false)
  const questionForm = ref({
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

  // Computed: Available questions for conditional logic
  const availableQuestions = computed(() => {
    return questions.value.filter(q => {
      if (q.id === questionForm.value.id) return false
      if (q.question_type === 'yes_no') return true
      if (q.question_type === 'radio' && q.options && Array.isArray(q.options)) {
        const options = q.options.map(opt => opt.toLowerCase().trim())
        return options.includes('yes') && options.includes('no') && options.length === 2
      }
      return false
    })
  })

  // Open modal for create or edit
  const openQuestionModal = (question = null) => {
    if (question) {
      questionForm.value = {
        ...question,
        options: question.options ? [...question.options] : []
      }
    } else {
      questionForm.value = {
        id: null,
        category: selectedCategory.value?.id || null,
        question_text: '',
        question_type: 'text',
        options: [],
        is_required: true,
        order: questions.value.length,
        is_active: true,
        placeholder_text: '',
        help_text: '',
        min_value: null,
        max_value: null,
        max_length: null,
        depends_on_question: null,
        depends_on_value: ''
      }
    }
    showQuestionModal.value = true
  }

  // Save question (create or update)
  const saveQuestion = async () => {
    try {
      if (questionForm.value.id) {
        await surveyService.updateQuestion(questionForm.value.id, questionForm.value)
      } else {
        await surveyService.createQuestion(questionForm.value)
      }
      closeQuestionModal()
      await loadQuestions()
      await loadCategories()
    } catch (error) {
      console.error('Error saving question:', error)
      if (error.response?.status === 400) {
        const errorData = error.response.data
        if (errorData.category && Array.isArray(errorData.category)) {
          alert(errorData.category[0])
        } else if (typeof errorData.category === 'string') {
          alert(errorData.category)
        } else {
          alert('Failed to save question. Please check your input and try again.')
        }
      } else {
        alert('An error occurred while saving the question. Please try again.')
      }
    }
  }

  // Close modal and reset form
  const closeQuestionModal = () => {
    showQuestionModal.value = false
    questionForm.value = {
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
    }
  }

  // Delete question
  const deleteQuestion = async (id) => {
    if (confirm('Are you sure you want to delete this question and all its responses?')) {
      try {
        const questionIndex = questions.value.findIndex(q => q.id === id)
        const removedQuestion = questions.value[questionIndex]
        if (questionIndex !== -1) {
          questions.value.splice(questionIndex, 1)
        }

        await surveyService.deleteQuestion(id)
        await loadQuestions()
        await loadCategories()
      } catch (error) {
        console.error('Error deleting question:', error)
        if (removedQuestion && questionIndex !== -1) {
          questions.value.splice(questionIndex, 0, removedQuestion)
        }
      }
    }
  }

  // Add option to choice question
  const addOption = () => {
    if (questionForm.value && questionForm.value.options) {
      questionForm.value.options.push('')
    }
  }

  // Remove option from choice question
  const removeOption = (index) => {
    if (questionForm.value && questionForm.value.options) {
      questionForm.value.options.splice(index, 1)
    }
  }

  // Stubs for functions that will be provided by parent
  const loadQuestions = async () => {}
  const loadCategories = async () => {}

  return {
    showQuestionModal,
    questionForm,
    availableQuestions,
    openQuestionModal,
    saveQuestion,
    closeQuestionModal,
    deleteQuestion,
    addOption,
    removeOption
  }
}
