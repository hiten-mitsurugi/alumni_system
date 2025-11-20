<template>
  <div class="super-admin-dashboard">
    <!-- Dashboard Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
      <div>
        <h1 :class="['text-2xl font-bold mb-2', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
          SuperAdmin Dashboard
        </h1>
        <p :class="['text-sm', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
          Survey system overview and management
        </p>
      </div>
      <div class="flex items-center space-x-3 mt-4 sm:mt-0">
        <div v-if="analyticsLastUpdated" :class="['text-xs', themeStore.isAdminDark() ? 'text-gray-500' : 'text-gray-500']">
          Updated: {{ formatUpdateTime(analyticsLastUpdated) }}
        </div>
        <button
          @click="refreshAllData"
          :disabled="analyticsLoading || dashboardLoading"
          :class="[
            'inline-flex items-center px-4 py-2 border-2 shadow-sm text-sm leading-4 font-semibold rounded-lg disabled:opacity-50 transition-all',
            themeStore.isAdminDark() 
              ? 'border-orange-600 text-orange-400 bg-orange-900/20 hover:bg-orange-900/40' 
              : 'border-orange-600 text-orange-600 bg-orange-50 hover:bg-orange-100'
          ]"
        >
          <RefreshCw 
            class="w-4 h-4 mr-2" 
            :class="{ 'animate-spin': analyticsLoading || dashboardLoading }" 
          />
          Refresh Data
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
    <SuperAdminAnalyticsCards
      :analytics="analytics"
      :last-updated="analyticsLastUpdated"
      :loading="analyticsLoading"
      @refresh="refreshAnalytics"
    />

    <!-- Pending Approvals (Prominent Section) -->
    <div class="mb-6">
      <SuperAdminPendingApprovals
        :pending-users="pendingApprovals"
        :loading="dashboardLoading"
        @approve-user="handleApproveUser"
        @reject-user="handleRejectUser"
        @refresh="refreshDashboardData"
      />
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- System Status -->
      <div>
        <SuperAdminSystemStatus
          :status="systemStatus"
          :uptime="systemUptime"
          :last-updated="analyticsLastUpdated"
          :loading="dashboardLoading"
          @refresh="refreshDashboardData"
        />
      </div>

      <!-- Quick Actions -->
      <div>
        <SuperAdminQuickActions
          :loading="dashboardLoading"
          :last-updated="analyticsLastUpdated"
          @refresh="refreshDashboardData"
        />
      </div>
    </div>

    <!-- Second Row Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- System Logs -->
      <div>
        <SuperAdminSystemLogs
          :logs="systemLogs"
          :loading="dashboardLoading"
          @refresh="refreshDashboardData"
          @view-all="handleViewAllLogs"
        />
      </div>

      <!-- Recent Activity -->
      <div>
        <SuperAdminRecentActivity
          :activities="recentActivity"
          :loading="dashboardLoading"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { RefreshCw, AlertCircle } from 'lucide-vue-next'
import { useThemeStore } from '@/stores/theme'

// Import modular components
import SuperAdminAnalyticsCards from '@/components/superadmin/SuperAdminAnalyticsCards.vue'
import SuperAdminPendingApprovals from '@/components/superadmin/SuperAdminPendingApprovals.vue'
import SuperAdminRecentActivity from '@/components/superadmin/SuperAdminRecentActivity.vue'
import SuperAdminQuickActions from '@/components/superadmin/SuperAdminQuickActions.vue'
import SuperAdminSystemStatus from '@/components/superadmin/SuperAdminSystemStatus.vue'
import SuperAdminSystemLogs from '@/components/superadmin/SuperAdminSystemLogs.vue'

// Import composables
import { useSuperAdminAnalytics } from '@/composables/useSuperAdminAnalytics'
import { useSuperAdminDashboard } from '@/composables/useSuperAdminDashboard'

// Theme store
const themeStore = useThemeStore()

// Analytics composable
const {
  loading: analyticsLoading,
  error: analyticsError,
  lastUpdated: analyticsLastUpdated,
  analytics,
  fetchAnalytics,
  startAutoRefresh,
  stopAutoRefresh
} = useSuperAdminAnalytics()

// Dashboard composable
const {
  loading: dashboardLoading,
  error: dashboardError,
  pendingApprovals,
  recentActivity,
  systemStatus,
  systemUptime,
  systemLogs,
  fetchAllData,
  approveUser,
  rejectUser
} = useSuperAdminDashboard()

// Methods
const refreshAnalytics = async () => {
  console.log('SuperAdmin Debug: Refreshing analytics...')
  await fetchAnalytics()
}

const refreshDashboardData = async () => {
  console.log('SuperAdmin Debug: Refreshing dashboard data...')
  await fetchAllData()
}

const refreshAllData = async () => {
  console.log('SuperAdmin Debug: Refreshing all data...')
  await Promise.all([
    refreshAnalytics(),
    refreshDashboardData()
  ])
}

// Action handlers
const handleApproveUser = async (userId) => {
  console.log('SuperAdmin Debug: Approving user', userId)
  const result = await approveUser(userId)
  if (!result.success) {
    console.error('Failed to approve user:', result.error)
  }
}

const handleRejectUser = async (userId) => {
  console.log('SuperAdmin Debug: Rejecting user', userId)
  const result = await rejectUser(userId)
  if (!result.success) {
    console.error('Failed to reject user:', result.error)
  }
}

const handleViewAllLogs = () => {
  console.log('SuperAdmin Debug: View all logs clicked')
  // Navigate to logs page or show modal
}

const formatUpdateTime = (date) => {
  if (!date) return 'Never'
  try {
    const now = new Date()
    const diff = Math.floor((now - new Date(date)) / 1000)
    
    if (diff < 60) return `${diff}s ago`
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
    return new Date(date).toLocaleTimeString()
  } catch {
    return 'Unknown'
  }
}

// Lifecycle
onMounted(async () => {
  console.log('SuperAdmin Debug: Component mounted, initializing...')
  
  // Load initial data
  await refreshAllData()
  
  // Start auto-refresh for analytics (every 30 seconds)
  startAutoRefresh(30000)
})

onUnmounted(() => {
  console.log('SuperAdmin Debug: Component unmounting, cleaning up...')
  stopAutoRefresh()
})
</script>
