<template>
  <div class="admin-dashboard">
    <!-- Dashboard Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Admin Dashboard
        </h1>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Welcome back! Here's what's happening with your alumni system.
        </p>
      </div>
      <div class="flex items-center space-x-3 mt-4 sm:mt-0">
        <button
          @click="refreshAllData"
          :disabled="analyticsLoading || dashboardLoading"
          class="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
        >
          <RefreshCw 
            class="w-4 h-4 mr-2" 
            :class="{ 'animate-spin': analyticsLoading || dashboardLoading }" 
          />
          Refresh
        </button>
      </div>
    </div>

    <!-- Error Display -->
    <div 
      v-if="analyticsError || dashboardError" 
      class="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
    >
      <div class="flex">
        <AlertCircle class="w-5 h-5 text-red-400 mr-2 mt-0.5" />
        <div>
          <h3 class="text-sm font-medium text-red-800 dark:text-red-200">
            Dashboard Error
          </h3>
          <div class="mt-1 text-sm text-red-700 dark:text-red-300">
            <p v-if="analyticsError">Analytics: {{ analyticsError }}</p>
            <p v-if="dashboardError">Dashboard: {{ dashboardError }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Analytics Cards -->
    <AdminAnalyticsCards
      :analytics="analytics"
      :activity-rate="activityRate"
      :approval-rate="approvalRate"
      :last-updated="analyticsLastUpdated"
      :loading="analyticsLoading"
      @refresh="refreshAnalytics"
    />

    <!-- Pending Approvals (Prominent Section) -->
    <div class="mb-6">
      <AdminPendingApprovals
        :pending-users="pendingApprovals"
        :loading="dashboardLoading"
        @approve-user="handleApproveUser"
        @reject-user="handleRejectUser"
        @refresh="refreshDashboardData"
      />
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Recent Posts -->
      <div>
        <AdminRecentPosts
          :posts="recentPosts"
          :loading="dashboardLoading"
          :error="dashboardError"
          @refresh="refreshDashboardData"
          @approve-post="handleApprovePost"
          @reject-post="handleRejectPost"
          @view-post="handleViewPost"
          @delete-post="handleDeletePost"
        />
      </div>

      <!-- Quick Actions -->
      <div>
        <AdminQuickActions
          :loading="dashboardLoading"
          :last-updated="analyticsLastUpdated"
          @refresh="refreshDashboardData"
          @refresh-analytics="refreshAnalytics"
        />
      </div>
    </div>

    <!-- Debug Information (Development Only) -->
    <div 
      v-if="showDebugInfo" 
      class="mt-8 p-4 rounded-lg text-xs border border-gray-300 dark:border-gray-700"
      style="background: linear-gradient(90deg, #f3f4f6 0%, #e5e7eb 100%); color: #222;"
      :class="'dark:bg-gray-900 dark:text-gray-100'"
    >
      <h4 class="font-semibold mb-2 text-blue-700 dark:text-blue-300">Debug Information:</h4>
      <ul class="space-y-1">
        <li><span class="font-semibold">Analytics Loading:</span> <span>{{ analyticsLoading }}</span></li>
        <li><span class="font-semibold">Dashboard Loading:</span> <span>{{ dashboardLoading }}</span></li>
        <li><span class="font-semibold">Analytics Error:</span> <span>{{ analyticsError }}</span></li>
        <li><span class="font-semibold">Dashboard Error:</span> <span>{{ dashboardError }}</span></li>
        <li><span class="font-semibold">Last Updated:</span> <span>{{ analyticsLastUpdated }}</span></li>
        <li><span class="font-semibold">Recent Posts Count:</span> <span>{{ recentPosts.length }}</span></li>
        <li><span class="font-semibold">Pending Users Count:</span> <span>{{ pendingApprovals.length }}</span></li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { RefreshCw, AlertCircle } from 'lucide-vue-next'
import { useThemeStore } from '@/stores/theme'

// Import modular components
import AdminAnalyticsCards from '@/components/admin/AdminAnalyticsCards.vue'
import AdminPendingApprovals from '@/components/admin/AdminPendingApprovals.vue'
import AdminRecentPosts from '@/components/admin/AdminRecentPosts.vue'
import AdminQuickActions from '@/components/admin/AdminQuickActions.vue'

// Import composables
import { useAdminAnalytics } from '@/composables/useAdminAnalytics'
import { useAdminDashboard } from '@/composables/useAdminDashboard'

// Theme store
const themeStore = useThemeStore()

// Analytics composable
const {
  loading: analyticsLoading,
  error: analyticsError,
  lastUpdated: analyticsLastUpdated,
  analytics,
  activityRate,
  approvalRate,
  fetchAnalytics,
  startAutoRefresh,
  stopAutoRefresh
} = useAdminAnalytics()

// Dashboard composable
const {
  loading: dashboardLoading,
  error: dashboardError,
  recentPosts,
  pendingApprovals,
  fetchAllRecentData,
  approveUser,
  rejectUser,
  approvePost,
  rejectPost,
  deletePost
} = useAdminDashboard()

// Debug mode (show in development)
const showDebugInfo = computed(() => {
  return import.meta.env.MODE === 'development'
})

// Methods
const refreshAnalytics = async () => {
  console.log('Dashboard Debug: Refreshing analytics...')
  await fetchAnalytics()
}

const refreshDashboardData = async () => {
  console.log('Dashboard Debug: Refreshing dashboard data...')
  await fetchAllRecentData()
}

const refreshAllData = async () => {
  console.log('Dashboard Debug: Refreshing all data...')
  await Promise.all([
    refreshAnalytics(),
    refreshDashboardData()
  ])
}

// Action handlers
const handleApproveUser = async (userId) => {
  console.log('Dashboard Debug: Approving user', userId)
  const result = await approveUser(userId)
  if (!result.success) {
    console.error('Failed to approve user:', result.error)
    // Could add toast notification here
  }
}

const handleRejectUser = async (userId) => {
  console.log('Dashboard Debug: Rejecting user', userId)
  const result = await rejectUser(userId)
  if (!result.success) {
    console.error('Failed to reject user:', result.error)
    // Could add toast notification here
  }
}

const handleApprovePost = async (postId) => {
  console.log('Dashboard Debug: Approving post', postId)
  const result = await approvePost(postId)
  if (!result.success) {
    console.error('Failed to approve post:', result.error)
  }
}

const handleRejectPost = async (postId) => {
  console.log('Dashboard Debug: Rejecting post', postId)
  const result = await rejectPost(postId)
  if (!result.success) {
    console.error('Failed to reject post:', result.error)
  }
}

const handleDeletePost = async (postId) => {
  console.log('Dashboard Debug: Deleting post', postId)
  const result = await deletePost(postId)
  if (!result.success) {
    console.error('Failed to delete post:', result.error)
  }
}

const handleViewPost = (post) => {
  console.log('Dashboard Debug: Viewing post', post.id)
  // Could navigate to post detail view
}

// Lifecycle
onMounted(async () => {
  console.log('Dashboard Debug: Component mounted, initializing...')
  
  // Load initial data
  await refreshAllData()
  
  // Start auto-refresh for analytics (every 30 seconds)
  startAutoRefresh(30000)
})

onUnmounted(() => {
  console.log('Dashboard Debug: Component unmounting, cleaning up...')
  stopAutoRefresh()
})
</script>
