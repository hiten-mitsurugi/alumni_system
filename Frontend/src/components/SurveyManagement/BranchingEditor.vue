<template>
  <DraggableModal
    title="Edit Branching Logic"
    @close="$emit('close')"
    large
  >
    <div class="space-y-6">
      <!-- Info -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex gap-3">
          <svg class="w-5 h-5 text-blue-600 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <div class="text-sm text-blue-800">
            <p class="font-medium mb-1">Branching Logic</p>
            <p>Configure where respondents go next based on their answer. If no branching is set, they proceed to the next section in order.</p>
          </div>
        </div>
      </div>

      <!-- Question Info -->
      <div class="bg-gray-50 rounded-lg p-4">
        <h4 class="text-sm font-semibold text-gray-700 mb-2">Question</h4>
        <p class="text-gray-900">{{ question.question_text }}</p>
        <p class="text-xs text-gray-500 mt-1">Type: {{ formatQuestionType(question.question_type) }}</p>
      </div>

      <!-- Branching Rules -->
      <div class="space-y-3">
        <h4 class="text-sm font-semibold text-gray-700">Branching Rules</h4>
        
        <div
          v-for="(option, index) in question.options"
          :key="index"
          class="bg-white border border-gray-200 rounded-lg p-4"
        >
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-3">
              <span class="bg-orange-100 text-orange-700 px-2 py-1 rounded text-sm font-medium">
                {{ option }}
              </span>
            </div>
            <span class="text-sm text-gray-500">goes to →</span>
          </div>

          <div class="flex items-center gap-3">
            <select
              v-model="branchingRules[option]"
              class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option :value="null">Continue to next section (default)</option>
              <option :value="'submit'">Submit form</option>
              <optgroup label="Jump to Section">
                <option
                  v-for="section in availableSections"
                  :key="section.id"
                  :value="section.id"
                >
                  {{ section.name }}
                </option>
              </optgroup>
            </select>

            <button
              v-if="branchingRules[option]"
              type="button"
              @click="branchingRules[option] = null"
              class="text-gray-400 hover:text-red-600 transition"
              title="Clear rule"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Preview -->
      <div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <h4 class="text-sm font-semibold text-purple-900 mb-3">Preview</h4>
        <div class="space-y-2 text-sm text-purple-800">
          <div v-for="(option, index) in question.options" :key="index">
            <span class="font-medium">{{ option }}</span>
            <span class="text-purple-600 mx-2">→</span>
            <span>{{ getBranchingDescription(branchingRules[option]) }}</span>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end gap-3 pt-4 border-t border-gray-200">
        <button
          type="button"
          @click="$emit('close')"
          class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
        >
          Cancel
        </button>
        <button
          type="button"
          @click="handleSave"
          class="bg-orange-600 text-white px-6 py-2 rounded-lg hover:bg-orange-700 transition"
        >
          Save Branching
        </button>
      </div>
    </div>
  </DraggableModal>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useSections } from './composables/useSections'
import DraggableModal from './DraggableModal.vue'

const props = defineProps({
  question: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'save'])

const { sections, loadSections } = useSections()

const branchingRules = reactive({})
const availableSections = ref([])

onMounted(async () => {
  // Load existing branching rules
  if (props.question.branching) {
    Object.assign(branchingRules, props.question.branching)
  }

  // Load available sections (from the same form)
  await loadSections()
  
  // Filter to get sections that come after the current question's section
  const currentSection = sections.value?.find(s => 
    s.questions?.some(q => q.id === props.question.id)
  )
  
  if (currentSection) {
    availableSections.value = sections.value?.filter(s => 
      s.order_index > currentSection.order_index
    ) || []
  }
})

const formatQuestionType = (type) => {
  const types = {
    'radio': 'Multiple Choice',
    'dropdown': 'Dropdown'
  }
  return types[type] || type
}

const getBranchingDescription = (target) => {
  if (!target) return 'Continue to next section'
  if (target === 'submit') return 'Submit form'
  
  const section = availableSections.value.find(s => s.id === target)
  return section ? `Jump to "${section.name}"` : 'Unknown section'
}

const handleSave = () => {
  // Filter out null values
  const cleanedRules = {}
  Object.entries(branchingRules).forEach(([option, target]) => {
    if (target !== null) {
      cleanedRules[option] = target
    }
  })
  
  emit('save', cleanedRules)
}
</script>
