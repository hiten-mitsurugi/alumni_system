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
          class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
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
        <div v-else-if="activeTab === 'responses'" class="text-center py-12">
          <div class="text-gray-400 text-5xl mb-4">📊</div>
          <h3 class="text-lg font-semibold text-gray-700 mb-2">Responses</h3>
          <p class="text-gray-500">Response management coming soon</p>
        </div>
      </div>
    </div>

    <!-- Preview Modal (placeholder) -->
    <div
      v-if="showPreview"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showPreview = false"
    >
      <div class="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold text-gray-900">Preview: {{ form.name }}</h3>
          <button
            @click="showPreview = false"
            class="text-gray-500 hover:text-gray-700"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="text-center py-12">
          <p class="text-gray-500">Preview mode coming soon</p>
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
      :categoryId="questionCategoryId"
      :allQuestions="allQuestionsInForm"
      @close="closeQuestionModal"
      @save="handleQuestionSave"
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
import DraggableModal from './DraggableModal.vue'
import QuestionModal from '../modals/QuestionModal.vue'

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
  page_break: false
})

const tabs = [
  { id: 'sections', name: 'Sections & Questions' },
  { id: 'settings', name: 'Settings' },
  { id: 'responses', name: 'Responses' }
]

const allQuestionsInForm = computed(() => {
  if (!props.form.sections) return []
  return props.form.sections.flatMap(s => s.questions || [])
})

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
      page_break: sectionForm.page_break
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

const handleQuestionSave = () => {
  closeQuestionModal()
  emit('refresh')
}
</script>
