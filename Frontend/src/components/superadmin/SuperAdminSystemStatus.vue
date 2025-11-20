<template>
  <div :class="['rounded-lg shadow-sm border', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
    <!-- Header -->
    <div :class="['p-6 border-b', themeStore.isAdminDark() ? 'border-gray-700' : 'border-gray-200']">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-green-900' : 'bg-green-100']">
            <Activity :class="['w-6 h-6', themeStore.isAdminDark() ? 'text-green-400' : 'text-green-600']" />
          </div>
          <div>
            <h3 :class="['text-lg font-semibold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
              System Status
            </h3>
            <p :class="['text-sm', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
              Real-time system health
            </p>
          </div>
        </div>
        <button
          @click="$emit('refresh')"
          :disabled="loading"
          :class="[
            'text-sm transition-colors disabled:opacity-50',
            themeStore.isAdminDark() ? 'text-orange-400 hover:text-orange-300' : 'text-orange-600 hover:text-orange-700'
          ]"
        >
          <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': loading }" />
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="p-6">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-8">
        <Loader class="w-8 h-8 mx-auto animate-spin text-orange-600" />
        <p :class="['mt-2 text-sm', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
          Checking system status...
        </p>
      </div>

      <!-- Status Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Overall Health -->
        <div :class="['p-4 rounded-lg border', themeStore.isAdminDark() ? 'bg-gray-900 border-gray-700' : 'bg-gray-50 border-gray-200']">
          <div class="flex items-center justify-between">
            <div>
              <p :class="['text-xs font-medium mb-1', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
                Overall Health
              </p>
              <p :class="['text-lg font-bold', systemHealth.color]">
                {{ systemHealth.status }}
              </p>
            </div>
            <div :class="['p-3 rounded-full', systemHealth.bgColor]">
              <component :is="systemHealth.icon" :class="['w-5 h-5', systemHealth.color]" />
            </div>
          </div>
        </div>

        <!-- Database -->
        <div :class="['p-4 rounded-lg border', themeStore.isAdminDark() ? 'bg-gray-900 border-gray-700' : 'bg-gray-50 border-gray-200']">
          <div class="flex items-center justify-between">
            <div>
              <p :class="['text-xs font-medium mb-1', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
                Database
              </p>
              <p :class="['text-lg font-bold', status.database ? 'text-green-600' : 'text-red-600']">
                {{ status.database ? 'Connected' : 'Disconnected' }}
              </p>
            </div>
            <div :class="['w-3 h-3 rounded-full', status.database ? 'bg-green-500 animate-pulse' : 'bg-red-500']"></div>
          </div>
        </div>

        <!-- Server -->
        <div :class="['p-4 rounded-lg border', themeStore.isAdminDark() ? 'bg-gray-900 border-gray-700' : 'bg-gray-50 border-gray-200']">
          <div class="flex items-center justify-between">
            <div>
              <p :class="['text-xs font-medium mb-1', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
                Server Status
              </p>
              <p :class="['text-lg font-bold', status.server ? 'text-green-600' : 'text-red-600']">
                {{ status.server ? 'Running' : 'Down' }}
              </p>
            </div>
            <div :class="['w-3 h-3 rounded-full', status.server ? 'bg-green-500 animate-pulse' : 'bg-red-500']"></div>
          </div>
        </div>

        <!-- API Services -->
        <div :class="['p-4 rounded-lg border', themeStore.isAdminDark() ? 'bg-gray-900 border-gray-700' : 'bg-gray-50 border-gray-200']">
          <div class="flex items-center justify-between">
            <div>
              <p :class="['text-xs font-medium mb-1', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
                API Services
              </p>
              <p :class="['text-lg font-bold', status.api ? 'text-green-600' : 'text-red-600']">
                {{ status.api ? 'Operational' : 'Error' }}
              </p>
            </div>
            <div :class="['w-3 h-3 rounded-full', status.api ? 'bg-green-500 animate-pulse' : 'bg-red-500']"></div>
          </div>
        </div>
      </div>

      <!-- Uptime -->
      <div :class="['mt-4 p-4 rounded-lg', themeStore.isAdminDark() ? 'bg-gray-900' : 'bg-gray-50']">
        <div class="flex items-center justify-between">
          <div>
            <p :class="['text-xs font-medium', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
              System Uptime
            </p>
            <p :class="['text-sm font-semibold mt-1', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
              {{ formatUptime(uptime) }}
            </p>
          </div>
          <div>
            <p :class="['text-xs font-medium text-right', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
              Last Check
            </p>
            <p :class="['text-sm font-semibold mt-1', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
              {{ formatRelativeTime(lastUpdated) }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Activity, RefreshCw, Loader, CheckCircle, AlertTriangle, XCircle } from 'lucide-vue-next'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

const props = defineProps({
  status: {
    type: Object,
    default: () => ({
      database: true,
      server: true,
      api: true
    })
  },
  uptime: {
    type: Number,
    default: 0 // in seconds
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

const systemHealth = computed(() => {
  const { database, server, api } = props.status
  
  if (database && server && api) {
    return {
      status: 'Healthy',
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900/30',
      icon: CheckCircle
    }
  } else if (database || server || api) {
    return {
      status: 'Degraded',
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100 dark:bg-yellow-900/30',
      icon: AlertTriangle
    }
  } else {
    return {
      status: 'Critical',
      color: 'text-red-600',
      bgColor: 'bg-red-100 dark:bg-red-900/30',
      icon: XCircle
    }
  }
})

const formatUptime = (seconds) => {
  if (!seconds) return 'Starting...'
  
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (days > 0) return `${days}d ${hours}h ${minutes}m`
  if (hours > 0) return `${hours}h ${minutes}m`
  return `${minutes}m`
}

const formatRelativeTime = (date) => {
  if (!date) return 'Never'
  
  try {
    const now = new Date()
    const diff = Math.floor((now - new Date(date)) / 1000)
    
    if (diff < 60) return 'Just now'
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
    return new Date(date).toLocaleDateString()
  } catch {
    return 'Unknown'
  }
}
</script>
