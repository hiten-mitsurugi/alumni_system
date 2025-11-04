<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="show" class="fixed inset-0 bg-black/50 z-40" @click="$emit('close')"></div>
    </Transition>
    <Transition name="scale">
      <div
        v-if="show"
        :style="modalPosition"
        @mousedown="$emit('drag-start', $event)"
        class="fixed bg-white rounded-xl shadow-2xl border border-slate-200 z-50 w-full max-w-2xl cursor-move transform transition-transform duration-200"
      >
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-gradient-to-r from-slate-50 to-slate-100 rounded-t-xl cursor-default" @mousedown.stop>
          <h3 class="text-lg font-semibold text-slate-800">
            {{ questionForm.id ? 'Edit Question' : 'Create New Question' }}
          </h3>
          <button
            @click="$emit('close')"
            class="p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-200 rounded-lg transition-all duration-200 cursor-pointer"
          >
            <X class="w-5 h-5" />
          </button>
        </div>

        <!-- Form Content -->
        <div class="px-6 py-6 space-y-5 max-h-[60vh] overflow-y-auto">
          <!-- Category Selection -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">
              Category <span class="text-red-500">*</span>
            </label>
            <select
              v-model="questionForm.category_id"
              class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-slate-800"
            >
              <option value="">Select a category</option>
              <option v-for="cat in availableQuestions" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
            <p v-if="errors.category_id" class="text-red-500 text-xs mt-1">{{ errors.category_id }}</p>
          </div>

          <!-- Question Text -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">
              Question <span class="text-red-500">*</span>
            </label>
            <textarea
              v-model="questionForm.question_text"
              placeholder="Enter your survey question"
              rows="3"
              class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-slate-800 placeholder-slate-400 resize-none"
            ></textarea>
            <p v-if="errors.question_text" class="text-red-500 text-xs mt-1">{{ errors.question_text }}</p>
          </div>

          <!-- Question Type -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">
              Question Type <span class="text-red-500">*</span>
            </label>
            <select
              v-model="questionForm.question_type"
              @change="resetOptions"
              class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-slate-800"
            >
              <option v-for="type in questionTypes" :key="type.value" :value="type.value">
                {{ type.label }}
              </option>
            </select>
            <p v-if="errors.question_type" class="text-red-500 text-xs mt-1">{{ errors.question_type }}</p>
          </div>

          <!-- Display Order -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">Display Order</label>
            <input
              v-model.number="questionForm.order"
              type="number"
              min="0"
              placeholder="0"
              class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-slate-800 placeholder-slate-400"
            />
          </div>

          <!-- Options (for select/radio/checkbox) -->
          <div v-if="['select', 'radio', 'checkbox', 'dropdown'].includes(questionForm.question_type)" class="space-y-3">
            <label class="block text-sm font-medium text-slate-700">Options</label>
            <div class="space-y-2 max-h-48 overflow-y-auto">
              <div v-for="(option, index) in questionForm.options" :key="index" class="flex gap-2">
                <input
                  v-model="option.value"
                  type="text"
                  placeholder="Option text"
                  class="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-slate-800"
                />
                <button
                  @click="removeOption(index)"
                  class="p-2 text-red-400 hover:bg-red-50 rounded-lg transition-all duration-200 cursor-pointer"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>
            <button
              @click="addOption"
              class="w-full px-3 py-2 border border-dashed border-slate-300 text-slate-600 rounded-lg hover:border-orange-500 hover:text-orange-600 transition-all duration-200 cursor-pointer text-sm font-medium"
            >
              + Add Option
            </button>
          </div>

          <!-- Placeholder Text -->
          <div v-if="['text', 'email', 'number', 'textarea'].includes(questionForm.question_type)">
            <label class="block text-sm font-medium text-slate-700 mb-2">Placeholder Text</label>
            <input
              v-model="questionForm.placeholder"
              type="text"
              placeholder="e.g., Enter your answer"
              class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-slate-800 placeholder-slate-400"
            />
          </div>

          <!-- Help Text -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">Help Text</label>
            <textarea
              v-model="questionForm.help_text"
              placeholder="Additional guidance for respondents"
              rows="2"
              class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-slate-800 placeholder-slate-400 resize-none"
            ></textarea>
          </div>

          <!-- Min/Max (for rating) -->
          <div v-if="questionForm.question_type === 'rating'" class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">Min Value</label>
              <input
                v-model.number="questionForm.min_value"
                type="number"
                min="1"
                placeholder="1"
                class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-slate-800"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">Max Value</label>
              <input
                v-model.number="questionForm.max_value"
                type="number"
                min="1"
                placeholder="5"
                class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-slate-800"
              />
            </div>
          </div>

          <!-- Conditional Logic -->
          <div class="space-y-3">
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                v-model="questionForm.has_conditional"
                type="checkbox"
                class="w-4 h-4 rounded border-slate-300 text-orange-600 focus:ring-orange-500"
              />
              <span class="text-sm font-medium text-slate-700">This question depends on another</span>
            </label>
            <div v-if="questionForm.has_conditional" class="space-y-3 p-3 bg-slate-50 rounded-lg">
              <select
                v-model="questionForm.depends_on_question"
                class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-slate-800"
              >
                <option value="">Select question to depend on</option>
                <option v-for="q in availableQuestions" :key="q.id" :value="q.id">
                  {{ q.question_text?.substring(0, 50) }}...
                </option>
              </select>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Expected Value</label>
                <input
                  v-model="questionForm.conditional_value"
                  type="text"
                  placeholder="e.g., Yes, Option 1"
                  class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-slate-800 placeholder-slate-400"
                />
              </div>
            </div>
          </div>

          <!-- Required & Active Status -->
          <div class="space-y-3 p-4 bg-slate-50 rounded-lg">
            <label class="flex items-center justify-between cursor-pointer">
              <span class="text-sm font-medium text-slate-700">Required</span>
              <input
                v-model="questionForm.is_required"
                type="checkbox"
                class="w-4 h-4 rounded border-slate-300 text-orange-600 focus:ring-orange-500"
              />
            </label>
            <label class="flex items-center justify-between cursor-pointer">
              <span class="text-sm font-medium text-slate-700">Active</span>
              <input
                v-model="questionForm.is_active"
                type="checkbox"
                class="w-4 h-4 rounded border-slate-300 text-orange-600 focus:ring-orange-500"
              />
            </label>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex gap-3 px-6 py-4 border-t border-slate-200 bg-slate-50 rounded-b-xl cursor-default" @mousedown.stop>
          <button
            @click="$emit('close')"
            class="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-100 transition-all duration-200 font-medium cursor-pointer"
          >
            Cancel
          </button>
          <button
            @click="handleSave"
            class="flex-1 px-4 py-2 bg-gradient-to-r from-orange-600 to-orange-500 text-white rounded-lg hover:from-orange-500 hover:to-orange-600 transition-all duration-200 font-medium cursor-pointer"
          >
            {{ questionForm.id ? 'Update' : 'Create' }}
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import { X, Trash2 } from 'lucide-vue-next'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  question: {
    type: Object,
    default: null
  },
  availableQuestions: {
    type: Array,
    required: true
  },
  questionTypes: {
    type: Array,
    required: true
  },
  isDragging: {
    type: Boolean,
    default: false
  },
  modalPosition: {
    type: Object,
    default: () => ({
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)'
    })
  }
})

const emit = defineEmits(['close', 'save', 'drag-start', 'reset-position'])

const questionForm = ref({
  id: null,
  category_id: '',
  question_text: '',
  question_type: 'text',
  order: 0,
  options: [],
  placeholder: '',
  help_text: '',
  min_value: 1,
  max_value: 5,
  has_conditional: false,
  depends_on_question: '',
  conditional_value: '',
  is_required: false,
  is_active: true
})

const errors = ref({
  category_id: '',
  question_text: '',
  question_type: ''
})

watch(() => props.show, (newVal) => {
  if (newVal) {
    if (props.question) {
      questionForm.value = {
        id: props.question.id,
        category_id: props.question.category_id || '',
        question_text: props.question.question_text || '',
        question_type: props.question.question_type || 'text',
        order: props.question.order || 0,
        options: props.question.options ? JSON.parse(JSON.stringify(props.question.options)) : [],
        placeholder: props.question.placeholder || '',
        help_text: props.question.help_text || '',
        min_value: props.question.min_value || 1,
        max_value: props.question.max_value || 5,
        has_conditional: !!props.question.depends_on_question,
        depends_on_question: props.question.depends_on_question || '',
        conditional_value: props.question.conditional_value || '',
        is_required: props.question.is_required ?? false,
        is_active: props.question.is_active ?? true
      }
    } else {
      questionForm.value = {
        id: null,
        category_id: '',
        question_text: '',
        question_type: 'text',
        order: 0,
        options: [],
        placeholder: '',
        help_text: '',
        min_value: 1,
        max_value: 5,
        has_conditional: false,
        depends_on_question: '',
        conditional_value: '',
        is_required: false,
        is_active: true
      }
    }
    errors.value = { category_id: '', question_text: '', question_type: '' }
  }
})

const resetOptions = () => {
  if (!['select', 'radio', 'checkbox', 'dropdown'].includes(questionForm.value.question_type)) {
    questionForm.value.options = []
  }
}

const addOption = () => {
  questionForm.value.options.push({ value: '' })
}

const removeOption = (index) => {
  questionForm.value.options.splice(index, 1)
}

const handleSave = () => {
  errors.value = { category_id: '', question_text: '', question_type: '' }

  if (!questionForm.value.category_id) {
    errors.value.category_id = 'Category is required'
  }
  if (!questionForm.value.question_text.trim()) {
    errors.value.question_text = 'Question text is required'
  }
  if (!questionForm.value.question_type) {
    errors.value.question_type = 'Question type is required'
  }

  if (errors.value.category_id || errors.value.question_text || errors.value.question_type) {
    return
  }

  emit('save', { ...questionForm.value })
  emit('close')
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.scale-enter-active,
.scale-leave-active {
  transition: all 0.3s ease;
}

.scale-enter-from,
.scale-leave-to {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.95);
}
</style>
