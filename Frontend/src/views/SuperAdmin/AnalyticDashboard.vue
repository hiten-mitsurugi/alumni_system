<!-- eslint-disable vue/multi-word-component-names -->
<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { 
  BarChart3, Download, Filter, Calendar, Printer, FileSpreadsheet, FileText, RefreshCw,
  TrendingUp, Briefcase, Target, BookOpen, GraduationCap, Trophy, GitCompare, Users, ChevronDown
} from 'lucide-vue-next'
import AnalyticsOverview from '@/components/analytics/AnalyticsOverview.vue'
import EmployabilityAnalytics from '@/components/analytics/EmployabilityAnalytics.vue'
import SkillsRelevanceAnalytics from '@/components/analytics/SkillsRelevanceAnalytics.vue'
import CurriculumEffectivenessAnalytics from '@/components/analytics/CurriculumEffectivenessAnalytics.vue'
import FurtherStudiesAnalytics from '@/components/analytics/FurtherStudiesAnalytics.vue'
import CompetitivenessAnalytics from '@/components/analytics/CompetitivenessAnalytics.vue'
import ProgramComparisonAnalytics from '@/components/analytics/ProgramComparisonAnalytics.vue'
import DemographicsAnalytics from '@/components/analytics/DemographicsAnalytics.vue'
import AnalyticsFilters from '@/components/analytics/AnalyticsFilters.vue'
import { analyticsService } from '@/services/analyticsService'

const themeStore = useThemeStore()

// Current active report
const activeReport = ref('overview')

// Analytics data
const analyticsData = ref(null)
const isLoading = ref(false)
const lastUpdated = ref(null)

// Filters
const filters = ref({
  programs: [],
  graduationYears: [],
  employmentStatus: [],
  location: [],
  gender: [],
  civilStatus: [],
  incomeRange: [0, 200000],
  skillsRatingRange: [1, 5],
  dateRange: {
    start: null,
    end: null
  }
})

const appliedFilters = ref({})
const showFilters = ref(false)
const showReportDropdown = ref(false)

// Report definitions
const reports = [
  {
    id: 'overview',
    title: 'Analytics Overview',
    description: 'Executive summary and key performance indicators',
    icon: TrendingUp
  },
  {
    id: 'employability',
    title: 'Employability Analytics',
    description: 'Employment outcomes and job market performance',
    icon: Briefcase
  },
  {
    id: 'skills',
    title: 'Skills Relevance Analytics',
    description: 'Competency strengths and skills gap analysis',
    icon: Target
  },
  {
    id: 'curriculum',
    title: 'Curriculum Effectiveness Analytics',
    description: 'Academic program components evaluation',
    icon: BookOpen
  },
  {
    id: 'studies',
    title: 'Further Studies Analytics',
    description: 'Lifelong learning and academic advancement patterns',
    icon: GraduationCap
  },
  {
    id: 'competitiveness',
    title: 'Competitiveness Analytics',
    description: 'Graduate confidence and market readiness',
    icon: Trophy
  },
  {
    id: 'comparison',
    title: 'Program Comparison Analytics',
    description: 'Cross-program performance evaluation',
    icon: GitCompare
  },
  {
    id: 'demographics',
    title: 'Demographics Analytics',
    description: 'Population context and diversity metrics',
    icon: Users
  }
]

// Computed properties
const filteredRespondentCount = computed(() => {
  if (!analyticsData.value) return 0
  return analyticsData.value.overview?.totalRespondents || 0
})

const hasActiveFilters = computed(() => {
  return Object.keys(appliedFilters.value).length > 0
})

const currentReport = computed(() => {
  return reports.find(report => report.id === activeReport.value) || reports[0]
})

// Methods
const loadAnalyticsData = async () => {
  isLoading.value = true
  try {
    const data = await analyticsService.getAnalyticsData(appliedFilters.value)
    analyticsData.value = data
    lastUpdated.value = new Date()
  } catch (error) {
    console.error('Failed to load analytics data:', error)
  } finally {
    isLoading.value = false
  }
}

const applyFilters = (newFilters) => {
  appliedFilters.value = { ...newFilters }
  loadAnalyticsData()
}

const clearFilters = () => {
  appliedFilters.value = {}
  filters.value = {
    programs: [],
    graduationYears: [],
    employmentStatus: [],
    location: [],
    gender: [],
    civilStatus: [],
    incomeRange: [0, 200000],
    skillsRatingRange: [1, 5],
    dateRange: {
      start: null,
      end: null
    }
  }
  loadAnalyticsData()
}

const exportReport = async (format) => {
  try {
    await analyticsService.exportReport(activeReport.value, format, appliedFilters.value)
  } catch (error) {
    console.error('Failed to export report:', error)
  }
}

const printReport = () => {
  window.print()
}

const refreshData = () => {
  loadAnalyticsData()
}

const selectReport = (reportId) => {
  activeReport.value = reportId
  showReportDropdown.value = false
}

// Close dropdown when clicking outside
const closeDropdown = () => {
  showReportDropdown.value = false
}

// Lifecycle
onMounted(() => {
  loadAnalyticsData()
})

// Watch for theme changes
const isDark = computed(() => themeStore.isAdminDark?.() || false)
</script>

<template>
  <div :class="['min-h-screen transition-colors', isDark ? 'bg-gray-900 text-gray-100' : 'bg-gray-50 text-gray-900']" @click="closeDropdown">
    <!-- Header Section -->
    <div :class="['sticky top-0 z-30 border-b backdrop-blur-sm', isDark ? 'bg-gray-800/95 border-gray-700' : 'bg-white/95 border-gray-200']">
      <div class="px-6 py-4">
        <!-- Title and Stats Row -->
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-4">
          <div class="flex items-center gap-3">
            <div :class="['p-2 rounded-lg', isDark ? 'bg-blue-600' : 'bg-blue-100']">
              <BarChart3 :class="['w-6 h-6', isDark ? 'text-white' : 'text-blue-600']" />
            </div>
            <div>
              <h1 :class="['text-2xl lg:text-3xl font-bold', isDark ? 'text-white' : 'text-gray-900']">
                Analytics Dashboard
              </h1>
              <p :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
                CSU Graduate Tracer Study Analytics System
              </p>
            </div>
          </div>

          <!-- Quick Stats -->
          <div class="flex flex-wrap gap-4">
            <div :class="['px-4 py-2 rounded-lg text-center', isDark ? 'bg-gray-700' : 'bg-white shadow-sm']">
              <div :class="['text-xl font-bold', isDark ? 'text-green-400' : 'text-green-600']">
                {{ filteredRespondentCount.toLocaleString() }}
              </div>
              <div :class="['text-xs', isDark ? 'text-gray-400' : 'text-gray-500']">
                {{ hasActiveFilters ? 'Filtered' : 'Total' }} Respondents
              </div>
            </div>
            <div v-if="lastUpdated" :class="['px-4 py-2 rounded-lg text-center', isDark ? 'bg-gray-700' : 'bg-white shadow-sm']">
              <div :class="['text-sm font-medium', isDark ? 'text-gray-300' : 'text-gray-600']">
                Last Updated
              </div>
              <div :class="['text-xs', isDark ? 'text-gray-400' : 'text-gray-500']">
                {{ lastUpdated.toLocaleTimeString() }}
              </div>
            </div>
          </div>
        </div>

        <!-- Action Bar -->
        <div class="flex flex-col sm:flex-row gap-3 justify-between items-start sm:items-center">
          <!-- Report Selection and Filter Controls -->
          <div class="flex flex-wrap gap-2">
            <!-- Report Dropdown -->
            <div class="relative" @click.stop>
              <button
                @click="showReportDropdown = !showReportDropdown"
                :class="[
                  'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors min-w-[200px] justify-between',
                  isDark ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-blue-600 text-white hover:bg-blue-700'
                ]"
              >
                <div class="flex items-center gap-2">
                  <component :is="currentReport.icon" class="w-4 h-4" />
                  <span>{{ currentReport.title }}</span>
                </div>
                <ChevronDown :class="['w-4 h-4 transition-transform', showReportDropdown ? 'rotate-180' : '']" />
              </button>
              
              <!-- Dropdown Menu -->
              <div 
                v-if="showReportDropdown"
                :class="[
                  'absolute top-full left-0 mt-1 w-80 rounded-lg shadow-lg border z-20',
                  isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
                ]"
                @click.stop
              >
                <div class="p-2 max-h-96 overflow-y-auto">
                  <button
                    v-for="report in reports"
                    :key="report.id"
                    @click="selectReport(report.id)"
                    :class="[
                      'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors',
                      activeReport === report.id
                        ? isDark ? 'bg-blue-600 text-white' : 'bg-blue-50 text-blue-700'
                        : isDark ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-100'
                    ]"
                  >
                    <component :is="report.icon" class="w-4 h-4 flex-shrink-0" />
                    <div class="min-w-0 flex-1">
                      <div class="text-sm font-medium">{{ report.title }}</div>
                      <div :class="['text-xs', activeReport === report.id ? 'opacity-75' : isDark ? 'text-gray-400' : 'text-gray-500']">
                        {{ report.description }}
                      </div>
                    </div>
                  </button>
                </div>
              </div>
            </div>

            <button
              @click="showFilters = !showFilters"
              :class="[
                'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                showFilters
                  ? isDark ? 'bg-blue-600 text-white' : 'bg-blue-100 text-blue-700'
                  : isDark ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' : 'bg-white text-gray-700 hover:bg-gray-50 border'
              ]"
            >
              <Filter class="w-4 h-4" />
              Filters
              <span v-if="hasActiveFilters" :class="['px-1.5 py-0.5 rounded text-xs', isDark ? 'bg-blue-500' : 'bg-blue-600 text-white']">
                {{ Object.keys(appliedFilters).length }}
              </span>
            </button>

            <button
              v-if="hasActiveFilters"
              @click="clearFilters"
              :class="['px-3 py-2 rounded-lg text-sm font-medium transition-colors', isDark ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' : 'bg-white text-gray-700 hover:bg-gray-50 border']"
            >
              Clear Filters
            </button>

            <button
              @click="refreshData"
              :class="['flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors', isDark ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' : 'bg-white text-gray-700 hover:bg-gray-50 border']"
              :disabled="isLoading"
            >
              <RefreshCw :class="['w-4 h-4', isLoading ? 'animate-spin' : '']" />
              Refresh
            </button>
          </div>

          <!-- Export Controls -->
          <div class="flex flex-wrap gap-2">
            <div class="relative group">
              <button
                :class="['flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors', isDark ? 'bg-green-600 text-white hover:bg-green-700' : 'bg-green-100 text-green-700 hover:bg-green-200']"
              >
                <Download class="w-4 h-4" />
                Export
              </button>
              <div :class="['absolute right-0 top-full mt-1 w-48 rounded-lg shadow-lg border opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-10', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
                <div class="p-2">
                  <button
                    @click="exportReport('pdf')"
                    :class="['w-full flex items-center gap-2 px-3 py-2 rounded text-sm hover:bg-opacity-10', isDark ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-100']"
                  >
                    <FileText class="w-4 h-4" />
                    Export as PDF
                  </button>
                  <button
                    @click="exportReport('xlsx')"
                    :class="['w-full flex items-center gap-2 px-3 py-2 rounded text-sm hover:bg-opacity-10', isDark ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-100']"
                  >
                    <FileSpreadsheet class="w-4 h-4" />
                    Export as Excel
                  </button>
                  <button
                    @click="exportReport('csv')"
                    :class="['w-full flex items-center gap-2 px-3 py-2 rounded text-sm hover:bg-opacity-10', isDark ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-100']"
                  >
                    <FileSpreadsheet class="w-4 h-4" />
                    Export as CSV
                  </button>
                </div>
              </div>
            </div>

            <button
              @click="printReport"
              :class="['flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors', isDark ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' : 'bg-white text-gray-700 hover:bg-gray-50 border']"
            >
              <Printer class="w-4 h-4" />
              Print
            </button>
          </div>
        </div>
      </div>

      <!-- Filters Panel -->
      <AnalyticsFilters
        v-if="showFilters"
        :filters="filters"
        :applied-filters="appliedFilters"
        @apply="applyFilters"
        @clear="clearFilters"
        :class="['border-t', isDark ? 'border-gray-700' : 'border-gray-200']"
      />
    </div>

    <!-- Content Area -->
    <div class="flex-1">
      <!-- Main Report Area -->
      <div class="p-6">
        <!-- Loading State -->
        <div v-if="isLoading" class="flex items-center justify-center py-12">
          <div class="flex items-center gap-3">
            <RefreshCw class="w-6 h-6 animate-spin text-blue-600" />
            <span :class="['text-lg', isDark ? 'text-gray-300' : 'text-gray-600']">
              Loading analytics data...
            </span>
          </div>
        </div>

        <!-- Report Components -->
        <div v-else-if="analyticsData">
          <AnalyticsOverview
            v-if="activeReport === 'overview'"
            :data="analyticsData"
            :applied-filters="appliedFilters"
          />
          <EmployabilityAnalytics
            v-else-if="activeReport === 'employability'"
            :data="analyticsData"
            :applied-filters="appliedFilters"
          />
          <SkillsRelevanceAnalytics
            v-else-if="activeReport === 'skills'"
            :data="analyticsData"
            :applied-filters="appliedFilters"
          />
          <CurriculumEffectivenessAnalytics
            v-else-if="activeReport === 'curriculum'"
            :data="analyticsData"
            :applied-filters="appliedFilters"
          />
          <FurtherStudiesAnalytics
            v-else-if="activeReport === 'studies'"
            :data="analyticsData"
            :applied-filters="appliedFilters"
          />
          <CompetitivenessAnalytics
            v-else-if="activeReport === 'competitiveness'"
            :data="analyticsData"
            :applied-filters="appliedFilters"
          />
          <ProgramComparisonAnalytics
            v-else-if="activeReport === 'comparison'"
            :data="analyticsData"
            :applied-filters="appliedFilters"
          />
          <DemographicsAnalytics
            v-else-if="activeReport === 'demographics'"
            :data="analyticsData"
            :applied-filters="appliedFilters"
          />
        </div>

        <!-- Error State -->
        <div v-else class="flex items-center justify-center py-12">
          <div class="text-center">
            <div :class="['w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center', isDark ? 'bg-gray-700' : 'bg-gray-100']">
              <BarChart3 :class="['w-8 h-8', isDark ? 'text-gray-500' : 'text-gray-400']" />
            </div>
            <h3 :class="['text-lg font-medium mb-2', isDark ? 'text-gray-300' : 'text-gray-900']">
              No Analytics Data Available
            </h3>
            <p :class="['text-sm mb-4', isDark ? 'text-gray-400' : 'text-gray-600']">
              Unable to load analytics data. Please try refreshing the page.
            </p>
            <button
              @click="loadAnalyticsData"
              :class="['px-4 py-2 rounded-lg text-sm font-medium transition-colors', isDark ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-blue-100 text-blue-700 hover:bg-blue-200']"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@media print {
  .no-print {
    display: none !important;
  }
}
</style>
