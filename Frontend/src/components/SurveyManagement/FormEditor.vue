<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between bg-white rounded-lg shadow-md p-6">
      <div class="flex items-center gap-4">
        <button
          @click="$emit('back')"
          class="text-gray-600 hover:text-gray-900 transition"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
          </svg>
        </button>
        <div>
          <h2 class="text-2xl font-bold text-gray-900">{{ form.name }}</h2>
          <p class="text-gray-600">{{ form.description || 'No description' }}</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <button
          @click="handlePublish"
          :class="[
            'px-6 py-2 rounded-lg font-medium transition',
            form.is_published
              ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              : 'bg-green-600 text-white hover:bg-green-700'
          ]"
        >
          {{ form.is_published ? 'Unpublish' : 'Publish' }}
        </button>
        <button
          @click="showPreview = true"
          class="bg-orange-600 text-white px-6 py-2 rounded-lg hover:bg-orange-700 transition"
        >
          Preview
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="bg-white rounded-lg shadow-md">
      <div class="border-b border-gray-200">
        <nav class="flex gap-8 px-6" aria-label="Tabs">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'py-4 px-1 border-b-2 font-medium text-sm transition',
              activeTab === tab.id
                ? 'border-orange-600 text-orange-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            {{ tab.name }}
          </button>
        </nav>
      </div>

      <div class="p-6">
        <!-- Sections Tab -->
        <SectionsGrid
          v-if="activeTab === 'sections'"
          :sections="form.sections || []"
          @add-section="handleAddSection"
          @section-click="handleSectionClick"
          @add-question="handleAddQuestion"
          @edit-section="handleEditSection"
          @delete-section="handleDeleteSection"
          @reorder-sections="handleReorderSections"
        />

        <!-- Settings Tab -->
        <FormSettings
          v-else-if="activeTab === 'settings'"
          :form="form"
          @save="handleSaveSettings"
        />

        <!-- Responses Tab -->
        <ResponsesView
          v-else-if="activeTab === 'responses'"
          :form="form"
        />

        <!-- Comprehensive Report Tab -->
        <ComprehensiveReportView
          v-else-if="activeTab === 'comprehensive-report'"
          :form="form"
        />
      </div>
    </div>

    <!-- Preview Modal -->
    <div
      v-if="showPreview"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showPreview = false"
    >
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-orange-50 to-white">
          <div>
            <h3 class="text-xl font-bold text-gray-900">{{ form.name }}</h3>
            <p v-if="form.description" class="text-sm text-gray-600 mt-1">{{ form.description }}</p>
          </div>
          <button
            @click="showPreview = false"
            class="text-gray-500 hover:text-gray-700 p-2 rounded-lg hover:bg-gray-100 transition"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- Preview Content -->
        <div class="flex-1 overflow-y-auto px-6 py-6">
          <div v-if="form.sections && form.sections.length > 0">
            <!-- Current Section Only -->
            <div
              v-if="form.sections[previewCurrentPage]"
              :key="form.sections[previewCurrentPage].category.id"
              class="bg-gray-50 rounded-lg p-6 border border-gray-200"
            >
              <!-- Section Header -->
              <div class="mb-6 pb-4 border-b border-gray-300">
                <div class="flex items-center gap-3 mb-2">
                  <span class="text-sm font-semibold text-orange-600 bg-orange-100 px-3 py-1 rounded-full">
                    Section {{ previewCurrentPage + 1 }} of {{ form.sections.length }}
                  </span>
                  <h4 class="text-lg font-bold text-gray-900">{{ form.sections[previewCurrentPage].category.name }}</h4>
                </div>
                <p v-if="form.sections[previewCurrentPage].category.page_description" class="text-sm text-gray-600 mt-2">
                  {{ form.sections[previewCurrentPage].category.page_description }}
                </p>
              </div>

              <!-- Questions -->
              <div v-if="form.sections[previewCurrentPage].questions && form.sections[previewCurrentPage].questions.length > 0" class="space-y-6">
                <div
                  v-for="(question, qIndex) in form.sections[previewCurrentPage].questions"
                  :key="question.id"
                  class="bg-white rounded-lg p-5 border border-gray-200"
                >
                  <!-- Question Label -->
                  <div class="mb-3">
                    <label class="block text-sm font-semibold text-gray-800">
                      {{ qIndex + 1 }}. {{ question.question_text }}
                      <span v-if="question.is_required" class="text-red-500 ml-1">*</span>
                    </label>
                    <p v-if="question.help_text" class="text-xs text-gray-500 mt-1">
                      {{ question.help_text }}
                    </p>
                  </div>

                  <!-- Preview Input (disabled/read-only) -->
                  <div class="mt-2">
                    <!-- Text/Email -->
                    <input
                      v-if="['text', 'email'].includes(question.question_type)"
                      type="text"
                      :placeholder="question.placeholder_text || 'Answer...'"
                      disabled
                      class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500"
                    />

                    <!-- Textarea -->
                    <textarea
                      v-else-if="question.question_type === 'textarea'"
                      :placeholder="question.placeholder_text || 'Answer...'"
                      rows="3"
                      disabled
                      class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500"
                    ></textarea>

                    <!-- Number/Year -->
                    <input
                      v-else-if="['number', 'year'].includes(question.question_type)"
                      type="number"
                      :placeholder="question.placeholder_text || 'Enter number...'"
                      disabled
                      class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500"
                    />

                    <!-- Date -->
                    <input
                      v-else-if="question.question_type === 'date'"
                      type="date"
                      disabled
                      class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500"
                    />

                    <!-- Radio -->
                    <div v-else-if="question.question_type === 'radio'" class="space-y-2">
                      <div
                        v-for="option in question.options"
                        :key="option"
                        class="flex items-center"
                      >
                        <input type="radio" disabled class="mr-2" />
                        <span class="text-sm text-gray-600">{{ option }}</span>
                      </div>
                    </div>

                    <!-- Checkbox -->
                    <div v-else-if="question.question_type === 'checkbox'" class="space-y-2">
                      <div
                        v-for="option in question.options"
                        :key="option"
                        class="flex items-center"
                      >
                        <input type="checkbox" disabled class="mr-2" />
                        <span class="text-sm text-gray-600">{{ option }}</span>
                      </div>
                    </div>

                    <!-- Select -->
                    <select
                      v-else-if="question.question_type === 'select'"
                      disabled
                      class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500"
                    >
                      <option value="">Select an option</option>
                      <option v-for="option in question.options" :key="option">{{ option }}</option>
                    </select>

                    <!-- Rating -->
                    <div v-else-if="question.question_type === 'rating'" class="flex items-center gap-2">
                      <span class="text-xs text-gray-500">{{ question.min_value || 1 }}</span>
                      <div class="flex gap-2">
                        <button
                          v-for="rating in getRatingRange(question)"
                          :key="rating"
                          disabled
                          class="w-10 h-10 border border-gray-300 rounded-md bg-gray-50 text-gray-400 text-sm font-medium"
                        >
                          {{ rating }}
                        </button>
                      </div>
                      <span class="text-xs text-gray-500">{{ question.max_value || 5 }}</span>
                    </div>

                    <!-- Yes/No -->
                    <div v-else-if="question.question_type === 'yes_no'" class="flex gap-4">
                      <div class="flex items-center">
                        <input type="radio" disabled class="mr-2" />
                        <span class="text-sm text-gray-600">Yes</span>
                      </div>
                      <div class="flex items-center">
                        <input type="radio" disabled class="mr-2" />
                        <span class="text-sm text-gray-600">No</span>
                      </div>
                    </div>

                    <!-- File -->
                    <input
                      v-else-if="question.question_type === 'file'"
                      type="file"
                      disabled
                      class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500"
                    />

                    <!-- Unknown type -->
                    <div v-else class="text-sm text-gray-400 italic">
                      {{ question.question_type }} input
                    </div>
                  </div>
                </div>
              </div>

              <!-- No questions -->
              <div v-else class="text-center py-8 text-gray-400">
                <p>No questions in this section</p>
              </div>
            </div>
          </div>

          <!-- No sections -->
          <div v-else class="text-center py-12 text-gray-400">
            <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            <p class="text-lg font-medium">No sections added yet</p>
            <p class="text-sm mt-1">Add sections and questions to preview the form</p>
          </div>
        </div>

        <!-- Footer with Navigation -->
        <div class="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div class="flex items-center justify-between">
            <!-- Navigation -->
            <div class="flex items-center gap-3">
              <button
                @click="previewCurrentPage = Math.max(0, previewCurrentPage - 1)"
                :disabled="previewCurrentPage === 0"
                class="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                </svg>
                Previous
              </button>
              
              <span class="text-sm text-gray-600 font-medium">
                Page {{ previewCurrentPage + 1 }} / {{ form.sections?.length || 0 }}
              </span>

              <button
                @click="previewCurrentPage = Math.min((form.sections?.length || 1) - 1, previewCurrentPage + 1)"
                :disabled="previewCurrentPage >= (form.sections?.length || 1) - 1"
                class="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                Next
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
              </button>
            </div>

            <!-- Close Button -->
            <button
              @click="showPreview = false; previewCurrentPage = 0"
              class="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
            >
              Close Preview
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Section View Side Panel -->
    <SectionView
      :isOpen="selectedSection !== null"
      :section="selectedSection"
      @close="selectedSection = null"
      @add-question="handleAddQuestion"
      @edit-question="handleEditQuestion"
      @delete-question="handleDeleteQuestion"
      @edit-section="handleEditSection"
      @delete-section="handleDeleteSection"
      @question-click="handleEditQuestion"
    />

    <!-- Section Create/Edit Modal -->
    <DraggableModal
      v-if="showSectionModal"
      :title="editingSectionData ? 'Edit Section' : 'Create Section'"
      @close="closeSectionModal"
    >
      <form @submit.prevent="handleSectionSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Section Name *</label>
          <input
            v-model="sectionForm.name"
            type="text"
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            placeholder="e.g., Personal Information"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Page Title</label>
          <input
            v-model="sectionForm.page_title"
            type="text"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            placeholder="Title shown on the page"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
          <textarea
            v-model="sectionForm.page_description"
            rows="3"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            placeholder="Optional description for this section"
          ></textarea>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Order</label>
          <input
            v-model.number="sectionForm.order"
            type="number"
            min="0"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          />
        </div>

        <div class="flex items-center gap-2">
          <input
            v-model="sectionForm.page_break"
            type="checkbox"
            id="page_break"
            class="rounded border-gray-300 text-orange-600 focus:ring-orange-500"
          />
          <label for="page_break" class="text-sm font-medium text-gray-700">
            Page break before this section
          </label>
        </div>

        <div class="flex items-center gap-2">
          <input
            v-model="sectionForm.include_in_registration"
            type="checkbox"
            id="include_in_registration"
            class="rounded border-gray-300 text-orange-600 focus:ring-orange-500"
          />
          <label for="include_in_registration" class="text-sm font-medium text-gray-700">
            Show this section in registration
          </label>
        </div>

        <div class="flex justify-end gap-3 pt-4">
          <button
            type="button"
            @click="closeSectionModal"
            class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="sectionLoading"
            class="bg-orange-600 text-white px-6 py-2 rounded-lg hover:bg-orange-700 transition disabled:opacity-50"
          >
            {{ sectionLoading ? 'Saving...' : (editingSectionData ? 'Update' : 'Create') }}
          </button>
        </div>
      </form>
    </DraggableModal>

    <!-- Question Modal -->
    <QuestionModal
      v-if="showQuestionModal"
      :question="editingQuestion"
      :selected-category-id="questionCategoryId"
      :categories="allCategories"
      :questions="allQuestionsInForm"
      :questions-length="allQuestionsInForm.length"
      :is-dragging="false"
      :dragged-modal="''"
      :modal-position="{ x: 0, y: 0 }"
      @close="closeQuestionModal"
      @save="handleQuestionSave"
      @start-drag="() => {}"
      @reset-position="() => {}"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useForms } from './composables/useForms'
import { useSections } from './composables/useSections'
import surveyService from '@/services/surveyService'
import SectionsGrid from './SectionsGrid.vue'
import SectionView from './SectionView.vue'
import FormSettings from './FormSettings.vue'
import ResponsesView from './ResponsesView.vue'
import ComprehensiveReportView from './ComprehensiveReportView.vue'
import DraggableModal from './DraggableModal.vue'
import QuestionModal from './QuestionModal.vue'

const props = defineProps({
  form: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['back', 'save', 'refresh'])

const { publishForm } = useForms()
const { createSection, updateSection, deleteSection } = useSections()

const activeTab = ref('sections')
const showPreview = ref(false)
const previewCurrentPage = ref(0) // For preview pagination
const selectedSection = ref(null)
const showSectionModal = ref(false)
const editingSectionData = ref(null)
const sectionLoading = ref(false)
const showQuestionModal = ref(false)
const editingQuestion = ref(null)
const questionCategoryId = ref(null)

const sectionForm = reactive({
  name: '',
  page_title: '',
  page_description: '',
  order: 0,
  page_break: false,
  include_in_registration: false
})

const tabs = [
  { id: 'sections', name: 'Sections & Questions' },
  { id: 'settings', name: 'Settings' },
  { id: 'comprehensive-report', name: 'Comprehensive Report' }
]

const allQuestionsInForm = computed(() => {
  if (!props.form.sections) return []
  return props.form.sections.flatMap(s => s.questions || [])
})

const allCategories = computed(() => {
  if (!props.form.sections) return []
  return props.form.sections.map(s => s.category)
})

// Helper to generate rating range for preview
const getRatingRange = (question) => {
  const min = question.min_value || 1
  const max = question.max_value || 5
  const range = []
  for (let i = min; i <= max; i++) {
    range.push(i)
  }
  return range
}

const handlePublish = async () => {
  const newStatus = !props.form.is_published
  await publishForm(props.form.id, { is_published: newStatus })
  emit('refresh')
}

const handleSaveSettings = (settings) => {
  emit('save', settings)
}

const handleSectionClick = (section) => {
  selectedSection.value = section
}

const handleAddSection = () => {
  showSectionModal.value = true
  editingSectionData.value = null
  sectionForm.name = ''
  sectionForm.page_title = ''
  sectionForm.page_description = ''
  sectionForm.order = props.form.sections?.length || 0
  sectionForm.page_break = false
}

const handleEditSection = (section) => {
  const cat = section.category || section
  editingSectionData.value = cat
  showSectionModal.value = true
  sectionForm.name = cat.name
  sectionForm.page_title = cat.page_title || ''
  sectionForm.page_description = cat.page_description || ''
  sectionForm.order = cat.order || 0
  sectionForm.page_break = cat.page_break || false
  sectionForm.include_in_registration = !!cat.include_in_registration
  selectedSection.value = null
}

const handleDeleteSection = async (categoryId) => {
  if (!confirm('Delete this section? All questions in this section will also be deleted.')) {
    return
  }
  
  try {
    await deleteSection(categoryId)
    selectedSection.value = null
    emit('refresh')
  } catch (err) {
    console.error('Error deleting section:', err)
    alert('Failed to delete section: ' + (err.response?.data?.detail || err.message))
  }
}

const handleReorderSections = async (newCategoryIds) => {
  try {
    console.log('Reordering sections with IDs:', newCategoryIds)
    await surveyService.updateForm(props.form.id, { category_ids: newCategoryIds })
    emit('refresh')
  } catch (err) {
    console.error('Error reordering sections:', err)
    alert('Failed to reorder sections: ' + (err.response?.data?.detail || err.message))
  }
}

const closeSectionModal = () => {
  showSectionModal.value = false
  editingSectionData.value = null
}

const handleSectionSubmit = async () => {
  sectionLoading.value = true
  
  try {
    const data = {
      name: sectionForm.name,
      page_title: sectionForm.page_title,
      page_description: sectionForm.page_description,
      order: sectionForm.order,
      page_break: sectionForm.page_break,
      include_in_registration: sectionForm.include_in_registration
    }
    
    if (editingSectionData.value) {
      // Update existing section
      await updateSection(editingSectionData.value.id, data)
    } else {
      // Create new section
      const newSection = await createSection(data)
      
      if (newSection) {
        // Link the new section to the form
        const currentCategoryIds = (props.form.sections || []).map(s => s.category?.id).filter(Boolean)
        const updatedCategoryIds = [...currentCategoryIds, newSection.id]
        
        await surveyService.updateForm(props.form.id, { category_ids: updatedCategoryIds })
      }
    }
    
    closeSectionModal()
    emit('refresh')
  } catch (err) {
    console.error('Error saving section:', err)
    alert('Failed to save section: ' + (err.response?.data?.detail || err.message))
  } finally {
    sectionLoading.value = false
  }
}

const handleAddQuestion = (categoryId) => {
  questionCategoryId.value = categoryId
  editingQuestion.value = null
  showQuestionModal.value = true
}

const handleEditQuestion = (question) => {
  editingQuestion.value = question
  questionCategoryId.value = question.category || question.category_id
  showQuestionModal.value = true
}

const handleDeleteQuestion = async (questionId) => {
  if (!confirm('Delete this question? This action cannot be undone.')) {
    return
  }
  
  try {
    await surveyService.deleteQuestion(questionId)
    emit('refresh')
  } catch (err) {
    console.error('Error deleting question:', err)
    alert('Failed to delete question: ' + (err.response?.data?.detail || err.message))
  }
}

const closeQuestionModal = () => {
  showQuestionModal.value = false
  editingQuestion.value = null
  questionCategoryId.value = null
}

const handleQuestionSave = async () => {
  // Store the currently selected section ID before refresh
  const selectedSectionId = selectedSection.value?.category?.id
  
  closeQuestionModal()
  emit('refresh')
  
  // Wait a bit for the refresh to complete, then restore the selected section
  if (selectedSectionId) {
    setTimeout(() => {
      const section = props.form.sections?.find(s => s.category.id === selectedSectionId)
      if (section) {
        selectedSection.value = section
      }
    }, 100)
  }
}
</script>
