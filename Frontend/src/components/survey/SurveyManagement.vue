<template>
  <div class="p-8 bg-gradient-to-br from-slate-50 to-slate-100 min-h-screen">
    <!-- Main Container -->
    <div class="max-w-7xl mx-auto">
      <!-- Header Section -->
      <SurveyHeader @export-click="showExportModal = true" />

      <!-- Tab Navigation -->
      <SurveyTabNavigation
        :activeTab="activeTab"
        @update:activeTab="activeTab = $event"
      />

      <!-- Tab Content -->
      <div class="mt-8">
        <!-- Categories Tab -->
        <CategoriesTab
          v-if="activeTab === 'categories'"
          :paginatedCategories="paginatedCategories"
          :currentPage="currentCategoryPage"
          :totalPages="totalCategoryPages"
          :pageNumbers="categoriesPageNumbers"
          @add-category="openCategoryModal()"
          @edit-category="openCategoryModal($event)"
          @delete-category="deleteCategory"
          @view-questions="viewCategoryQuestions"
          @page-change="goToCategoryPage"
        />

        <!-- Questions Tab -->
        <QuestionsTab
          v-if="activeTab === 'questions'"
          :paginatedQuestions="paginatedQuestions"
          :questionTypes="questionTypes"
          :currentPage="currentQuestionPage"
          :totalPages="totalQuestionPages"
          :totalQuestions="questions.length"
          :itemsPerPage="questionsPerPage"
          :pageNumbers="questionsPageNumbers"
          @add-question="openQuestionModal()"
          @edit-question="openQuestionModal($event)"
          @delete-question="deleteQuestion"
          @page-change="goToQuestionPage"
        />

        <!-- Analytics Tab -->
        <AnalyticsTab
          v-if="activeTab === 'analytics'"
          :analytics="analytics"
          :isLoading="loading"
        />
      </div>

      <!-- Modals -->
      <CategoryModal
        :show="showCategoryModal"
        :category="selectedCategoryForModal"
        :isDragging="isDragging && draggedModal === 'category'"
        :modalPosition="modalPositions.category"
        @close="showCategoryModal = false"
        @save="saveCategory"
        @drag-start="startDrag('category', $event)"
        @reset-position="resetModalPosition('category')"
      />

      <QuestionModal
        :show="showQuestionModal"
        :question="questionForm.id ? questions.find(q => q.id === questionForm.id) : null"
        :availableQuestions="categories"
        :questionTypes="questionTypes"
        :isDragging="isDragging && draggedModal === 'question'"
        :modalPosition="modalPositions.question"
        @close="showQuestionModal = false"
        @save="saveQuestion"
        @drag-start="startDrag('question', $event)"
        @reset-position="resetModalPosition('question')"
      />

      <AnalyticsModal
        :show="showAnalyticsModal"
        :analytics="analytics"
        :isDragging="isDragging && draggedModal === 'analytics'"
        :modalPosition="modalPositions.analytics"
        @close="showAnalyticsModal = false"
        @drag-start="startDrag('analytics', $event)"
        @reset-position="resetModalPosition('analytics')"
      />

      <ExportModal
        :show="showExportModal"
        :categories="categories"
        :isExporting="isExporting"
        :exportFormat="exportFormat"
        :exportCategory="exportCategory"
        :exportDateFrom="exportDateFrom"
        :exportDateTo="exportDateTo"
        :exportProfileFields="exportProfileFields"
        :isDragging="isDragging && draggedModal === 'export'"
        :modalPosition="modalPositions.export"
        @close="showExportModal = false"
        @export="handleExport"
        @drag-start="startDrag('export', $event)"
        @reset-position="resetModalPosition('export')"
      />

      <CategoryQuestionsModal
        :show="showCategoryQuestionsModal"
        :category="selectedCategoryForQuestions"
        :questions="questions"
        :questionTypes="questionTypes"
        :isDragging="isDragging && draggedModal === 'categoryQuestions'"
        :modalPosition="modalPositions.categoryQuestions"
        @close="showCategoryQuestionsModal = false"
        @drag-start="startDrag('categoryQuestions', $event)"
        @reset-position="resetModalPosition('categoryQuestions')"
      />
    </div>

    <!-- Global drag handler -->
    <div v-if="isDragging" @mousemove="onDrag" @mouseup="stopDrag" class="fixed inset-0 z-50 cursor-grabbing" />
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

// Components
import SurveyHeader from './SurveyHeader.vue'
import SurveyTabNavigation from './SurveyTabNavigation.vue'
import CategoriesTab from './CategoriesTab.vue'
import QuestionsTab from './QuestionsTab.vue'
import AnalyticsTab from './AnalyticsTab.vue'
import CategoryModal from './CategoryModal.vue'
import QuestionModal from './QuestionModal.vue'
import AnalyticsModal from './AnalyticsModal.vue'
import ExportModal from './ExportModal.vue'
import CategoryQuestionsModal from './CategoryQuestionsModal.vue'

// Composables
import { useSurveyManagementLogic } from '../../composables/useSurveyManagementLogic'
import { useCategoryManagement } from '../../composables/useCategoryManagement'
import { useQuestionManagement } from '../../composables/useQuestionManagement'
import { useExportManagement } from '../../composables/useExportManagement'
import { useDraggableModals } from '../../composables/useDraggableModals'
import { usePaginationLogic } from '../../composables/usePaginationLogic'

// Core logic
const {
  loading,
  activeTab,
  categories,
  questions,
  analytics,
  questionTypes
} = useSurveyManagementLogic()

// Category management
const {
  categoryForm: categoryFormRef,
  showCategoryModal,
  selectedCategoryForModal,
  categoryQuestions,
  openCategoryModal,
  saveCategory,
  deleteCategory,
  selectCategory
} = useCategoryManagement()

// Question management
const {
  questionForm,
  showQuestionModal,
  openQuestionModal,
  saveQuestion,
  deleteQuestion
} = useQuestionManagement()

// Export management
const {
  exportFormat,
  exportCategory,
  exportDateFrom,
  exportDateTo,
  exportProfileFields,
  isExporting,
  showExportModal,
  exportData: handleExport
} = useExportManagement()

// Drag and drop
const {
  isDragging,
  draggedModal,
  dragOffset,
  modalPositions,
  startDrag,
  onDrag,
  stopDrag,
  resetModalPosition
} = useDraggableModals()

// Pagination
const {
  currentCategoryPage,
  currentQuestionPage,
  totalCategoryPages,
  totalQuestionPages,
  paginatedCategories,
  paginatedQuestions,
  categoriesPageNumbers,
  questionsPageNumbers,
  goToCategoryPage,
  goToQuestionPage,
  questionsPerPage
} = usePaginationLogic()

// Category Questions Modal
const showCategoryQuestionsModal = ref(false)
const selectedCategoryForQuestions = ref(null)

const viewCategoryQuestions = (category) => {
  selectedCategoryForQuestions.value = category
  showCategoryQuestionsModal.value = true
}

// Lifecycle
onMounted(() => {
  // Data loaded automatically via composables
})

onUnmounted(() => {
  // Cleanup if needed
})
</script>

<style scoped>
/* Any global styles for SurveyManagement component */
</style>
