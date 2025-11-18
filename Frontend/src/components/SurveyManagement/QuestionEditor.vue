<template>
  <DraggableModal
    :title="question ? 'Edit Question' : 'Create Question'"
    @close="$emit('close')"
    large
  >
    <form @submit.prevent="handleSubmit" class="space-y-5">
      <!-- Question Text -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Question Text *
        </label>
        <input
          v-model="form.question_text"
          type="text"
          required
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          placeholder="Enter your question"
        />
      </div>

      <!-- Help Text -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Help Text (optional)
        </label>
        <input
          v-model="form.help_text"
          type="text"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          placeholder="Additional guidance for respondents"
        />
      </div>

      <!-- Question Type -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Question Type *
        </label>
        <select
          v-model="form.question_type"
          required
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
        >
          <optgroup label="Text Input">
            <option value="text">Short Text</option>
            <option value="textarea">Long Text (Paragraph)</option>
            <option value="email">Email</option>
            <option value="tel">Phone Number</option>
            <option value="number">Number</option>
            <option value="date">Date</option>
          </optgroup>
          <optgroup label="Choice">
            <option value="radio">Multiple Choice</option>
            <option value="checkbox">Checkboxes</option>
            <option value="dropdown">Dropdown</option>
          </optgroup>
          <optgroup label="Scale & Grid">
            <option value="rating">Star Rating</option>
            <option value="linear_scale">Linear Scale</option>
            <option value="multi_choice_grid">Multiple Choice Grid</option>
            <option value="checkbox_grid">Checkbox Grid</option>
          </optgroup>
          <optgroup label="Upload">
            <option value="file">File Upload</option>
          </optgroup>
        </select>
      </div>

      <!-- Options (for choice-based questions) -->
      <div v-if="needsOptions" class="bg-gray-50 rounded-lg p-4">
        <label class="block text-sm font-medium text-gray-700 mb-3">
          Answer Options *
        </label>
        <div class="space-y-2">
          <div
            v-for="(option, index) in options"
            :key="index"
            class="flex items-center gap-2"
          >
            <span class="text-gray-500 text-sm w-6">{{ index + 1 }}.</span>
            <input
              v-model="options[index]"
              type="text"
              class="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"
              :placeholder="`Option ${index + 1}`"
            />
            <button
              v-if="options.length > 1"
              type="button"
              @click="removeOption(index)"
              class="text-red-600 hover:bg-red-50 p-2 rounded transition"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>
        <button
          type="button"
          @click="addOption"
          class="mt-3 text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          Add Option
        </button>
      </div>

      <!-- Scale Settings (for linear_scale) -->
      <div v-if="form.question_type === 'linear_scale'" class="bg-gray-50 rounded-lg p-4 space-y-3">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Minimum</label>
            <input
              v-model.number="scaleSettings.min"
              type="number"
              min="0"
              max="1"
              class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Maximum</label>
            <input
              v-model.number="scaleSettings.max"
              type="number"
              min="2"
              max="10"
              class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"
            />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Min Label</label>
          <input
            v-model="scaleSettings.minLabel"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"
            placeholder="e.g., Not at all satisfied"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Max Label</label>
          <input
            v-model="scaleSettings.maxLabel"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"
            placeholder="e.g., Extremely satisfied"
          />
        </div>
      </div>

      <!-- Validation Settings -->
      <div class="bg-gray-50 rounded-lg p-4 space-y-3">
        <h4 class="text-sm font-semibold text-gray-700">Validation</h4>
        
        <div class="flex items-center">
          <input
            v-model="form.is_required"
            type="checkbox"
            id="required"
            class="w-4 h-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
          />
          <label for="required" class="ml-2 text-sm text-gray-700">
            Required question
          </label>
        </div>

        <div v-if="form.question_type === 'text' || form.question_type === 'textarea'">
          <label class="block text-sm font-medium text-gray-700 mb-2">Character Limit</label>
          <input
            v-model.number="form.max_length"
            type="number"
            min="0"
            class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"
            placeholder="No limit"
          />
        </div>
      </div>

      <!-- Order -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Order
        </label>
        <input
          v-model.number="form.order_index"
          type="number"
          min="0"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
        />
      </div>

      <!-- Submit Buttons -->
      <div class="flex justify-end gap-3 pt-4 border-t border-gray-200">
        <button
          type="button"
          @click="$emit('close')"
          class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
        >
          Cancel
        </button>
        <button
          type="submit"
          :disabled="loading"
          class="bg-orange-600 text-white px-6 py-2 rounded-lg hover:bg-orange-700 transition disabled:opacity-50"
        >
          {{ loading ? 'Saving...' : (question ? 'Update' : 'Create') }}
        </button>
      </div>
    </form>
  </DraggableModal>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useQuestions } from './composables/useQuestions'
import DraggableModal from './DraggableModal.vue'

const props = defineProps({
  question: {
    type: Object,
    default: null
  },
  sectionId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['close', 'save'])

const { createQuestion, updateQuestion, loading } = useQuestions()

const form = reactive({
  question_text: props.question?.question_text || '',
  help_text: props.question?.help_text || '',
  question_type: props.question?.question_type || 'text',
  is_required: props.question?.is_required || false,
  max_length: props.question?.max_length || null,
  order_index: props.question?.order_index || 0
})

const options = ref(
  props.question?.options ? [...props.question.options] : ['']
)

const scaleSettings = reactive({
  min: props.question?.validation_rules?.min || 1,
  max: props.question?.validation_rules?.max || 5,
  minLabel: props.question?.validation_rules?.minLabel || '',
  maxLabel: props.question?.validation_rules?.maxLabel || ''
})

const needsOptions = computed(() => {
  return ['radio', 'checkbox', 'dropdown'].includes(form.question_type)
})

watch(() => form.question_type, (newType) => {
  if (!['radio', 'checkbox', 'dropdown'].includes(newType)) {
    options.value = ['']
  } else if (options.value.length === 1 && options.value[0] === '') {
    options.value = ['Option 1', 'Option 2']
  }
})

const addOption = () => {
  options.value.push(`Option ${options.value.length + 1}`)
}

const removeOption = (index) => {
  options.value.splice(index, 1)
}

const handleSubmit = async () => {
  const data = {
    ...form,
    category: props.sectionId
  }

  // Add options for choice-based questions
  if (needsOptions.value) {
    data.options = options.value.filter(opt => opt.trim() !== '')
  }

  // Add scale settings
  if (form.question_type === 'linear_scale') {
    data.validation_rules = { ...scaleSettings }
  }

  if (props.question) {
    await updateQuestion(props.question.id, data)
  } else {
    await createQuestion(data)
  }

  emit('save')
}
</script>
