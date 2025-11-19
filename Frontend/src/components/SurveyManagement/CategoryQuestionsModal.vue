<script setup>
import { ref, computed } from 'vue'
import { Edit, Trash2 } from 'lucide-vue-next'
import { useThemeStore } from '@/stores/theme'

const props = defineProps({
  category: {
    type: Object,
    default: null
  },
  questions: {
    type: Array,
    default: () => []
  },
  isDragging: Boolean,
  draggedModal: String,
  modalPosition: {
    type: Object,
    default: () => ({ x: 0, y: 0 })
  }
})

const emit = defineEmits(['close', 'editQuestion', 'deleteQuestion', 'startDrag', 'resetPosition'])

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isAdminDark?.())

const categoryQuestions = computed(() => {
  if (!props.category) return []
  return props.questions.filter(q => q.category === props.category.id)
})

const getQuestionTypeLabel = (type) => {
  const types = {
    'text': 'Short Text',
    'textarea': 'Long Text',
    'number': 'Number',
    'email': 'Email',
    'date': 'Date',
    'radio': 'Single Choice',
    'checkbox': 'Multiple Choice',
    'select': 'Dropdown',
    'rating': 'Rating Scale',
    'yes_no': 'Yes/No'
  }
  return types[type] || type
}
</script>

<template>
  <div
    v-if="show"
    class="fixed inset-0 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
    @click.self="closeModal"
  >
    <div 
      :class="[
        'draggable-modal relative rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden',
        isDark ? 'bg-gray-800' : 'bg-white',
        isDragging && draggedModal === 'categoryQuestions' ? 'dragging' : ''
      ]"
      data-modal="categoryQuestions"
      @click.stop
      :style="{ transform: `translate(${modalPosition.x}px, ${modalPosition.y}px)` }"
    >
      <div 
        :class="[
          'bg-gradient-to-r from-orange-600 to-orange-500 p-6 select-none flex items-center justify-between',
          isDragging && draggedModal === 'categoryQuestions' ? 'cursor-grabbing' : 'cursor-move'
        ]"
        @mousedown="emit('startDrag', $event, 'categoryQuestions')"
      >
        <div>
          <h3 class="text-xl font-bold text-white flex items-center gap-2">
            Questions in {{ category?.name }}
          </h3>
          <p class="text-purple-100 text-sm mt-1">
            {{ categoryQuestions.length }} question{{ categoryQuestions.length !== 1 ? 's' : '' }} found
          </p>
        </div>
        <button
          @click="emit('resetPosition', 'categoryQuestions')"
          class="text-purple-200 hover:text-white p-1 rounded transition-colors"
          title="Reset position"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
      
      <div class="p-6 max-h-[calc(90vh-120px)] overflow-y-auto">
        <div v-if="categoryQuestions.length === 0" :class="['text-center py-12', isDark ? 'text-gray-400' : 'text-slate-500']">
          <svg class="mx-auto h-12 w-12 mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="text-lg font-medium">No questions in this category</p>
          <p class="text-sm mt-1">Add questions to get started</p>
        </div>
        
        <div v-else class="space-y-3">
          <div
            v-for="question in categoryQuestions"
            :key="question.id"
            :class="[
              'p-4 rounded-lg border transition-all',
              isDark ? 'bg-gray-700 border-gray-600 hover:border-purple-500' : 'bg-white border-slate-200 hover:border-purple-300 hover:shadow-md'
            ]"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1">
                <div class="flex items-start gap-3">
                  <span :class="[
                    'px-2 py-1 text-xs font-semibold rounded-full shrink-0',
                    isDark ? 'bg-purple-900/30 text-purple-300' : 'bg-purple-100 text-purple-700'
                  ]">
                    {{ getQuestionTypeLabel(question.question_type) }}
                  </span>
                  <div class="flex-1">
                    <p :class="['font-medium', isDark ? 'text-white' : 'text-slate-900']">
                      {{ question.question_text }}
                    </p>
                    <div class="flex items-center gap-3 mt-2 text-xs">
                      <span :class="[
                        'px-2 py-0.5 rounded',
                        question.is_required 
                          ? isDark ? 'bg-red-900/30 text-red-300' : 'bg-red-100 text-red-700'
                          : isDark ? 'bg-gray-600 text-gray-300' : 'bg-slate-100 text-slate-600'
                      ]">
                        {{ question.is_required ? 'Required' : 'Optional' }}
                      </span>
                      <span :class="[
                        'px-2 py-0.5 rounded',
                        question.is_active 
                          ? isDark ? 'bg-green-900/30 text-green-300' : 'bg-green-100 text-green-700'
                          : isDark ? 'bg-gray-600 text-gray-300' : 'bg-slate-100 text-slate-600'
                      ]">
                        {{ question.is_active ? 'Active' : 'Inactive' }}
                      </span>
                      <span :class="['px-2 py-0.5 rounded', isDark ? 'bg-gray-600 text-gray-300' : 'bg-slate-100 text-slate-600']">
                        Order: {{ question.order }}
                      </span>
                    </div>
                    
                    <div v-if="question.options && question.options.length > 0" class="mt-3">
                      <p :class="['text-xs font-medium mb-1', isDark ? 'text-gray-400' : 'text-slate-600']">Options:</p>
                      <div class="flex flex-wrap gap-1">
                        <span 
                          v-for="(option, index) in question.options.slice(0, 3)" 
                          :key="index"
                          :class="[
                            'text-xs px-2 py-0.5 rounded',
                            isDark ? 'bg-gray-600 text-gray-300' : 'bg-slate-100 text-slate-700'
                          ]"
                        >
                          {{ option }}
                        </span>
                        <span 
                          v-if="question.options.length > 3"
                          :class="[
                            'text-xs px-2 py-0.5 rounded',
                            isDark ? 'bg-gray-600 text-gray-400' : 'bg-slate-100 text-slate-500'
                          ]"
                        >
                          +{{ question.options.length - 3 }} more
                        </span>
                      </div>
                    </div>

                    <div v-if="question.help_text" class="mt-2">
                      <p :class="['text-xs italic', isDark ? 'text-gray-400' : 'text-slate-500']">
                        Help: {{ question.help_text }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="flex gap-2">
                <button
                  @click="emit('editQuestion', question)"
                  :class="[
                    'p-2 rounded-lg transition-colors',
                    isDark ? 'bg-orange-900/30 text-orange-400 hover:bg-orange-900/50' : 'bg-orange-50 text-orange-600 hover:bg-orange-100'
                  ]"
                  title="Edit question"
                >
                  <Edit class="w-4 h-4" />
                </button>
                <button
                  @click="emit('deleteQuestion', question.id)"
                  :class="[
                    'p-2 rounded-lg transition-colors',
                    isDark ? 'bg-red-900/30 text-red-400 hover:bg-red-900/50' : 'bg-red-50 text-red-600 hover:bg-red-100'
                  ]"
                  title="Delete question"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div :class="['flex justify-end pt-6 mt-6 border-t', isDark ? 'border-gray-700' : 'border-slate-200']">
          <button
            type="button"
            @click="emit('close')"
            :class="[
              'px-6 py-3 text-sm font-medium rounded-lg transition-colors',
              isDark ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' : 'text-slate-700 bg-slate-100 hover:bg-slate-200'
            ]"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
