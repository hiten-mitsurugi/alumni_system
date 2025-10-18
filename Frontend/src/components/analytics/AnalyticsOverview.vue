<script setup>
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { TrendingUp, TrendingDown, Users, Briefcase, GraduationCap, Trophy, Globe, DollarSign } from 'lucide-vue-next'

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

const overviewData = computed(() => props.data.overview || {})
const quickInsights = computed(() => overviewData.value.quickInsights || [])
const kpiCards = computed(() => overviewData.value.kpiCards || [])

const getIconComponent = (category) => {
  const icons = {
    'respondents': Users,
    'employment': Briefcase,
    'income': DollarSign,
    'studies': GraduationCap,
    'competitiveness': Trophy,
    'international': Globe
  }
  return icons[category] || Users
}

const getTrendIcon = (trend) => {
  return trend >= 0 ? TrendingUp : TrendingDown
}

const getTrendColor = (trend) => {
  if (trend > 0) return isDark.value ? 'text-green-400' : 'text-green-600'
  if (trend < 0) return isDark.value ? 'text-red-400' : 'text-red-600'
  return isDark.value ? 'text-gray-400' : 'text-gray-500'
}

const formatValue = (value, format) => {
  switch (format) {
    case 'number':
      return parseInt(value).toLocaleString()
    case 'percentage':
      return `${value}%`
    case 'currency':
      return `₱${parseInt(value).toLocaleString()}`
    case 'rating':
      return `${parseFloat(value).toFixed(1)}/5.0`
    default:
      return value.toString()
  }
}
</script>

<template>
  <div class="space-y-8">
    <!-- Page Header -->
    <div>
      <h1 :class="['text-3xl font-bold mb-2', isDark ? 'text-white' : 'text-gray-900']">
        Analytics Overview
      </h1>
      <p :class="['text-lg', isDark ? 'text-gray-400' : 'text-gray-600']">
        Executive summary and key performance indicators from survey responses
      </p>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="kpi in kpiCards"
        :key="kpi.title"
        :class="[
          'p-6 rounded-xl border transition-shadow hover:shadow-lg',
          isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
        ]"
      >
        <div class="flex items-center justify-between mb-4">
          <div :class="['p-3 rounded-lg', isDark ? 'bg-blue-600' : 'bg-blue-100']">
            <component 
              :is="getIconComponent(kpi.category)" 
              :class="['w-6 h-6', isDark ? 'text-white' : 'text-blue-600']" 
            />
          </div>
          <div v-if="kpi.trend !== 0" class="flex items-center gap-1">
            <component 
              :is="getTrendIcon(kpi.trend)" 
              :class="['w-4 h-4', getTrendColor(kpi.trend)]" 
            />
            <span :class="['text-sm font-medium', getTrendColor(kpi.trend)]">
              {{ Math.abs(kpi.trend) }}%
            </span>
          </div>
        </div>
        
        <div>
          <h3 :class="['text-2xl font-bold mb-1', isDark ? 'text-white' : 'text-gray-900']">
            {{ formatValue(kpi.value, kpi.format) }}
          </h3>
          <p :class="['text-sm font-medium', isDark ? 'text-gray-400' : 'text-gray-600']">
            {{ kpi.title }}
          </p>
        </div>
      </div>
    </div>

    <!-- Quick Insights -->
    <div :class="['rounded-xl border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <h2 :class="['text-xl font-bold mb-4', isDark ? 'text-white' : 'text-gray-900']">
        Quick Insights
      </h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Top Performing Program -->
        <div :class="['p-4 rounded-lg', isDark ? 'bg-gray-700' : 'bg-gray-50']">
          <h3 :class="['font-semibold mb-2', isDark ? 'text-gray-300' : 'text-gray-700']">
            Top Performing Program
          </h3>
          <div v-if="overviewData.topProgram">
            <p :class="['text-lg font-bold', isDark ? 'text-white' : 'text-gray-900']">
              {{ overviewData.topProgram.name }}
            </p>
            <p :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
              {{ overviewData.topProgram.employmentRate }}% employment rate
            </p>
          </div>
          <p v-else :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-500']">
            Data not available
          </p>
        </div>

        <!-- Most Valued Skill -->
        <div :class="['p-4 rounded-lg', isDark ? 'bg-gray-700' : 'bg-gray-50']">
          <h3 :class="['font-semibold mb-2', isDark ? 'text-gray-300' : 'text-gray-700']">
            Most Valued Skill
          </h3>
          <div v-if="overviewData.topSkill">
            <p :class="['text-lg font-bold', isDark ? 'text-white' : 'text-gray-900']">
              {{ overviewData.topSkill.name }}
            </p>
            <p :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
              {{ overviewData.topSkill.average }}/5.0 average rating
            </p>
          </div>
          <p v-else :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-500']">
            Data not available
          </p>
        </div>
      </div>

      <!-- Additional Insights -->
      <div v-if="quickInsights.length > 0" class="mt-6">
        <h3 :class="['font-semibold mb-3', isDark ? 'text-gray-300' : 'text-gray-700']">
          Key Findings
        </h3>
        <div class="space-y-2">
          <div
            v-for="(insight, index) in quickInsights"
            :key="index"
            :class="[
              'p-3 rounded-lg border-l-4',
              isDark ? 'bg-gray-700 border-blue-500' : 'bg-blue-50 border-blue-400'
            ]"
          >
            <p :class="['text-sm', isDark ? 'text-gray-300' : 'text-gray-700']">
              {{ insight }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary Statistics -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Employment Overview -->
      <div :class="['rounded-xl border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
        <h3 :class="['text-lg font-bold mb-4', isDark ? 'text-white' : 'text-gray-900']">
          Employment Overview
        </h3>
        <div class="space-y-3">
          <div class="flex justify-between items-center">
            <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
              Employment Rate
            </span>
            <span :class="['font-semibold', isDark ? 'text-green-400' : 'text-green-600']">
              {{ overviewData.employmentRate }}%
            </span>
          </div>
          <div class="flex justify-between items-center">
            <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
              International Employment
            </span>
            <span :class="['font-semibold', isDark ? 'text-blue-400' : 'text-blue-600']">
              {{ overviewData.internationalRate }}%
            </span>
          </div>
          <div class="flex justify-between items-center">
            <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
              Average Monthly Income
            </span>
            <span :class="['font-semibold', isDark ? 'text-white' : 'text-gray-900']">
              ₱{{ parseInt(overviewData.averageIncome).toLocaleString() }}
            </span>
          </div>
        </div>
      </div>

      <!-- Academic Performance -->
      <div :class="['rounded-xl border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
        <h3 :class="['text-lg font-bold mb-4', isDark ? 'text-white' : 'text-gray-900']">
          Academic Performance
        </h3>
        <div class="space-y-3">
          <div class="flex justify-between items-center">
            <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
              Further Studies Rate
            </span>
            <span :class="['font-semibold', isDark ? 'text-purple-400' : 'text-purple-600']">
              {{ overviewData.furtherStudiesRate }}%
            </span>
          </div>
          <div class="flex justify-between items-center">
            <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
              Competitiveness Score
            </span>
            <span :class="['font-semibold', isDark ? 'text-yellow-400' : 'text-yellow-600']">
              {{ parseFloat(overviewData.competitivenessScore).toFixed(1) }}/5.0
            </span>
          </div>
          <div class="flex justify-between items-center">
            <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
              Total Respondents
            </span>
            <span :class="['font-semibold', isDark ? 'text-white' : 'text-gray-900']">
              {{ parseInt(overviewData.totalRespondents).toLocaleString() }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Access to Reports -->
    <div :class="['rounded-xl border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <h2 :class="['text-xl font-bold mb-4', isDark ? 'text-white' : 'text-gray-900']">
        Detailed Reports
      </h2>
      <p :class="['text-sm mb-4', isDark ? 'text-gray-400' : 'text-gray-600']">
        Access comprehensive analytics for specific areas of interest
      </p>
      
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div 
          v-for="report in [
            { title: 'Employability', component: Briefcase, color: 'blue' },
            { title: 'Skills Analysis', component: Trophy, color: 'green' },
            { title: 'Curriculum', component: GraduationCap, color: 'purple' },
            { title: 'Demographics', component: Users, color: 'orange' }
          ]"
          :key="report.title"
          :class="[
            'p-4 text-center rounded-lg border cursor-pointer transition-all hover:scale-105',
            isDark ? 'bg-gray-700 border-gray-600 hover:bg-gray-600' : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
          ]"
        >
          <div class="flex justify-center mb-2">
            <component :is="report.component" :class="['w-6 h-6', isDark ? 'text-gray-300' : 'text-gray-700']" />
          </div>
          <p :class="['text-sm font-medium', isDark ? 'text-gray-300' : 'text-gray-700']">
            {{ report.title }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>