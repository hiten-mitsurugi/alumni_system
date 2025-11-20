<template>
  <div class="admin-dashboard">
    <!-- Dashboard Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
      <div>
        <h1 :class="['text-2xl font-bold mb-2', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
          Admin Dashboard
        </h1>
        <p :class="['text-sm', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
          Welcome back! Here's what's happening with your alumni system.
        </p>
      </div>
      <div class="flex items-center space-x-3 mt-4 sm:mt-0">
        <button
          @click="refreshAllData"
          :disabled="analyticsLoading || dashboardLoading"
          :class="[
            'inline-flex items-center px-3 py-2 border shadow-sm text-sm leading-4 font-medium rounded-md disabled:opacity-50',
            themeStore.isAdminDark() 
              ? 'border-gray-600 text-gray-300 bg-gray-800 hover:bg-gray-700' 
              : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
          ]"
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
      :class="[
        'mb-6 p-4 border rounded-lg',
        themeStore.isAdminDark() 
          ? 'bg-red-900/20 border-red-800' 
          : 'bg-red-50 border-red-200'
      ]"
    >
      <div class="flex">
        <AlertCircle class="w-5 h-5 text-red-400 mr-2 mt-0.5" />
        <div>
          <h3 :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-red-200' : 'text-red-800']">
            Dashboard Error
          </h3>
          <div :class="['mt-1 text-sm', themeStore.isAdminDark() ? 'text-red-300' : 'text-red-700']">
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

    <!-- Quick Actions -->
    <div class="max-w-2xl">
      <AdminQuickActions
        :loading="dashboardLoading"
        :last-updated="analyticsLastUpdated"
        @refresh="refreshDashboardData"
        @refresh-analytics="refreshAnalytics"
      />
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
  pendingApprovals,
  fetchAllRecentData,
  approveUser,
  rejectUser
} = useAdminDashboard()

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
