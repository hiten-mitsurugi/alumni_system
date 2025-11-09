<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { 
  Plus, 
  Edit, 
  Trash2, 
  Eye, 
  BarChart3, 
  Settings,
  ListChecks,
  FolderPlus,
  Download,
  FileText,
  FileSpreadsheet,
  ChevronLeft,
  ChevronRight,
  TrendingUp,
  Users,
  FileCheck,
  Calendar,
  Move
} from 'lucide-vue-next'
import surveyService from '@/services/surveyService'
import { useThemeStore } from '@/stores/theme'

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
  is_active: true
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
      is_active: true
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
</script>

<template>
<div>
  <div :class="['min-h-screen p-6', isDark ? 'bg-gray-900' : 'bg-gradient-to-br from-slate-50 to-orange-50']">
    <!-- Header Section -->
    <div :class="[
      'rounded-xl shadow-sm border p-8 mb-8',
      isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-slate-200'
    ]">
      <div class="flex justify-between items-center">
        <div>
          <h1 :class="['text-4xl font-bold mb-2', isDark ? 'text-white' : 'text-slate-800']">Survey Management</h1>
          <p :class="[isDark ? 'text-gray-300' : 'text-slate-600']">Create, manage, and analyze your dynamic survey system</p>
        </div>
        <div class="flex gap-3">
          <button
            @click="showExportModal = true"
            :class="[
              'group flex items-center gap-2 px-5 py-3 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg cursor-pointer transform hover:scale-105',
              isDark 
                ? 'bg-gray-700 hover:bg-gray-600 text-white'
                : 'bg-gradient-to-r from-orange-600 to-orange-500 text-white hover:from-orange-500 hover:to-orange-600'
            ]"
          >
            <Download class="w-4 h-4 group-hover:animate-bounce" />
            Export Data
          </button>
        </div>
      </div>
    </div>

    <!-- Tab Navigation -->
    <div :class="[
      'rounded-xl shadow-sm border mb-6',
      isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-slate-200'
    ]">
      <nav class="flex space-x-1 p-2">
        <button
          @click="activeTab = 'categories'"
          :class="[
            'flex items-center gap-2 px-6 py-3 rounded-lg font-medium text-sm transition-all duration-200 cursor-pointer',
            activeTab === 'categories'
              ? isDark 
                ? 'bg-gray-700 text-white shadow-md'
                : 'bg-gradient-to-r from-orange-600 to-orange-500 text-white shadow-md'
              : isDark
                ? 'text-gray-300 hover:text-white hover:bg-gray-700'
                : 'text-slate-600 hover:text-slate-800 hover:bg-slate-100'
          ]"
        >
          <FolderPlus class="w-4 h-4" />
          Categories
        </button>
        <button
          @click="goToQuestionsTab"
          :class="[
            'flex items-center gap-2 px-6 py-3 rounded-lg font-medium text-sm transition-all duration-200 cursor-pointer',
            activeTab === 'questions'
              ? isDark 
                ? 'bg-gray-700 text-white shadow-md'
                : 'bg-gradient-to-r from-orange-600 to-orange-500 text-white shadow-md'
              : isDark
                ? 'text-gray-300 hover:text-white hover:bg-gray-700'
                : 'text-slate-600 hover:text-slate-800 hover:bg-slate-100'
          ]"
        >
          <ListChecks class="w-4 h-4" />
          Questions
        </button>
        <button
          @click="activeTab = 'analytics'"
          :class="[
            'flex items-center gap-2 px-6 py-3 rounded-lg font-medium text-sm transition-all duration-200 cursor-pointer',
            activeTab === 'analytics'
              ? isDark 
                ? 'bg-gray-700 text-white shadow-md'
                : 'bg-gradient-to-r from-orange-600 to-orange-500 text-white shadow-md'
              : isDark
                ? 'text-gray-300 hover:text-white hover:bg-gray-700'
                : 'text-slate-600 hover:text-slate-800 hover:bg-slate-100'
          ]"
        >
              : 'text-slate-600 hover:text-slate-800 hover:bg-slate-100'
          ]"
        >
          <BarChart3 class="w-4 h-4" />
          Analytics
        </button>
      </nav>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <div class="flex flex-col items-center">
        <div class="animate-spin rounded-full h-16 w-16 border-4 border-orange-200 border-t-orange-600"></div>
        <p class="mt-4 text-slate-600 font-medium">Loading survey data...</p>
      </div>
    </div>

    <!-- Categories Tab -->
    <div v-else-if="activeTab === 'categories'" class="space-y-6">
      <div class="flex justify-between items-center">
        <div>
          <h2 :class="['text-2xl font-bold', isDark ? 'text-white' : 'text-slate-800']">Survey Categories</h2>
          <p :class="['mt-1', isDark ? 'text-gray-300' : 'text-slate-600']">Organize your survey questions into logical categories</p>
        </div>
        <button
          @click="openCategoryModal()"
          :class="[
            'group flex items-center gap-2 px-6 py-3 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg cursor-pointer transform hover:scale-105',
            isDark 
              ? 'bg-gray-700 hover:bg-gray-600 text-white'
              : 'bg-gradient-to-r from-orange-600 to-orange-500 text-white hover:from-orange-500 hover:to-orange-600'
          ]"
        >
          <Plus class="w-5 h-5 group-hover:rotate-90 transition-transform" />
          Add Category
        </button>
      </div>

      <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="category in paginatedCategories"
          :key="category.id"
          :class="[
            'group rounded-xl border p-6 hover:shadow-lg transition-all duration-300 cursor-pointer transform hover:scale-105',
            isDark 
              ? 'bg-gray-800 border-gray-700 hover:border-gray-600' 
              : 'bg-white border-slate-200 hover:border-indigo-300'
          ]"
        >
          <div class="flex justify-between items-start mb-4">
            <div class="flex-1">
              <h3 :class="[
                'font-bold text-lg transition-colors',
                isDark
                  ? 'text-white group-hover:text-gray-400'
                  : 'text-slate-800 group-hover:text-orange-600'
              ]">
                {{ category.name }}
              </h3>
              <p :class="['text-sm mt-2 line-clamp-2', isDark ? 'text-gray-300' : 'text-slate-600']">{{ category.description }}</p>
            </div>
            <div class="flex gap-1 ml-4">
              <button
                @click.stop="openCategoryModal(category)"
                :class="[
                  'p-2 rounded-lg transition-all duration-200 cursor-pointer',
                  isDark
                    ? 'text-gray-400 hover:text-gray-200 hover:bg-gray-700'
                    : 'text-slate-400 hover:text-orange-600 hover:bg-orange-50'
                ]"
                title="Edit Category"
              >
                <Edit class="w-4 h-4" />
              </button>
              <button
                @click.stop="deleteCategory(category.id)"
                class="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-200 cursor-pointer"
                title="Delete Category"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <div class="flex justify-between items-center text-sm mb-4">
            <span class="inline-flex items-center gap-1 px-3 py-1 bg-slate-100 text-slate-700 rounded-full">
              <FileText class="w-3 h-3" />
              {{ category.active_questions_count || 0 }} questions
              <span class="ml-1 text-xs" :class="[
                (category.total_questions_count || 0) >= 50 
                  ? 'text-red-600' 
                  : (category.total_questions_count || 0) >= 40 
                    ? 'text-yellow-600' 
                    : 'text-orange-500'
              ]">
                ({{ category.total_questions_count || 0 }}/50)
              </span>
            </span>
            <span :class="[
              'inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium',
              category.is_active 
                ? 'bg-emerald-100 text-emerald-700' 
                : 'bg-red-100 text-red-700'
            ]">
              <div :class="[
                'w-2 h-2 rounded-full',
                category.is_active ? 'bg-emerald-500' : 'bg-red-500'
              ]"></div>
              {{ category.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          
          <button
            @click.stop="selectCategory(category)"
            class="w-full px-4 py-2 text-sm bg-gradient-to-r from-orange-600 to-orange-500 text-white rounded-lg hover:from-orange-500 hover:to-orange-600 transition-all duration-200 cursor-pointer shadow-md hover:shadow-lg transform hover:scale-105"
          >
            View Questions →
          </button>
        </div>
      </div>

      <!-- Categories Pagination -->
      <div v-if="totalCategoryPages > 1" class="flex items-center justify-center mt-8">
        <nav class="flex items-center gap-2">
          <button
            @click="goToCategoryPage(currentCategoryPage - 1)"
            :disabled="currentCategoryPage === 1"
            :class="[
              'flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200',
              currentCategoryPage === 1
                ? 'text-slate-400 cursor-not-allowed'
                : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 cursor-pointer'
            ]"
          >
            <ChevronLeft class="w-4 h-4" />
            Previous
          </button>
          
          <div class="flex gap-1 mx-4">
            <button
              v-for="page in Math.min(totalCategoryPages, 5)"
              :key="page"
              @click="goToCategoryPage(page)"
              :class="[
                'w-10 h-10 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer',
                currentCategoryPage === page
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50'
              ]"
            >
              {{ page }}
            </button>
          </div>
          
          <button
            @click="goToCategoryPage(currentCategoryPage + 1)"
            :disabled="currentCategoryPage === totalCategoryPages"
            :class="[
              'flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200',
              currentCategoryPage === totalCategoryPages
                ? 'text-slate-400 cursor-not-allowed'
                : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 cursor-pointer'
            ]"
          >
            Next
            <ChevronRight class="w-4 h-4" />
          </button>
        </nav>
      </div>
    </div>

    <!-- Questions Tab -->
    <div v-else-if="activeTab === 'questions'" class="space-y-6">
      <div class="flex justify-between items-center">
        <div>
          <h2 :class="['text-2xl font-bold', isDark ? 'text-white' : 'text-slate-800']">All Survey Questions</h2>
          <p :class="['mt-1', isDark ? 'text-gray-300' : 'text-slate-600']">Manage all survey questions across all categories</p>
        </div>
        <div class="flex gap-3">
          <button
            @click="openQuestionModal()"
            :class="[
              'group flex items-center gap-2 px-6 py-3 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg cursor-pointer transform hover:scale-105',
              isDark 
                ? 'bg-gray-700 hover:bg-gray-600 text-white'
                : 'bg-gradient-to-r from-orange-600 to-orange-500 text-white hover:from-orange-500 hover:to-orange-600'
            ]"
          >
            <Plus class="w-5 h-5 group-hover:rotate-90 transition-transform" />
            Add Question
          </button>
        </div>
      </div>

      <div :class="[
        'rounded-xl border overflow-hidden shadow-sm',
        isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-slate-200'
      ]">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200">
            <thead :class="[
              isDark ? 'bg-gray-700' : 'bg-gradient-to-r from-slate-50 to-slate-100'
            ]">
              <tr>
                <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', isDark ? 'text-gray-300' : 'text-slate-600']">
                  Question
                </th>
                <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', isDark ? 'text-gray-300' : 'text-slate-600']">
                  Category
                </th>
                <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', isDark ? 'text-gray-300' : 'text-slate-600']">
                  Type
                </th>
                <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', isDark ? 'text-gray-300' : 'text-slate-600']">
                  Required
                </th>
                <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', isDark ? 'text-gray-300' : 'text-slate-600']">
                  Status
                </th>
                <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', isDark ? 'text-gray-300' : 'text-slate-600']">
                  Responses
                </th>
                <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', isDark ? 'text-gray-300' : 'text-slate-600']">
                  Conditional
                </th>
                <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', isDark ? 'text-gray-300' : 'text-slate-600']">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody :class="[
              'divide-y', 
              isDark ? 'bg-gray-800 divide-gray-700' : 'bg-white divide-slate-100'
            ]">
              <tr v-for="question in paginatedQuestions" :key="question.id" :class="[
                'transition-colors duration-150',
                isDark ? 'hover:bg-gray-700' : 'hover:bg-slate-50'
              ]">
                <td class="px-6 py-4">
                  <div :class="['text-sm font-medium max-w-xs', isDark ? 'text-white' : 'text-slate-800']">
                    {{ question.question_text.length > 50 ? question.question_text.substring(0, 50) + '...' : question.question_text }}
                  </div>
                  <div v-if="question.help_text" :class="['text-sm mt-1 max-w-xs', isDark ? 'text-gray-400' : 'text-slate-500']">
                    {{ question.help_text }}
                  </div>
                </td>
                <td class="px-6 py-4">
                  <span :class="[
                    'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium',
                    isDark ? 'bg-gray-700 text-gray-300' : 'bg-orange-100 text-orange-600'
                  ]">
                    {{ question.category?.name }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                    {{ questionTypes.find(t => t.value === question.question_type)?.label }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <span :class="[
                    'inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium',
                    question.is_required 
                      ? 'bg-red-100 text-red-800' 
                      : 'bg-slate-100 text-slate-600'
                  ]">
                    <div :class="[
                      'w-2 h-2 rounded-full',
                      question.is_required ? 'bg-red-500' : 'bg-slate-400'
                    ]"></div>
                    {{ question.is_required ? 'Required' : 'Optional' }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <span :class="[
                    'inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium',
                    question.is_active 
                      ? 'bg-emerald-100 text-emerald-800' 
                      : 'bg-red-100 text-red-800'
                  ]">
                    <div :class="[
                      'w-2 h-2 rounded-full',
                      question.is_active ? 'bg-emerald-500' : 'bg-red-500'
                    ]"></div>
                    {{ question.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center gap-2">
                    <BarChart3 class="w-4 h-4 text-slate-400" />
                    <span class="text-sm font-semibold text-slate-700">{{ question.response_count || 0 }}</span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div v-if="question.depends_on_question" class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-orange-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                    </svg>
                    <span class="text-xs text-orange-600 font-medium">
                      Conditional
                    </span>
                  </div>
                  <div v-else class="flex items-center gap-2">
                    <span class="text-xs text-slate-400">Always shown</span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="flex gap-2">
                    <button
                      @click="openQuestionModal(question)"
                      class="p-2 text-slate-400 hover:text-orange-600 hover:bg-orange-50 rounded-lg transition-all duration-200 cursor-pointer"
                      title="Edit Question"
                    >
                      <Edit class="w-4 h-4" />
                    </button>
                    <button
                      @click="deleteQuestion(question.id)"
                      class="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-200 cursor-pointer"
                      title="Delete Question"
                    >
                      <Trash2 class="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Empty State -->
        <div v-if="questions.length === 0" class="text-center py-12">
          <ListChecks class="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 class="text-lg font-semibold text-slate-600 mb-2">No questions found</h3>
          <p class="text-slate-500 mb-4">
            {{ selectedCategory ? `No questions in ${selectedCategory.name} category` : 'No questions available' }}
          </p>
          <button
            @click="openQuestionModal()"
            class="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-600 to-orange-500 text-white rounded-lg hover:from-orange-500 hover:to-orange-600 transition-all duration-200 cursor-pointer"
          >
            <Plus class="w-4 h-4" />
            Create First Question
          </button>
        </div>

        <!-- Questions Pagination -->
        <div v-if="paginatedQuestions.length > 0 && totalQuestionPages > 1" class="flex items-center justify-between mt-6 pt-6 border-t border-slate-200">
          <div class="text-sm text-slate-600">
            Showing {{ (currentQuestionPage - 1) * itemsPerPage + 1 }} to 
            {{ Math.min(currentQuestionPage * itemsPerPage, questions.length) }} of 
            {{ questions.length }} questions
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="currentQuestionPage--"
              :disabled="currentQuestionPage === 1"
              class="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:text-slate-400 disabled:hover:bg-transparent cursor-pointer"
            >
              <ChevronLeft class="w-5 h-5" />
            </button>
            
            <div class="flex gap-1">
              <button
                v-for="page in questionsPageButtons" 
                :key="`q-page-${page}`"
                @click="currentQuestionPage = page"
                :class="[
                  'w-10 h-10 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer',
                  page === currentQuestionPage
                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg'
                    : 'text-slate-600 hover:bg-indigo-50 hover:text-indigo-600'
                ]"
              >
                {{ page }}
              </button>
              <span 
                v-for="(ellipsis, index) in questionsEllipsis" 
                :key="`q-ellipsis-${index}`"
                class="flex items-center justify-center w-10 h-10 text-slate-400"
              >
                ...
              </span>
            </div>
            
            <button
              @click="currentQuestionPage++"
              :disabled="currentQuestionPage === totalQuestionPages"
              class="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:text-slate-400 disabled:hover:bg-transparent cursor-pointer"
            >
              <ChevronRight class="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Analytics Tab -->
    <div v-else-if="activeTab === 'analytics'" class="space-y-6">
      <div class="flex justify-between items-center">
        <div>
          <h2 class="text-2xl font-bold text-slate-800">Survey Analytics</h2>
          <p class="text-slate-600">Comprehensive overview of survey performance and responses</p>
        </div>
      </div>

      <!-- Analytics Content -->
      <div v-if="analytics" class="space-y-6">
        <!-- Analytics Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div class="bg-gradient-to-br from-orange-50 to-orange-100 p-6 rounded-xl border border-orange-200 hover:shadow-lg transition-all duration-200">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-semibold text-orange-600">Total Questions</h4>
              <div class="w-8 h-8 bg-orange-600 rounded-lg flex items-center justify-center">
                <FileCheck class="w-4 h-4 text-white" />
              </div>
            </div>
            <p class="text-3xl font-bold text-orange-500">{{ analytics.total_questions }}</p>
            <p class="text-xs text-orange-600 mt-1">Active survey questions</p>
          </div>
          
          <div class="bg-gradient-to-br from-orange-50 to-orange-100 p-6 rounded-xl border border-orange-200 hover:shadow-lg transition-all duration-200">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-semibold text-orange-600">Total Responses</h4>
              <div class="w-8 h-8 bg-orange-600 rounded-lg flex items-center justify-center">
                <TrendingUp class="w-4 h-4 text-white" />
              </div>
            </div>
            <p class="text-3xl font-bold text-orange-500">{{ analytics.total_responses }}</p>
            <p class="text-xs text-orange-600 mt-1">Submitted answers</p>
          </div>
          
          <div class="bg-gradient-to-br from-amber-50 to-amber-100 p-6 rounded-xl border border-amber-200 hover:shadow-lg transition-all duration-200">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-semibold text-amber-900">Active Users</h4>
              <div class="w-8 h-8 bg-amber-600 rounded-lg flex items-center justify-center">
                <Users class="w-4 h-4 text-white" />
              </div>
            </div>
            <p class="text-3xl font-bold text-amber-700">{{ analytics.total_users_responded }}</p>
            <p class="text-xs text-amber-600 mt-1">Unique participants</p>
          </div>
          
          <div class="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl border border-purple-200 hover:shadow-lg transition-all duration-200">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-semibold text-purple-900">Completion Rate</h4>
              <div class="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
                <BarChart3 class="w-4 h-4 text-white" />
              </div>
            </div>
            <p class="text-3xl font-bold text-purple-700">{{ analytics.completion_rate }}%</p>
            <p class="text-xs text-purple-600 mt-1">Survey completion</p>
          </div>
        </div>

        <!-- Additional Analytics -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h3 class="text-lg font-semibold text-slate-800 mb-4">Response Trends</h3>
            <div class="text-center py-8 text-slate-500">
              <BarChart3 class="w-12 h-12 mx-auto mb-3 text-slate-300" />
              <p>Chart visualization would go here</p>
            </div>
          </div>
          
          <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h3 class="text-lg font-semibold text-slate-800 mb-4">Category Distribution</h3>
            <div class="text-center py-8 text-slate-500">
              <Calendar class="w-12 h-12 mx-auto mb-3 text-slate-300" />
              <p>Category breakdown would go here</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading Analytics -->
      <div v-else class="text-center py-12">
        <div class="animate-spin rounded-full h-16 w-16 border-4 border-orange-200 border-t-orange-600 mx-auto mb-4"></div>
        <p class="text-slate-600 font-medium">Loading analytics data...</p>
      </div>
    </div>

    <!-- Modals Container -->
    <div
      v-if="showCategoryModal"
      class="fixed inset-0 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4"
    >
      <div 
        :class="[
          'draggable-modal relative rounded-2xl shadow-2xl w-full max-w-md',
          isDark ? 'bg-gray-800' : 'bg-white',
          isDragging && draggedModal === 'category' ? 'dragging' : ''
        ]"
        data-modal="category"
        @click.stop
        :style="{ transform: `translate(${modalPositions.category.x}px, ${modalPositions.category.y}px)` }"
      >
        <div 
          :class="[
            'bg-gradient-to-r from-orange-600 to-orange-500 p-6 rounded-t-2xl select-none flex items-center justify-between',
            isDragging && draggedModal === 'category' ? 'cursor-grabbing' : 'cursor-move'
          ]"
          @mousedown="startDrag($event, 'category')"
        >
          <div>
            <h3 class="text-xl font-bold text-white flex items-center gap-2">
              <Move class="w-5 h-5 opacity-70" />
              {{ categoryForm.id ? 'Edit Category' : 'Create New Category' }}
            </h3>
            <p class="text-orange-100 text-sm mt-1">
              {{ categoryForm.id ? 'Update category information' : 'Add a new category for organizing questions' }}
            </p>
          </div>
          <button
            @click="resetModalPosition('category')"
            class="text-orange-200 hover:text-white p-1 rounded transition-colors"
            title="Reset position"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
          </button>
        </div>
        
        <form @submit.prevent="saveCategory" class="p-6 space-y-6">
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-2">Category Name *</label>
            <input
              v-model="categoryForm.name"
              type="text"
              required
              placeholder="e.g., Personal Information"
              class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors"
            />
          </div>
          
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-2">Description</label>
            <textarea
              v-model="categoryForm.description"
              rows="3"
              placeholder="Brief description of this category..."
              class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors resize-none"
            ></textarea>
          </div>
          
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-2">Display Order</label>
            <input
              v-model.number="categoryForm.order"
              type="number"
              min="0"
              placeholder="0"
              class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors"
            />
            <p class="text-xs text-slate-500 mt-1">Lower numbers appear first</p>
          </div>
          
          <div class="flex items-center">
            <input
              v-model="categoryForm.is_active"
              type="checkbox"
              class="h-4 w-4 text-orange-600 focus:ring-orange-500 border-slate-300 rounded cursor-pointer"
            />
            <label class="ml-3 block text-sm font-medium text-slate-700 cursor-pointer">
              Active Category
            </label>
          </div>
          
          <div class="flex justify-end gap-3 pt-4 border-t border-slate-200">
            <button
              type="button"
              @click="showCategoryModal = false"
              class="px-6 py-3 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-6 py-3 text-sm font-medium text-white bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-600 rounded-lg transition-all duration-200 cursor-pointer shadow-md hover:shadow-lg"
            >
              {{ categoryForm.id ? 'Update Category' : 'Create Category' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Question Modal -->
    <div
      v-if="showQuestionModal"
      class="fixed inset-0 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4"
    >
      <div 
        :class="[
          'draggable-modal relative bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden',
          isDragging && draggedModal === 'question' ? 'dragging' : ''
        ]"
        data-modal="question"
        @click.stop
        :style="{ transform: `translate(${modalPositions.question.x}px, ${modalPositions.question.y}px)` }"
      >
        <div 
          :class="[
            'bg-gradient-to-r from-orange-600 to-orange-500 p-6 select-none flex items-center justify-between',
            isDragging && draggedModal === 'question' ? 'cursor-grabbing' : 'cursor-move'
          ]"
          @mousedown="startDrag($event, 'question')"
        >
          <div>
            <h3 class="text-xl font-bold text-white flex items-center gap-2">
              <Move class="w-5 h-5 opacity-70" />
              {{ questionForm.id ? 'Edit Question' : 'Create New Question' }}
            </h3>
            <p class="text-orange-100 text-sm mt-1">
              {{ questionForm.id ? 'Update question details and settings' : 'Add a new question to your survey' }}
            </p>
          </div>
          <button
            @click="resetModalPosition('question')"
            class="text-orange-200 hover:text-white p-1 rounded transition-colors"
            title="Reset position"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
          </button>
        </div>
        
        <form @submit.prevent="saveQuestion" class="p-6 space-y-6 max-h-[calc(90vh-120px)] overflow-y-auto">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-slate-700 mb-2">Category *</label>
              <select
                v-model="questionForm.category"
                required
                class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 cursor-pointer"
              >
                <option value="">Select a category</option>
                <option
                  v-for="category in categories"
                  :key="category.id"
                  :value="category.id"
                >
                  {{ category.name }}
                </option>
              </select>
            </div>
            
            <div class="md:col-span-2">
              <label class="block text-sm font-semibold text-slate-700 mb-2">Question Text *</label>
              <textarea
                v-model="questionForm.question_text"
                required
                rows="3"
                placeholder="Enter your survey question..."
                class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 resize-none"
              ></textarea>
            </div>
            
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-2">Question Type *</label>
              <select
                v-model="questionForm.question_type"
                class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 cursor-pointer"
              >
                <option
                  v-for="type in questionTypes"
                  :key="type.value"
                  :value="type.value"
                >
                  {{ type.label }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-2">Display Order</label>
              <input
                v-model.number="questionForm.order"
                type="number"
                min="0"
                placeholder="0"
                class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              />
            </div>
          </div>
          
          <!-- Options for choice questions -->
          <div v-if="questionTypes.find(t => t.value === questionForm.question_type)?.hasOptions" class="bg-slate-50 p-4 rounded-lg">
            <label class="block text-sm font-semibold text-slate-700 mb-3">Answer Options *</label>
            <div class="space-y-3">
              <div
                v-for="(option, index) in questionForm.options"
                :key="index"
                class="flex gap-3 items-center"
              >
                <input
                  v-model="questionForm.options[index]"
                  type="text"
                  placeholder="Enter option"
                  class="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                />
                <button
                  type="button"
                  @click="removeOption(index)"
                  class="p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors cursor-pointer"
                  title="Remove option"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
              <button
                type="button"
                @click="addOption"
                class="flex items-center gap-2 px-4 py-2 text-sm text-orange-600 hover:text-orange-600 hover:bg-orange-50 rounded-lg transition-colors cursor-pointer"
              >
                <Plus class="w-4 h-4" />
                Add Option
              </button>
            </div>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-2">Placeholder Text</label>
              <input
                v-model="questionForm.placeholder_text"
                type="text"
                placeholder="Hint text for users..."
                class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              />
            </div>

            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-2">Help Text</label>
              <input
                v-model="questionForm.help_text"
                type="text"
                placeholder="Additional guidance..."
                class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              />
            </div>
          </div>

          <!-- Rating Scale Min/Max Section -->
          <div v-if="questionForm.question_type === 'rating'" class="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 bg-indigo-50 rounded-lg border border-indigo-200">
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-2">Minimum Value *</label>
              <input
                v-model.number="questionForm.min_value"
                type="number"
                min="1"
                placeholder="e.g., 1"
                required
                class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
              <p class="text-xs text-indigo-600 mt-1">The lowest rating option (e.g., 1 for 1-5 scale)</p>
            </div>

            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-2">Maximum Value *</label>
              <input
                v-model.number="questionForm.max_value"
                type="number"
                min="1"
                placeholder="e.g., 5"
                required
                class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
              <p class="text-xs text-indigo-600 mt-1">The highest rating option (e.g., 5 for 1-5 scale)</p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Conditional Logic Section -->
            <div class="space-y-4 p-4 bg-orange-50 rounded-lg border border-orange-200">
              <h4 class="text-sm font-semibold text-orange-600 flex items-center gap-2">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"></path>
                </svg>
                Conditional Logic (Optional)
              </h4>
              <p class="text-xs text-orange-600">
                Make this question appear only when another question has a specific answer.
              </p>
              
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Depends on Question</label>
                <select
                  v-model="questionForm.depends_on_question"
                  class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                >
                  <option value="">No dependency</option>
                  <option 
                    v-for="question in availableQuestions" 
                    :key="question.id" 
                    :value="question.id"
                  >
                    {{ question.question_text }}
                  </option>
                </select>
              </div>

              <div v-if="questionForm.depends_on_question">
                <label class="block text-sm font-medium text-slate-700 mb-2">Show when answer is</label>
                <select
                  v-model="questionForm.depends_on_value"
                  class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                >
                  <option value="">Select required answer</option>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
                <p class="text-xs text-slate-500 mt-1">
                  This question will only appear when the selected question is answered with the chosen value.
                </p>
              </div>
            </div>
          </div>
          
          <div class="flex items-center gap-6 p-4 bg-slate-50 rounded-lg">
            <div class="flex items-center">
              <input
                v-model="questionForm.is_required"
                type="checkbox"
                class="h-4 w-4 text-orange-600 focus:ring-orange-500 border-slate-300 rounded cursor-pointer"
              />
              <label class="ml-3 block text-sm font-medium text-slate-700 cursor-pointer">
                Required Question
              </label>
            </div>
            
            <div class="flex items-center">
              <input
                v-model="questionForm.is_active"
                type="checkbox"
                class="h-4 w-4 text-orange-600 focus:ring-orange-500 border-slate-300 rounded cursor-pointer"
              />
              <label class="ml-3 block text-sm font-medium text-slate-700 cursor-pointer">
                Active Question
              </label>
            </div>
          </div>
          
          <div class="flex justify-end gap-3 pt-6 border-t border-slate-200">
            <button
              type="button"
              @click="closeQuestionModal"
              class="px-6 py-3 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-6 py-3 text-sm font-medium text-white bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-600 rounded-lg transition-all duration-200 cursor-pointer shadow-md hover:shadow-lg"
            >
              {{ questionForm.id ? 'Update Question' : 'Create Question' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Analytics Modal -->
    <div
      v-if="showAnalyticsModal && analytics"
      class="fixed inset-0 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4"
    >
      <div 
        :class="[
          'draggable-modal relative bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden',
          isDragging && draggedModal === 'analytics' ? 'dragging' : ''
        ]"
        data-modal="analytics"
        @click.stop
        :style="{ transform: `translate(${modalPositions.analytics.x}px, ${modalPositions.analytics.y}px)` }"
      >
        <div 
          :class="[
            'bg-gradient-to-r from-purple-600 to-pink-600 p-6 select-none flex items-center justify-between',
            isDragging && draggedModal === 'analytics' ? 'cursor-grabbing' : 'cursor-move'
          ]"
          @mousedown="startDrag($event, 'analytics')"
        >
          <div>
            <h3 class="text-xl font-bold text-white flex items-center gap-2">
              <Move class="w-5 h-5 opacity-70" />
              Survey Analytics Dashboard
            </h3>
            <p class="text-purple-100 text-sm mt-1">Comprehensive overview of survey performance and responses</p>
          </div>
          <button
            @click="resetModalPosition('analytics')"
            class="text-purple-200 hover:text-white p-1 rounded transition-colors"
            title="Reset position"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
          </button>
        </div>
        
        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div class="bg-gradient-to-br from-orange-50 to-orange-100 p-6 rounded-xl border border-orange-200 hover:shadow-lg transition-all duration-200 cursor-default">
              <div class="flex items-center justify-between mb-3">
                <h4 class="text-sm font-semibold text-orange-600">Total Questions</h4>
                <div class="w-8 h-8 bg-orange-600 rounded-lg flex items-center justify-center">
                  <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                </div>
              </div>
              <p class="text-3xl font-bold text-orange-500">{{ analytics.total_questions }}</p>
              <p class="text-xs text-orange-600 mt-1">Active survey questions</p>
            </div>
            
            <div class="bg-gradient-to-br from-orange-50 to-orange-100 p-6 rounded-xl border border-orange-200 hover:shadow-lg transition-all duration-200 cursor-default">
              <div class="flex items-center justify-between mb-3">
                <h4 class="text-sm font-semibold text-orange-600">Total Responses</h4>
                <div class="w-8 h-8 bg-orange-600 rounded-lg flex items-center justify-center">
                  <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                  </svg>
                </div>
              </div>
              <p class="text-3xl font-bold text-orange-500">{{ analytics.total_responses }}</p>
              <p class="text-xs text-orange-600 mt-1">Submitted answers</p>
            </div>
            
            <div class="bg-gradient-to-br from-amber-50 to-amber-100 p-6 rounded-xl border border-amber-200 hover:shadow-lg transition-all duration-200 cursor-default">
              <div class="flex items-center justify-between mb-3">
                <h4 class="text-sm font-semibold text-amber-900">Active Users</h4>
                <div class="w-8 h-8 bg-amber-600 rounded-lg flex items-center justify-center">
                  <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
                  </svg>
                </div>
              </div>
              <p class="text-3xl font-bold text-amber-700">{{ analytics.total_users_responded }}</p>
              <p class="text-xs text-amber-600 mt-1">Unique participants</p>
            </div>
            
            <div class="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl border border-purple-200 hover:shadow-lg transition-all duration-200 cursor-default">
              <div class="flex items-center justify-between mb-3">
                <h4 class="text-sm font-semibold text-purple-900">Completion Rate</h4>
                <div class="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
                  <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                  </svg>
                </div>
              </div>
              <p class="text-3xl font-bold text-purple-700">{{ analytics.completion_rate }}%</p>
              <p class="text-xs text-purple-600 mt-1">Survey completion</p>
            </div>
          </div>
          
          <div class="flex justify-end pt-6 border-t border-slate-200">
            <button
              @click="showAnalyticsModal = false"
              class="px-6 py-3 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors cursor-pointer"
            >
              Close Dashboard
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Export Modal -->
    <div
      v-if="showExportModal"
      class="fixed inset-0 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4"
    >
      <div 
        :class="[
          'draggable-modal relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl',
          isDragging && draggedModal === 'export' ? 'dragging' : ''
        ]"
        data-modal="export"
        @click.stop
        :style="{ transform: `translate(${modalPositions.export.x}px, ${modalPositions.export.y}px)` }"
      >
        <div 
          :class="[
            'bg-gradient-to-r from-orange-600 to-emerald-600 p-6 rounded-t-2xl select-none flex items-center justify-between',
            isDragging && draggedModal === 'export' ? 'cursor-grabbing' : 'cursor-move'
          ]"
          @mousedown="startDrag($event, 'export')"
        >
          <div>
            <h3 class="text-xl font-bold text-white flex items-center gap-2">
              <Move class="w-5 h-5 opacity-70" />
              Export Survey Data
            </h3>
            <p class="text-orange-100 text-sm mt-1">Choose export format and filters</p>
          </div>
          <button
            @click="resetModalPosition('export')"
            class="text-orange-200 hover:text-white p-1 rounded transition-colors"
            title="Reset position"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
          </button>
        </div>
        
        <div class="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
          <!-- Export Format -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-3">Export Format</label>
            <div class="grid grid-cols-2 gap-3">
              <button
                @click="exportFormat = 'json'"
                :class="[
                  'p-4 border-2 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer',
                  exportFormat === 'json'
                    ? 'border-orange-500 bg-orange-50 text-orange-500'
                    : 'border-slate-300 text-slate-600 hover:border-orange-300 hover:bg-orange-50'
                ]"
              >
                <FileText class="w-5 h-5 mx-auto mb-2" />
                JSON Data
              </button>
              <button
                @click="exportFormat = 'xlsx'"
                :class="[
                  'p-4 border-2 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer',
                  exportFormat === 'xlsx'
                    ? 'border-orange-500 bg-orange-50 text-orange-500'
                    : 'border-slate-300 text-slate-600 hover:border-orange-300 hover:bg-orange-50'
                ]"
              >
                <FileSpreadsheet class="w-5 h-5 mx-auto mb-2" />
                Excel File
              </button>
            </div>
          </div>
          
          <!-- Category Filter -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-3">Category Filter</label>
            <select
              v-model="exportCategory"
              class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 cursor-pointer"
            >
              <option value="">All Categories</option>
              <option
                v-for="category in categories"
                :key="category.id"
                :value="category.id"
              >
                {{ category.name }} ({{ category.active_questions_count }} questions)
              </option>
            </select>
          </div>
          
          <!-- Date Range Filter -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-2">From Date</label>
              <input
                v-model="exportDateFrom"
                type="date"
                class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              />
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-2">To Date</label>
              <input
                v-model="exportDateTo"
                type="date"
                class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              />
            </div>
          </div>
          
          <!-- Profile Fields Selection (only for Excel) -->
          <div v-if="exportFormat === 'xlsx'">
            <label class="block text-sm font-semibold text-slate-700 mb-3">Include Profile Fields</label>
            <div class="grid grid-cols-2 gap-2 p-4 bg-slate-50 rounded-lg max-h-40 overflow-y-auto">
              <label v-for="field in [
                { key: 'first_name', label: 'First Name' },
                { key: 'last_name', label: 'Last Name' },
                { key: 'email', label: 'Email' },
                { key: 'program', label: 'Program' },
                { key: 'year_graduated', label: 'Year Graduated' },
                { key: 'student_id', label: 'Student ID' },
                { key: 'birth_date', label: 'Birth Date' },
                { key: 'user_type', label: 'User Type' },
                { key: 'date_joined', label: 'Date Joined' }
              ]" 
              :key="field.key"
              class="flex items-center space-x-2 cursor-pointer"
              >
                <input
                  type="checkbox"
                  :value="field.key"
                  v-model="exportProfileFields"
                  class="h-4 w-4 text-orange-600 focus:ring-orange-500 border-slate-300 rounded"
                />
                <span class="text-sm text-slate-700">{{ field.label }}</span>
              </label>
            </div>
          </div>
          
          <!-- Export Summary -->
          <div class="p-4 bg-orange-50 rounded-lg border-l-4 border-orange-400">
            <div class="flex items-start">
              <div class="flex-shrink-0">
                <svg class="w-5 h-5 text-orange-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <h4 class="text-sm font-medium text-orange-600">Export Summary</h4>
                <div class="mt-1 text-sm text-orange-600">
                  <p v-if="exportFormat === 'xlsx'">
                    Excel file with user profiles and survey responses
                  </p>
                  <p v-else>
                    JSON data of survey responses only
                  </p>
                  <p v-if="exportCategory">
                    Filtered by: {{ categories.find(c => c.id == exportCategory)?.name || 'Selected Category' }}
                  </p>
                  <p v-if="exportDateFrom || exportDateTo">
                    Date range: {{ exportDateFrom || 'No start' }} to {{ exportDateTo || 'No end' }}
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Action Buttons -->
          <div class="flex justify-end gap-3 pt-6 border-t border-slate-200">
            <button
              @click="showExportModal = false"
              :disabled="isExporting"
              class="px-6 py-3 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              @click="exportData"
              :disabled="isExporting"
              class="px-6 py-3 text-sm font-medium text-white bg-gradient-to-r from-orange-600 to-emerald-600 hover:from-orange-500 hover:to-emerald-700 rounded-lg transition-all duration-200 cursor-pointer shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Download v-if="!isExporting" class="w-4 h-4" />
              <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isExporting ? 'Exporting...' : 'Export Data' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Category Questions Modal -->
    <div
      v-if="showCategoryQuestionsModal"
      class="fixed inset-0 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4"
    >
      <div 
        :class="[
          'draggable-modal relative bg-white rounded-2xl shadow-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden',
          isDragging && draggedModal === 'categoryQuestions' ? 'dragging' : ''
        ]"
        data-modal="categoryQuestions"
        @click.stop
        :style="{ transform: `translate(${modalPositions.categoryQuestions.x}px, ${modalPositions.categoryQuestions.y}px)` }"
      >
          <div 
            :class="[
              'bg-gradient-to-r from-orange-600 to-orange-500 p-6 select-none flex items-center justify-between',
              isDragging && draggedModal === 'categoryQuestions' ? 'cursor-grabbing' : 'cursor-move'
            ]"
            @mousedown="startDrag($event, 'categoryQuestions')"
          >
            <div>
              <h3 class="text-xl font-bold text-white flex items-center gap-2">
                <Move class="w-5 h-5 opacity-70" />
                Questions in "{{ selectedCategoryForModal?.name }}" Category
              </h3>
              <p class="text-indigo-100 text-sm mt-1">
                {{ categoryQuestions.length }} question{{ categoryQuestions.length !== 1 ? 's' : '' }} found
              </p>
            </div>
            <button
              @click="resetModalPosition('categoryQuestions')"
              class="text-indigo-200 hover:text-white p-1 rounded transition-colors"
              title="Reset position"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
            </button>
          </div>        <div class="p-6 max-h-[calc(90vh-200px)] overflow-y-auto">
          <!-- Questions Table -->
          <div v-if="categoryQuestions.length > 0" class="overflow-x-auto">
            <table class="w-full table-auto">
              <thead class="sticky top-0 bg-white z-10">
                <tr class="bg-slate-50 text-left">
                  <th class="px-6 py-4 text-xs font-semibold text-slate-600 uppercase tracking-wider border-b border-slate-200">
                    Question
                  </th>
                  <th class="px-6 py-4 text-xs font-semibold text-slate-600 uppercase tracking-wider border-b border-slate-200">
                    Type
                  </th>
                  <th class="px-6 py-4 text-xs font-semibold text-slate-600 uppercase tracking-wider border-b border-slate-200">
                    Required
                  </th>
                  <th class="px-6 py-4 text-xs font-semibold text-slate-600 uppercase tracking-wider border-b border-slate-200">
                    Status
                  </th>
                  <th class="px-6 py-4 text-xs font-semibold text-slate-600 uppercase tracking-wider border-b border-slate-200">
                    Responses
                  </th>
                  <th class="px-6 py-4 text-xs font-semibold text-slate-600 uppercase tracking-wider border-b border-slate-200">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-slate-200">
                <tr v-for="question in categoryQuestions" :key="question.id" class="hover:bg-slate-50 transition-colors duration-150">
                  <td class="px-6 py-4">
                    <div class="max-w-md">
                      <p class="text-sm font-medium text-slate-900 line-clamp-2">{{ question.question_text }}</p>
                      <p v-if="question.help_text" class="text-xs text-slate-500 mt-1">{{ question.help_text }}</p>
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-600">
                      {{ questionTypes.find(t => t.value === question.question_type)?.label }}
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <span :class="[
                      'inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium',
                      question.is_required 
                        ? 'bg-red-100 text-red-800' 
                        : 'bg-slate-100 text-slate-600'
                    ]">
                      <div :class="[
                        'w-2 h-2 rounded-full',
                        question.is_required ? 'bg-red-500' : 'bg-slate-400'
                      ]"></div>
                      {{ question.is_required ? 'Required' : 'Optional' }}
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <span :class="[
                      'inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium',
                      question.is_active 
                        ? 'bg-emerald-100 text-emerald-800' 
                        : 'bg-red-100 text-red-800'
                    ]">
                      <div :class="[
                        'w-2 h-2 rounded-full',
                        question.is_active ? 'bg-emerald-500' : 'bg-red-500'
                      ]"></div>
                      {{ question.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <div class="flex items-center gap-2">
                      <BarChart3 class="w-4 h-4 text-slate-400" />
                      <span class="text-sm font-semibold text-slate-700">{{ question.response_count || 0 }}</span>
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <div class="flex gap-2">
                      <button
                        @click="openQuestionModal(question)"
                        class="p-2 text-slate-400 hover:text-orange-600 hover:bg-orange-50 rounded-lg transition-all duration-200 cursor-pointer"
                        title="Edit Question"
                      >
                        <Edit class="w-4 h-4" />
                      </button>
                      <button
                        @click="deleteQuestion(question.id)"
                        class="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-200 cursor-pointer"
                        title="Delete Question"
                      >
                        <Trash2 class="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Empty State -->
          <div v-else class="text-center py-12">
            <ListChecks class="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 class="text-lg font-semibold text-slate-600 mb-2">No questions found</h3>
            <p class="text-slate-500 mb-4">
              No questions have been created for the "{{ selectedCategoryForModal?.name }}" category yet.
            </p>
            <button
              @click="openQuestionModal(); showCategoryQuestionsModal = false"
              class="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-600 to-orange-500 text-white rounded-lg hover:from-orange-500 hover:to-orange-600 transition-all duration-200 cursor-pointer"
            >
              <Plus class="w-4 h-4" />
              Create First Question
            </button>
          </div>

          <div class="flex justify-end pt-6 border-t border-slate-200 mt-6 sticky bottom-0 bg-white">
            <button
              @click="showCategoryQuestionsModal = false"
              class="px-6 py-3 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors cursor-pointer"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
/* Draggable modal styles */
.draggable-modal {
  transition: transform 0.1s ease-out;
  z-index: 9999;
}

.draggable-modal.dragging {
  transition: none;
  z-index: 10000;
}

/* Custom cursor styles for drag handles */
.cursor-move {
  cursor: move;
}

.cursor-grabbing {
  cursor: grabbing;
}

/* Ensure proper stacking for modals */
.fixed.z-50 {
  z-index: 50;
}

.draggable-modal[data-modal] {
  position: relative;
}

/* Animation for modal positioning */
@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.95) translate(0, -20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translate(0, 0);
  }
}

.draggable-modal {
  animation: modalSlideIn 0.2s ease-out;
}

/* Disable text selection during drag */
.select-none {
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}
</style>
