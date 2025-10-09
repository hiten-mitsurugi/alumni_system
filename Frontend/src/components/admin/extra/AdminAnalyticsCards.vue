<template>
  <div>
    <!-- Analytics Cards Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
    <!-- Total Users Card -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border dark:border-gray-700 p-6">
      <div class="flex items-center">
        <div class="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
          <Users class="w-6 h-6 text-blue-600 dark:text-blue-400" />
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Users</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ formatNumber(analytics.totalUsers) }}
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {{ formatNumber(analytics.activeUsers) }} active
          </p>
        </div>
      </div>
    </div>

    <!-- Pending Approvals Card -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border dark:border-gray-700 p-6">
      <div class="flex items-center">
        <div class="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
          <Clock class="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Pending Approvals</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ formatNumber(analytics.pendingApprovals) }}
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Alumni registrations
          </p>
        </div>
      </div>
    </div>

    <!-- Total Posts Card -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border dark:border-gray-700 p-6">
      <div class="flex items-center">
        <div class="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
          <FileText class="w-6 h-6 text-green-600 dark:text-green-400" />
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Posts</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ formatNumber(analytics.totalPosts) }}
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {{ formatNumber(analytics.weeklyPosts) }} this week
          </p>
        </div>
      </div>
    </div>

    <!-- Reports Card -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border dark:border-gray-700 p-6">
      <div class="flex items-center">
        <div class="p-2 bg-red-100 dark:bg-red-900 rounded-lg">
          <AlertTriangle class="w-6 h-6 text-red-600 dark:text-red-400" />
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Reported Posts</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ formatNumber(analytics.reportedPosts) }}
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Need attention
          </p>
        </div>
      </div>
    </div>

    <!-- Activity Rate Card -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border dark:border-gray-700 p-6">
      <div class="flex items-center">
        <div class="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
          <Activity class="w-6 h-6 text-purple-600 dark:text-purple-400" />
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Activity Rate</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ activityRate }}%
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {{ formatNumber(analytics.onlineUsers) }} online now
          </p>
        </div>
      </div>
    </div>

    <!-- Recent Registrations Card -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border dark:border-gray-700 p-6">
      <div class="flex items-center">
        <div class="p-2 bg-indigo-100 dark:bg-indigo-900 rounded-lg">
          <UserPlus class="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">New Users</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ formatNumber(analytics.recentRegistrations) }}
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            This week
          </p>
        </div>
      </div>
    </div>

    <!-- Post Status Card -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border dark:border-gray-700 p-6">
      <div class="flex items-center">
        <div class="p-2 bg-orange-100 dark:bg-orange-900 rounded-lg">
          <CheckCircle class="w-6 h-6 text-orange-600 dark:text-orange-400" />
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Pending Posts</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ formatNumber(analytics.pendingPosts) }}
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Awaiting approval
          </p>
        </div>
      </div>
    </div>

    <!-- Engagement Card -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border dark:border-gray-700 p-6">
      <div class="flex items-center">
        <div class="p-2 bg-teal-100 dark:bg-teal-900 rounded-lg">
          <TrendingUp class="w-6 h-6 text-teal-600 dark:text-teal-400" />
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">User Engagement</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ formatNumber(analytics.userEngagement) }}%
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Active participation
          </p>
        </div>
      </div>
    </div>
  </div>

  <!-- Summary Stats Row -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
    <!-- Approval Rate -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border dark:border-gray-700 p-6">
      <div class="text-center">
        <div class="text-3xl font-bold text-green-600 dark:text-green-400 mb-2">
          {{ approvalRate }}%
        </div>
        <p class="text-sm text-gray-500 dark:text-gray-400">Post Approval Rate</p>
        <div class="mt-2 text-xs text-gray-400">
          {{ formatNumber(analytics.approvedPosts) }} approved, 
          {{ formatNumber(analytics.declinedPosts) }} declined
        </div>
      </div>
    </div>

    <!-- System Health -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border dark:border-gray-700 p-6">
      <div class="text-center">
        <div class="text-3xl font-bold mb-2" :class="systemHealthColor">
          {{ systemHealthStatus }}
        </div>
        <p class="text-sm text-gray-500 dark:text-gray-400">System Status</p>
        <div class="mt-2 text-xs text-gray-400">
          {{ formatNumber(analytics.pendingActions) }} pending actions
        </div>
      </div>
    </div>

    <!-- Last Updated -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border dark:border-gray-700 p-6">
      <div class="text-center">
        <div class="text-sm font-medium text-gray-900 dark:text-white mb-2">
          Last Updated
        </div>
        <p class="text-xs text-gray-500 dark:text-gray-400">
          {{ formatDateTime(lastUpdated) }}
        </p>
        <button 
          @click="$emit('refresh')" 
          :disabled="loading"
          class="mt-2 text-xs text-blue-600 dark:text-blue-400 hover:underline disabled:opacity-50"
        >
          <span v-if="loading">Refreshing...</span>
          <span v-else>Refresh Now</span>
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
  switch (status) {
    case 'Excellent': return 'text-green-600 dark:text-green-400'
    case 'Good': return 'text-blue-600 dark:text-blue-400'
    case 'Fair': return 'text-yellow-600 dark:text-yellow-400'
    case 'Needs Attention': return 'text-red-600 dark:text-red-400'
    default: return 'text-gray-600 dark:text-gray-400'
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