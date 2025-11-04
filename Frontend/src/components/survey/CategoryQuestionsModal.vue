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
        class="fixed bg-white rounded-xl shadow-2xl border border-slate-200 z-50 w-full max-w-4xl cursor-move transform transition-transform duration-200"
      >
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-gradient-to-r from-slate-50 to-slate-100 rounded-t-xl cursor-default" @mousedown.stop>
          <div>
            <h3 class="text-lg font-semibold text-slate-800">{{ category?.name || 'Category' }} Questions</h3>
            <p class="text-sm text-slate-500 mt-1">{{ categoryQuestions.length }} question(s)</p>
          </div>
          <button
            @click="$emit('close')"
            class="p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-200 rounded-lg transition-all duration-200 cursor-pointer"
          >
            <X class="w-5 h-5" />
          </button>
        </div>

        <!-- Content -->
        <div class="px-6 py-6 max-h-[60vh] overflow-y-auto">
          <div v-if="categoryQuestions.length > 0" class="overflow-x-auto">
            <table class="min-w-full divide-y divide-slate-200">
              <thead class="bg-gradient-to-r from-slate-50 to-slate-100">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Question</th>
                  <th class="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Type</th>
                  <th class="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Required</th>
                  <th class="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Status</th>
                  <th class="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Responses</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-slate-100">
                <tr v-for="question in categoryQuestions" :key="question.id" class="hover:bg-slate-50 transition-colors duration-150">
                  <td class="px-6 py-4">
                    <div class="text-sm font-medium text-slate-800 max-w-xs">
                      {{ question.question_text.length > 50 ? question.question_text.substring(0, 50) + '...' : question.question_text }}
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                      {{ getQuestionTypeLabel(question.question_type) }}
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <span :class="[
                      'inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium',
                      question.is_required
                        ? 'bg-red-100 text-red-800'
                        : 'bg-slate-100 text-slate-600'
                    ]">
                      <div :class="[
                        'w-2 h-2 rounded-full',
                        question.is_required ? 'bg-red-500' : 'bg-slate-400'
                      ]"></div>
                      {{ question.is_required ? 'Yes' : 'No' }}
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <span :class="[
                      'inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium',
                      question.is_active
                        ? 'bg-emerald-100 text-emerald-800'
                        : 'bg-red-100 text-red-800'
                    ]">
                      <div :class="[
                        'w-2 h-2 rounded-full',
                        question.is_active ? 'bg-emerald-500' : 'bg-red-500'
                      ]"></div>
                      {{ question.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <div class="flex items-center gap-2">
                      <BarChart3 class="w-4 h-4 text-slate-400" />
                      <span class="text-sm font-semibold text-slate-700">{{ question.response_count || 0 }}</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Empty State -->
          <div v-else class="text-center py-12">
            <ListChecks class="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 class="text-lg font-semibold text-slate-600 mb-2">No questions in this category</h3>
            <p class="text-slate-500">Add questions to this category to see them here</p>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex gap-3 px-6 py-4 border-t border-slate-200 bg-slate-50 rounded-b-xl cursor-default" @mousedown.stop>
          <button
            @click="$emit('close')"
            class="w-full px-4 py-2 bg-gradient-to-r from-orange-600 to-orange-500 text-white rounded-lg hover:from-orange-500 hover:to-orange-600 transition-all duration-200 font-medium cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { X, BarChart3, ListChecks } from 'lucide-vue-next'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  category: {
    type: Object,
    default: null
  },
  questions: {
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

defineEmits(['close', 'drag-start', 'reset-position'])

const categoryQuestions = computed(() => {
  if (!props.category) return []
  return props.questions.filter(q => q.category_id === props.category.id)
})

const getQuestionTypeLabel = (typeValue) => {
  return props.questionTypes.find(t => t.value === typeValue)?.label || typeValue
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
