<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Survey Management</h1>
        <p class="mt-2 text-gray-600">Manage dynamic survey categories and questions</p>
      </div>

      <!-- Action Buttons -->
      <div class="mb-6 flex flex-wrap gap-4">
        <button
          @click="showCreateCategoryModal = true"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          Add Category
        </button>
        <button
          @click="showCreateQuestionModal = true"
          class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          Add Question
        </button>
        <button
          @click="viewAnalytics"
          class="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
          View Analytics
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>

      <!-- Error State -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <div class="flex">
          <svg class="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
          </svg>
          <p class="text-red-800">{{ error }}</p>
        </div>
      </div>

      <!-- Categories Grid -->
      <div v-if="!loading" class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        <div
          v-for="category in categories"
          :key="category.id"
          class="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
        >
          <!-- Category Header -->
          <div class="p-4 border-b border-gray-200">
            <div class="flex justify-between items-start">
              <div>
                <h3 class="text-lg font-semibold text-gray-900">{{ category.name }}</h3>
                <p class="text-sm text-gray-600 mt-1">{{ category.description }}</p>
                <div class="flex items-center gap-4 mt-2">
                  <span class="text-xs text-gray-500">Order: {{ category.order }}</span>
                  <span class="text-xs text-gray-500">Questions: {{ category.questions?.length || 0 }}</span>
                  <span
                    :class="[
                      'px-2 py-1 rounded-full text-xs font-medium',
                      category.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    ]"
                  >
                    {{ category.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </div>
              </div>
              <div class="flex gap-2">
                <button
                  @click="editCategory(category)"
                  class="text-blue-600 hover:text-blue-800 p-1"
                  title="Edit Category"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                  </svg>
                </button>
                <button
                  @click="deleteCategory(category)"
                  class="text-red-600 hover:text-red-800 p-1"
                  title="Delete Category"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Questions List -->
          <div class="p-4">
            <div class="flex justify-between items-center mb-3">
              <h4 class="text-sm font-medium text-gray-700">Questions</h4>
              <button
                @click="addQuestionToCategory(category)"
                class="text-green-600 hover:text-green-800 text-sm flex items-center gap-1"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                </svg>
                Add Question
              </button>
            </div>
            
            <div v-if="category.questions && category.questions.length > 0" class="space-y-2">
              <div
                v-for="question in category.questions"
                :key="question.id"
                class="bg-gray-50 rounded-lg p-3 hover:bg-gray-100 transition-colors"
              >
                <div class="flex justify-between items-start">
                  <div class="flex-1">
                    <p class="text-sm font-medium text-gray-900">{{ question.question_text }}</p>
                    <div class="flex items-center gap-2 mt-1">
                      <span class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {{ question.question_type }}
                      </span>
                      <span
                        v-if="question.is_required"
                        class="text-xs bg-red-100 text-red-800 px-2 py-1 rounded"
                      >
                        Required
                      </span>
                      <span class="text-xs text-gray-500">Order: {{ question.order }}</span>
                    </div>
                  </div>
                  <div class="flex gap-1 ml-2">
                    <button
                      @click="editQuestion(question)"
                      class="text-blue-600 hover:text-blue-800 p-1"
                      title="Edit Question"
                    >
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                      </svg>
                    </button>
                    <button
                      @click="deleteQuestion(question)"
                      class="text-red-600 hover:text-red-800 p-1"
                      title="Delete Question"
                    >
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else class="text-center py-4">
              <p class="text-sm text-gray-500">No questions yet</p>
              <button
                @click="addQuestionToCategory(category)"
                class="text-green-600 hover:text-green-800 text-sm mt-1"
              >
                Add the first question
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && categories.length === 0" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No survey categories</h3>
        <p class="mt-1 text-sm text-gray-500">Get started by creating your first survey category.</p>
        <div class="mt-6">
          <button
            @click="showCreateCategoryModal = true"
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Create Category
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Category Modal -->
    <CategoryModal
      v-if="showCreateCategoryModal || showEditCategoryModal"
      :show="showCreateCategoryModal || showEditCategoryModal"
      :category="editingCategory"
      @close="closeCategoryModal"
      @saved="onCategorySaved"
    />

    <!-- Create/Edit Question Modal -->
    <QuestionModal
      v-if="showCreateQuestionModal || showEditQuestionModal"
      :show="showCreateQuestionModal || showEditQuestionModal"
      :question="editingQuestion"
      :categories="categories"
      :selectedCategory="selectedCategory"
      @close="closeQuestionModal"
      @saved="onQuestionSaved"
    />

    <!-- Analytics Modal -->
    <AnalyticsModal
      v-if="showAnalyticsModal"
      :show="showAnalyticsModal"
      @close="showAnalyticsModal = false"
    />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { surveyService } from '@/services/surveyService'
import CategoryModal from '@/components/modals/CategoryModal.vue'
import QuestionModal from '@/components/modals/QuestionModal.vue'
import AnalyticsModal from '@/components/modals/AnalyticsModal.vue'

export default {
  name: 'SurveyManagement',
  components: {
    CategoryModal,
    QuestionModal,
    AnalyticsModal
  },
  setup() {
    const categories = ref([])
    const loading = ref(false)
    const error = ref(null)
    
    // Modal states
    const showCreateCategoryModal = ref(false)
    const showEditCategoryModal = ref(false)
    const showCreateQuestionModal = ref(false)
    const showEditQuestionModal = ref(false)
    const showAnalyticsModal = ref(false)
    
    // Editing states
    const editingCategory = ref(null)
    const editingQuestion = ref(null)
    const selectedCategory = ref(null)

    // Load categories and questions
    const loadCategories = async () => {
      try {
        loading.value = true
        error.value = null
        const response = await surveyService.getCategories()
        categories.value = response.data
      } catch (err) {
        error.value = 'Failed to load survey categories'
        console.error('Error loading categories:', err)
      } finally {
        loading.value = false
      }
    }

    // Category actions
    const editCategory = (category) => {
      editingCategory.value = { ...category }
      showEditCategoryModal.value = true
    }

    const deleteCategory = async (category) => {
      if (!confirm(`Are you sure you want to delete "${category.name}"? This will also delete all questions in this category.`)) {
        return
      }
      
      try {
        await surveyService.deleteCategory(category.id)
        await loadCategories()
      } catch (err) {
        error.value = 'Failed to delete category'
        console.error('Error deleting category:', err)
      }
    }

    const closeCategoryModal = () => {
      showCreateCategoryModal.value = false
      showEditCategoryModal.value = false
      editingCategory.value = null
    }

    const onCategorySaved = () => {
      closeCategoryModal()
      loadCategories()
    }

    // Question actions
    const addQuestionToCategory = (category) => {
      selectedCategory.value = category
      editingQuestion.value = null
      showCreateQuestionModal.value = true
    }

    const editQuestion = (question) => {
      editingQuestion.value = { ...question }
      selectedCategory.value = null
      showEditQuestionModal.value = true
    }

    const deleteQuestion = async (question) => {
      if (!confirm(`Are you sure you want to delete this question?`)) {
        return
      }
      
      try {
        await surveyService.deleteQuestion(question.id)
        await loadCategories()
      } catch (err) {
        error.value = 'Failed to delete question'
        console.error('Error deleting question:', err)
      }
    }

    const closeQuestionModal = () => {
      showCreateQuestionModal.value = false
      showEditQuestionModal.value = false
      editingQuestion.value = null
      selectedCategory.value = null
    }

    const onQuestionSaved = () => {
      closeQuestionModal()
      loadCategories()
    }

    // Analytics
    const viewAnalytics = () => {
      showAnalyticsModal.value = true
    }

    // Initialize
    onMounted(() => {
      loadCategories()
    })

    return {
      categories,
      loading,
      error,
      showCreateCategoryModal,
      showEditCategoryModal,
      showCreateQuestionModal,
      showEditQuestionModal,
      showAnalyticsModal,
      editingCategory,
      editingQuestion,
      selectedCategory,
      editCategory,
      deleteCategory,
      closeCategoryModal,
      onCategorySaved,
      addQuestionToCategory,
      editQuestion,
      deleteQuestion,
      closeQuestionModal,
      onQuestionSaved,
      viewAnalytics
    }
  }
}
</script>

<style scoped>
/* Custom scrollbar for long lists */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
