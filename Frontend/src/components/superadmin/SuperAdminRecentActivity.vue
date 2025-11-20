<template>
  <div :class="['rounded-lg shadow-sm border', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
    <!-- Header -->
    <div :class="['p-6 border-b', themeStore.isAdminDark() ? 'border-gray-700' : 'border-gray-200']">
      <div class="flex items-center space-x-3">
        <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-orange-900' : 'bg-orange-100']">
          <Activity :class="['w-6 h-6', themeStore.isAdminDark() ? 'text-orange-400' : 'text-orange-600']" />
        </div>
        <div>
          <h3 :class="['text-lg font-semibold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
            Recent Activity
          </h3>
          <p :class="['text-sm', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
            Latest survey operations
          </p>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="p-6">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-8">
        <Loader class="w-8 h-8 mx-auto animate-spin text-orange-600" />
        <p :class="['mt-2 text-sm', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
          Loading activity...
        </p>
      </div>

      <!-- Empty State -->
      <div v-else-if="activities.length === 0" class="text-center py-8">
        <Inbox :class="['w-12 h-12 mx-auto mb-3', themeStore.isAdminDark() ? 'text-gray-600' : 'text-gray-400']" />
        <p :class="['text-sm', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
          No recent activity
        </p>
      </div>

      <!-- Activity List -->
      <div v-else class="space-y-3">
        <div
          v-for="activity in activities"
          :key="activity.id"
          :class="[
            'flex items-start space-x-3 p-3 rounded-lg',
            themeStore.isAdminDark() ? 'hover:bg-gray-900' : 'hover:bg-gray-50'
          ]"
        >
          <!-- Icon -->
          <div :class="[
            'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
            getActionColor(activity.action)
          ]">
            <component :is="getActionIcon(activity.action)" class="w-4 h-4" />
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0">
            <p :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
              {{ activity.action }} Survey
            </p>
            <p :class="['text-sm truncate', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
              {{ activity.title }}
            </p>
            <p :class="['text-xs mt-1', themeStore.isAdminDark() ? 'text-gray-500' : 'text-gray-500']">
              {{ formatRelativeTime(activity.timestamp) }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Activity, Loader, Inbox, FileText, CheckCircle, XCircle, FilePlus } from 'lucide-vue-next'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

defineProps({
  activities: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const getActionIcon = (action) => {
  switch (action.toLowerCase()) {
    case 'created':
      return FilePlus
    case 'published':
      return CheckCircle
    case 'closed':
      return XCircle
    default:
      return FileText
  }
}

const getActionColor = (action) => {
  const isDark = themeStore.isAdminDark()
  switch (action.toLowerCase()) {
    case 'created':
      return isDark ? 'bg-blue-900 text-blue-400' : 'bg-blue-100 text-blue-600'
    case 'published':
      return isDark ? 'bg-green-900 text-green-400' : 'bg-green-100 text-green-600'
    case 'closed':
      return isDark ? 'bg-gray-700 text-gray-400' : 'bg-gray-200 text-gray-600'
    default:
      return isDark ? 'bg-orange-900 text-orange-400' : 'bg-orange-100 text-orange-600'
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
    if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`
    if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`
    if (diffDays < 7) return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`
    
    return date.toLocaleDateString()
  } catch {
    return 'Invalid date'
  }
}
</script>
