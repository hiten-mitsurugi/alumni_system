<template>
  <teleport to="body">
    <div
      v-if="show"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      @click.self="$emit('close')"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="bg-purple-600 px-6 py-4 flex items-center justify-between">
          <div>
            <h3 class="text-xl font-bold text-white">Survey Analytics Report</h3>
            <p class="text-purple-100 text-sm mt-1" v-if="!loading && analytics.summary">
              {{ analytics.summary.total_responses }} responses • {{ analytics.summary.unique_respondents }} unique respondents
            </p>
          </div>
          <button
            @click="$emit('close')"
            class="text-purple-200 hover:text-white transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="flex-1 flex justify-center items-center">
          <div class="text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
            <p class="text-slate-600">Loading analytics...</p>
          </div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="flex-1 p-6">
          <div class="bg-red-50 border border-red-200 rounded-lg p-4">
            <div class="flex">
              <svg class="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
              </svg>
              <p class="text-red-800">{{ error }}</p>
            </div>
          </div>
        </div>

        <!-- Analytics Content -->
        <div v-else class="flex-1 overflow-y-auto p-6">
          <!-- Survey Summary -->
          <div v-if="analytics.summary" class="mb-8">
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
          <div v-if="analytics.questions && analytics.questions.length > 0" class="space-y-6">
            <h4 class="text-lg font-semibold text-slate-800 mb-4">Question-by-Question Analysis</h4>
            
            <div 
              v-for="qa in analytics.questions" 
              :key="qa.question_id"
              class="bg-white border border-slate-200 rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <!-- Question Header -->
              <div class="mb-4">
                <h5 class="text-base font-medium text-slate-800 mb-1">{{ qa.question_text }}</h5>
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

              <!-- Yes/No Questions -->
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
            <p class="text-slate-500 font-medium">No Responses Yet</p>
            <p class="text-sm text-slate-400 mt-1">Response analytics will appear here once users submit the survey.</p>
          </div>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { surveyService } from '@/services/surveyService'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  categoryId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['close'])

const loading = ref(false)
const error = ref(null)
const analytics = ref({})

const loadAnalytics = async () => {
  try {
    loading.value = true
    error.value = null
    
    // If categoryId provided, get category-specific analytics
    // Otherwise get overall analytics
    if (props.categoryId) {
      const response = await surveyService.getCategoryAnalytics(props.categoryId)
      analytics.value = response.data
    } else {
      // Get all categories and combine analytics
      const response = await surveyService.getAnalytics()
      analytics.value = response.data
    }
  } catch (err) {
    error.value = 'Failed to load analytics data. Please try again.'
    console.error('Error loading analytics:', err)
  } finally {
    loading.value = false
  }
}

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

// Watch for show prop changes to load data
watch(() => props.show, (newVal) => {
  if (newVal) {
    loadAnalytics()
  }
})

// Load on mount if already visible
onMounted(() => {
  if (props.show) {
    loadAnalytics()
  }
})
</script>

        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900">Survey Analytics</h3>
            <div class="flex items-center gap-3">
              <button
                @click="exportData"
                :disabled="loading"
                :class="[
                  'text-sm flex items-center gap-1 transition-colors',
                  isDark 
                    ? 'text-gray-400 hover:text-gray-200' 
                    : 'text-orange-600 hover:text-orange-800'
                ]"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                Export CSV
              </button>
              <button
                @click="$emit('close')"
                class="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="flex justify-center items-center h-64">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="p-6">
          <div class="bg-red-50 border border-red-200 rounded-lg p-4">
            <div class="flex">
              <svg class="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
              </svg>
              <p class="text-red-800">{{ error }}</p>
            </div>
          </div>
        </div>

        <!-- Analytics Content -->
        <div v-else class="p-6">
          <!-- Summary Cards -->
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div class="bg-blue-50 rounded-lg p-4">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                    </svg>
                  </div>
                </div>
                <div class="ml-3">
                  <p class="text-sm font-medium text-gray-500">Total Responses</p>
                  <p class="text-2xl font-semibold text-gray-900">{{ analytics.totalResponses || 0 }}</p>
                </div>
              </div>
            </div>

            <div class="bg-green-50 rounded-lg p-4">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                  </div>
                </div>
                <div class="ml-3">
                  <p class="text-sm font-medium text-gray-500">Completion Rate</p>
                  <p class="text-2xl font-semibold text-gray-900">{{ Math.round(analytics.completionRate || 0) }}%</p>
                </div>
              </div>
            </div>

            <div class="bg-yellow-50 rounded-lg p-4">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                    <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                  </div>
                </div>
                <div class="ml-3">
                  <p class="text-sm font-medium text-gray-500">Total Questions</p>
                  <p class="text-2xl font-semibold text-gray-900">{{ Object.keys(analytics.questionStats || {}).length }}</p>
                </div>
              </div>
            </div>

            <div class="bg-purple-50 rounded-lg p-4">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                    <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                    </svg>
                  </div>
                </div>
                <div class="ml-3">
                  <p class="text-sm font-medium text-gray-500">Avg Response Rate</p>
                  <p class="text-2xl font-semibold text-gray-900">{{ calculateAverageResponseRate() }}%</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Question Analytics -->
          <div v-if="analytics.questionStats" class="space-y-6">
            <h4 class="text-lg font-medium text-gray-900">Question-by-Question Analysis</h4>
            
            <div
              v-for="(stats, questionId) in analytics.questionStats"
              :key="questionId"
              class="bg-white border border-gray-200 rounded-lg p-6"
            >
              <!-- Question Header -->
              <div class="mb-4">
                <h5 class="text-md font-medium text-gray-900">{{ stats.question }}</h5>
                <div class="flex items-center gap-4 mt-2">
                  <span class="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    {{ formatQuestionType(stats.type) }}
                  </span>
                  <span class="text-sm text-gray-600">
                    {{ stats.responseCount }} responses ({{ Math.round(stats.responseRate) }}%)
                  </span>
                </div>
              </div>

              <!-- Rating Analytics -->
              <div v-if="stats.type === 'rating' && stats.distribution" class="space-y-3">
                <div class="flex items-center gap-4">
                  <span class="text-sm font-medium text-gray-700">Average:</span>
                  <span class="text-lg font-semibold text-blue-600">{{ stats.average?.toFixed(1) || 'N/A' }}</span>
                </div>
                <div class="space-y-2">
                  <div
                    v-for="(count, rating) in stats.distribution"
                    :key="rating"
                    class="flex items-center gap-3"
                  >
                    <span class="text-sm font-medium text-gray-600 w-8">{{ rating }}</span>
                    <div class="flex-1 bg-gray-200 rounded-full h-4 relative">
                      <div
                        class="bg-blue-600 h-4 rounded-full transition-all duration-300"
                        :style="{ width: `${(count / Math.max(...Object.values(stats.distribution))) * 100}%` }"
                      ></div>
                    </div>
                    <span class="text-sm text-gray-600 w-8">{{ count }}</span>
                  </div>
                </div>
              </div>

              <!-- Choice Analytics -->
              <div v-else-if="['radio', 'select'].includes(stats.type) && stats.distribution" class="space-y-2">
                <div
                  v-for="(count, option) in stats.distribution"
                  :key="option"
                  class="flex items-center gap-3"
                >
                  <span class="text-sm font-medium text-gray-600 flex-1 truncate">{{ option }}</span>
                  <div class="flex-1 bg-gray-200 rounded-full h-4 relative">
                    <div
                      class="bg-green-600 h-4 rounded-full transition-all duration-300"
                      :style="{ width: `${(count / Math.max(...Object.values(stats.distribution))) * 100}%` }"
                    ></div>
                  </div>
                  <span class="text-sm text-gray-600 w-12 text-right">{{ count }} ({{ Math.round((count / stats.responseCount) * 100) }}%)</span>
                </div>
              </div>

              <!-- Multi-Choice Analytics -->
              <div v-else-if="stats.type === 'checkbox' && stats.distribution" class="space-y-2">
                <p class="text-sm text-gray-600 mb-3">Multiple selections allowed:</p>
                <div
                  v-for="(count, option) in stats.distribution"
                  :key="option"
                  class="flex items-center gap-3"
                >
                  <span class="text-sm font-medium text-gray-600 flex-1 truncate">{{ option }}</span>
                  <div class="flex-1 bg-gray-200 rounded-full h-4 relative">
                    <div
                      class="bg-purple-600 h-4 rounded-full transition-all duration-300"
                      :style="{ width: `${(count / Math.max(...Object.values(stats.distribution))) * 100}%` }"
                    ></div>
                  </div>
                  <span class="text-sm text-gray-600 w-12 text-right">{{ count }}</span>
                </div>
              </div>

              <!-- Text/Number Analytics -->
              <div v-else-if="['text', 'textarea', 'number', 'email', 'phone', 'url'].includes(stats.type)" class="space-y-2">
                <p class="text-sm text-gray-600">Sample responses:</p>
                <div class="bg-gray-50 rounded-lg p-3 max-h-32 overflow-y-auto">
                  <div
                    v-for="(value, index) in stats.values.slice(0, 5)"
                    :key="index"
                    class="text-sm text-gray-700 py-1 border-b border-gray-200 last:border-b-0"
                  >
                    {{ value || 'No response' }}
                  </div>
                  <p v-if="stats.values.length > 5" class="text-xs text-gray-500 mt-2">
                    +{{ stats.values.length - 5 }} more responses
                  </p>
                </div>
              </div>

              <!-- Yes/No Analytics -->
              <div v-else-if="stats.type === 'yes_no' && stats.distribution" class="space-y-2">
                <div class="grid grid-cols-2 gap-4">
                  <div class="text-center p-4 bg-green-50 rounded-lg">
                    <p class="text-2xl font-bold text-green-600">{{ stats.distribution.true || 0 }}</p>
                    <p class="text-sm text-gray-600">Yes</p>
                  </div>
                  <div class="text-center p-4 bg-red-50 rounded-lg">
                    <p class="text-2xl font-bold text-red-600">{{ stats.distribution.false || 0 }}</p>
                    <p class="text-sm text-gray-600">No</p>
                  </div>
                </div>
              </div>

              <!-- No Responses -->
              <div v-else class="text-center py-4">
                <p class="text-gray-500">No responses yet</p>
              </div>
            </div>
          </div>

          <!-- No Data -->
          <div v-else class="text-center py-12">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">No survey responses yet</h3>
            <p class="mt-1 text-sm text-gray-500">Analytics will appear here once alumni start submitting survey responses.</p>
          </div>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { surveyService } from '@/services/surveyService'
import { useThemeStore } from '@/stores/theme'

export default {
  name: 'AnalyticsModal',
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close'],
  setup(props) {
    const themeStore = useThemeStore()
    const isDark = computed(() => themeStore.isAdminDark?.())
    
    const loading = ref(false)
    const error = ref(null)
    const analytics = ref({})

    const loadAnalytics = async () => {
      try {
        loading.value = true
        error.value = null
        const response = await surveyService.getAnalytics()
        analytics.value = response.data
      } catch (err) {
        error.value = 'Failed to load analytics data'
        console.error('Error loading analytics:', err)
      } finally {
        loading.value = false
      }
    }

    const exportData = async () => {
      try {
        const response = await surveyService.exportResponses('csv')
        
        // Create blob and download
        const blob = new Blob([response.data], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `survey_responses_${new Date().toISOString().split('T')[0]}.csv`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Error exporting data:', err)
      }
    }

    const calculateAverageResponseRate = () => {
      if (!analytics.value.questionStats) return 0
      
      const rates = Object.values(analytics.value.questionStats).map(stat => stat.responseRate)
      const average = rates.length > 0 ? rates.reduce((sum, rate) => sum + rate, 0) / rates.length : 0
      return Math.round(average)
    }

    const formatQuestionType = (type) => {
      return surveyService.formatQuestionType(type)
    }

    // Load analytics when modal opens
    onMounted(() => {
      if (props.show) {
        loadAnalytics()
      }
    })

    // Watch for show prop changes
    watch(
      () => props.show,
      (show) => {
        if (show) {
          loadAnalytics()
        }
      }
    )

    return {
      isDark,
      loading,
      error,
      analytics,
      exportData,
      calculateAverageResponseRate,
      formatQuestionType
    }
  }
}
</script>

<style scoped>
/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Smooth transitions for bars */
.transition-all {
  transition: all 0.3s ease-in-out;
}
</style>
