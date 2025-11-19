<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-gray-900">Form Sections</h3>
      <button
        @click="showCreateModal = true"
        class="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition flex items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
        </svg>
        Add Section
      </button>
    </div>

    <!-- Empty State -->
    <div v-if="!sections || sections.length === 0" class="text-center py-16 bg-gray-50 rounded-lg">
      <div class="text-gray-400 text-6xl mb-4">📄</div>
      <h3 class="text-lg font-semibold text-gray-700 mb-2">No sections yet</h3>
      <p class="text-gray-500 mb-4">Create your first section to start building the form</p>
      <button
        @click="showCreateModal = true"
        class="bg-orange-600 text-white px-6 py-2 rounded-lg hover:bg-orange-700 transition"
      >
        Create Section
      </button>
    </div>

    <!-- Sections List (Draggable) -->
    <div v-else class="space-y-3">
      <div
        v-for="(section, index) in sortedSections"
        :key="section.id"
        draggable="true"
        @dragstart="handleDragStart(index)"
        @dragover.prevent
        @drop="handleDrop(index)"
        class="bg-white rounded-lg border-2 border-gray-200 p-5 hover:border-orange-300 transition cursor-move"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-start gap-4 flex-1">
            <!-- Drag Handle -->
            <div class="text-gray-400 mt-1">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16"/>
              </svg>
            </div>
            
            <!-- Section Info -->
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h4 class="text-lg font-semibold text-gray-900">{{ section.category.name }}</h4>
                <span class="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                  Order {{ section.category.order }}
                </span>
              </div>
              <p v-if="section.category.description" class="text-gray-600 text-sm mb-3">
                {{ section.category.description }}
              </p>
              <div class="flex items-center gap-4 text-sm text-gray-500">
                <span>{{ section.questions?.length || 0 }} questions</span>
                <span v-if="section.category.include_in_registration" class="text-orange-600 font-medium">
                  📋 Registration Section
                </span>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2">
            <button
              @click="selectSection(section)"
              class="text-orange-600 hover:bg-orange-50 p-2 rounded transition"
              title="View Questions"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
            </button>
            <button
              @click="editSection(section)"
              class="text-gray-600 hover:bg-gray-100 p-2 rounded transition"
              title="Edit Section"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
            </button>
            <button
              @click="confirmDelete(section)"
              class="text-red-600 hover:bg-red-50 p-2 rounded transition"
              title="Delete Section"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Questions Preview (if section is selected) -->
        <QuestionList
          v-if="selectedSectionId === section.category.id"
          :sectionId="section.category.id"
          :questions="section.questions"
          @refresh="$emit('refresh')"
          class="mt-4 pt-4 border-t border-gray-200"
        />
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <DraggableModal
      v-if="showCreateModal || editingSection"
      :title="editingSection ? 'Edit Section' : 'Create Section'"
      @close="closeModal"
    >
      <form @submit.prevent="handleSubmit" class="space-y-4">
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
          <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
          <textarea
            v-model="sectionForm.description"
            rows="3"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            placeholder="Optional description for this section"
          ></textarea>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Order</label>
          <input
            v-model.number="sectionForm.order_index"
            type="number"
            min="0"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          />
        </div>

        <div class="flex justify-end gap-3 pt-4">
          <button
            type="button"
            @click="closeModal"
            class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="loading"
            class="bg-orange-600 text-white px-6 py-2 rounded-lg hover:bg-orange-700 transition disabled:opacity-50"
          >
            {{ loading ? 'Saving...' : (editingSection ? 'Update' : 'Create') }}
          </button>
        </div>
      </form>
    </DraggableModal>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useSections } from './composables/useSections'
import surveyService from '@/services/surveyService'
import QuestionList from './QuestionList.vue'
import DraggableModal from './DraggableModal.vue'

const props = defineProps({
  formId: {
    type: Number,
    required: true
  },
  sections: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['refresh'])

const { createSection, updateSection, deleteSection, loading } = useSections()

const showCreateModal = ref(false)
const editingSection = ref(null)
const selectedSectionId = ref(null)
const draggedIndex = ref(null)

const sectionForm = reactive({
  name: '',
  description: '',
  order_index: 0
})

const sortedSections = computed(() => {
  return [...props.sections].sort((a, b) => (a.category?.order || 0) - (b.category?.order || 0))
})

const selectSection = (section) => {
  selectedSectionId.value = selectedSectionId.value === section.category.id ? null : section.category.id
}

const editSection = (section) => {
  editingSection.value = section.category
  sectionForm.name = section.category.name
  sectionForm.description = section.category.description || ''
  sectionForm.order_index = section.category.order
}

const confirmDelete = async (section) => {
  if (confirm(`Delete section "${section.category.name}"? All questions in this section will also be deleted.`)) {
    await deleteSection(section.category.id)
    emit('refresh')
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingSection.value = null
  sectionForm.name = ''
  sectionForm.description = ''
  sectionForm.order_index = props.sections.length
}

const handleSubmit = async () => {
  const data = {
    name: sectionForm.name,
    description: sectionForm.description,
    order: sectionForm.order_index
  }
  
  if (editingSection.value) {
    await updateSection(editingSection.value.id, data)
  } else {
    // Create the section
    console.log('Creating section with data:', data)
    const newSection = await createSection(data)
    console.log('Section created:', newSection)
    
    // If section was created successfully, link it to the form
    if (newSection) {
      try {
        // Get current category IDs from the form
        const currentCategoryIds = props.sections.map(s => s.category?.id).filter(Boolean)
        console.log('Current category IDs:', currentCategoryIds)
        
        // Add the new section ID
        const updatedCategoryIds = [...currentCategoryIds, newSection.id]
        console.log('Updated category IDs:', updatedCategoryIds)
        console.log('Updating form ID:', props.formId)
        
        const updatePayload = {
          category_ids: updatedCategoryIds
        }
        console.log('Update payload:', JSON.stringify(updatePayload, null, 2))
        
        // Update the form with the new category_ids
        const response = await surveyService.updateForm(props.formId, updatePayload)
        console.log('Form update response:', response)
      } catch (err) {
        console.error('Error linking section to form:', err)
        console.error('Error details:', err.response?.data)
        console.error('Error status:', err.response?.status)
        console.error('Full error:', JSON.stringify(err.response?.data, null, 2))
        alert('Section created but failed to link to form: ' + JSON.stringify(err.response?.data))
      }
    }
  }
  
  closeModal()
  emit('refresh')
}

const handleDragStart = (index) => {
  draggedIndex.value = index
}

const handleDrop = (targetIndex) => {
  if (draggedIndex.value === null || draggedIndex.value === targetIndex) return
  
  // Reorder logic would go here - update order_index for affected sections
  const newOrder = [...sortedSections.value]
  const [removed] = newOrder.splice(draggedIndex.value, 1)
  newOrder.splice(targetIndex, 0, removed)
  
  // Update order_index for all affected sections
  newOrder.forEach((section, index) => {
    if (section.order_index !== index) {
      updateSection(section.id, { order_index: index })
    }
  })
  
  draggedIndex.value = null
  emit('refresh')
}
</script>
