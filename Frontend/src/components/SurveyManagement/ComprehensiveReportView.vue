<template>
  <div class="space-y-6">
    <!-- Header with Filters -->
    <div class="flex justify-between items-start">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">Comprehensive Report</h2>
        <p class="text-gray-600">Filtered analytics and insights for {{ form?.name }}</p>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div class="flex items-center gap-4 mb-4">
        <Filter class="w-5 h-5 text-orange-600" />
        <h3 class="text-lg font-semibold text-gray-900">Filters</h3>
        <button
          v-if="hasActiveFilters"
          @click="clearFilters"
          class="ml-auto text-sm text-orange-600 hover:text-orange-700 font-medium"
        >
          Clear All Filters
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Program Filter -->
        <div class="relative">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Filter by Program
          </label>
          <div class="relative">
            <button
              @click="toggleProgramDropdown"
              type="button"
              class="w-full px-4 py-2 text-left border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 bg-white flex items-center justify-between"
            >
              <span class="text-gray-700">
                {{ filters.selectedPrograms.length > 0 ? `${filters.selectedPrograms.length} selected` : 'Select programs' }}
              </span>
              <ChevronDown class="w-4 h-4 text-gray-500" />
            </button>
            
            <div
              v-if="showProgramDropdown"
              class="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-auto"
            >
              <label
                v-for="program in availablePrograms"
                :key="program.value"
                class="flex items-center px-4 py-2 hover:bg-orange-50 cursor-pointer"
              >
                <input
                  type="checkbox"
                  :value="program.value"
                  v-model="filters.selectedPrograms"
                  class="w-4 h-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
                />
                <span class="ml-3 text-sm text-gray-700">{{ program.label }}</span>
              </label>
            </div>
          </div>
          <p class="text-xs text-gray-500 mt-1">BSCS, BSIS, BSIT</p>
        </div>

        <!-- Graduation Year Filter -->
        <div class="relative">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Filter by Graduation Year
          </label>
          <div class="relative">
            <button
              @click="toggleYearDropdown"
              type="button"
              class="w-full px-4 py-2 text-left border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 bg-white flex items-center justify-between"
            >
              <span class="text-gray-700">
                {{ filters.selectedYears.length > 0 ? `${filters.selectedYears.length} selected` : 'Select years' }}
              </span>
              <ChevronDown class="w-4 h-4 text-gray-500" />
            </button>
            
            <div
              v-if="showYearDropdown"
              class="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-auto"
            >
              <label
                v-for="year in availableYears"
                :key="year.value"
                class="flex items-center px-4 py-2 hover:bg-orange-50 cursor-pointer"
              >
                <input
                  type="checkbox"
                  :value="year.value"
                  v-model="filters.selectedYears"
                  class="w-4 h-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
                />
                <span class="ml-3 text-sm text-gray-700">{{ year.label }} ({{ year.count }} alumni)</span>
              </label>
            </div>
          </div>
          <p class="text-xs text-gray-500 mt-1">Select one or more years</p>
        </div>
      </div>

      <div class="mt-4 flex items-center justify-between">
        <div class="flex items-center gap-2 text-sm text-gray-600">
          <span v-if="filters.selectedPrograms.length > 0">
            {{ filters.selectedPrograms.length }} program(s) selected
          </span>
          <span v-if="filters.selectedYears.length > 0">
            · {{ filters.selectedYears.length }} year(s) selected
          </span>
          <span v-if="!hasActiveFilters" class="text-gray-400">
            No filters applied - showing all responses
          </span>
        </div>
        <button
          @click="applyFilters"
          :disabled="loading"
          class="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition disabled:opacity-50"
        >
          {{ loading ? 'Loading...' : 'Apply Filters' }}
        </button>
      </div>
    </div>

    <!-- Export Actions -->
    <div class="flex gap-3 justify-end">
      <button
        @click="exportFilteredPDF"
        :disabled="!questionAnalytics.length || loading"
        class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-orange-600 rounded-lg hover:bg-orange-700 transition disabled:opacity-50"
      >
        <Download class="w-4 h-4" />
        Export Filtered PDF Report
      </button>
      <button
        @click="exportFilteredExcel"
        :disabled="!responses.length || loading"
        class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition disabled:opacity-50"
      >
        <Download class="w-4 h-4" />
        Export Filtered Excel
      </button>
    </div>

    <!-- Question Analytics (Same as ResponsesView but filtered) -->
    <div v-if="loading" class="bg-white rounded-lg shadow-md p-12 text-center">
      <RefreshCw class="w-8 h-8 text-gray-400 animate-spin mx-auto mb-4" />
      <p class="text-gray-500">Loading filtered analytics...</p>
    </div>

    <div v-else-if="questionAnalytics.length === 0" class="bg-white rounded-lg shadow-md p-12 text-center">
      <FileText class="w-16 h-16 mx-auto mb-4 text-gray-300" />
      <h3 class="text-xl font-semibold text-gray-700 mb-2">No Data Available</h3>
      <p class="text-gray-500">
        {{ hasActiveFilters 
          ? 'No responses match your current filters. Try adjusting your selection.' 
          : 'Response analytics will appear here once users submit the survey.' 
        }}
      </p>
    </div>

    <!-- Reuse ResponsesView component with filtered data -->
    <ResponsesView
      v-else
      :form="formWithFilteredData"
      :is-filtered="true"
      @refresh="applyFilters"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import {
  FileText, Users, TrendingUp, Clock, Download, RefreshCw, Filter, ChevronDown
} from 'lucide-vue-next'
import surveyService from '@/services/surveyService'
import api from '@/services/api'
import ResponsesView from './ResponsesView.vue'

const props = defineProps({
  form: {
    type: Object,
    required: true
  }
})

// State
const loading = ref(false)
const responses = ref([])
const questionAnalytics = ref([])
const selectedSectionId = ref(null)
const availablePrograms = ref([])
const availableYears = ref([])

// Dropdown visibility state
const showProgramDropdown = ref(false)
const showYearDropdown = ref(false)

const filters = ref({
  selectedPrograms: [],
  selectedYears: []
})

// Computed
const hasActiveFilters = computed(() => {
  return filters.value.selectedPrograms.length > 0 || 
         filters.value.selectedYears.length > 0
})

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

// Create a form object with filtered data for ResponsesView
const formWithFilteredData = computed(() => {
  return {
    ...props.form,
    _filteredAnalytics: questionAnalytics.value,
    _filteredResponses: responses.value,
    _isFiltered: hasActiveFilters.value
  }
})

// Methods
const loadFilterOptions = async () => {
  try {
    // Use standardized 3-program list (matching Alumni Directory)
    availablePrograms.value = [
      { value: 'BS in Computer Science', label: 'BS in Computer Science', count: 0 },
      { value: 'BS in Information Systems', label: 'BS in Information Systems', count: 0 },
      { value: 'BS in Information Technology', label: 'BS in Information Technology', count: 0 }
    ]
    
    // Fetch actual graduation years from backend
    const result = await api.get('/survey/admin/analytics/filter-options/')
    
    // Get program counts from backend
    if (result.data.programs && result.data.programs.length > 0) {
      const programCounts = {}
      result.data.programs.forEach(p => {
        programCounts[p.value] = p.count || 0
      })
      
      // Update counts for our standardized programs
      availablePrograms.value = availablePrograms.value.map(prog => ({
        ...prog,
        count: programCounts[prog.value] || 0
      }))
    }
    
    // Use actual graduation years from database
    availableYears.value = result.data.graduationYears || []
  } catch (error) {
    console.error('Failed to load filter options:', error)
    // Keep standardized programs even if API fails
    availableYears.value = []
  }
}

const applyFilters = async () => {
  loading.value = true
  try {
    const sectionIds = props.form.sections?.map(s => s.category.id) || []
    
    if (sectionIds.length === 0) {
      console.warn('No sections in form')
      questionAnalytics.value = []
      loading.value = false
      return
    }

    const filterParams = {
      programs: filters.value.selectedPrograms,
      graduation_years: filters.value.selectedYears
    }

    // Load analytics for each section with filters
    const allAnalytics = []
    for (const sectionId of sectionIds) {
      try {
        const result = await surveyService.getCategoryAnalytics(sectionId, filterParams)
        if (result.data && result.data.questions) {
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

    // Load raw responses for stats with filters
    const responseFilters = {
      category_ids: sectionIds.join(',')
    }
    
    if (filterParams.programs.length > 0) {
      responseFilters.programs = filterParams.programs.join(',')
    }
    if (filterParams.graduation_years.length > 0) {
      responseFilters.graduation_years = filterParams.graduation_years.join(',')
    }

    const responsesResult = await surveyService.getResponses(responseFilters)
    responses.value = responsesResult.data || []

    // Set default selected section
    if (!selectedSectionId.value && props.form.sections && props.form.sections.length > 0) {
      selectedSectionId.value = props.form.sections[0].category.id
    }
  } catch (error) {
    console.error('Failed to load filtered data:', error)
  } finally {
    loading.value = false
  }
}

const clearFilters = () => {
  filters.value.selectedPrograms = []
  filters.value.selectedYears = []
  applyFilters()
}

const toggleProgramDropdown = () => {
  showProgramDropdown.value = !showProgramDropdown.value
  if (showProgramDropdown.value) {
    showYearDropdown.value = false
  }
}

const toggleYearDropdown = () => {
  showYearDropdown.value = !showYearDropdown.value
  if (showYearDropdown.value) {
    showProgramDropdown.value = false
  }
}

const handleClickOutside = (event) => {
  const target = event.target
  const isDropdownClick = target.closest('.relative')
  if (!isDropdownClick) {
    showProgramDropdown.value = false
    showYearDropdown.value = false
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

const exportFilteredPDF = async () => {
  try {
    loading.value = true
    
    const categoryIds = props.form.sections?.map(s => s.category.id) || []
    
    if (categoryIds.length === 0) {
      alert('No sections found in this form.')
      return
    }
    
    const filterParams = {
      programs: filters.value.selectedPrograms,
      graduation_years: filters.value.selectedYears
    }
    
    const response = await surveyService.exportFormPDF(categoryIds, filterParams)
    
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    
    const link = document.createElement('a')
    link.href = url
    
    const formName = props.form.title || props.form.name || 'Survey'
    const timestamp = new Date().toISOString().split('T')[0]
    const filterSuffix = hasActiveFilters.value ? '_Filtered' : ''
    
    link.download = `${formName}_Comprehensive_Report${filterSuffix}_${timestamp}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    alert('Filtered PDF report downloaded successfully!')
  } catch (error) {
    console.error('Failed to export filtered PDF:', error)
    alert('Failed to export PDF report. Please try again.')
  } finally {
    loading.value = false
  }
}

const exportFilteredExcel = async () => {
  try {
    loading.value = true
    
    const categoryIds = props.form.sections?.map(section => section.category?.id).filter(id => id !== undefined && id !== null) || []
    
    if (categoryIds.length === 0) {
      alert('No valid category IDs found. Please check the form configuration.')
      return
    }
    
    const result = await surveyService.exportResponses({
      format: 'xlsx',
      category_ids: categoryIds,
      programs: filters.value.selectedPrograms,
      graduation_years: filters.value.selectedYears
    })
    
    const blob = new Blob([result.data], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    const formName = props.form.name || 'Survey'
    const timestamp = new Date().toISOString().split('T')[0]
    const filterSuffix = hasActiveFilters.value ? '_Filtered' : ''
    
    link.download = `${formName}_responses${filterSuffix}_${timestamp}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    alert('Filtered Excel export completed successfully!')
  } catch (error) {
    console.error('Failed to export filtered Excel:', error)
    alert('Failed to export responses. Please try again.')
  } finally {
    loading.value = false
  }
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
  
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

// Watch for form changes
watch(() => props.form, (newForm) => {
  if (newForm?.id) {
    applyFilters()
  }
}, { immediate: false })

// Load on mount
onMounted(async () => {
  await loadFilterOptions()
  if (props.form?.id) {
    await applyFilters()
  }
  // Add click outside listener
  document.addEventListener('click', handleClickOutside)
})

// Cleanup on unmount
onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
