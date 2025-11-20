
<template>
  <div>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
    <!-- Total Alumni (All in Directory) -->
    <div :class="['rounded-lg shadow-sm border p-6', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <div class="flex items-center justify-between">
        <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-blue-900' : 'bg-blue-100']">
          <Users :class="['w-6 h-6', themeStore.isAdminDark() ? 'text-blue-400' : 'text-blue-600']" />
        </div>
        <div class="text-right">
          <p :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
            Total Alumni
          </p>
          <p :class="['text-2xl font-bold mt-1', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
            {{ formatNumber(analytics.totalAlumni) }}
          </p>
          <p :class="['text-xs mt-1', themeStore.isAdminDark() ? 'text-gray-500' : 'text-gray-500']">
            In directory
          </p>
        </div>
      </div>
    </div>

    <!-- Registered Alumni -->
    <div :class="['rounded-lg shadow-sm border p-6', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <div class="flex items-center justify-between">
        <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-green-900' : 'bg-green-100']">
          <UserCheck :class="['w-6 h-6', themeStore.isAdminDark() ? 'text-green-400' : 'text-green-600']" />
        </div>
        <div class="text-right">
          <p :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
            Registered Alumni
          </p>
          <p :class="['text-2xl font-bold mt-1', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
            {{ formatNumber(analytics.registeredAlumni) }}
          </p>
          <p :class="['text-xs mt-1', analytics.registrationRate >= 70 ? 'text-green-600' : analytics.registrationRate >= 50 ? 'text-yellow-600' : 'text-red-600']">
            {{ analytics.registrationRate.toFixed(1) }}% registered
          </p>
        </div>
      </div>
    </div>

    <!-- Active Surveys -->
    <div :class="['rounded-lg shadow-sm border p-6', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <div class="flex items-center justify-between">
        <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-orange-900' : 'bg-orange-100']">
          <FileText :class="['w-6 h-6', themeStore.isAdminDark() ? 'text-orange-400' : 'text-orange-600']" />
        </div>
        <div class="text-right">
          <p :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
            Active Surveys
          </p>
          <p :class="['text-2xl font-bold mt-1', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
            {{ formatNumber(analytics.activeSurveys) }}
          </p>
        </div>
      </div>
    </div>

    <!-- Responses Today -->
    <div :class="['rounded-lg shadow-sm border p-6', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <div class="flex items-center justify-between">
        <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-purple-900' : 'bg-purple-100']">
          <TrendingUp :class="['w-6 h-6', themeStore.isAdminDark() ? 'text-purple-400' : 'text-purple-600']" />
        </div>
        <div class="text-right">
          <p :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
            Responses Today
          </p>
          <p :class="['text-2xl font-bold mt-1', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
            {{ formatNumber(analytics.responsesToday) }}
          </p>
        </div>
      </div>
    </div>
  </div>

  <!-- Secondary Metrics Row -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
    <div :class="['rounded-lg border p-4', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <p :class="['text-xs font-medium mb-1', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
        Pending Approvals
      </p>
      <p :class="['text-lg font-bold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
        {{ formatNumber(analytics.pendingApprovals) }}
      </p>
    </div>

    <div :class="['rounded-lg border p-4', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <div class="flex items-center justify-between mb-1">
        <p :class="['text-xs font-medium', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
          Users Online
        </p>
        <div class="flex items-center">
          <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
        </div>
      </div>
      <p :class="['text-lg font-bold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
        {{ formatNumber(analytics.onlineUsers) }}
      </p>
      <p :class="['text-xs mt-1', themeStore.isAdminDark() ? 'text-gray-500' : 'text-gray-500']">
        Active in last 15 min
      </p>
    </div>

    <div :class="['rounded-lg border p-4', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <p :class="['text-xs font-medium mb-1', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
        User Engagement
      </p>
      <p :class="['text-lg font-bold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
        {{ analytics.userEngagement }}%
      </p>
      <p :class="['text-xs mt-1', themeStore.isAdminDark() ? 'text-gray-500' : 'text-gray-500']">
        {{ formatNumber(analytics.activeUsers) }} active users
      </p>
    </div>

    <div :class="['rounded-lg border p-4', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <p :class="['text-xs font-medium mb-1', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
        Avg. Completion
      </p>
      <p :class="['text-lg font-bold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
        {{ analytics.avgCompletionRate.toFixed(1) }}%
      </p>
    </div>
  </div>

  <!-- Refresh Banner -->
  <div 
    v-if="lastUpdated"
    :class="['mb-6 px-4 py-2 rounded-lg border text-xs flex items-center justify-between',
      themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700 text-gray-400' : 'bg-gray-50 border-gray-200 text-gray-600']"
  >
    <span>Last updated: {{ formatDateTime(lastUpdated) }}</span>
    <button 
      @click="$emit('refresh')"
      :disabled="loading"
      :class="[
        'ml-2 text-xs disabled:opacity-50 transition-colors',
        themeStore.isAdminDark() ? 'text-orange-400 hover:text-orange-300' : 'text-orange-600 hover:text-orange-700'
      ]"
    >
    </button>
  </div>
  </div>
</template>


<script setup>
import { Users, FileText, TrendingUp, UserCheck, RefreshCw } from 'lucide-vue-next'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

defineProps({
  analytics: {
    type: Object,
    required: true,
    default: () => ({
      totalAlumni: 0,
      registeredAlumni: 0,
      registrationRate: 0,
      activeSurveys: 0,
      responsesToday: 0,
      pendingApprovals: 0,
      totalResponses: 0,
      respondents: 0,
      nonRespondents: 0,
      responseRate: 0,
      closedSurveys: 0,
      avgCompletionRate: 0,
      onlineUsers: 0,
      userEngagement: 0,
      activeUsers: 0
    })
  },
  lastUpdated: {
    type: Date,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['refresh'])

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0'
  return num.toLocaleString()
}

const formatDateTime = (date) => {
  if (!date) return 'Never'
  try {
    return new Date(date).toLocaleString()
  } catch {
    return 'Invalid Date'
  }
}
</script>
