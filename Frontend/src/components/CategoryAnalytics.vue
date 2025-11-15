<script setup>
import { ref, computed, onMounted } from 'vue'
import { Bar, Pie, Doughnut } from 'vue-chartjs'
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
import { Download, FileText, X, BarChart3, PieChart } from 'lucide-vue-next'
import surveyService from '@/services/surveyService'
import { useThemeStore } from '@/stores/theme'

// Register Chart.js components
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement)

const props = defineProps({
  category: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close'])

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isDarkMode)

const loading = ref(true)
const analytics = ref(null)
const exportingPDF = ref(false)
const exportingXLSX = ref(false)

// Load analytics data
onMounted(async () => {
  try {
    loading.value = true
    const response = await surveyService.getCategoryAnalytics(props.category.id)
    analytics.value = response.data
  } catch (error) {
    console.error('Error loading category analytics:', error)
  } finally {
    loading.value = false
  }
})

// Chart colors - vibrant mix
const chartColors = [
  '#f97316', // Orange
  '#3b82f6', // Blue
  '#10b981', // Green
  '#ef4444', // Red
  '#8b5cf6', // Purple
  '#f59e0b', // Amber
  '#ec4899', // Pink
  '#14b8a6', // Teal
  '#6366f1', // Indigo
  '#84cc16', // Lime
  '#f43f5e', // Rose
  '#06b6d4', // Cyan
  '#eab308', // Yellow
  '#a855f7', // Violet
  '#22c55e', // Green
  '#fb923c', // Orange Light
  '#60a5fa', // Blue Light
  '#34d399', // Green Light
  '#f87171', // Red Light
  '#a78bfa'  // Purple Light
]

// Get chart options
const getBarChartOptions = (title) => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    title: {
      display: true,
      text: title,
      color: isDark.value ? '#e5e7eb' : '#1f2937',
      font: { size: 14, weight: 'bold' }
    },
    tooltip: {
      backgroundColor: isDark.value ? '#1f2937' : '#ffffff',
      titleColor: isDark.value ? '#e5e7eb' : '#1f2937',
      bodyColor: isDark.value ? '#e5e7eb' : '#1f2937',
      borderColor: isDark.value ? '#374151' : '#e5e7eb',
      borderWidth: 1
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        color: isDark.value ? '#9ca3af' : '#6b7280'
      },
      grid: {
        color: isDark.value ? '#374151' : '#e5e7eb'
      }
    },
    x: {
      ticks: {
        color: isDark.value ? '#9ca3af' : '#6b7280'
      },
      grid: {
        color: isDark.value ? '#374151' : '#e5e7eb'
      }
    }
  }
})

const getPieChartOptions = (title) => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        color: isDark.value ? '#e5e7eb' : '#1f2937',
        padding: 15,
        font: { size: 12 }
      }
    },
    title: {
      display: true,
      text: title,
      color: isDark.value ? '#e5e7eb' : '#1f2937',
      font: { size: 14, weight: 'bold' }
    },
    tooltip: {
      backgroundColor: isDark.value ? '#1f2937' : '#ffffff',
      titleColor: isDark.value ? '#e5e7eb' : '#1f2937',
      bodyColor: isDark.value ? '#e5e7eb' : '#1f2937',
      borderColor: isDark.value ? '#374151' : '#e5e7eb',
      borderWidth: 1
    }
  }
})

// Prepare chart data for different question types
const getChartData = (question) => {
  if (!question.distribution) return null

  const labels = Object.keys(question.distribution)
  const data = Object.values(question.distribution)
  
  // Create array of colors based on number of data points
  const backgroundColors = labels.map((_, index) => chartColors[index % chartColors.length])
  
  return {
    labels,
    datasets: [{
      label: 'Responses',
      data,
      backgroundColor: backgroundColors,
      borderColor: isDark.value ? '#1f2937' : '#ffffff',
      borderWidth: 2
    }]
  }
}

// Export handlers
const exportPDF = async () => {
  try {
    exportingPDF.value = true
    const response = await surveyService.exportCategoryPDF(props.category.id)
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `survey_analytics_${props.category.name}_${Date.now()}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error exporting PDF:', error)
    alert('Failed to export PDF. Please try again.')
  } finally {
    exportingPDF.value = false
  }
}

const exportXLSX = async () => {
  try {
    exportingXLSX.value = true
    const response = await surveyService.exportResponses({
      format: 'xlsx',
      category_id: props.category.id
    })
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `survey_responses_${props.category.name}_${Date.now()}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error exporting XLSX:', error)
    alert('Failed to export Excel file. Please try again.')
  } finally {
    exportingXLSX.value = false
  }
}
</script>

<template>
  <div class="fixed inset-0 z-50 overflow-y-auto bg-black/50 backdrop-blur-sm bg-opacity-50 flex items-start justify-center p-4">
    <div :class="[
      'relative w-full max-w-6xl my-8 rounded-lg shadow-2xl',
      isDark ? 'bg-gray-800' : 'bg-white'
    ]">
      <!-- Header -->
      <div :class="[
        'sticky top-0 z-10 flex items-center justify-between p-6 border-b',
        isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
      ]">
        <div>
          <h2 :class="[
            'text-2xl font-bold',
            isDark ? 'text-white' : 'text-gray-900'
          ]">
            {{ category.name }} - Analytics
          </h2>
          <p :class="[
            'text-sm mt-1',
            isDark ? 'text-gray-400' : 'text-gray-600'
          ]" v-if="category.description">
            {{ category.description }}
          </p>
        </div>
        
        <div class="flex items-center gap-3">
          <!-- Export Buttons -->
          <button
            @click="exportPDF"
            :disabled="exportingPDF || loading"
            :class="[
              'flex items-center gap-2 px-4 py-2 rounded-lg transition-colors text-sm font-medium',
              exportingPDF || loading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-red-600 text-white hover:bg-red-700'
            ]"
          >
            <FileText class="w-4 h-4" />
            {{ exportingPDF ? 'Exporting...' : 'Export PDF' }}
          </button>
          
          <button
            @click="exportXLSX"
            :disabled="exportingXLSX || loading"
            :class="[
              'flex items-center gap-2 px-4 py-2 rounded-lg transition-colors text-sm font-medium',
              exportingXLSX || loading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-green-600 text-white hover:bg-green-700'
            ]"
          >
            <Download class="w-4 h-4" />
            {{ exportingXLSX ? 'Exporting...' : 'Export Excel' }}
          </button>
          
          <button
            @click="emit('close')"
            :class="[
              'p-2 rounded-lg transition-colors',
              isDark
                ? 'hover:bg-gray-700 text-gray-400 hover:text-white'
                : 'hover:bg-gray-100 text-gray-600 hover:text-gray-900'
            ]"
          >
            <X class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="p-6 max-h-[calc(100vh-200px)] overflow-y-auto">
        <!-- Loading -->
        <div v-if="loading" class="flex justify-center py-12">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>

        <!-- Analytics Content -->
        <div v-else-if="analytics" class="space-y-6">
          <!-- Summary Cards -->
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div :class="[
              'p-4 rounded-lg',
              isDark ? 'bg-gray-700' : 'bg-blue-50'
            ]">
              <p :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">Total Questions</p>
              <p :class="['text-2xl font-bold mt-1', isDark ? 'text-white' : 'text-gray-900']">
                {{ analytics.category.total_questions }}
              </p>
            </div>
            
            <div :class="[
              'p-4 rounded-lg',
              isDark ? 'bg-gray-700' : 'bg-green-50'
            ]">
              <p :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">Total Responses</p>
              <p :class="['text-2xl font-bold mt-1', isDark ? 'text-white' : 'text-gray-900']">
                {{ analytics.summary.total_responses }}
              </p>
            </div>
            
            <div :class="[
              'p-4 rounded-lg',
              isDark ? 'bg-gray-700' : 'bg-purple-50'
            ]">
              <p :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">Unique Respondents</p>
              <p :class="['text-2xl font-bold mt-1', isDark ? 'text-white' : 'text-gray-900']">
                {{ analytics.summary.unique_respondents }}
              </p>
            </div>
            
            <div :class="[
              'p-4 rounded-lg',
              isDark ? 'bg-gray-700' : 'bg-orange-50'
            ]">
              <p :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">Response Rate</p>
              <p :class="['text-2xl font-bold mt-1', isDark ? 'text-white' : 'text-gray-900']">
                {{ analytics.summary.response_rate }}%
              </p>
            </div>
          </div>

          <!-- Question Analytics -->
          <div class="space-y-6">
            <div
              v-for="question in analytics.questions"
              :key="question.question_id"
              :class="[
                'p-6 rounded-lg border',
                isDark ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-200'
              ]"
            >
              <!-- Question Header -->
              <div class="mb-4">
                <h3 :class="[
                  'text-lg font-semibold mb-2',
                  isDark ? 'text-white' : 'text-gray-900'
                ]">
                  {{ question.question_text }}
                </h3>
                <div class="flex items-center gap-4 text-sm">
                  <span :class="[
                    'px-2 py-1 rounded',
                    isDark ? 'bg-gray-600 text-gray-300' : 'bg-gray-100 text-gray-700'
                  ]">
                    {{ question.question_type }}
                  </span>
                  <span :class="isDark ? 'text-gray-400' : 'text-gray-600'">
                    {{ question.response_count }} responses ({{ question.response_rate }}%)
                  </span>
                </div>
              </div>

              <!-- Chart rendering based on question type -->
              <!-- Pie charts: radio, select, dropdown, yes_no -->
              <div v-if="question.distribution && ['radio', 'select', 'yes_no'].includes(question.question_type)" class="h-64">
                <Pie
                  :data="getChartData(question)"
                  :options="getPieChartOptions(question.question_text)"
                />
              </div>

              <!-- Bar chart (vertical/column): checkbox (multi-select) -->
              <div v-else-if="question.distribution && question.question_type === 'checkbox'" class="h-64">
                <Bar
                  :data="getChartData(question)"
                  :options="getBarChartOptions('Multi-Select Distribution')"
                />
              </div>
              
              <!-- Bar chart (vertical): rating scale -->
              <div v-else-if="question.distribution && question.question_type === 'rating'" class="h-64">
                <Bar
                  :data="getChartData(question)"
                  :options="getBarChartOptions(`Rating Distribution (Avg: ${question.average})`)"
                />
              </div>
              
              <!-- Bar chart (vertical/histogram): number -->
              <div v-else-if="question.distribution && question.question_type === 'number'" class="h-64">
                <Bar
                  :data="getChartData(question)"
                  :options="getBarChartOptions(`Number Distribution (Avg: ${question.average})`)"
                />
              </div>

              <!-- Number statistics (fallback if no distribution) -->
              <div v-else-if="question.question_type === 'number' && !question.distribution && question.average !== undefined" :class="[
                'p-4 rounded',
                isDark ? 'bg-gray-600' : 'bg-gray-50'
              ]">
                <div class="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">Average</p>
                    <p :class="['text-xl font-bold', isDark ? 'text-white' : 'text-gray-900']">
                      {{ question.average }}
                    </p>
                  </div>
                  <div>
                    <p :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">Min</p>
                    <p :class="['text-xl font-bold', isDark ? 'text-white' : 'text-gray-900']">
                      {{ question.min }}
                    </p>
                  </div>
                  <div>
                    <p :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">Max</p>
                    <p :class="['text-xl font-bold', isDark ? 'text-white' : 'text-gray-900']">
                      {{ question.max }}
                    </p>
                  </div>
                </div>
              </div>

              <!-- Text samples -->
              <div v-else-if="question.sample_responses && question.sample_responses.length > 0" class="space-y-2">
                <p :class="['text-sm font-medium mb-3', isDark ? 'text-gray-300' : 'text-gray-700']">
                  Sample Responses:
                </p>
                <div
                  v-for="(sample, idx) in question.sample_responses"
                  :key="idx"
                  :class="[
                    'p-3 rounded text-sm',
                    isDark ? 'bg-gray-600 text-gray-200' : 'bg-gray-50 text-gray-700'
                  ]"
                >
                  {{ sample.value }}
                </div>
              </div>

              <!-- No responses -->
              <div v-else :class="[
                'p-4 rounded text-center',
                isDark ? 'bg-gray-600 text-gray-400' : 'bg-gray-50 text-gray-500'
              ]">
                No responses yet
              </div>
            </div>
          </div>
        </div>

        <!-- No Data -->
        <div v-else :class="[
          'text-center py-12',
          isDark ? 'text-gray-400' : 'text-gray-500'
        ]">
          <BarChart3 class="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p>No analytics data available</p>
        </div>
      </div>
    </div>
  </div>
</template>
