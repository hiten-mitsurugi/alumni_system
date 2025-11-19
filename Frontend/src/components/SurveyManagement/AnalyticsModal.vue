<template>
  <div
    v-if="analytics"
    class="fixed inset-0 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4"
  >
    <div 
      :class="[
        'draggable-modal relative bg-white rounded-2xl shadow-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden flex flex-col',
        isDragging && draggedModal === 'analytics' ? 'dragging' : ''
      ]"
      data-modal="analytics"
      @click.stop
      :style="{ transform: `translate(${modalPosition.x}px, ${modalPosition.y}px)` }"
    >
      <div 
        :class="[
          'bg-gradient-to-r from-purple-600 to-pink-600 p-6 select-none flex items-center justify-between',
          isDragging && draggedModal === 'analytics' ? 'cursor-grabbing' : 'cursor-move'
        ]"
        @mousedown="$emit('startDrag', $event, 'analytics')"
      >
        <div>
          <h3 class="text-xl font-bold text-white flex items-center gap-2">
            <BarChart3 class="w-5 h-5 opacity-70" />
            Survey Analytics Report
          </h3>
          <p class="text-purple-100 text-sm mt-1">{{ analytics.total_responses }} responses • {{ analytics.total_users_responded }} unique respondents</p>
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="$emit('resetPosition', 'analytics')"
            class="text-purple-200 hover:text-white p-1 rounded transition-colors"
            title="Reset position"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
          </button>
          <button
            @click="$emit('close')"
            class="text-purple-200 hover:text-white p-1 rounded transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>
      
      <div class="flex-1 overflow-y-auto p-6">
        <!-- Who has responded? Section -->
        <div v-if="analytics.summary && analytics.summary.unique_respondents > 0" class="mb-8">
          <h4 class="text-lg font-semibold text-slate-800 mb-4">Survey Summary</h4>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="bg-blue-50 p-4 rounded-lg border border-blue-200">
              <p class="text-sm text-blue-600 font-medium">Total Responses</p>
              <p class="text-3xl font-bold text-blue-700">{{ analytics.summary.total_responses }}</p>
            </div>
            <div class="bg-green-50 p-4 rounded-lg border border-green-200">
              <p class="text-sm text-green-600 font-medium">Unique Respondents</p>
              <p class="text-3xl font-bold text-green-700">{{ analytics.summary.unique_respondents }}</p>
            </div>
            <div class="bg-purple-50 p-4 rounded-lg border border-purple-200">
              <p class="text-sm text-purple-600 font-medium">Response Rate</p>
              <p class="text-3xl font-bold text-purple-700">{{ analytics.summary.response_rate }}%</p>
            </div>
          </div>
        </div>

        <!-- Questions Analytics -->
        <div v-if="analytics.questions && analytics.questions.length > 0" class="space-y-8">
          <h4 class="text-lg font-semibold text-slate-800 mb-4">Question-by-Question Analysis</h4>
          
          <div 
            v-for="qa in analytics.questions" 
            :key="qa.question_id"
            class="bg-white border border-slate-200 rounded-lg p-6 hover:shadow-md transition-shadow"
          >
            <!-- Question Header -->
            <div class="mb-4">
              <h4 class="text-base font-medium text-slate-800 mb-1">{{ qa.question_text }}</h4>
              <p class="text-sm text-slate-500">{{ qa.response_count }} responses</p>
            </div>

            <!-- Chart/Data for choice-based questions -->
            <div v-if="isChoiceQuestion(qa.question_type) && qa.distribution">
              <!-- Horizontal Bar Chart -->
              <div class="space-y-3">
                <div 
                  v-for="(count, answer) in qa.distribution" 
                  :key="answer"
                  class="space-y-1"
                >
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-slate-700 truncate max-w-[70%]">{{ answer }}</span>
                    <span class="text-slate-500 font-medium">{{ count }} ({{ getPercentage(count, qa.response_count) }}%)</span>
                  </div>
                  <div class="w-full bg-slate-100 rounded-full h-6 overflow-hidden">
                    <div 
                      class="bg-purple-500 h-full rounded-full flex items-center justify-end pr-2 transition-all duration-500"
                      :style="{ width: getPercentage(count, qa.response_count) + '%' }"
                    >
                      <span class="text-xs text-white font-medium" v-if="getPercentage(count, qa.response_count) > 10">
                        {{ getPercentage(count, qa.response_count) }}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Data Table -->
              <div class="mt-4 bg-slate-50 rounded p-3">
                <p class="text-xs font-semibold text-slate-600 mb-2">Value | Count</p>
                <div class="space-y-1">
                  <div 
                    v-for="(count, answer) in qa.distribution" 
                    :key="answer"
                    class="text-sm text-slate-700 flex justify-between"
                  >
                    <span>{{ answer }}</span>
                    <span class="font-medium">{{ count }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Rating Scale Visualization -->
            <div v-else-if="qa.question_type === 'rating' && qa.distribution">
              <div class="space-y-3">
                <div 
                  v-for="rating in getRatingRange(qa)" 
                  :key="rating"
                  class="space-y-1"
                >
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-slate-700 font-medium">{{ rating }}</span>
                    <span class="text-slate-500">{{ qa.distribution[rating] || 0 }} ({{ getPercentage(qa.distribution[rating] || 0, qa.response_count) }}%)</span>
                  </div>
                  <div class="w-full bg-slate-100 rounded-full h-6 overflow-hidden">
                    <div 
                      class="bg-amber-500 h-full rounded-full flex items-center justify-end pr-2 transition-all duration-500"
                      :style="{ width: getPercentage(qa.distribution[rating] || 0, qa.response_count) + '%' }"
                    >
                      <span class="text-xs text-white font-medium" v-if="getPercentage(qa.distribution[rating] || 0, qa.response_count) > 10">
                        {{ getPercentage(qa.distribution[rating] || 0, qa.response_count) }}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Statistics -->
              <div class="mt-4 grid grid-cols-3 gap-3">
                <div class="bg-slate-50 rounded p-3 text-center">
                  <p class="text-xs text-slate-500">Average</p>
                  <p class="text-lg font-bold text-slate-700">{{ qa.average?.toFixed(2) || 'N/A' }}</p>
                </div>
                <div class="bg-slate-50 rounded p-3 text-center">
                  <p class="text-xs text-slate-500">Min</p>
                  <p class="text-lg font-bold text-slate-700">{{ qa.min_value || 'N/A' }}</p>
                </div>
                <div class="bg-slate-50 rounded p-3 text-center">
                  <p class="text-xs text-slate-500">Max</p>
                  <p class="text-lg font-bold text-slate-700">{{ qa.max_value || 'N/A' }}</p>
                </div>
              </div>

              <!-- Data Table -->
              <div class="mt-4 bg-slate-50 rounded p-3">
                <p class="text-xs font-semibold text-slate-600 mb-2">Value | Count</p>
                <div class="space-y-1">
                  <div 
                    v-for="rating in getRatingRange(qa)" 
                    :key="rating"
                    class="text-sm text-slate-700 flex justify-between"
                  >
                    <span>{{ rating }}</span>
                    <span class="font-medium">{{ qa.distribution[rating] || 0 }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Text/Textarea Questions - Show count only -->
            <div v-else-if="isTextQuestion(qa.question_type)">
              <div class="bg-slate-50 rounded-lg p-4 text-center">
                <p class="text-3xl font-bold text-purple-600">{{ qa.response_count }}</p>
                <p class="text-sm text-slate-600 mt-1">text responses submitted</p>
              </div>
            </div>

            <!-- Numeric Questions - Show statistics -->
            <div v-else-if="qa.question_type === 'number' && qa.response_count > 0">
              <div class="grid grid-cols-3 gap-4">
                <div class="bg-slate-50 rounded-lg p-4 text-center">
                  <p class="text-xs text-slate-500 mb-1">Average</p>
                  <p class="text-2xl font-bold text-slate-700">{{ qa.average?.toFixed(2) || 'N/A' }}</p>
                </div>
                <div class="bg-slate-50 rounded-lg p-4 text-center">
                  <p class="text-xs text-slate-500 mb-1">Minimum</p>
                  <p class="text-2xl font-bold text-slate-700">{{ qa.min || 'N/A' }}</p>
                </div>
                <div class="bg-slate-50 rounded-lg p-4 text-center">
                  <p class="text-xs text-slate-500 mb-1">Maximum</p>
                  <p class="text-2xl font-bold text-slate-700">{{ qa.max || 'N/A' }}</p>
                </div>
              </div>
            </div>

            <!-- Yes/No Questions - Pie chart style -->
            <div v-else-if="qa.question_type === 'yes_no' && qa.distribution">
              <div class="space-y-3">
                <div 
                  v-for="(count, answer) in qa.distribution" 
                  :key="answer"
                  class="space-y-1"
                >
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-slate-700 font-medium">{{ answer }}</span>
                    <span class="text-slate-500">{{ count }} ({{ getPercentage(count, qa.response_count) }}%)</span>
                  </div>
                  <div class="w-full bg-slate-100 rounded-full h-8 overflow-hidden">
                    <div 
                      :class="answer === 'Yes' ? 'bg-green-500' : 'bg-red-500'"
                      class="h-full rounded-full flex items-center justify-end pr-3 transition-all duration-500"
                      :style="{ width: getPercentage(count, qa.response_count) + '%' }"
                    >
                      <span class="text-sm text-white font-bold" v-if="getPercentage(count, qa.response_count) > 15">
                        {{ getPercentage(count, qa.response_count) }}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Default: Just show response count -->
            <div v-else>
              <div class="bg-slate-50 rounded-lg p-4 text-center">
                <p class="text-2xl font-bold text-purple-600">{{ qa.response_count }}</p>
                <p class="text-sm text-slate-600 mt-1">responses</p>
              </div>
            </div>
          </div>
        </div>

        <!-- No data message -->
        <div v-else class="text-center py-12">
          <div class="text-slate-400 mb-2">
            <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </div>
          <p class="text-slate-500 font-medium">No question analytics available</p>
          <p class="text-sm text-slate-400 mt-1">Responses will appear here once submitted</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { BarChart3 } from 'lucide-vue-next'

defineProps({
  analytics: {
    type: Object,
    default: null
  },
  isDragging: {
    type: Boolean,
    default: false
  },
  draggedModal: {
    type: String,
    default: null
  },
  modalPosition: {
    type: Object,
    default: () => ({ x: 0, y: 0 })
  }
})

defineEmits(['close', 'startDrag', 'resetPosition'])

// Helper methods
const isChoiceQuestion = (type) => {
  return ['radio', 'select', 'checkbox'].includes(type)
}

const isTextQuestion = (type) => {
  return ['text', 'textarea', 'email'].includes(type)
}

const getPercentage = (value, total) => {
  if (!total || total === 0) return 0
  return Math.round((value / total) * 100)
}

const getRatingRange = (qa) => {
  const min = qa.min_value || 1
  const max = qa.max_value || 5
  const range = []
  for (let i = max; i >= min; i--) {
    range.push(i)
  }
  return range
}
</script>

<style scoped>
.draggable-modal.dragging {
  cursor: grabbing;
  user-select: none;
}
</style>
