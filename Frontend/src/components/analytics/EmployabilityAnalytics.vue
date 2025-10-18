<script setup>
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { Briefcase, TrendingUp, MapPin, Building, DollarSign, Star } from 'lucide-vue-next'

const props = defineProps({
  data: {
    type: Object,
    required: true
  },
  appliedFilters: {
    type: Object,
    default: () => ({})
  }
})

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isAdminDark?.() || false)

const employabilityData = computed(() => props.data.employability || {})
const overallStats = computed(() => employabilityData.value.overallStats || {})
const programAnalysis = computed(() => employabilityData.value.programAnalysis || [])
const topPerformers = computed(() => employabilityData.value.topPerformers || [])
const incomeAnalysis = computed(() => employabilityData.value.incomeAnalysis || {})
const jobRelevance = computed(() => employabilityData.value.jobRelevance || {})
const employmentSectors = computed(() => employabilityData.value.employmentSectors || {})

const formatCurrency = (amount) => {
  return `₱${parseInt(amount).toLocaleString()}`
}

const getEmploymentStatusColor = (rate) => {
  if (rate >= 90) return isDark.value ? 'text-green-400' : 'text-green-600'
  if (rate >= 75) return isDark.value ? 'text-yellow-400' : 'text-yellow-600'
  return isDark.value ? 'text-red-400' : 'text-red-600'
}

const getRatingColor = (rating) => {
  if (rating >= 4.0) return isDark.value ? 'text-green-400' : 'text-green-600'
  if (rating >= 3.0) return isDark.value ? 'text-yellow-400' : 'text-yellow-600'
  return isDark.value ? 'text-red-400' : 'text-red-600'
}
</script>

<template>
  <div class="space-y-8">
    <!-- Page Header -->
    <div>
      <h1 :class="['text-3xl font-bold mb-2', isDark ? 'text-white' : 'text-gray-900']">
        Employability Analytics
      </h1>
      <p :class="['text-lg', isDark ? 'text-gray-400' : 'text-gray-600']">
        Comprehensive employment outcome analysis for institutional reporting and CHED compliance
      </p>
    </div>

    <!-- Overall Employment Dashboard -->
    <div :class="['rounded-xl border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <h2 :class="['text-xl font-bold mb-4', isDark ? 'text-white' : 'text-gray-900']">
        Overall Employment Dashboard
      </h2>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <!-- Employment Status Breakdown -->
        <div :class="['p-4 rounded-lg', isDark ? 'bg-gray-700' : 'bg-gray-50']">
          <h3 :class="['font-semibold mb-3', isDark ? 'text-gray-300' : 'text-gray-700']">
            Employment Status
          </h3>
          <div class="space-y-3">
            <div class="flex justify-between items-center">
              <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
                Employed
              </span>
              <span :class="['font-bold text-lg', getEmploymentStatusColor(overallStats.employmentRate)]">
                {{ overallStats.employmentRate }}%
              </span>
            </div>
            <div class="flex justify-between items-center">
              <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
                Self-Employed
              </span>
              <span :class="['font-semibold', isDark ? 'text-blue-400' : 'text-blue-600']">
                {{ overallStats.selfEmployedRate }}%
              </span>
            </div>
            <div class="flex justify-between items-center">
              <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
                Unemployed
              </span>
              <span :class="['font-semibold', isDark ? 'text-gray-300' : 'text-gray-500']">
                {{ overallStats.unemploymentRate }}%
              </span>
            </div>
          </div>
        </div>

        <!-- Location Distribution -->
        <div :class="['p-4 rounded-lg', isDark ? 'bg-gray-700' : 'bg-gray-50']">
          <h3 :class="['font-semibold mb-3', isDark ? 'text-gray-300' : 'text-gray-700']">
            Employment Location
          </h3>
          <div class="space-y-3">
            <div class="flex justify-between items-center">
              <span :class="['text-sm flex items-center gap-1', isDark ? 'text-gray-400' : 'text-gray-600']">
                <MapPin class="w-4 h-4" />
                Local Employment
              </span>
              <span :class="['font-semibold', isDark ? 'text-green-400' : 'text-green-600']">
                {{ overallStats.localEmploymentRate }}%
              </span>
            </div>
            <div class="flex justify-between items-center">
              <span :class="['text-sm flex items-center gap-1', isDark ? 'text-gray-400' : 'text-gray-600']">
                International
              </span>
              <span :class="['font-semibold', isDark ? 'text-blue-400' : 'text-blue-600']">
                {{ overallStats.internationalRate }}%
              </span>
            </div>
          </div>
        </div>

        <!-- Income Overview -->
        <div :class="['p-4 rounded-lg', isDark ? 'bg-gray-700' : 'bg-gray-50']">
          <h3 :class="['font-semibold mb-3', isDark ? 'text-gray-300' : 'text-gray-700']">
            Income Overview
          </h3>
          <div class="space-y-3">
            <div class="flex justify-between items-center">
              <span :class="['text-sm flex items-center gap-1', isDark ? 'text-gray-400' : 'text-gray-600']">
                <DollarSign class="w-4 h-4" />
                Average Monthly
              </span>
              <span :class="['font-bold text-lg', isDark ? 'text-yellow-400' : 'text-yellow-600']">
                {{ formatCurrency(overallStats.averageIncome) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Top Performing Programs -->
    <div :class="['rounded-xl border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <h2 :class="['text-xl font-bold mb-4', isDark ? 'text-white' : 'text-gray-900']">
        Top Performing Programs
      </h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="(program, index) in topPerformers.slice(0, 5)"
          :key="program.name"
          :class="[
            'p-4 rounded-lg border relative',
            index === 0 
              ? isDark ? 'bg-yellow-900/20 border-yellow-500' : 'bg-yellow-50 border-yellow-300'
              : isDark ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'
          ]"
        >
          <!-- Rank Badge -->
          <div :class="[
            'absolute -top-2 -right-2 w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold',
            index === 0 
              ? 'bg-yellow-500 text-white'
              : index === 1
              ? 'bg-gray-400 text-white'
              : index === 2
              ? 'bg-orange-500 text-white'
              : isDark ? 'bg-gray-600 text-gray-300' : 'bg-gray-200 text-gray-600'
          ]">
            {{ index + 1 }}
          </div>
          
          <h3 :class="['font-semibold mb-2', isDark ? 'text-white' : 'text-gray-900']">
            {{ program.name }}
          </h3>
          <div class="space-y-2">
            <div class="flex justify-between items-center">
              <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
                Employment Rate
              </span>
              <span :class="['font-bold', getEmploymentStatusColor(program.employmentRate)]">
                {{ program.employmentRate }}%
              </span>
            </div>
            <div class="flex justify-between items-center">
              <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
                Avg. Income
              </span>
              <span :class="['font-semibold', isDark ? 'text-gray-300' : 'text-gray-700']">
                {{ formatCurrency(program.averageIncome) }}
              </span>
            </div>
            <div class="flex justify-between items-center">
              <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
                International %
              </span>
              <span :class="['font-semibold', isDark ? 'text-blue-400' : 'text-blue-600']">
                {{ program.internationalRate }}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Program-Level Analysis Table -->
    <div :class="['rounded-xl border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <h2 :class="['text-xl font-bold mb-4', isDark ? 'text-white' : 'text-gray-900']">
        Program-Level Analysis
      </h2>
      
      <div class="overflow-x-auto">
        <table :class="['w-full text-sm', isDark ? 'text-gray-300' : 'text-gray-700']">
          <thead>
            <tr :class="['border-b', isDark ? 'border-gray-600' : 'border-gray-200']">
              <th :class="['text-left py-3 px-4 font-semibold', isDark ? 'text-white' : 'text-gray-900']">
                Program
              </th>
              <th :class="['text-center py-3 px-4 font-semibold', isDark ? 'text-white' : 'text-gray-900']">
                Employment Rate
              </th>
              <th :class="['text-center py-3 px-4 font-semibold', isDark ? 'text-white' : 'text-gray-900']">
                Local Employment
              </th>
              <th :class="['text-center py-3 px-4 font-semibold', isDark ? 'text-white' : 'text-gray-900']">
                International
              </th>
              <th :class="['text-center py-3 px-4 font-semibold', isDark ? 'text-white' : 'text-gray-900']">
                Avg. Income
              </th>
              <th :class="['text-center py-3 px-4 font-semibold', isDark ? 'text-white' : 'text-gray-900']">
                Job Relevance
              </th>
              <th :class="['text-center py-3 px-4 font-semibold', isDark ? 'text-white' : 'text-gray-900']">
                Respondents
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="program in programAnalysis"
              :key="program.name"
              :class="['border-b hover:bg-opacity-50', isDark ? 'border-gray-700 hover:bg-gray-700' : 'border-gray-100 hover:bg-gray-50']"
            >
              <td class="py-3 px-4 font-medium">
                {{ program.name }}
              </td>
              <td class="text-center py-3 px-4">
                <span :class="['font-semibold', getEmploymentStatusColor(program.employmentRate)]">
                  {{ program.employmentRate }}%
                </span>
              </td>
              <td class="text-center py-3 px-4">
                {{ program.localEmployment }}%
              </td>
              <td class="text-center py-3 px-4">
                <span :class="['font-semibold', isDark ? 'text-blue-400' : 'text-blue-600']">
                  {{ program.internationalEmployment }}%
                </span>
              </td>
              <td class="text-center py-3 px-4">
                {{ formatCurrency(program.averageIncome) }}
              </td>
              <td class="text-center py-3 px-4">
                <span :class="['font-semibold', getRatingColor(program.jobRelevanceScore)]">
                  {{ program.jobRelevancePercentage }}%
                </span>
              </td>
              <td class="text-center py-3 px-4">
                {{ program.respondentCount }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Employment Sectors & Job Relevance -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Employment Sectors -->
      <div :class="['rounded-xl border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
        <h3 :class="['text-lg font-bold mb-4', isDark ? 'text-white' : 'text-gray-900']">
          🏢 Employment Sectors
        </h3>
        <div class="space-y-3">
          <div
            v-for="(percentage, sector) in employmentSectors"
            :key="sector"
            class="flex justify-between items-center"
          >
            <span :class="['text-sm flex items-center gap-2', isDark ? 'text-gray-400' : 'text-gray-600']">
              <Building class="w-4 h-4" />
              {{ sector }}
            </span>
            <span :class="['font-semibold', isDark ? 'text-gray-300' : 'text-gray-700']">
              {{ percentage }}%
            </span>
          </div>
        </div>
      </div>

      <!-- Job Relevance -->
      <div :class="['rounded-xl border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
        <h3 :class="['text-lg font-bold mb-3', isDark ? 'text-white' : 'text-gray-900']">
          Job Relevance Analysis
        </h3>
        <div class="space-y-3">
          <div
            v-for="(data, relevanceLevel) in jobRelevance"
            :key="relevanceLevel"
            class="flex justify-between items-center"
          >
            <span :class="['text-sm flex items-center gap-2', isDark ? 'text-gray-400' : 'text-gray-600']">
              <Star class="w-4 h-4" />
              {{ relevanceLevel }}
            </span>
            <span :class="['font-semibold', getRatingColor(data.percentage)]">
              {{ data.percentage }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Income Analysis -->
    <div :class="['rounded-xl border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <h2 :class="['text-xl font-bold mb-6', isDark ? 'text-white' : 'text-gray-900']">
        Income Analysis
      </h2>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Income Distribution -->
        <div>
          <h3 :class="['font-semibold mb-3', isDark ? 'text-gray-300' : 'text-gray-700']">
            Income Distribution
          </h3>
          <div class="space-y-2">
            <div
              v-for="(count, range) in incomeAnalysis.distribution || {}"
              :key="range"
              class="flex justify-between items-center"
            >
              <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
                {{ range }}
              </span>
              <span :class="['font-semibold', isDark ? 'text-gray-300' : 'text-gray-700']">
                {{ count }}
              </span>
            </div>
          </div>
        </div>

        <!-- Local vs International -->
        <div>
          <h3 :class="['font-semibold mb-3', isDark ? 'text-gray-300' : 'text-gray-700']">
            Local vs International
          </h3>
          <div class="space-y-2">
            <div class="flex justify-between items-center">
              <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
                Local Avg.
              </span>
              <span :class="['font-semibold', isDark ? 'text-green-400' : 'text-green-600']">
                {{ formatCurrency(incomeAnalysis.localAverage || 0) }}
              </span>
            </div>
            <div class="flex justify-between items-center">
              <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
                International Avg.
              </span>
              <span :class="['font-semibold', isDark ? 'text-blue-400' : 'text-blue-600']">
                {{ formatCurrency(incomeAnalysis.internationalAverage || 0) }}
              </span>
            </div>
          </div>
        </div>

        <!-- By Sector -->
        <div>
          <h3 :class="['font-semibold mb-3', isDark ? 'text-gray-300' : 'text-gray-700']">
            Average by Sector
          </h3>
          <div class="space-y-2">
            <div
              v-for="(average, sector) in incomeAnalysis.bySector || {}"
              :key="sector"
              class="flex justify-between items-center"
            >
              <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
                {{ sector }}
              </span>
              <span :class="['font-semibold', isDark ? 'text-gray-300' : 'text-gray-700']">
                {{ formatCurrency(average) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>