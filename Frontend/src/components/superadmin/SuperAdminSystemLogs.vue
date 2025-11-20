<template>
  <div :class="['rounded-lg shadow-sm border', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
    <!-- Header -->
    <div :class="['p-6 border-b', themeStore.isAdminDark() ? 'border-gray-700' : 'border-gray-200']">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-purple-900' : 'bg-purple-100']">
            <FileText :class="['w-6 h-6', themeStore.isAdminDark() ? 'text-purple-400' : 'text-purple-600']" />
          </div>
          <div>
            <h3 :class="['text-lg font-semibold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
              Recent System Logs
            </h3>
            <p :class="['text-sm', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
              Latest system events and activities
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
          Loading logs...
        </p>
      </div>

      <!-- Empty State -->
      <div v-else-if="logs.length === 0" class="text-center py-8">
        <Inbox :class="['w-12 h-12 mx-auto mb-3', themeStore.isAdminDark() ? 'text-gray-600' : 'text-gray-400']" />
        <p :class="['text-sm', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
          No system logs available
        </p>
      </div>

      <!-- Logs List -->
      <div v-else class="space-y-2 max-h-96 overflow-y-auto">
        <div
          v-for="log in logs"
          :key="log.id"
          :class="[
            'flex items-start space-x-3 p-3 rounded-lg text-sm',
            themeStore.isAdminDark() ? 'hover:bg-gray-900' : 'hover:bg-gray-50'
          ]"
        >
          <!-- Icon -->
          <div :class="[
            'flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center',
            getLogColor(log.level).bg
          ]">
            <component :is="getLogIcon(log.level)" :class="['w-3 h-3', getLogColor(log.level).text]" />
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between gap-2">
              <div class="flex-1">
                <p :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
                  {{ log.action }}
                </p>
                <p :class="['text-xs mt-1', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
                  {{ log.message }}
                </p>
              </div>
              <span :class="['text-xs whitespace-nowrap', themeStore.isAdminDark() ? 'text-gray-500' : 'text-gray-500']">
                {{ formatRelativeTime(log.timestamp) }}
              </span>
            </div>
            <div v-if="log.user" class="flex items-center mt-1 text-xs">
              <User :class="['w-3 h-3 mr-1', themeStore.isAdminDark() ? 'text-gray-500' : 'text-gray-400']" />
              <span :class="themeStore.isAdminDark() ? 'text-gray-500' : 'text-gray-500'">
                {{ log.user }}
              </span>
            </div>
          </div>
        </div>
      </div>

     
    </div>
  </div>
</template>

<script setup>
import { FileText, RefreshCw, Loader, Inbox, User, Info, AlertTriangle, XCircle, CheckCircle, Settings } from 'lucide-vue-next'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

defineProps({
  logs: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['refresh', 'view-all'])

const getLogIcon = (level) => {
  switch (level?.toLowerCase()) {
    case 'info':
      return Info
    case 'warning':
      return AlertTriangle
    case 'error':
      return XCircle
    case 'success':
      return CheckCircle
    default:
      return Settings
  }
}

const getLogColor = (level) => {
  const isDark = themeStore.isAdminDark()
  switch (level?.toLowerCase()) {
    case 'info':
      return {
        bg: isDark ? 'bg-blue-900/30' : 'bg-blue-100',
        text: isDark ? 'text-blue-400' : 'text-blue-600'
      }
    case 'warning':
      return {
        bg: isDark ? 'bg-yellow-900/30' : 'bg-yellow-100',
        text: isDark ? 'text-yellow-400' : 'text-yellow-600'
      }
    case 'error':
      return {
        bg: isDark ? 'bg-red-900/30' : 'bg-red-100',
        text: isDark ? 'text-red-400' : 'text-red-600'
      }
    case 'success':
      return {
        bg: isDark ? 'bg-green-900/30' : 'bg-green-100',
        text: isDark ? 'text-green-400' : 'text-green-600'
      }
    default:
      return {
        bg: isDark ? 'bg-gray-700' : 'bg-gray-200',
        text: isDark ? 'text-gray-400' : 'text-gray-600'
      }
  }
}

const formatRelativeTime = (timestamp) => {
  if (!timestamp) return 'Unknown'
  
  try {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    
    return date.toLocaleDateString()
  } catch {
    return 'Invalid date'
  }
}
</script>
