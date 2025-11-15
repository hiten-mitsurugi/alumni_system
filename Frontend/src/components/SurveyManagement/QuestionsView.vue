<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h2 :class="['text-2xl font-bold', isDark ? 'text-white' : 'text-slate-800']">All Survey Questions</h2>
        <p :class="['mt-1', isDark ? 'text-gray-300' : 'text-slate-600']">Manage all survey questions across all categories</p>
      </div>
      <div class="flex gap-3">
        <button
          @click="$emit('add-question')"
          :class="[
            'group flex items-center gap-2 px-6 py-3 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg cursor-pointer transform hover:scale-105',
            isDark 
              ? 'bg-gray-700 hover:bg-gray-600 text-white'
              : 'bg-gradient-to-r from-orange-600 to-orange-500 text-white hover:from-orange-500 hover:to-orange-600'
          ]"
        >
          <Plus class="w-5 h-5 group-hover:rotate-90 transition-transform" />
          Add Question
        </button>
      </div>
    </div>

    <QuestionsTable
      :questions="paginatedQuestions"
      :question-types="questionTypes"
      :is-dark="isDark"
      @edit="$emit('edit', $event)"
      @delete="$emit('delete', $event)"
    />

    <!-- Empty State -->
    <div v-if="totalQuestions === 0" class="text-center py-12">
      <FileText :class="['w-16 h-16 mx-auto mb-4', isDark ? 'text-gray-600' : 'text-slate-300']" />
      <p :class="['text-lg font-medium', isDark ? 'text-gray-400' : 'text-slate-500']">No questions yet</p>
      <p :class="['mt-2', isDark ? 'text-gray-500' : 'text-slate-400']">Create your first question to get started</p>
    </div>

    <PaginationControls
      v-if="totalPages > 1"
      :current-page="currentPage"
      :total-pages="totalPages"
      :is-dark="isDark"
      @prev="$emit('prev-page')"
      @next="$emit('next-page')"
      @goto="$emit('goto-page', $event)"
    />
  </div>
</template>

<script setup>
import { Plus, FileText } from 'lucide-vue-next'
import QuestionsTable from './QuestionsTable.vue'
import PaginationControls from './PaginationControls.vue'

defineProps({
  paginatedQuestions: {
    type: Array,
    required: true
  },
  totalQuestions: {
    type: Number,
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
  isDark: {
    type: Boolean,
    default: false
  }
})

defineEmits(['add-question', 'edit', 'delete', 'prev-page', 'next-page', 'goto-page'])
</script>
