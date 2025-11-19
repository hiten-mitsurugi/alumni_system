<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">Survey Responses</h2>
        <p class="text-gray-600">View and analyze all responses for {{ form?.name }}</p>
      </div>
      <div class="flex gap-3">
        <button
          @click="refreshData"
          :disabled="loading"
          class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition disabled:opacity-50"
        >
          <RefreshCw :class="['w-4 h-4', loading && 'animate-spin']" />
          Refresh
        </button>
        <button
          @click="exportPDFReport"
          :disabled="!questionAnalytics.length"
          class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition disabled:opacity-50"
        >
          <Download class="w-4 h-4" />
          Export PDF Report
        </button>
        <button
          @click="exportAllResponses"
          :disabled="!responses.length"
          class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition disabled:opacity-50"
        >
          <Download class="w-4 h-4" />
          Export Excel
        </button>
      </div>
    </div>

    <!-- Summary Stats -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Total Responses -->
      <div class="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 p-6 rounded-xl">
        <div class="flex items-center justify-between mb-3">
          <h4 class="text-sm font-semibold text-blue-600">Total Responses</h4>
          <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <FileText class="w-4 h-4 text-white" />
          </div>
        </div>
        <p class="text-3xl font-bold text-blue-700">{{ stats.totalResponses }}</p>
        <p class="text-xs text-blue-600 mt-1">Across all sections</p>
      </div>

      <!-- Unique Respondents -->
      <div class="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 p-6 rounded-xl">
        <div class="flex items-center justify-between mb-3">
          <h4 class="text-sm font-semibold text-purple-600">Respondents</h4>
          <div class="w-8 h-8 rounded-lg bg-purple-600 flex items-center justify-center">
            <Users class="w-4 h-4 text-white" />
          </div>
        </div>
        <p class="text-3xl font-bold text-purple-700">{{ stats.uniqueRespondents }}</p>
        <p class="text-xs text-purple-600 mt-1">Unique users</p>
      </div>

      <!-- Completion Rate -->
      <div class="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 p-6 rounded-xl">
        <div class="flex items-center justify-between mb-3">
          <h4 class="text-sm font-semibold text-green-600">Completion Rate</h4>
          <div class="w-8 h-8 rounded-lg bg-green-600 flex items-center justify-center">
            <TrendingUp class="w-4 h-4 text-white" />
          </div>
        </div>
        <p class="text-3xl font-bold text-green-700">{{ stats.completionRate }}%</p>
        <p class="text-xs text-green-600 mt-1">Average progress</p>
      </div>

      <!-- Latest Response -->
      <div class="bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 p-6 rounded-xl">
        <div class="flex items-center justify-between mb-3">
          <h4 class="text-sm font-semibold text-orange-600">Latest Response</h4>
          <div class="w-8 h-8 rounded-lg bg-orange-600 flex items-center justify-center">
            <Clock class="w-4 h-4 text-white" />
          </div>
        </div>
        <p class="text-lg font-bold text-orange-700">{{ stats.latestResponse }}</p>
        <p class="text-xs text-orange-600 mt-1">Most recent activity</p>
      </div>
    </div>

    <!-- Question Analytics - Google Forms Style -->
    <div v-if="loading" class="bg-white rounded-lg shadow-md p-12 text-center">
      <RefreshCw class="w-8 h-8 text-gray-400 animate-spin mx-auto mb-4" />
      <p class="text-gray-500">Loading response analytics...</p>
    </div>

    <div v-else-if="questionAnalytics.length === 0" class="bg-white rounded-lg shadow-md p-12 text-center">
      <FileText class="w-16 h-16 mx-auto mb-4 text-gray-300" />
      <h3 class="text-xl font-semibold text-gray-700 mb-2">No Responses Yet</h3>
      <p class="text-gray-500">Response analytics will appear here once users submit the survey.</p>
    </div>

    <div v-else class="space-y-6">
      <!-- Section Tabs -->
      <div class="bg-white rounded-lg shadow-md p-4">
        <div class="flex gap-2 overflow-x-auto">
          <button
            v-for="section in form?.sections"
            :key="section.category.id"
            @click="selectedSectionId = section.category.id"
            :class="[
              'px-4 py-2 rounded-lg font-medium text-sm whitespace-nowrap transition',
              selectedSectionId === section.category.id
                ? 'bg-orange-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            ]"
          >
            {{ section.category.name }}
          </button>
        </div>
      </div>

      <!-- Question Cards with Charts -->
      <div class="space-y-6">
        <div
          v-for="qa in filteredQuestionAnalytics"
          :key="qa.question_id"
          class="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden"
        >
          <!-- Question Header -->
          <div class="bg-gradient-to-r from-gray-50 to-white p-6 border-b border-gray-200">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ qa.question_text }}</h3>
                <div class="flex items-center gap-3 text-sm text-gray-600">
                  <span class="px-2 py-1 bg-blue-100 text-blue-700 rounded font-medium">
                    {{ qa.question_type }}
                  </span>
                  <span>{{ qa.response_count }} responses</span>
                  <span v-if="qa.response_rate">{{ qa.response_rate }}% response rate</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Chart/Data Visualization -->
          <div class="p-6">
            <!-- Multiple Choice / Checkbox - BAR GRAPH -->
            <div v-if="qa.question_type === 'checkbox'">
              <div class="mb-6">
                <h4 class="text-sm font-semibold text-gray-700 mb-4">Response Distribution</h4>
                <div class="h-64">
                  <Bar
                    :data="getBarChartData(qa, 'blue')"
                    :options="barChartOptions"
                  />
                </div>
              </div>
              
              <!-- Response Table -->
              <div class="mt-6">
                <h4 class="text-sm font-semibold text-gray-700 mb-3">Response Summary</h4>
                <div class="overflow-x-auto">
                  <table class="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg">
                    <thead class="bg-gray-50">
                      <tr>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Option</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Responses</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Percentage</th>
                      </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                      <tr v-for="option in getAllOptions(qa)" :key="option" class="hover:bg-gray-50">
                        <td class="px-4 py-3 text-sm text-gray-900">{{ option }}</td>
                        <td class="px-4 py-3 text-sm text-gray-600">{{ getOptionCount(qa, option) }}</td>
                        <td class="px-4 py-3 text-sm text-gray-600">{{ getPercentage(getOptionCount(qa, option), qa.response_count) }}%</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <!-- Radio (Single Choice) - PIE CHART -->
            <div v-else-if="qa.question_type === 'radio'">
              <div class="mb-6">
                <h4 class="text-sm font-semibold text-gray-700 mb-4">Response Distribution</h4>
                <div class="h-80 flex justify-center">
                  <Pie
                    :data="getPieChartData(qa)"
                    :options="pieChartOptions"
                  />
                </div>
              </div>
              
              <!-- Response Table -->
              <div class="mt-6">
                <h4 class="text-sm font-semibold text-gray-700 mb-3">Response Summary</h4>
                <div class="overflow-x-auto">
                  <table class="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg">
                    <thead class="bg-gray-50">
                      <tr>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Option</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Responses</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Percentage</th>
                      </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                      <tr v-for="option in getAllOptions(qa)" :key="option" class="hover:bg-gray-50">
                        <td class="px-4 py-3 text-sm text-gray-900">{{ option }}</td>
                        <td class="px-4 py-3 text-sm text-gray-600">{{ getOptionCount(qa, option) }}</td>
                        <td class="px-4 py-3 text-sm text-gray-600">{{ getPercentage(getOptionCount(qa, option), qa.response_count) }}%</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <!-- Dropdown/Select - PIE CHART -->
            <div v-else-if="qa.question_type === 'select'">
              <div class="mb-6">
                <h4 class="text-sm font-semibold text-gray-700 mb-4">Response Distribution</h4>
                <div class="h-80 flex justify-center">
                  <Pie
                    :data="getPieChartData(qa)"
                    :options="pieChartOptions"
                  />
                </div>
              </div>
              
              <!-- Response Table -->
              <div class="mt-6">
                <h4 class="text-sm font-semibold text-gray-700 mb-3">Response Summary</h4>
                <div class="overflow-x-auto">
                  <table class="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg">
                    <thead class="bg-gray-50">
                      <tr>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Option</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Responses</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Percentage</th>
                      </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                      <tr v-for="option in getAllOptions(qa)" :key="option" class="hover:bg-gray-50">
                        <td class="px-4 py-3 text-sm text-gray-900">{{ option }}</td>
                        <td class="px-4 py-3 text-sm text-gray-600">{{ getOptionCount(qa, option) }}</td>
                        <td class="px-4 py-3 text-sm text-gray-600">{{ getPercentage(getOptionCount(qa, option), qa.response_count) }}%</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <!-- Yes/No Questions - PIE CHART -->
            <div v-else-if="qa.question_type === 'yes_no'">
              <div class="mb-6">
                <h4 class="text-sm font-semibold text-gray-700 mb-4">Response Distribution</h4>
                <div class="h-80 flex justify-center">
                  <Pie
                    :data="getYesNoPieChartData(qa)"
                    :options="pieChartOptions"
                  />
                </div>
              </div>
              
              <!-- Response Table -->
              <div class="mt-6">
                <h4 class="text-sm font-semibold text-gray-700 mb-3">Response Summary</h4>
                <div class="overflow-x-auto">
                  <table class="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg">
                    <thead class="bg-gray-50">
                      <tr>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Option</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Responses</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Percentage</th>
                      </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                      <tr class="hover:bg-gray-50">
                        <td class="px-4 py-3 text-sm text-gray-900">Yes</td>
                        <td class="px-4 py-3 text-sm text-gray-600">{{ getYesNoCount(qa, 'Yes') }}</td>
                        <td class="px-4 py-3 text-sm text-gray-600">{{ getPercentage(getYesNoCount(qa, 'Yes'), qa.response_count) }}%</td>
                      </tr>
                      <tr class="hover:bg-gray-50">
                        <td class="px-4 py-3 text-sm text-gray-900">No</td>
                        <td class="px-4 py-3 text-sm text-gray-600">{{ getYesNoCount(qa, 'No') }}</td>
                        <td class="px-4 py-3 text-sm text-gray-600">{{ getPercentage(getYesNoCount(qa, 'No'), qa.response_count) }}%</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <!-- Rating Questions - BAR GRAPH with Average -->
            <div v-else-if="qa.question_type === 'rating'">
              <div class="mb-6">
                <div class="text-center mb-6 bg-gradient-to-r from-orange-50 to-yellow-50 rounded-lg p-6 border-2 border-orange-200">
                  <div class="text-6xl font-bold text-orange-600 mb-2">{{ qa.average?.toFixed(1) || 'N/A' }}</div>
                  <div class="text-lg font-medium text-orange-700">Average Rating</div>
                  <div class="text-sm text-gray-600 mt-1">Based on {{ qa.response_count }} responses</div>
                </div>
              </div>
              
              <div class="mb-6">
                <h4 class="text-sm font-semibold text-gray-700 mb-4">Rating Distribution</h4>
                <div class="h-64">
                  <Bar
                    :data="getRatingBarChartData(qa)"
                    :options="barChartOptions"
                  />
                </div>
              </div>
              
              <!-- Response Table -->
              <div class="mt-6">
                <h4 class="text-sm font-semibold text-gray-700 mb-3">Response Summary</h4>
                <div class="overflow-x-auto">
                  <table class="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg">
                    <thead class="bg-gray-50">
                      <tr>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Rating</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Responses</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Percentage</th>
                      </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                      <tr v-for="rating in getRatingRange(qa)" :key="rating" class="hover:bg-gray-50">
                        <td class="px-4 py-3 text-sm text-gray-900">{{ rating }} {{ rating === 1 ? 'star' : 'stars' }}</td>
                        <td class="px-4 py-3 text-sm text-gray-600">{{ getRatingCount(qa, rating) }}</td>
                        <td class="px-4 py-3 text-sm text-gray-600">{{ getPercentage(getRatingCount(qa, rating), qa.response_count) }}%</td>
                      </tr>
                      <tr class="bg-orange-50 font-semibold">
                        <td class="px-4 py-3 text-sm text-orange-900">Average</td>
                        <td class="px-4 py-3 text-sm text-orange-900" colspan="2">{{ qa.average?.toFixed(2) || 'N/A' }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <!-- Number Questions - BAR GRAPH with Stats -->
            <div v-else-if="qa.question_type === 'number'">
              <div class="mb-6">
                <div class="grid grid-cols-3 gap-4 mb-6">
                  <div class="bg-gradient-to-br from-blue-50 to-blue-100 border-2 border-blue-200 rounded-lg p-4 text-center">
                    <div class="text-3xl font-bold text-blue-600">{{ qa.average?.toFixed(2) || 'N/A' }}</div>
                    <div class="text-sm text-blue-700 mt-1 font-medium">Average</div>
                  </div>
                  <div class="bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-200 rounded-lg p-4 text-center">
                    <div class="text-3xl font-bold text-green-600">{{ qa.min || 'N/A' }}</div>
                    <div class="text-sm text-green-700 mt-1 font-medium">Minimum</div>
                  </div>
                  <div class="bg-gradient-to-br from-purple-50 to-purple-100 border-2 border-purple-200 rounded-lg p-4 text-center">
                    <div class="text-3xl font-bold text-purple-600">{{ qa.max || 'N/A' }}</div>
                    <div class="text-sm text-purple-700 mt-1 font-medium">Maximum</div>
                  </div>
                </div>
              </div>
              
              <div v-if="qa.distribution" class="mb-6">
                <h4 class="text-sm font-semibold text-gray-700 mb-4">Value Distribution</h4>
                <div class="h-64">
                  <Bar
                    :data="getBarChartData(qa, 'teal')"
                    :options="barChartOptions"
                  />
                </div>
              </div>
              
              <!-- Response Table -->
              <div v-if="qa.distribution" class="mt-6">
                <h4 class="text-sm font-semibold text-gray-700 mb-3">Response Summary</h4>
                <div class="overflow-x-auto">
                  <table class="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg">
                    <thead class="bg-gray-50">
                      <tr>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Value</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Responses</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Percentage</th>
                      </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                      <tr v-for="(count, value) in qa.distribution" :key="value" class="hover:bg-gray-50">
                        <td class="px-4 py-3 text-sm text-gray-900">{{ value }}</td>
                        <td class="px-4 py-3 text-sm text-gray-600">{{ count }}</td>
                        <td class="px-4 py-3 text-sm text-gray-600">{{ getPercentage(count, qa.response_count) }}%</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <!-- Text/Textarea Questions - Response Count Only -->
            <div v-else-if="['text', 'textarea', 'email'].includes(qa.question_type)">
              <div class="bg-blue-50 border-2 border-blue-200 rounded-lg p-8 text-center">
                <FileText class="w-16 h-16 mx-auto mb-4 text-blue-500" />
                <div class="text-4xl font-bold text-blue-600 mb-2">{{ qa.response_count }}</div>
                <div class="text-sm text-blue-700 font-medium">Text Responses Received</div>
                <p class="text-xs text-gray-600 mt-2">Individual responses are protected for privacy</p>
              </div>
            </div>

            <!-- Year Questions - BAR GRAPH -->
            <div v-else-if="qa.question_type === 'year'">
              <div v-if="qa.distribution" class="mb-6">
                <h4 class="text-sm font-semibold text-gray-700 mb-4">Year Distribution</h4>
                <div class="h-64">
                  <Bar
                    :data="getYearBarChartData(qa)"
                    :options="barChartOptions"
                  />
                </div>
              </div>
              
              <!-- Response Table -->
              <div v-if="qa.distribution" class="mt-6">
                <h4 class="text-sm font-semibold text-gray-700 mb-3">Response Summary</h4>
                <div class="overflow-x-auto">
                  <table class="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg">
                    <thead class="bg-gray-50">
                      <tr>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Year</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Responses</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Percentage</th>
                      </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                      <tr v-for="(count, year) in sortedYearDistribution(qa)" :key="year" class="hover:bg-gray-50">
                        <td class="px-4 py-3 text-sm text-gray-900">{{ year }}</td>
                        <td class="px-4 py-3 text-sm text-gray-600">{{ count }}</td>
                        <td class="px-4 py-3 text-sm text-gray-600">{{ getPercentage(count, qa.response_count) }}%</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <!-- Date Questions - Timeline -->
            <div v-else-if="qa.question_type === 'date' && qa.responses">
              <div class="space-y-2">
                <div
                  v-for="(response, index) in qa.responses.slice(0, 10)"
                  :key="index"
                  class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
                >
                  <Clock class="w-4 h-4 text-gray-400" />
                  <span class="text-sm text-gray-700">{{ formatDate(response) }}</span>
                </div>
              </div>
            </div>

            <!-- Fallback for other types -->
            <div v-else class="text-center py-8 text-gray-400">
              <FileText class="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p class="text-sm">No visualization available for this question type</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import {
  FileText, Users, TrendingUp, Clock, Download, RefreshCw,
  Search
} from 'lucide-vue-next'
import { Bar, Pie } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement
} from 'chart.js'
import surveyService from '@/services/surveyService'

// Register Chart.js components
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement)

const props = defineProps({
  form: {
    type: Object,
    required: true
  }
})

// State
const responses = ref([])
const questionAnalytics = ref([])
const loading = ref(false)
const selectedSectionId = ref(null)

// Chart.js options
const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          return `Responses: ${context.parsed.y}`
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        stepSize: 1
      }
    }
  }
}

const pieChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right'
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          const label = context.label || ''
          const value = context.parsed || 0
          const total = context.dataset.data.reduce((a, b) => a + b, 0)
          const percentage = total > 0 ? Math.round((value / total) * 100) : 0
          return `${label}: ${value} (${percentage}%)`
        }
      }
    }
  }
}

// Computed - Stats
const stats = computed(() => {
  const uniqueUsers = new Set(responses.value.map(r => r.user?.id).filter(Boolean))
  const latest = responses.value.length > 0
    ? responses.value.sort((a, b) => new Date(b.submitted_at) - new Date(a.submitted_at))[0]
    : null

  return {
    totalResponses: responses.value.length,
    uniqueRespondents: uniqueUsers.size,
    completionRate: calculateCompletionRate(),
    latestResponse: latest ? formatRelativeTime(latest.submitted_at) : 'N/A'
  }
})

// Filter question analytics by selected section
const filteredQuestionAnalytics = computed(() => {
  if (!selectedSectionId.value) {
    return questionAnalytics.value
  }
  return questionAnalytics.value.filter(qa => qa.category_id === selectedSectionId.value)
})

// Methods
const loadResponses = async () => {
  loading.value = true
  try {
    // Load analytics data directly from backend
    const sectionIds = props.form.sections?.map(s => s.category.id) || []
    
    if (sectionIds.length === 0) {
      console.warn('No sections in form')
      questionAnalytics.value = []
      loading.value = false
      return
    }

    // Load analytics for each section
    const allAnalytics = []
    for (const sectionId of sectionIds) {
      try {
        const result = await surveyService.getCategoryAnalytics(sectionId)
        console.log('Category analytics result:', result.data)
        if (result.data && result.data.questions) {
          // Add category_id to each question for filtering
          const questionsWithCategory = result.data.questions.map(q => ({
            ...q,
            category_id: sectionId
          }))
          allAnalytics.push(...questionsWithCategory)
        }
      } catch (error) {
        console.error(`Failed to load analytics for section ${sectionId}:`, error)
      }
    }

    questionAnalytics.value = allAnalytics
    console.log('Total question analytics loaded:', allAnalytics.length)
    
    // Also load raw responses for stats
    const responsesResult = await surveyService.getResponses({})
    responses.value = responsesResult.data || []

    // Set default selected section
    if (!selectedSectionId.value && props.form.sections && props.form.sections.length > 0) {
      selectedSectionId.value = props.form.sections[0].category.id
    }
  } catch (error) {
    console.error('Failed to load responses:', error)
  } finally {
    loading.value = false
  }
}

const calculateCompletionRate = () => {
  if (!props.form?.sections || responses.value.length === 0) return 0

  const totalQuestions = props.form.sections.reduce((sum, s) => sum + (s.questions?.length || 0), 0)
  if (totalQuestions === 0) return 0

  const uniqueUsers = new Set(responses.value.map(r => r.user?.id || r.user).filter(Boolean))
  const avgResponsesPerUser = responses.value.length / uniqueUsers.size

  return Math.min(100, Math.round((avgResponsesPerUser / totalQuestions) * 100))
}

const refreshData = () => {
  loadResponses()
}

const exportAllResponses = async () => {
  try {
    // Extract category IDs from form sections dynamically
    const categoryIds = props.form.sections?.map(section => section.category?.id).filter(id => id !== undefined && id !== null) || []
    
    if (categoryIds.length === 0) {
      alert('No valid category IDs found. Please check the form configuration.')
      return
    }
    
    const result = await surveyService.exportResponses({
      format: 'xlsx',
      category_ids: categoryIds
    })
    
    const blob = new Blob([result.data], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${props.form.name}_responses_${new Date().toISOString().split('T')[0]}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Failed to export responses:', error)
    alert('Failed to export responses. Please try again.')
  }
}

const exportPDFReport = async () => {
  try {
    loading.value = true
    
    // Get category IDs from form sections
    const categoryIds = props.form.sections?.map(s => s.category.id) || []
    
    if (categoryIds.length === 0) {
      alert('No sections found in this form.')
      return
    }
    
    // Export entire form (all sections combined)
    const response = await surveyService.exportFormPDF(categoryIds)
    
    // Create blob from response
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    
    // Create download link
    const link = document.createElement('a')
    link.href = url
    
    const formName = props.form.title || 'Survey'
    const timestamp = new Date().toISOString().split('T')[0]
    
    link.download = `${formName}_Complete_Analytics_Report_${timestamp}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    // Show success message
    alert('Complete PDF report downloaded successfully!')
  } catch (error) {
    console.error('Failed to export PDF report:', error)
    alert('Failed to export PDF report. Please try again.')
  } finally {
    loading.value = false
  }
}

const getPercentage = (value, total) => {
  if (!total) return 0
  return Math.round((value / total) * 100)
}

// Chart.js Data Generation Functions
const getBarChartData = (qa, colorName = 'blue') => {
  const options = getAllOptions(qa)
  const data = options.map(option => getOptionCount(qa, option))
  
  const colors = {
    blue: 'rgba(59, 130, 246, 0.8)',
    teal: 'rgba(20, 184, 166, 0.8)',
    emerald: 'rgba(16, 185, 129, 0.8)',
    yellow: 'rgba(234, 179, 8, 0.8)'
  }
  
  return {
    labels: options,
    datasets: [{
      label: 'Responses',
      data: data,
      backgroundColor: colors[colorName] || colors.blue,
      borderColor: colors[colorName]?.replace('0.8', '1') || colors.blue.replace('0.8', '1'),
      borderWidth: 2
    }]
  }
}

const getPieChartData = (qa) => {
  const options = getAllOptions(qa)
  const data = options.map(option => getOptionCount(qa, option))
  
  // Generate distinct colors for pie chart
  const backgroundColors = [
    'rgba(147, 51, 234, 0.8)',   // purple
    'rgba(99, 102, 241, 0.8)',   // indigo
    'rgba(59, 130, 246, 0.8)',   // blue
    'rgba(14, 165, 233, 0.8)',   // sky
    'rgba(20, 184, 166, 0.8)',   // teal
    'rgba(34, 197, 94, 0.8)',    // green
    'rgba(234, 179, 8, 0.8)',    // yellow
    'rgba(249, 115, 22, 0.8)',   // orange
    'rgba(239, 68, 68, 0.8)',    // red
    'rgba(236, 72, 153, 0.8)',   // pink
  ]
  
  return {
    labels: options,
    datasets: [{
      data: data,
      backgroundColor: backgroundColors.slice(0, options.length),
      borderColor: backgroundColors.slice(0, options.length).map(c => c.replace('0.8', '1')),
      borderWidth: 2
    }]
  }
}

const getYesNoPieChartData = (qa) => {
  return {
    labels: ['Yes', 'No'],
    datasets: [{
      data: [getYesNoCount(qa, 'Yes'), getYesNoCount(qa, 'No')],
      backgroundColor: [
        'rgba(34, 197, 94, 0.8)',  // green
        'rgba(239, 68, 68, 0.8)'   // red
      ],
      borderColor: [
        'rgba(34, 197, 94, 1)',
        'rgba(239, 68, 68, 1)'
      ],
      borderWidth: 2
    }]
  }
}

const getRatingBarChartData = (qa) => {
  const ratings = getRatingRange(qa)
  const data = ratings.map(rating => getRatingCount(qa, rating))
  
  return {
    labels: ratings.map(r => `${r} ${r === 1 ? 'star' : 'stars'}`),
    datasets: [{
      label: 'Responses',
      data: data,
      backgroundColor: 'rgba(234, 179, 8, 0.8)',
      borderColor: 'rgba(234, 179, 8, 1)',
      borderWidth: 2
    }]
  }
}

const getYearBarChartData = (qa) => {
  const sorted = sortedYearDistribution(qa)
  const years = Object.keys(sorted)
  const data = Object.values(sorted)
  
  return {
    labels: years,
    datasets: [{
      label: 'Responses',
      data: data,
      backgroundColor: 'rgba(16, 185, 129, 0.8)',
      borderColor: 'rgba(16, 185, 129, 1)',
      borderWidth: 2
    }]
  }
}

// Get all options for a question (including those with 0 responses)
const getAllOptions = (qa) => {
  if (!qa.options) return Object.keys(qa.distribution || {})
  
  // Merge options from question definition with distribution to show all options
  const allOptions = [...qa.options]
  
  // Add any distribution keys not in options (edge case)
  if (qa.distribution) {
    Object.keys(qa.distribution).forEach(key => {
      if (!allOptions.includes(key)) {
        allOptions.push(key)
      }
    })
  }
  
  return allOptions
}

// Get count for a specific option (returns 0 if not in distribution)
const getOptionCount = (qa, option) => {
  if (!qa.distribution) return 0
  return qa.distribution[option] || 0
}

// Get count for Yes/No questions
const getYesNoCount = (qa, option) => {
  if (!qa.distribution) return 0
  return qa.distribution[option] || 0
}

// Get count for rating
const getRatingCount = (qa, rating) => {
  if (!qa.distribution) return 0
  return qa.distribution[rating.toString()] || 0
}

// Sort year distribution chronologically
const sortedYearDistribution = (qa) => {
  if (!qa.distribution) return {}
  
  const entries = Object.entries(qa.distribution)
  entries.sort((a, b) => {
    const yearA = parseInt(a[0])
    const yearB = parseInt(b[0])
    return yearB - yearA // Descending order (newest first)
  })
  
  return Object.fromEntries(entries)
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

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const formatRelativeTime = (dateString) => {
  if (!dateString) return 'N/A'
  
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  
  return formatDate(dateString)
}

// Watch for form changes to reload data
watch(() => props.form, (newForm) => {
  if (newForm?.id) {
    loadResponses()
  }
}, { immediate: false })

// Load data on mount
onMounted(() => {
  if (props.form?.id) {
    loadResponses()
  }
})
</script>
