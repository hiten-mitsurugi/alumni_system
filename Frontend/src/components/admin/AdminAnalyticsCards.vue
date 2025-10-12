<template>
  <div>
    <!-- Analytics Cards Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
    <!-- Total Users Card -->
    <div :class="['rounded-lg shadow-sm border p-6', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <div class="flex items-center">
        <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-blue-900' : 'bg-blue-100']">
          <Users :class="['w-6 h-6', themeStore.isAdminDark() ? 'text-blue-400' : 'text-blue-600']" />
        </div>
        <div class="ml-4">
          <p :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">Total Users</p>
          <p :class="['text-2xl font-bold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
            {{ formatNumber(analytics.totalUsers) }}
          </p>
          <p :class="['text-xs mt-1', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
            {{ formatNumber(analytics.activeUsers) }} active
          </p>
        </div>
      </div>
    </div>

    <!-- Pending Approvals Card -->
    <div :class="['rounded-lg shadow-sm border p-6', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <div class="flex items-center">
        <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-yellow-900' : 'bg-yellow-100']">
          <Clock :class="['w-6 h-6', themeStore.isAdminDark() ? 'text-yellow-400' : 'text-yellow-600']" />
        </div>
        <div class="ml-4">
          <p :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">Pending Approvals</p>
          <p :class="['text-2xl font-bold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
            {{ formatNumber(analytics.pendingApprovals) }}
          </p>
          <p :class="['text-xs mt-1', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
            Alumni registrations
          </p>
        </div>
      </div>
    </div>

    <!-- Total Posts Card -->
    <div :class="['rounded-lg shadow-sm border p-6', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <div class="flex items-center">
        <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-green-900' : 'bg-green-100']">
          <FileText :class="['w-6 h-6', themeStore.isAdminDark() ? 'text-green-400' : 'text-green-600']" />
        </div>
        <div class="ml-4">
          <p :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">Total Posts</p>
          <p :class="['text-2xl font-bold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
            {{ formatNumber(analytics.totalPosts) }}
          </p>
          <p :class="['text-xs mt-1', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
            {{ formatNumber(analytics.weeklyPosts) }} this week
          </p>
        </div>
      </div>
    </div>

    <!-- Reports Card (Clickable) -->
    <router-link 
      to="/admin/reports" 
      :class="[
        'rounded-lg shadow-sm border p-6 block transition-all duration-200 hover:shadow-lg hover:scale-105 cursor-pointer',
        themeStore.isAdminDark() 
          ? 'bg-gray-800 border-gray-700 hover:bg-gray-750' 
          : 'bg-white border-gray-200 hover:bg-gray-50'
      ]"
    >
      <div class="flex items-center">
        <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-red-900' : 'bg-red-100']">
          <AlertTriangle :class="['w-6 h-6', themeStore.isAdminDark() ? 'text-red-400' : 'text-red-600']" />
        </div>
        <div class="ml-4 flex-1">
          <p :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">Reported Posts</p>
          <div class="flex items-center justify-between">
            <p :class="['text-2xl font-bold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
              {{ formatNumber(analytics.reportedPosts) }}
            </p>
            <svg :class="['w-4 h-4 opacity-50', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </div>
          <p :class="['text-xs mt-1', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
            Need attention
          </p>
        </div>
      </div>
    </router-link>

    <!-- Activity Rate Card -->
    <div :class="['rounded-lg shadow-sm border p-6', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <div class="flex items-center">
        <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-purple-900' : 'bg-purple-100']">
          <Activity :class="['w-6 h-6', themeStore.isAdminDark() ? 'text-purple-400' : 'text-purple-600']" />
        </div>
        <div class="ml-4">
          <p :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">Activity Rate</p>
          <p :class="['text-2xl font-bold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
            {{ activityRate }}%
          </p>
          <p :class="['text-xs mt-1', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
            {{ formatNumber(analytics.onlineUsers) }} online now
          </p>
        </div>
      </div>
    </div>

    <!-- Recent Registrations Card -->
    <div :class="['rounded-lg shadow-sm border p-6', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <div class="flex items-center">
        <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-indigo-900' : 'bg-indigo-100']">
          <UserPlus :class="['w-6 h-6', themeStore.isAdminDark() ? 'text-indigo-400' : 'text-indigo-600']" />
        </div>
        <div class="ml-4">
          <p :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">New Users</p>
          <p :class="['text-2xl font-bold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
            {{ formatNumber(analytics.recentRegistrations) }}
          </p>
          <p :class="['text-xs mt-1', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
            This week
          </p>
        </div>
      </div>
    </div>

    <!-- Post Status Card -->
    <div :class="['rounded-lg shadow-sm border p-6', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <div class="flex items-center">
        <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-orange-900' : 'bg-orange-100']">
          <CheckCircle :class="['w-6 h-6', themeStore.isAdminDark() ? 'text-orange-400' : 'text-orange-600']" />
        </div>
        <div class="ml-4">
          <p :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">Pending Posts</p>
          <p :class="['text-2xl font-bold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
            {{ formatNumber(analytics.pendingPosts) }}
          </p>
          <p :class="['text-xs mt-1', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
            Awaiting approval
          </p>
        </div>
      </div>
    </div>

    <!-- Engagement Card -->
    <div :class="['rounded-lg shadow-sm border p-6', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <div class="flex items-center">
        <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-teal-900' : 'bg-teal-100']">
          <TrendingUp :class="['w-6 h-6', themeStore.isAdminDark() ? 'text-teal-400' : 'text-teal-600']" />
        </div>
        <div class="ml-4">
          <p :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">User Engagement</p>
          <p :class="['text-2xl font-bold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
            {{ formatNumber(analytics.userEngagement) }}%
          </p>
          <p :class="['text-xs mt-1', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
            Active participation
          </p>
        </div>
      </div>
    </div>
  </div>

  <!-- Summary Stats Row -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
    <!-- Approval Rate -->
    <div :class="['rounded-lg shadow-sm border p-6', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <div class="text-center">
        <div :class="['text-3xl font-bold mb-2', themeStore.isAdminDark() ? 'text-green-400' : 'text-green-600']">
          {{ approvalRate }}%
        </div>
        <p :class="['text-sm', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">Post Approval Rate</p>
        <div :class="['mt-2 text-xs', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
          {{ formatNumber(analytics.approvedPosts) }} approved, 
          {{ formatNumber(analytics.declinedPosts) }} declined
        </div>
      </div>
    </div>

    <!-- System Health -->
    <div :class="['rounded-lg shadow-sm border p-6', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <div class="text-center">
        <div class="text-3xl font-bold mb-2" :class="systemHealthColor">
          {{ systemHealthStatus }}
        </div>
        <p :class="['text-sm', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">System Status</p>
        <div :class="['mt-2 text-xs', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
          {{ formatNumber(analytics.pendingActions) }} pending actions
        </div>
      </div>
    </div>

    <!-- Last Updated -->
    <div :class="['rounded-lg shadow-sm border p-6', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <div class="text-center">
        <div :class="['text-sm font-medium mb-2', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
          Last Updated
        </div>
        <p :class="['text-xs', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
          {{ formatDateTime(lastUpdated) }}
        </p>
        <button 
          @click="$emit('refresh')" 
          :disabled="loading"
          :class="['mt-2 text-xs hover:underline disabled:opacity-50', themeStore.isAdminDark() ? 'text-blue-400' : 'text-blue-600']"
        >
          <span v-if="loading">Refreshing...</span>
          <span v-else">Refresh Now</span>
        </button>
      </div>
    </div>
  </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { 
  Users, Clock, FileText, AlertTriangle, Activity, UserPlus, 
  CheckCircle, TrendingUp 
} from 'lucide-vue-next'
import { useThemeStore } from '@/stores/theme'

// Theme store
const themeStore = useThemeStore()

// Props
const props = defineProps({
  analytics: {
    type: Object,
    required: true,
    default: () => ({
      totalUsers: 0,
      activeUsers: 0,
      pendingApprovals: 0,
      recentRegistrations: 0,
      onlineUsers: 0,
      totalPosts: 0,
      pendingPosts: 0,
      reportedPosts: 0,
      approvedPosts: 0,
      declinedPosts: 0,
      weeklyPosts: 0,
      userEngagement: 0,
      pendingActions: 0
    })
  },
  activityRate: {
    type: String,
    default: '0.0'
  },
  approvalRate: {
    type: String,
    default: '0.0'
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

// Emits
const emit = defineEmits(['refresh'])

// Computed properties
const systemHealthStatus = computed(() => {
  const pendingCount = props.analytics.pendingActions || 0
  if (pendingCount === 0) return 'Excellent'
  if (pendingCount <= 5) return 'Good'
  if (pendingCount <= 15) return 'Fair'
  return 'Needs Attention'
})

const systemHealthColor = computed(() => {
  const status = systemHealthStatus.value
  const isDark = themeStore.isAdminDark()
  switch (status) {
    case 'Excellent': return isDark ? 'text-green-400' : 'text-green-600'
    case 'Good': return isDark ? 'text-blue-400' : 'text-blue-600'
    case 'Fair': return isDark ? 'text-yellow-400' : 'text-yellow-600'
    case 'Needs Attention': return isDark ? 'text-red-400' : 'text-red-600'
    default: return isDark ? 'text-gray-400' : 'text-gray-600'
  }
})

// Utility methods
const formatNumber = (num) => {
  if (typeof num !== 'number') return '0'
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