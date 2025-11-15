<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import surveyService from '@/services/surveyService'
import { useThemeStore } from '@/stores/theme'
import CategoryAnalytics from '@/components/CategoryAnalytics.vue'
import CategoryModal from '@/components/SurveyManagement/CategoryModal.vue'
import QuestionModal from '@/components/SurveyManagement/QuestionModal.vue'
import ExportModal from '@/components/SurveyManagement/ExportModal.vue'
import CategoryQuestionsModal from '@/components/SurveyManagement/CategoryQuestionsModal.vue'
import AnalyticsModal from '@/components/SurveyManagement/AnalyticsModal.vue'
import HeaderSection from '@/components/SurveyManagement/HeaderSection.vue'
import TabNavigation from '@/components/SurveyManagement/TabNavigation.vue'
import AnalyticsView from '@/components/SurveyManagement/AnalyticsView.vue'
import LoadingState from '@/components/SurveyManagement/LoadingState.vue'
import CategoriesView from '@/components/SurveyManagement/CategoriesView.vue'
import QuestionsView from '@/components/SurveyManagement/QuestionsView.vue'

// Theme setup
const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isAdminDark?.())

// Reactive data
const loading = ref(true)
const activeTab = ref('categories')
const categories = ref([])
const questions = ref([])
const selectedCategory = ref(null)
const showCategoryModal = ref(false)
const showQuestionModal = ref(false)
const showAnalyticsModal = ref(false)
const showExportModal = ref(false)
const showCategoryQuestionsModal = ref(false)
const showCategoryAnalytics = ref(false)
const selectedCategoryForModal = ref(null)
const categoryQuestions = ref([])
const analytics = ref(null)

// Export data
const exportFormat = ref('xlsx')
const exportCategory = ref('')
const includeInactive = ref(false)
const exportDateFrom = ref('')
const exportDateTo = ref('')
const exportProfileFields = ref([
  'first_name', 'last_name', 'email', 'program', 
  'year_graduated', 'student_id', 'birth_date', 'user_type'
])
const isExporting = ref(false)

// Pagination
const currentCategoryPage = ref(1)
const currentQuestionPage = ref(1)
const itemsPerPage = 6

// Computed properties for pagination
const totalCategoryPages = computed(() => Math.ceil(categories.value.length / itemsPerPage))
const totalQuestionPages = computed(() => Math.ceil(questions.value.length / itemsPerPage))

const paginatedCategories = computed(() => {
  const start = (currentCategoryPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return categories.value.slice(start, end)
})

const paginatedQuestions = computed(() => {
  const start = (currentQuestionPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return questions.value.slice(start, end)
})

const questionsPageNumbers = computed(() => {
  const pages = []
  const total = totalQuestionPages.value
  const current = currentQuestionPage.value
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) pages.push(i)
      pages.push('...')
      pages.push(total)
    } else if (current >= total - 3) {
      pages.push(1)
      pages.push('...')
      for (let i = total - 4; i <= total; i++) pages.push(i)
    } else {
      pages.push(1)
      pages.push('...')
      for (let i = current - 1; i <= current + 1; i++) pages.push(i)
      pages.push('...')
      pages.push(total)
    }
  }
  
  return pages
})

const questionsPageButtons = computed(() => {
  return questionsPageNumbers.value.filter(page => page !== '...')
})

const questionsEllipsis = computed(() => {
  return questionsPageNumbers.value.filter(page => page === '...')
})

// Available questions for conditional logic (exclude current question being edited)
const availableQuestions = computed(() => {
  return questions.value.filter(q => {
    // Exclude current question being edited
    if (q.id === questionForm.value.id) return false
    
    // Include yes_no question type
    if (q.question_type === 'yes_no') return true
    
    // Include radio questions with exactly Yes/No options
    if (q.question_type === 'radio' && q.options && Array.isArray(q.options)) {
      const options = q.options.map(opt => opt.toLowerCase().trim())
      return options.includes('yes') && options.includes('no') && options.length === 2
    }
    
    return false
  })
})

// Pagination functions
const goToCategoryPage = (page) => {
  if (page >= 1 && page <= totalCategoryPages.value) {
    currentCategoryPage.value = page
  }
}

const goToQuestionPage = (page) => {
  if (page >= 1 && page <= totalQuestionPages.value) {
    currentQuestionPage.value = page
  }
}

// Modal data
const categoryForm = ref({
  id: null,
  name: '',
  description: '',
  order: 0,
  is_active: true,
  include_in_registration: false
})

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

// Draggable functionality
const isDragging = ref(false)
const draggedModal = ref(null)
const dragOffset = ref({ x: 0, y: 0 })
const modalPositions = ref({
  category: { x: 0, y: 0 },
  question: { x: 0, y: 0 },
  analytics: { x: 0, y: 0 },
  export: { x: 0, y: 0 },
  categoryQuestions: { x: 0, y: 0 }
})

const startDrag = (event, modalType) => {
  isDragging.value = true
  draggedModal.value = modalType
  
  const rect = event.target.closest('.draggable-modal').getBoundingClientRect()
  dragOffset.value = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }
  
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
  event.preventDefault()
}

const onDrag = (event) => {
  if (!isDragging.value || !draggedModal.value) return
  
  const modal = document.querySelector(`[data-modal="${draggedModal.value}"]`)
  if (!modal) return
  
  const newX = event.clientX - dragOffset.value.x
  const newY = event.clientY - dragOffset.value.y
  
  // Keep modal within viewport bounds
  const maxX = window.innerWidth - modal.offsetWidth
  const maxY = window.innerHeight - modal.offsetHeight
  
  const clampedX = Math.max(0, Math.min(newX, maxX))
  const clampedY = Math.max(0, Math.min(newY, maxY))
  
  modalPositions.value[draggedModal.value] = { x: clampedX, y: clampedY }
  
  modal.style.transform = `translate(${clampedX}px, ${clampedY}px)`
  modal.style.position = 'fixed'
}

const stopDrag = () => {
  isDragging.value = false
  draggedModal.value = null
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

const resetModalPosition = (modalType) => {
  modalPositions.value[modalType] = { x: 0, y: 0 }
  nextTick(() => {
    const modal = document.querySelector(`[data-modal="${modalType}"]`)
    if (modal) {
      modal.style.transform = 'translate(0px, 0px)'
      modal.style.position = 'relative'
    }
  })
}

// Load data
const loadCategories = async () => {
  try {
    const response = await surveyService.getCategories()
    categories.value = response.data
  } catch (error) {
    console.error('Error loading categories:', error)
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

// Category management
const openCategoryModal = (category = null) => {
  if (category) {
    categoryForm.value = { ...category }
  } else {
    categoryForm.value = {
      id: null,
      name: '',
      description: '',
      order: categories.value.length,
      is_active: true,
      include_in_registration: false
    }
  }
  showCategoryModal.value = true
}

const saveCategory = async () => {
  try {
    if (categoryForm.value.id) {
      await surveyService.updateCategory(categoryForm.value.id, categoryForm.value)
    } else {
      await surveyService.createCategory(categoryForm.value)
    }
    showCategoryModal.value = false
    await loadCategories()
  } catch (error) {
    console.error('Error saving category:', error)
  }
}

const deleteCategory = async (id) => {
  if (confirm('Are you sure you want to delete this category and all its questions?')) {
    try {
      // Optimistically remove from UI first (real-time update)
      const categoryIndex = categories.value.findIndex(cat => cat.id === id)
      const removedCategory = categories.value[categoryIndex]
      if (categoryIndex !== -1) {
        categories.value.splice(categoryIndex, 1)
      }
      
      // Make API call
      await surveyService.deleteCategory(id)
      
      // Reload data to ensure consistency (in background)
      await loadCategories()
    } catch (error) {
      console.error('Error deleting category:', error)
      
      // Restore the category if deletion failed
      if (removedCategory && categoryIndex !== -1) {
        categories.value.splice(categoryIndex, 0, removedCategory)
      }
    }
  }
}

// Question management
const openQuestionModal = (question = null) => {
  if (question) {
    questionForm.value = { 
      ...question,
      options: question.options ? [...question.options] : [] // Ensure options is always an array
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

const saveQuestion = async () => {
  try {

    if (questionForm.value.id) {
      await surveyService.updateQuestion(questionForm.value.id, questionForm.value)
    } else {
      await surveyService.createQuestion(questionForm.value)
    }
    closeQuestionModal()
    await loadQuestions(selectedCategory.value?.id)
    await loadCategories() // Reload categories to update counters
  } catch (error) {
    console.error('Error saving question:', error)
    
    // Handle specific error responses
    if (error.response?.status === 400) {
      const errorData = error.response.data
      if (errorData.category && Array.isArray(errorData.category)) {
        alert(errorData.category[0]) // Show the specific error message
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

const closeQuestionModal = () => {
  showQuestionModal.value = false
  // Reset form to prevent null reference issues
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

const deleteQuestion = async (id) => {
  if (confirm('Are you sure you want to delete this question and all its responses?')) {
    try {
      // Optimistically remove from UI first (real-time update)
      const questionIndex = questions.value.findIndex(q => q.id === id)
      const removedQuestion = questions.value[questionIndex]
      if (questionIndex !== -1) {
        questions.value.splice(questionIndex, 1)
      }
      
      // Make API call
      await surveyService.deleteQuestion(id)
      
      // Reload data to ensure consistency (in background)
      await loadQuestions(selectedCategory.value?.id)
      await loadCategories() // Reload categories to update counters
    } catch (error) {
      console.error('Error deleting question:', error)
      
      // Restore the question if deletion failed
      if (removedQuestion && questionIndex !== -1) {
        questions.value.splice(questionIndex, 0, removedQuestion)
      }
    }
  }
}

// Options management for choice questions
const addOption = () => {
  if (questionForm.value && questionForm.value.options) {
    questionForm.value.options.push('')
  } else {
    console.error('questionForm or options array is not properly initialized')
  }
}

const removeOption = (index) => {
  if (questionForm.value && questionForm.value.options) {
    questionForm.value.options.splice(index, 1)
  } else {
    console.error('questionForm or options array is not properly initialized')
  }
}

// Initialize
onMounted(async () => {
  await loadCategories()
  await loadQuestions() // Load ALL questions initially
  await loadAnalytics()
  loading.value = false
  
  // Add global event listeners for drag functionality
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
})

// Clean up event listeners
onUnmounted(() => {
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
})

// Watch category selection
const selectCategory = async (category) => {
  selectedCategoryForModal.value = category
  try {
    const response = await surveyService.getQuestions(category.id)
    categoryQuestions.value = response.data
    showCategoryQuestionsModal.value = true
  } catch (error) {
    console.error('Error loading category questions:', error)
  }
}

// Questions tab handler
const goToQuestionsTab = async () => {
  activeTab.value = 'questions'
  selectedCategory.value = null // Clear any category filter
  currentQuestionPage.value = 1 // Reset pagination
  await loadQuestions() // Load ALL questions
}

const handleTabChange = async (tab) => {
  if (tab === 'questions') {
    await goToQuestionsTab()
  } else {
    activeTab.value = tab
  }
}

// Export data
const exportData = async () => {
  if (isExporting.value) return
  
  try {
    isExporting.value = true
    
    const exportParams = {
      format: exportFormat.value,
      category_id: exportCategory.value || null,
      date_from: exportDateFrom.value || null,
      date_to: exportDateTo.value || null,
      include_profile_fields: exportProfileFields.value
    }
    
    const response = await surveyService.exportResponses(exportParams)
    
    // Handle file download
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    
    // Set filename based on format
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
    const extension = exportFormat.value === 'xlsx' ? 'xlsx' : 'csv'
    const filename = `survey_responses_${timestamp}.${extension}`
    
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    // Close modal
    showExportModal.value = false
    
    // Show success message (if you have a toast system)
    console.log('Export completed successfully!')
    
  } catch (error) {
    console.error('Error exporting data:', error)
    // Show error message (if you have a toast system)
    alert('Failed to export data. Please try again.')
  } finally {
    isExporting.value = false
  }
}

// Category Analytics Functions
const viewCategoryAnalytics = (category) => {
  selectedCategory.value = category
  showCategoryAnalytics.value = true
}

const exportCategoryExcel = async (category) => {
  try {
    const exportParams = {
      format: 'xlsx',
      category_id: category.id,
      include_profile_fields: exportProfileFields.value
    }
    
    const response = await surveyService.exportResponses(exportParams)
    
    // Handle file download
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
    const filename = `survey_${category.name.replace(/\s+/g, '_')}_${timestamp}.xlsx`
    
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    console.log('Excel export completed successfully!')
  } catch (error) {
    console.error('Error exporting Excel:', error)
    alert('Failed to export Excel file. Please try again.')
  }
}

// Helper functions for category table
const getQuestionCountByCategory = (categoryId) => {
  return questions.value.filter(q => q.category === categoryId).length
}

const getResponseCountByCategory = (categoryId) => {
  // Get all questions for this category
  const categoryQuestionIds = questions.value
    .filter(q => q.category === categoryId)
    .map(q => q.id)
  
  // This is a placeholder - in a real implementation, you'd need to track responses
  // For now, return a computed value or fetch from analytics
  return 0 // Will be populated from analytics data when available
}
</script>

<template>
<div>
  <div :class="['min-h-screen p-6', isDark ? 'bg-gray-900' : 'bg-gradient-to-br from-slate-50 to-orange-50']">
    <HeaderSection :is-dark="isDark" @export="showExportModal = true" />

    <TabNavigation :active-tab="activeTab" :is-dark="isDark" @change-tab="handleTabChange" />

    <!-- Loading -->
    <LoadingState v-if="loading" />

    <!-- Categories Tab -->
    <CategoriesView
      v-else-if="activeTab === 'categories'"
      :paginated-categories="paginatedCategories"
      :current-page="currentCategoryPage"
      :total-pages="totalCategoryPages"
      :is-dark="isDark"
      @add-category="openCategoryModal()"
      @edit="openCategoryModal"
      @delete="deleteCategory"
      @view-questions="selectCategory"
      @view-analytics="viewCategoryAnalytics"
      @prev-page="currentCategoryPage--"
      @next-page="currentCategoryPage++"
      @goto-page="currentCategoryPage = $event"
    />

    <!-- Questions Tab -->
    <QuestionsView
      v-else-if="activeTab === 'questions'"
      :paginated-questions="paginatedQuestions"
      :total-questions="questions.length"
      :question-types="questionTypes"
      :current-page="currentQuestionPage"
      :total-pages="totalQuestionPages"
      :is-dark="isDark"
      @add-question="openQuestionModal()"
      @edit="openQuestionModal"
      @delete="deleteQuestion"
      @prev-page="currentQuestionPage--"
      @next-page="currentQuestionPage++"
      @goto-page="currentQuestionPage = $event"
    />

    <!-- Analytics Tab -->
    <AnalyticsView
      v-else-if="activeTab === 'analytics'"
      :categories="categories"
      :analytics="analytics"
      :is-dark="isDark"
      @view-analytics="viewCategoryAnalytics"
      @export-excel="exportCategoryExcel"
    />

    <!-- Category Analytics Modal -->
    <CategoryAnalytics
      v-if="showCategoryAnalytics"
      :category="selectedCategory"
      @close="showCategoryAnalytics = false"
    />

    <!-- Category Modal -->
    <CategoryModal
      v-if="showCategoryModal"
      :category="categoryForm.id ? categoryForm : null"
      :categories-length="categories.length"
      :is-dragging="isDragging"
      :dragged-modal="draggedModal"
      :modal-position="modalPositions.category"
      @close="showCategoryModal = false"
      @save="loadCategories"
      @start-drag="startDrag"
      @reset-position="resetModalPosition"
    />

    <!-- Question Modal -->
    <QuestionModal
      v-if="showQuestionModal"
      :question="questionForm.id ? questionForm : null"
      :selected-category-id="selectedCategoryId"
      :categories="categories"
      :questions="questions"
      :questions-length="questions.length"
      :is-dragging="isDragging"
      :dragged-modal="draggedModal"
      :modal-position="modalPositions.question"
      @close="showQuestionModal = false"
      @save="saveQuestion"
      @start-drag="startDrag"
      @reset-position="resetModalPosition"
    />

    <!-- Analytics Modal -->
    <AnalyticsModal
      v-if="showAnalyticsModal"
      :analytics="analytics"
      :is-dragging="isDragging"
      :dragged-modal="draggedModal"
      :modal-position="modalPositions.analytics"
      @close="showAnalyticsModal = false"
      @start-drag="startDrag"
      @reset-position="resetModalPosition"
    />

    <!-- Export Modal -->
    <ExportModal
      v-if="showExportModal"
      :categories="categories"
      :is-dragging="isDragging"
      :dragged-modal="draggedModal"
      :modal-position="modalPositions.export"
      @close="showExportModal = false"
      @start-drag="startDrag"
      @reset-position="resetModalPosition"
    />

    <!-- Category Questions Modal -->
    <CategoryQuestionsModal
      v-if="showCategoryQuestionsModal"
      :category="selectedCategoryForModal"
      :questions="categoryQuestions"
      :is-dragging="isDragging"
      :dragged-modal="draggedModal"
      :modal-position="modalPositions.categoryQuestions"
      @close="showCategoryQuestionsModal = false"
      @edit-question="openQuestionModal"
      @delete-question="deleteQuestion"
      @start-drag="startDrag"
      @reset-position="resetModalPosition"
    />

  </div>
</div>
</template>