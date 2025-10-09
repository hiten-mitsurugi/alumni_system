<template>
  <div class="min-h-screen bg-gradient-to-br from-green-50 to-white py-8 font-['Poppins']">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8 bg-white rounded-xl shadow-sm border border-green-200 p-6">
        <h1 class="text-4xl font-bold text-green-800 font-['Poppins']">Survey Management</h1>
        <p class="mt-2 text-green-600 font-['Poppins']">Manage dynamic survey categories and questions professionally</p>
      </div>

      <!-- Action Buttons -->
      <div class="mb-6 flex flex-wrap gap-4">
        <button
          @click="showCreateCategoryModal = true"
          class="group bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-3 rounded-xl hover:from-green-700 hover:to-green-800 transition-all duration-200 flex items-center gap-2 font-['Poppins'] font-medium shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          <svg class="w-5 h-5 group-hover:rotate-90 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          Add Category
        </button>
        <button
          @click="showCreateQuestionModal = true"
          class="group bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-3 rounded-xl hover:from-green-700 hover:to-green-800 transition-all duration-200 flex items-center gap-2 font-['Poppins'] font-medium shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          <svg class="w-5 h-5 group-hover:bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          Add Question
        </button>
        <button
          @click="viewAnalytics"
          class="group bg-gradient-to-r from-green-500 to-green-600 text-white px-6 py-3 rounded-xl hover:from-green-600 hover:to-green-700 transition-all duration-200 flex items-center gap-2 font-['Poppins'] font-medium shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          <svg class="w-5 h-5 group-hover:pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
          View Analytics
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center h-64">
        <div class="flex flex-col items-center">
          <div class="animate-spin rounded-full h-16 w-16 border-4 border-green-200 border-t-green-600"></div>
          <p class="mt-4 text-green-700 font-['Poppins'] font-medium">Loading survey data...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-if="error" class="bg-gradient-to-r from-red-50 to-red-100 border-2 border-red-300 rounded-xl p-6 mb-6 shadow-lg">
        <div class="flex">
          <svg class="w-6 h-6 text-red-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
          </svg>
          <p class="text-red-800 font-['Poppins'] font-medium">{{ error }}</p>
        </div>
      </div>

      <!-- Categories Grid -->
      <div v-if="!loading" class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        <div
          v-for="category in categories"
          :key="category.id"
          class="group bg-white rounded-xl shadow-lg border-2 border-green-200 hover:border-green-400 hover:shadow-xl transition-all duration-300 transform hover:scale-105"
        >
          <!-- Category Header -->
          <div class="p-6 border-b-2 border-green-100">
            <div class="flex justify-between items-start">
              <div>
                <h3 class="text-xl font-bold text-green-800 group-hover:text-green-600 transition-colors font-['Poppins']">{{ category.name }}</h3>
                <p class="text-sm text-green-600 mt-2 font-['Poppins']">{{ category.description }}</p>
                <div class="flex items-center gap-4 mt-3">
                  <span class="text-xs text-green-500 bg-green-100 px-2 py-1 rounded-full font-['Poppins'] font-medium">Order: {{ category.order }}</span>
                  <span class="text-xs text-green-500 bg-green-100 px-2 py-1 rounded-full font-['Poppins'] font-medium">Questions: {{ category.questions?.length || 0 }}</span>
                  <span
                    :class="[
                      'px-3 py-1 rounded-full text-xs font-bold font-[\'Poppins\']',
                      category.is_active
                        ? 'bg-gradient-to-r from-green-100 to-green-200 text-green-800'
                        : 'bg-gradient-to-r from-red-100 to-red-200 text-red-800'
                    ]"
                  >
                    {{ category.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </div>
              </div>
              <div class="flex gap-2">
                <button
                  @click="editCategory(category)"
                  class="text-green-600 hover:text-green-800 hover:bg-green-50 p-2 rounded-lg transition-all duration-200"
                  title="Edit Category"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                  </svg>
                </button>
                <button
                  @click="deleteCategory(category)"
                  class="text-red-600 hover:text-red-800 hover:bg-red-50 p-2 rounded-lg transition-all duration-200"
                  title="Delete Category"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Questions List -->
          <div class="p-6">
            <div class="flex justify-between items-center mb-4">
              <h4 class="text-sm font-bold text-green-800 font-['Poppins']">Questions</h4>
              <button
                @click="addQuestionToCategory(category)"
                class="text-green-600 hover:text-green-800 hover:bg-green-50 text-sm flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200 font-['Poppins'] font-medium"
              >
                <svg class="w-4 h-4 hover:rotate-90 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                </svg>
                Add Question
              </button>
            </div>
            
            <div v-if="category.questions && category.questions.length > 0" class="space-y-3">
              <div
                v-for="question in category.questions"
                :key="question.id"
                class="bg-gradient-to-r from-green-50 to-white rounded-xl p-4 hover:from-green-100 hover:to-green-50 transition-all duration-200 border border-green-200 hover:border-green-300 hover:shadow-md"
              >
                <div class="flex justify-between items-start">
                  <div class="flex-1">
                    <p class="text-sm font-semibold text-green-900 font-['Poppins']">{{ question.question_text }}</p>
                    <div class="flex items-center gap-2 mt-2">
                      <span class="text-xs bg-gradient-to-r from-green-100 to-green-200 text-green-800 px-3 py-1 rounded-full font-['Poppins'] font-medium">
                        {{ question.question_type }}
                      </span>
                      <span
                        v-if="question.is_required"
                        class="text-xs bg-gradient-to-r from-red-100 to-red-200 text-red-800 px-3 py-1 rounded-full font-['Poppins'] font-medium"
                      >
                        Required
                      </span>
                      <span class="text-xs text-green-600 bg-green-100 px-2 py-1 rounded-full font-['Poppins']">Order: {{ question.order }}</span>
                    </div>
                  </div>
                  <div class="flex gap-2 ml-2">
                    <button
                      @click="editQuestion(question)"
                      class="text-green-600 hover:text-green-800 hover:bg-green-100 p-2 rounded-lg transition-all duration-200"
                      title="Edit Question"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                      </svg>
                    </button>
                    <button
                      @click="deleteQuestion(question)"
                      class="text-red-600 hover:text-red-800 hover:bg-red-100 p-2 rounded-lg transition-all duration-200"
                      title="Delete Question"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else class="text-center py-8 bg-green-50 rounded-xl border-2 border-dashed border-green-200">
              <p class="text-sm text-green-600 font-['Poppins'] font-medium mb-3">No questions yet</p>
              <button
                @click="addQuestionToCategory(category)"
                class="text-green-600 hover:text-green-800 hover:bg-green-100 text-sm px-4 py-2 rounded-lg transition-all duration-200 font-['Poppins'] font-medium"
              >
                Add the first question
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && categories.length === 0" class="text-center py-16 bg-white rounded-xl shadow-lg border-2 border-green-200">
        <svg class="mx-auto h-16 w-16 text-green-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
        </svg>
        <h3 class="mt-4 text-xl font-bold text-green-800 font-['Poppins']">No survey categories</h3>
        <p class="mt-2 text-sm text-green-600 font-['Poppins']">Get started by creating your first survey category.</p>
        <div class="mt-8">
          <button
            @click="showCreateCategoryModal = true"
            class="bg-gradient-to-r from-green-600 to-green-700 text-white px-8 py-3 rounded-xl hover:from-green-700 hover:to-green-800 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 font-['Poppins'] font-medium"
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
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

/* Custom scrollbar for long lists */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f0f9ff;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #10b981, #059669);
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, #059669, #047857);
}

/* Professional animations */
@keyframes slideInUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.group:hover {
  animation: slideInUp 0.2s ease-out;
}

/* Poppins font class */
.font-poppins {
  font-family: 'Poppins', sans-serif;
}
</style>
