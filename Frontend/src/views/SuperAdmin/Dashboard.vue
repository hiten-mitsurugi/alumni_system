<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <div :class="['min-h-screen transition-colors', isDark ? 'bg-gray-900' : 'bg-gray-50']">
    <!-- Header Section -->
    <div :class="['border-b', isDark ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200']">
      <div class="px-6 py-6">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 :class="['text-3xl font-bold', isDark ? 'text-white' : 'text-gray-900']">
              Dashboard
            </h1>
            <p :class="['text-lg mt-1', isDark ? 'text-gray-400' : 'text-gray-600']">
              CSU Graduate Tracer Study System Overview
            </p>
          </div>
          
          <div class="flex flex-col sm:flex-row items-start sm:items-center gap-4">
            <!-- Real-time Clock -->
            <div :class="['flex items-center gap-2 px-4 py-2 rounded-lg', isDark ? 'bg-gray-800 text-gray-300' : 'bg-gray-100 text-gray-700']">
              <Calendar class="w-5 h-5" />
              <span class="text-sm font-medium">{{ currentTime }}</span>
            </div>
            
            <!-- Auto-refresh Status -->
            <div class="flex items-center gap-2">
              <RefreshCw class="w-4 h-4 text-green-500 animate-spin" />
              <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
                Live Data
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="p-6 space-y-8">
      <!-- Key Metrics Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-8">
        <!-- Survey Responses -->
        <div :class="['rounded-lg border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div :class="['p-2 rounded-lg bg-blue-100']">
                <TrendingUp class="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 :class="['text-sm font-medium', isDark ? 'text-gray-400' : 'text-gray-600']">Survey Responses</h3>
                <p :class="['text-2xl font-bold', isDark ? 'text-white' : 'text-gray-900']">{{ dashboardStats.totalResponses || 0 }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Response Rate -->
        <div :class="['rounded-lg border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div :class="['p-2 rounded-lg bg-green-100']">
                <Users class="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h3 :class="['text-sm font-medium', isDark ? 'text-gray-400' : 'text-gray-600']">Response Rate</h3>
                <p :class="['text-2xl font-bold', getStatusColor(responseRateStatus)]">
                  {{ dashboardStats.responseRate || 0 }}%
                </p>
              </div>
            </div>
          </div>
          <div :class="['w-full bg-gray-200 rounded-full h-2', isDark ? 'bg-gray-700' : 'bg-gray-200']">
            <div 
              :class="['h-2 rounded-full transition-all', getProgressBarColor(dashboardStats.responseRate || 0)]"
              :style="{ width: `${Math.min(dashboardStats.responseRate || 0, 100)}%` }"
            ></div>
          </div>
        </div>

        <!-- Employment Rate -->
        <div :class="['rounded-lg border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div :class="['p-2 rounded-lg bg-purple-100']">
                <Briefcase class="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h3 :class="['text-sm font-medium', isDark ? 'text-gray-400' : 'text-gray-600']">Employment Rate</h3>
                <p :class="['text-2xl font-bold', getStatusColor(employmentRateStatus)]">
                  {{ dashboardStats.employmentRate || 0 }}%
                </p>
              </div>
            </div>
          </div>
          <div :class="['w-full bg-gray-200 rounded-full h-2', isDark ? 'bg-gray-700' : 'bg-gray-200']">
            <div 
              :class="['h-2 rounded-full transition-all', getProgressBarColor(dashboardStats.employmentRate || 0)]"
              :style="{ width: `${Math.min(dashboardStats.employmentRate || 0, 100)}%` }"
            ></div>
          </div>
        </div>

        <!-- Competitiveness Score -->
        <div :class="['rounded-lg border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div :class="['p-2 rounded-lg bg-yellow-100']">
                <Star class="w-6 h-6 text-yellow-600" />
              </div>
              <div>
                <h3 :class="['text-sm font-medium', isDark ? 'text-gray-400' : 'text-gray-600']">Competitiveness Score</h3>
                <p :class="['text-2xl font-bold', getStatusColor(competitivenessStatus)]">
                  {{ (dashboardStats.competitivenessScore || 0).toFixed(1) }}/5.0
                </p>
              </div>
            </div>
          </div>
          <div :class="['w-full bg-gray-200 rounded-full h-2', isDark ? 'bg-gray-700' : 'bg-gray-200']">
            <div 
              :class="['h-2 rounded-full transition-all', getProgressBarColor(((dashboardStats.competitivenessScore || 0) / 5) * 100)]"
              :style="{ width: `${Math.min(((dashboardStats.competitivenessScore || 0) / 5) * 100, 100)}%` }"
            ></div>
          </div>
        </div>
      </div>

      <!-- Survey Responses by Program -->
      <div :class="['rounded-lg border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
        <div class="flex items-center gap-2 mb-6">
          <BarChart3 class="w-5 h-5 text-blue-500" />
          <h2 :class="['text-lg font-semibold', isDark ? 'text-white' : 'text-gray-900']">
            Response Rate by Program
          </h2>
        </div>
        <div class="space-y-4">
          <div 
            v-for="program in (dashboardStats.programStats || [])" 
            :key="program.name"
            class="space-y-2"
          >
            <div class="flex justify-between items-center">
              <span :class="['text-sm font-medium', isDark ? 'text-white' : 'text-gray-900']">
                {{ program.name }}
              </span>
              <div class="flex items-center gap-2">
                <span :class="['text-sm', isDark ? 'text-gray-300' : 'text-gray-600']">
                  {{ program.responses }} responses
                </span>
                <span :class="['text-sm font-bold', getProgramStatusColor(program.percentage)]">
                  ({{ program.percentage }}%)
                </span>
              </div>
            </div>
            <div :class="['w-full bg-gray-200 rounded-full h-3', isDark ? 'bg-gray-700' : 'bg-gray-200']">
              <div 
                :class="['h-3 rounded-full transition-all', getProgressBarColor(program.percentage)]"
                :style="{ width: `${Math.min(program.percentage, 100)}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Employment Overview -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Employment Status Distribution -->
        <div :class="['rounded-lg border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
          <div class="flex items-center gap-2 mb-6">
            <Briefcase class="w-5 h-5 text-green-500" />
            <h2 :class="['text-lg font-semibold', isDark ? 'text-white' : 'text-gray-900']">
              Employment Status Distribution
            </h2>
          </div>
          
          <!-- Donut Chart Simulation -->
          <div class="flex items-center justify-center mb-6">
            <div class="relative w-32 h-32">
              <svg class="w-32 h-32 transform -rotate-90" viewBox="0 0 100 100">
                <!-- Background circle -->
                <circle cx="50" cy="50" r="40" fill="none" :stroke="isDark ? '#374151' : '#E5E7EB'" stroke-width="10"/>
                <!-- Employed segment -->
                <circle 
                  cx="50" cy="50" r="40" fill="none" stroke="#10B981" stroke-width="10"
                  :stroke-dasharray="`${(dashboardStats.employmentStats?.employed || 0) * 2.51} 251.2`"
                  stroke-dashoffset="0"
                />
                <!-- Self-employed segment -->
                <circle 
                  cx="50" cy="50" r="40" fill="none" stroke="#3B82F6" stroke-width="10"
                  :stroke-dasharray="`${(dashboardStats.employmentStats?.selfEmployed || 0) * 2.51} 251.2`"
                  :stroke-dashoffset="`-${(dashboardStats.employmentStats?.employed || 0) * 2.51}`"
                />
                <!-- Unemployed segment -->
                <circle 
                  cx="50" cy="50" r="40" fill="none" stroke="#EF4444" stroke-width="10"
                  :stroke-dasharray="`${(dashboardStats.employmentStats?.unemployed || 0) * 2.51} 251.2`"
                  :stroke-dashoffset="`-${((dashboardStats.employmentStats?.employed || 0) + (dashboardStats.employmentStats?.selfEmployed || 0)) * 2.51}`"
                />
              </svg>
              <div class="absolute inset-0 flex items-center justify-center">
                <div class="text-center">
                  <div :class="['text-lg font-bold', isDark ? 'text-white' : 'text-gray-900']">
                    {{ dashboardStats.employmentRate }}%
                  </div>
                  <div :class="['text-xs', isDark ? 'text-gray-400' : 'text-gray-500']">
                    Employed
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Legend -->
          <div class="space-y-2">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-green-500"></div>
              <span :class="['text-sm', isDark ? 'text-gray-300' : 'text-gray-600']">
                Employed ({{ dashboardStats.employmentStats?.employed || 0 }}%)
              </span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-blue-500"></div>
              <span :class="['text-sm', isDark ? 'text-gray-300' : 'text-gray-600']">
                Self-employed ({{ dashboardStats.employmentStats?.selfEmployed || 0 }}%)
              </span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-red-500"></div>
              <span :class="['text-sm', isDark ? 'text-gray-300' : 'text-gray-600']">
                Unemployed ({{ dashboardStats.employmentStats?.unemployed || 0 }}%)
              </span>
            </div>
          </div>
        </div>

        <!-- Employment Metrics -->
        <div :class="['rounded-lg border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
          <h3 :class="['text-lg font-semibold mb-6', isDark ? 'text-white' : 'text-gray-900']">
            Employment Metrics
          </h3>
          
          <div class="grid grid-cols-2 gap-4">
            <!-- Average Income -->
            <div :class="['p-4 rounded-lg', isDark ? 'bg-gray-700' : 'bg-gray-50']">
              <div :class="['text-2xl font-bold text-green-500']">
                {{ formatCurrency(dashboardStats.employmentStats?.avgIncome || 0) }}
              </div>
              <div :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
                Average Monthly Income
              </div>
            </div>

            <!-- Job Relevance -->
            <div :class="['p-4 rounded-lg', isDark ? 'bg-gray-700' : 'bg-gray-50']">
              <div :class="['text-2xl font-bold text-blue-500']">
                {{ dashboardStats.employmentStats?.jobRelevance || 0 }}%
              </div>
              <div :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
                Job Relevant to Degree
              </div>
            </div>

            <!-- International Employment -->
            <div :class="['p-4 rounded-lg', isDark ? 'bg-gray-700' : 'bg-gray-50']">
              <div :class="['text-2xl font-bold text-purple-500']">
                {{ dashboardStats.employmentStats?.international || 0 }}%
              </div>
              <div :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
                Working Abroad
              </div>
            </div>

            <!-- Local Employment -->
            <div :class="['p-4 rounded-lg', isDark ? 'bg-gray-700' : 'bg-gray-50']">
              <div :class="['text-2xl font-bold text-orange-500']">
                {{ dashboardStats.employmentStats?.local || 0 }}%
              </div>
              <div :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
                Working Locally
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Skills Performance -->
      <div :class="['rounded-lg border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
        <div class="flex items-center gap-2 mb-6">
          <Target class="w-5 h-5 text-orange-500" />
          <h2 :class="['text-lg font-semibold', isDark ? 'text-white' : 'text-gray-900']">
            Top Skills Ratings
          </h2>
        </div>
        <div class="space-y-4">
          <div 
            v-for="skill in (dashboardStats.skillsStats || [])" 
            :key="skill.name"
            class="space-y-2"
          >
            <div class="flex justify-between items-center">
              <span :class="['text-sm font-medium', isDark ? 'text-white' : 'text-gray-900']">
                {{ skill.name }}
              </span>
              <span :class="['text-sm font-bold', getSkillColor(skill.rating) ? 'text-green-500' : skill.rating >= 3.0 ? 'text-yellow-500' : 'text-red-500']">
                {{ skill.rating.toFixed(1) }}
              </span>
            </div>
            <div :class="['w-full bg-gray-200 rounded-full h-2', isDark ? 'bg-gray-700' : 'bg-gray-200']">
              <div 
                :class="['h-2 rounded-full transition-all', getSkillColor(skill.rating)]"
                :style="{ width: `${(skill.rating / 5) * 100}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Program Employment Performance & System Stats -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Program Employment Performance -->
        <div :class="['lg:col-span-2 rounded-lg border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
          <div class="flex items-center gap-2 mb-6">
            <BookOpen class="w-5 h-5 text-indigo-500" />
            <h2 :class="['text-lg font-semibold', isDark ? 'text-white' : 'text-gray-900']">
              Employment Rate by Program
            </h2>
          </div>
          <div class="grid grid-cols-5 gap-4">
            <div 
              v-for="program in (dashboardStats.programEmployment || [])" 
              :key="program.name"
              class="text-center"
            >
              <div class="flex flex-col items-center h-32 justify-end mb-2">
                <div 
                  :class="['w-8 rounded-t transition-all', getProgressBarColor(program.employmentRate)]"
                  :style="{ height: `${(program.employmentRate / 100) * 100}px` }"
                ></div>
              </div>
              <div :class="['text-lg font-bold', getProgramStatusColor(program.employmentRate)]">
                {{ program.employmentRate }}%
              </div>
              <div :class="['text-xs', isDark ? 'text-gray-400' : 'text-gray-600']">
                {{ program.name }}
              </div>
            </div>
          </div>
        </div>

        <!-- System Statistics -->
        <div :class="['rounded-lg border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
          <h2 :class="['text-lg font-semibold mb-6', isDark ? 'text-white' : 'text-gray-900']">
            System Overview
          </h2>
          
          <div class="space-y-4">
            <!-- Total Alumni -->
            <div :class="['p-3 rounded-lg', isDark ? 'bg-gray-700' : 'bg-gray-50']">
              <div :class="['text-xl font-bold', isDark ? 'text-white' : 'text-gray-900']">
                {{ dashboardStats.systemStats?.totalAlumni || 0 }}
              </div>
              <div :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
                Total Alumni Registered
              </div>
            </div>

            <!-- Pending Approvals -->
            <div :class="['p-3 rounded-lg', isDark ? 'bg-gray-700' : 'bg-gray-50']">
              <div :class="[
                'text-xl font-bold',
                (dashboardStats.systemStats?.pendingApprovals || 0) > 10 ? 'text-red-500' :
                (dashboardStats.systemStats?.pendingApprovals || 0) > 5 ? 'text-yellow-500' : 'text-green-500'
              ]">
                {{ dashboardStats.systemStats?.pendingApprovals || 0 }}
              </div>
              <div :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
                Pending Approvals
              </div>
            </div>

            <!-- Active Surveys -->
            <div :class="['p-3 rounded-lg', isDark ? 'bg-gray-700' : 'bg-gray-50']">
              <div :class="['text-xl font-bold text-blue-500']">
                {{ dashboardStats.systemStats?.activeSurveys || 0 }}
              </div>
              <div :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
                Active Surveys
              </div>
            </div>

            <!-- Data Completeness -->
            <div :class="['p-3 rounded-lg', isDark ? 'bg-gray-700' : 'bg-gray-50']">
              <div :class="['text-xl font-bold text-green-500']">
                {{ dashboardStats.systemStats?.dataCompleteness || 0 }}%
              </div>
              <div :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
                Data Completeness
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Further Studies & Demographics -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Further Studies -->
        <div :class="['rounded-lg border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
          <h2 :class="['text-lg font-semibold mb-6', isDark ? 'text-white' : 'text-gray-900']">
            Pursuing Further Studies
          </h2>
          
          <div class="text-center mb-6">
            <div :class="['text-4xl font-bold text-purple-500 mb-2']">
              {{ dashboardStats.furtherStudies?.percentage || 0 }}%
            </div>
            <div :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">
              pursuing postgraduate education
            </div>
          </div>

          <div class="space-y-3">
            <div class="flex justify-between items-center">
              <span :class="['text-sm', isDark ? 'text-gray-300' : 'text-gray-600']">Masters</span>
              <span :class="['text-sm font-medium', isDark ? 'text-white' : 'text-gray-900']">
                {{ dashboardStats.furtherStudies?.masters || 0 }}%
              </span>
            </div>
            <div class="flex justify-between items-center">
              <span :class="['text-sm', isDark ? 'text-gray-300' : 'text-gray-600']">Doctorate</span>
              <span :class="['text-sm font-medium', isDark ? 'text-white' : 'text-gray-900']">
                {{ dashboardStats.furtherStudies?.doctorate || 0 }}%
              </span>
            </div>
            <div class="flex justify-between items-center">
              <span :class="['text-sm', isDark ? 'text-gray-300' : 'text-gray-600']">Certificate</span>
              <span :class="['text-sm font-medium', isDark ? 'text-white' : 'text-gray-900']">
                {{ dashboardStats.furtherStudies?.certificate || 0 }}%
              </span>
            </div>
          </div>
        </div>

        <!-- Demographics -->
        <div :class="['rounded-lg border p-6', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
          <h2 :class="['text-lg font-semibold mb-6', isDark ? 'text-white' : 'text-gray-900']">
            Respondent Profile
          </h2>
          
          <div class="space-y-6">
            <!-- Gender Distribution -->
            <div>
              <h3 :class="['text-sm font-medium mb-3', isDark ? 'text-gray-300' : 'text-gray-700']">
                Gender Distribution
              </h3>
              <div class="space-y-2">
                <div class="flex justify-between items-center">
                  <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">Male</span>
                  <span :class="['text-sm font-medium', isDark ? 'text-white' : 'text-gray-900']">
                    {{ dashboardStats.demographics?.gender?.male || 0 }}%
                  </span>
                </div>
                <div class="flex justify-between items-center">
                  <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">Female</span>
                  <span :class="['text-sm font-medium', isDark ? 'text-white' : 'text-gray-900']">
                    {{ dashboardStats.demographics?.gender?.female || 0 }}%
                  </span>
                </div>
              </div>
            </div>

            <!-- Location -->
            <div>
              <h3 :class="['text-sm font-medium mb-3', isDark ? 'text-gray-300' : 'text-gray-700']">
                Location
              </h3>
              <div class="space-y-2">
                <div class="flex justify-between items-center">
                  <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">Philippines</span>
                  <span :class="['text-sm font-medium', isDark ? 'text-white' : 'text-gray-900']">
                    {{ dashboardStats.demographics?.location?.philippines || 0 }}%
                  </span>
                </div>
                <div class="flex justify-between items-center">
                  <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">International</span>
                  <span :class="['text-sm font-medium', isDark ? 'text-white' : 'text-gray-900']">
                    {{ dashboardStats.demographics?.location?.international || 0 }}%
                  </span>
                </div>
              </div>
            </div>

            <!-- Civil Status -->
            <div>
              <h3 :class="['text-sm font-medium mb-3', isDark ? 'text-gray-300' : 'text-gray-700']">
                Civil Status
              </h3>
              <div class="space-y-2">
                <div class="flex justify-between items-center">
                  <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">Single</span>
                  <span :class="['text-sm font-medium', isDark ? 'text-white' : 'text-gray-900']">
                    {{ dashboardStats.demographics?.civilStatus?.single || 0 }}%
                  </span>
                </div>
                <div class="flex justify-between items-center">
                  <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">Married</span>
                  <span :class="['text-sm font-medium', isDark ? 'text-white' : 'text-gray-900']">
                    {{ dashboardStats.demographics?.civilStatus?.married || 0 }}%
                  </span>
                </div>
                <div class="flex justify-between items-center">
                  <span :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-600']">Others</span>
                  <span :class="['text-sm font-medium', isDark ? 'text-white' : 'text-gray-900']">
                    {{ dashboardStats.demographics?.civilStatus?.others || 0 }}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { 
  TrendingUp, 
  Users, 
  Star, 
  Calendar,
  RefreshCw,
  Briefcase,
  BarChart3,
  Target,
  BookOpen
} from 'lucide-vue-next'
import { useThemeStore } from '@/stores/theme'
import { dashboardService } from '@/services/dashboardService'

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isAdminDark?.() || false)

// Reactive data
const currentTime = ref('')
const dashboardStats = ref({})

// Computed properties for status determination
const responseRateStatus = computed(() => {
  if (!dashboardStats.value.responseRate) return 'unknown'
  const rate = dashboardStats.value.responseRate
  if (rate >= 80) return 'excellent'
  if (rate >= 60) return 'good'
  if (rate >= 40) return 'fair'
  return 'poor'
})

const employmentRateStatus = computed(() => {
  if (!dashboardStats.value.employmentRate) return 'unknown'
  const rate = dashboardStats.value.employmentRate
  if (rate >= 85) return 'excellent'
  if (rate >= 70) return 'good'
  if (rate >= 50) return 'fair'
  return 'poor'
})

const competitivenessStatus = computed(() => {
  if (!dashboardStats.value.competitivenessScore) return 'unknown'
  const score = dashboardStats.value.competitivenessScore
  if (score >= 4.5) return 'excellent'
  if (score >= 3.8) return 'good'
  if (score >= 3.0) return 'fair'
  return 'poor'
})

// Helper functions
const getStatusColor = (status) => {
  const colors = {
    excellent: 'text-green-500',
    good: 'text-blue-500',
    fair: 'text-yellow-500',
    poor: 'text-red-500',
    unknown: 'text-gray-500'
  }
  return colors[status] || colors.unknown
}

const getProgressBarColor = (percentage) => {
  if (percentage >= 80) return 'bg-green-500'
  if (percentage >= 60) return 'bg-blue-500'
  if (percentage >= 40) return 'bg-yellow-500'
  return 'bg-red-500'
}

const getProgramStatusColor = (percentage) => {
  if (percentage >= 80) return 'text-green-500'
  if (percentage >= 60) return 'text-blue-500'
  if (percentage >= 40) return 'text-yellow-500'
  return 'text-red-500'
}

const getSkillColor = (rating) => {
  if (rating >= 4.0) return 'bg-green-500'
  if (rating >= 3.0) return 'bg-yellow-500'
  return 'bg-red-500'
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('en-PH', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// Lifecycle
onMounted(async () => {
  console.log('Dashboard mounting...')
  updateTime()
  setInterval(updateTime, 1000)
  
  try {
    console.log('Loading dashboard data...')
    dashboardStats.value = await dashboardService.getDashboardStats()
    console.log('Dashboard data loaded:', dashboardStats.value)
  } catch (error) {
    console.error('Error loading dashboard data:', error)
  }
})
</script>