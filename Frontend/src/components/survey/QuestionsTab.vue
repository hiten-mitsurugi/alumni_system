<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold text-slate-800">All Survey Questions</h2>
        <p class="text-slate-600 mt-1">Manage all survey questions across all categories</p>
      </div>
      <button
        @click="$emit('add-question')"
        class="group flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-600 to-orange-500 text-white rounded-lg hover:from-orange-500 hover:to-orange-600 transition-all duration-200 shadow-md hover:shadow-lg cursor-pointer transform hover:scale-105"
      >
        <Plus class="w-5 h-5 group-hover:rotate-90 transition-transform" />
        Add Question
      </button>
    </div>

    <div class="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200">
          <thead class="bg-gradient-to-r from-slate-50 to-slate-100">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Question</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Category</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Type</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Required</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Status</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Responses</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Conditional</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-slate-100">
            <tr v-for="question in paginatedQuestions" :key="question.id" class="hover:bg-slate-50 transition-colors duration-150">
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-slate-800 max-w-xs">
                  {{ question.question_text.length > 50 ? question.question_text.substring(0, 50) + '...' : question.question_text }}
                </div>
                <div v-if="question.help_text" class="text-sm text-slate-500 mt-1 max-w-xs">
                  {{ question.help_text }}
                </div>
              </td>
              <td class="px-6 py-4">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-600">
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
                  <span class="text-xs text-orange-600 font-medium">Conditional</span>
                </div>
                <div v-else class="flex items-center gap-2">
                  <span class="text-xs text-slate-400">Always shown</span>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="flex gap-2">
                  <button
                    @click="$emit('edit-question', question)"
                    class="p-2 text-slate-400 hover:text-orange-600 hover:bg-orange-50 rounded-lg transition-all duration-200 cursor-pointer"
                    title="Edit Question"
                  >
                    <Edit class="w-4 h-4" />
                  </button>
                  <button
                    @click="$emit('delete-question', question.id)"
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

      <!-- Empty State -->
      <div v-if="paginatedQuestions.length === 0" class="text-center py-12">
        <ListChecks class="w-16 h-16 text-slate-300 mx-auto mb-4" />
        <h3 class="text-lg font-semibold text-slate-600 mb-2">No questions found</h3>
        <p class="text-slate-500 mb-4">No questions available</p>
        <button
          @click="$emit('add-question')"
          class="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-600 to-orange-500 text-white rounded-lg hover:from-orange-500 hover:to-orange-600 transition-all duration-200 cursor-pointer"
        >
          <Plus class="w-4 h-4" />
          Create First Question
        </button>
      </div>

      <!-- Questions Pagination -->
      <div v-if="paginatedQuestions.length > 0 && totalPages > 1" class="flex items-center justify-between mt-6 pt-6 border-t border-slate-200 px-6">
        <div class="text-sm text-slate-600">
          Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to
          {{ Math.min(currentPage * itemsPerPage, totalQuestions) }} of
          {{ totalQuestions }} questions
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="$emit('page-change', currentPage - 1)"
            :disabled="currentPage === 1"
            class="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:text-slate-400 disabled:hover:bg-transparent cursor-pointer"
          >
            <ChevronLeft class="w-5 h-5" />
          </button>

          <div class="flex gap-1">
            <button
              v-for="page in pageButtons"
              :key="`q-page-${page}`"
              @click="$emit('page-change', page)"
              :class="[
                'w-10 h-10 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer',
                page === currentPage
                  ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg'
                  : 'text-slate-600 hover:bg-indigo-50 hover:text-indigo-600'
              ]"
            >
              {{ page }}
            </button>
            <span
              v-for="(ellipsis, index) in pageEllipsis"
              :key="`q-ellipsis-${index}`"
              class="flex items-center justify-center w-10 h-10 text-slate-400"
            >
              ...
            </span>
          </div>

          <button
            @click="$emit('page-change', currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:text-slate-400 disabled:hover:bg-transparent cursor-pointer"
          >
            <ChevronRight class="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Plus, Edit, Trash2, BarChart3, ListChecks, ChevronLeft, ChevronRight } from 'lucide-vue-next'

const props = defineProps({
  paginatedQuestions: {
    type: Array,
    required: true
  },
  questionTypes: {
    type: Array,
    required: true
  },
  currentPage: {
    type: Number,
    required: true
  },
  totalPages: {
    type: Number,
    required: true
  },
  totalQuestions: {
    type: Number,
    required: true
  },
  itemsPerPage: {
    type: Number,
    default: 6
  },
  pageNumbers: {
    type: Array,
    required: true
  }
})

defineEmits(['add-question', 'edit-question', 'delete-question', 'page-change'])

const pageButtons = computed(() => {
  return props.pageNumbers.filter(page => page !== '...')
})

const pageEllipsis = computed(() => {
  return props.pageNumbers.filter(page => page === '...')
})

const getQuestionTypeLabel = (typeValue) => {
  return props.questionTypes.find(t => t.value === typeValue)?.label || typeValue
}
</script>
