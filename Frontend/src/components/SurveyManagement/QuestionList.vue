<template>
  <div class="space-y-3">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h4 class="text-md font-semibold text-gray-700">Questions</h4>
      <button
        @click="showCreateModal = true"
        class="bg-orange-600 text-white px-3 py-1.5 rounded text-sm hover:bg-orange-700 transition flex items-center gap-1"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
        </svg>
        Add Question
      </button>
    </div>

    <!-- Empty State -->
    <div v-if="!questions || questions.length === 0" class="text-center py-8 bg-gray-50 rounded border border-dashed border-gray-300">
      <p class="text-gray-500 text-sm">No questions yet. Click "Add Question" to create one.</p>
    </div>

    <!-- Questions Table -->
    <div v-else class="bg-white rounded border border-gray-200">
      <table class="w-full">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-12">#</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Question</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-32">Type</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-24">Required</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-32">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr
            v-for="question in sortedQuestions"
            :key="question.id"
            class="hover:bg-gray-50 transition"
          >
            <td class="px-4 py-3 text-sm text-gray-500">{{ question.order_index }}</td>
            <td class="px-4 py-3">
              <div class="text-sm font-medium text-gray-900">{{ question.question_text }}</div>
              <div v-if="question.help_text" class="text-xs text-gray-500 mt-1">{{ question.help_text }}</div>
              <div v-if="hasBranching(question)" class="mt-1">
                <span class="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">
                  🔀 Has branching logic
                </span>
              </div>
            </td>
            <td class="px-4 py-3">
              <span class="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                {{ formatQuestionType(question.question_type) }}
              </span>
            </td>
            <td class="px-4 py-3 text-center">
              <span v-if="question.is_required" class="text-red-600 font-bold">✓</span>
              <span v-else class="text-gray-300">-</span>
            </td>
            <td class="px-4 py-3">
              <div class="flex items-center gap-1">
                <button
                  @click="editQuestion(question)"
                  class="text-orange-600 hover:bg-orange-50 p-1.5 rounded transition"
                  title="Edit"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                  </svg>
                </button>
                <button
                  v-if="canHaveBranching(question)"
                  @click="editBranching(question)"
                  class="text-purple-600 hover:bg-purple-50 p-1.5 rounded transition"
                  title="Edit Branching"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/>
                  </svg>
                </button>
                <button
                  @click="confirmDelete(question)"
                  class="text-red-600 hover:bg-red-50 p-1.5 rounded transition"
                  title="Delete"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Question Editor Modal -->
    <QuestionEditor
      v-if="showCreateModal || editingQuestion"
      :question="editingQuestion"
      :sectionId="sectionId"
      @close="closeEditor"
      @save="handleSave"
    />

    <!-- Branching Editor Modal -->
    <BranchingEditor
      v-if="branchingQuestion"
      :question="branchingQuestion"
      @close="branchingQuestion = null"
      @save="handleSaveBranching"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useQuestions } from './composables/useQuestions'
import QuestionEditor from './QuestionEditor.vue'
import BranchingEditor from './BranchingEditor.vue'

const props = defineProps({
  sectionId: {
    type: Number,
    required: true
  },
  questions: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['refresh'])

const { updateQuestion, deleteQuestion } = useQuestions()

const showCreateModal = ref(false)
const editingQuestion = ref(null)
const branchingQuestion = ref(null)

const sortedQuestions = computed(() => {
  return [...props.questions].sort((a, b) => a.order_index - b.order_index)
})

const formatQuestionType = (type) => {
  const types = {
    'text': 'Text',
    'textarea': 'Long Text',
    'number': 'Number',
    'email': 'Email',
    'tel': 'Phone',
    'date': 'Date',
    'radio': 'Multiple Choice',
    'checkbox': 'Checkboxes',
    'dropdown': 'Dropdown',
    'file': 'File Upload',
    'rating': 'Rating',
    'linear_scale': 'Linear Scale',
    'multi_choice_grid': 'Multiple Choice Grid',
    'checkbox_grid': 'Checkbox Grid'
  }
  return types[type] || type
}

const canHaveBranching = (question) => {
  return ['radio', 'dropdown'].includes(question.question_type)
}

const hasBranching = (question) => {
  return question.branching && Object.keys(question.branching).length > 0
}

const editQuestion = (question) => {
  editingQuestion.value = question
}

const editBranching = (question) => {
  branchingQuestion.value = question
}

const confirmDelete = async (question) => {
  if (confirm(`Delete question "${question.question_text}"?`)) {
    await deleteQuestion(question.id)
    emit('refresh')
  }
}

const closeEditor = () => {
  showCreateModal.value = false
  editingQuestion.value = null
}

const handleSave = () => {
  closeEditor()
  emit('refresh')
}

const handleSaveBranching = async (branchingData) => {
  await updateQuestion(branchingQuestion.value.id, { branching: branchingData })
  branchingQuestion.value = null
  emit('refresh')
}
</script>
