<template>
  <div :class="[
    'rounded-xl border overflow-hidden shadow-sm',
    isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-slate-200'
  ]">
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-slate-200">
        <thead :class="[
          isDark ? 'bg-gray-700' : 'bg-gradient-to-r from-slate-50 to-slate-100'
        ]">
          <tr>
            <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', isDark ? 'text-gray-300' : 'text-slate-600']">
              Question
            </th>
            <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', isDark ? 'text-gray-300' : 'text-slate-600']">
              Category
            </th>
            <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', isDark ? 'text-gray-300' : 'text-slate-600']">
              Type
            </th>
            <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', isDark ? 'text-gray-300' : 'text-slate-600']">
              Required
            </th>
            <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', isDark ? 'text-gray-300' : 'text-slate-600']">
              Status
            </th>
            <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', isDark ? 'text-gray-300' : 'text-slate-600']">
              Responses
            </th>
            <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', isDark ? 'text-gray-300' : 'text-slate-600']">
              Conditional
            </th>
            <th :class="['px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider', isDark ? 'text-gray-300' : 'text-slate-600']">
              Actions
            </th>
          </tr>
        </thead>
        <tbody :class="[
          'divide-y', 
          isDark ? 'bg-gray-800 divide-gray-700' : 'bg-white divide-slate-100'
        ]">
          <tr v-for="question in questions" :key="question.id" :class="[
            'transition-colors duration-150',
            isDark ? 'hover:bg-gray-700' : 'hover:bg-slate-50'
          ]">
            <td class="px-6 py-4">
              <div :class="['text-sm font-medium max-w-xs', isDark ? 'text-white' : 'text-slate-800']">
                {{ question.question_text.length > 50 ? question.question_text.substring(0, 50) + '...' : question.question_text }}
              </div>
              <div v-if="question.help_text" :class="['text-sm mt-1 max-w-xs', isDark ? 'text-gray-400' : 'text-slate-500']">
                {{ question.help_text }}
              </div>
            </td>
            <td class="px-6 py-4">
              <span :class="[
                'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium',
                isDark ? 'bg-gray-700 text-gray-300' : 'bg-orange-100 text-orange-600'
              ]">
                {{ question.category?.name }}
              </span>
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
                {{ question.is_required ? 'Required' : 'Optional' }}
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
            <td class="px-6 py-4">
              <div v-if="question.depends_on_question" class="flex items-center gap-2">
                <svg class="w-4 h-4 text-orange-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
                <span class="text-xs text-orange-600 font-medium">
                  Conditional
                </span>
              </div>
              <div v-else class="flex items-center gap-2">
                <span class="text-xs text-slate-400">Always shown</span>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="flex gap-2">
                <button
                  @click="$emit('edit', question)"
                  class="p-2 text-slate-400 hover:text-orange-600 hover:bg-orange-50 rounded-lg transition-all duration-200 cursor-pointer"
                  title="Edit Question"
                >
                  <Edit class="w-4 h-4" />
                </button>
                <button
                  @click="$emit('delete', question.id)"
                  class="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-200 cursor-pointer"
                  title="Delete Question"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { BarChart3, Edit, Trash2 } from 'lucide-vue-next'

const props = defineProps({
  questions: {
    type: Array,
    required: true
  },
  questionTypes: {
    type: Array,
    default: () => []
  },
  isDark: {
    type: Boolean,
    default: false
  }
})

defineEmits(['edit', 'delete'])

const getQuestionTypeLabel = (type) => {
  const found = props.questionTypes.find(t => t.value === type)
  return found ? found.label : type
}
</script>
