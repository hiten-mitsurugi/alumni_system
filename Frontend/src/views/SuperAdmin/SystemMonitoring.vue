<!-- eslint-disable vue/multi-word-component-names -->
<script setup>
import { ref, onMounted, computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { dashboardService } from '@/services/dashboardService'

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isAdminDark?.() || false)

const loading = ref(true)
const overview = ref(null)
const alerts = ref([])

async function load() {
  loading.value = true
  try {
    console.log('SystemMonitoring: Loading dashboard overview...')
    // get the overview which contains systemMonitoring and recentActivity in the mock service
    const data = await dashboardService.getDashboardOverview()
    console.log('SystemMonitoring: Data loaded:', data)
    overview.value = data
    alerts.value = data.alerts || []
    console.log('SystemMonitoring: Component ready with data')
  } catch (e) {
    console.error('Failed loading system monitoring data', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  console.log('SystemMonitoring: Component mounted, starting data load...')
  load()
})
</script>

<template>
  <div>
    <div :class="[ 'mb-6', isDark ? 'text-white' : 'text-gray-900' ]">
      <h1 class="text-2xl font-bold">System Monitoring</h1>
      <p class="text-sm text-gray-500" v-if="!isDark">Overview of system health and recent activity</p>
      <p class="text-sm text-gray-300" v-else>Overview of system health and recent activity</p>
    </div>

    <div v-if="loading" class="py-12 text-center text-gray-500">Loading system data...</div>

    <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- Left column: key cards -->
        <div class="md:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div :class="['rounded-lg p-4 border', isDark ? 'bg-gray-800 border-gray-700 text-white' : 'bg-white border-gray-200 text-gray-900']">
          <p class="text-sm">Uptime</p>
          <div class="flex items-baseline justify-between">
            <h2 class="text-2xl font-semibold">{{ overview?.systemMonitoring?.uptime ?? overview?.uptime ?? '--' }}%</h2>
            <p :class="['text-sm', overview?.systemMonitoring?.status === 'online' ? 'text-green-500' : 'text-red-500']">{{ overview?.systemMonitoring?.status ?? 'unknown' }}</p>
          </div>
          <p class="text-xs text-gray-400 mt-2">Last backup: {{ overview?.systemMonitoring?.lastBackup ?? 'N/A' }}</p>
        </div>        <div :class="['rounded-lg p-4 border', isDark ? 'bg-gray-800 border-gray-700 text-white' : 'bg-white border-gray-200 text-gray-900']">
          <p class="text-sm">Storage Used</p>
          <h2 class="text-2xl font-semibold">{{ overview?.systemMonitoring?.storageUsed ?? overview?.storageUsed ?? 0 }}%</h2>
          <div class="w-full bg-gray-200 h-2 rounded mt-2 overflow-hidden">
            <div :style="{ width: (overview?.systemMonitoring?.storageUsed || 0) + '%'}" :class="['h-2', isDark ? 'bg-green-500' : 'bg-green-600']"></div>
          </div>
          <p class="text-xs text-gray-400 mt-2">Backup status: {{ overview?.systemMonitoring?.backupStatus ?? 'unknown' }}</p>
        </div>

        <div :class="['rounded-lg p-4 border', isDark ? 'bg-gray-800 border-gray-700 text-white' : 'bg-white border-gray-200 text-gray-900']">
          <p class="text-sm">Active Sessions</p>
          <h2 class="text-2xl font-semibold">{{ overview?.systemMonitoring?.activeSessions ?? overview?.activeSessions ?? 0 }}</h2>
          <p class="text-xs text-gray-400 mt-2">Peak hour: {{ overview?.quickStats?.peakHour ?? 'N/A' }}</p>
        </div>

        <div :class="['rounded-lg p-4 border', isDark ? 'bg-gray-800 border-gray-700 text-white' : 'bg-white border-gray-200 text-gray-900']">
          <p class="text-sm">Pending Approvals</p>
          <h2 class="text-2xl font-semibold">{{ overview?.pendingApprovals?.total ?? overview?.pendingApprovals ?? 0 }}</h2>
          <p class="text-xs text-gray-400 mt-2">Oldest: {{ overview?.pendingApprovals?.oldestDays ?? 'N/A' }} days</p>
        </div>
      </div>

      <!-- Right column: db/redis/alerts -->
      <div class="space-y-4">
        <div :class="['rounded-lg p-4 border', isDark ? 'bg-gray-800 border-gray-700 text-white' : 'bg-white border-gray-200 text-gray-900']">
          <p class="text-sm font-medium">Database & Cache</p>
          <div class="mt-3 grid grid-cols-2 gap-3">
            <div>
              <p class="text-xs text-gray-400">Postgres</p>
              <p class="font-semibold">Healthy</p>
            </div>
            <div>
              <p class="text-xs text-gray-400">Redis</p>
              <p class="font-semibold">Healthy</p>
            </div>
            <div>
              <p class="text-xs text-gray-400">Celery</p>
              <p class="font-semibold">Running</p>
            </div>
            <div>
              <p class="text-xs text-gray-400">Channels</p>
              <p class="font-semibold">{{ overview?.messaging?.connections ?? 'n/a' }}</p>
            </div>
          </div>
        </div>

        <div :class="['rounded-lg p-4 border', isDark ? 'bg-gray-800 border-gray-700 text-white' : 'bg-white border-gray-200 text-gray-900']">
          <p class="text-sm font-medium">Recent Alerts</p>
          <ul class="mt-2 space-y-2">
            <li v-for="a in alerts" :key="a.id" :class="['p-2 rounded', a.priority === 'critical' ? 'bg-red-100 text-red-800' : a.priority === 'warning' ? 'bg-yellow-50 text-yellow-800' : 'bg-gray-50 text-gray-800']">
              <div class="flex justify-between items-start">
                <div>
                  <p class="text-sm font-semibold">{{ a.message }}</p>
                  <p class="text-xs text-gray-500">Source: {{ a.source }}</p>
                </div>
                <div>
                  <button class="text-xs underline" @click.prevent="() => console.log('handle', a.id)">Action</button>
                </div>
              </div>
            </li>
            <li v-if="alerts.length === 0" class="text-sm text-gray-400">No alerts</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Recent activity -->
    <div class="mt-6">
      <h3 class="text-lg font-semibold mb-3">Recent Activity</h3>
      <div :class="['rounded-lg p-4 border', isDark ? 'bg-gray-800 border-gray-700 text-white' : 'bg-white border-gray-200 text-gray-900']">
        <ul class="space-y-3">
          <li v-for="act in overview?.recentActivity || []" :key="act.id" class="flex items-start gap-3">
            <div :class="['w-8 h-8 rounded flex items-center justify-center', isDark ? 'bg-gray-700' : 'bg-gray-100']">
              <span class="text-sm">✓</span>
            </div>
            <div>
              <p class="text-sm font-medium">{{ act.description }}</p>
              <p class="text-xs text-gray-400">{{ act.timestamp }}</p>
            </div>
          </li>
          <li v-if="(overview?.recentActivity || []).length === 0" class="text-sm text-gray-400">No recent activity</li>
        </ul>
      </div>
    </div>
  </div>
</template>
