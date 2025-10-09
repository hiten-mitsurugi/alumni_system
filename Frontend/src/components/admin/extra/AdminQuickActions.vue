<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border dark:border-gray-700">
    <!-- Header -->
    <div class="p-6 border-b dark:border-gray-700">
      <div class="flex items-center space-x-3">
        <div class="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
          <Zap class="w-6 h-6 text-blue-600 dark:text-blue-400" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            Quick Actions
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            Shortcuts to common admin tasks
          </p>
        </div>
      </div>
    </div>

    <!-- Navigation Actions -->
    <div class="p-6">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

        <!-- User Management -->
        <router-link 
          to="/admin/user-management"
          class="group block p-4 rounded-xl border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-blue-500 dark:hover:border-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all duration-200"
        >
          <div class="flex items-center space-x-3">
            <div class="p-3 bg-blue-100 dark:bg-blue-900 rounded-lg group-hover:bg-blue-200 dark:group-hover:bg-blue-800 transition-colors">
              <Users class="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p class="text-sm font-semibold text-gray-900 dark:text-white group-hover:text-blue-700 dark:group-hover:text-blue-300">
                Manage Users
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                User accounts & permissions
              </p>
            </div>
          </div>
        </router-link>

        <!-- Post Management -->
        <router-link 
          to="/admin/contents"
          class="group block p-4 rounded-xl border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-green-500 dark:hover:border-green-400 hover:bg-green-50 dark:hover:bg-green-900/20 transition-all duration-200"
        >
          <div class="flex items-center space-x-3">
            <div class="p-3 bg-green-100 dark:bg-green-900 rounded-lg group-hover:bg-green-200 dark:group-hover:bg-green-800 transition-colors">
              <FileText class="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p class="text-sm font-semibold text-gray-900 dark:text-white group-hover:text-green-700 dark:group-hover:text-green-300">
                Manage Posts
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                Content moderation & approval
              </p>
            </div>
          </div>
        </router-link>

        <!-- Reports Management -->
        <router-link 
          to="/admin/post-reports"
          class="group block p-4 rounded-xl border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-red-500 dark:hover:border-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all duration-200"
        >
          <div class="flex items-center space-x-3">
            <div class="p-3 bg-red-100 dark:bg-red-900 rounded-lg group-hover:bg-red-200 dark:group-hover:bg-red-800 transition-colors">
              <Shield class="w-5 h-5 text-red-600 dark:text-red-400" />
            </div>
            <div>
              <p class="text-sm font-semibold text-gray-900 dark:text-white group-hover:text-red-700 dark:group-hover:text-red-300">
                View Reports
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                Content reports & violations
              </p>
            </div>
          </div>
        </router-link>

        <!-- System Refresh -->
        <button 
          @click="$emit('refresh-analytics')"
          :disabled="loading"
          class="group block p-4 rounded-xl border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-purple-500 dark:hover:border-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-all duration-200 disabled:opacity-50"
        >
          <div class="flex items-center space-x-3">
            <div class="p-3 bg-purple-100 dark:bg-purple-900 rounded-lg group-hover:bg-purple-200 dark:group-hover:bg-purple-800 transition-colors">
              <RefreshCw class="w-5 h-5 text-purple-600 dark:text-purple-400" :class="{ 'animate-spin': loading }" />
            </div>
            <div>
              <p class="text-sm font-semibold text-gray-900 dark:text-white group-hover:text-purple-700 dark:group-hover:text-purple-300">
                Refresh Data
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                Update dashboard analytics
              </p>
            </div>
          </div>
        </button>
      </div>

      <!-- System Status -->
      <div class="mt-6 p-4 bg-gray-50 dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="flex-shrink-0">
              <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-900 dark:text-white">
                System Online
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                Last updated: {{ formatDateTime(lastUpdated) }}
              </p>
            </div>
          </div>
          <button 
            @click="$emit('refresh')"
            :disabled="loading"
            class="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 disabled:opacity-50 transition-colors"
            title="Refresh system status"
          >
            <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': loading }" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { 
  Zap, Users, FileText, Shield, RefreshCw 
} from 'lucide-vue-next'

// Props
const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  },
  lastUpdated: {
    type: Date,
    default: null
  }
})

// Emits
const emit = defineEmits([
  'refresh', 'refresh-analytics'
])

// Methods
const formatDateTime = (date) => {
  if (!date) return 'Never'
  try {
    return new Date(date).toLocaleString()
  } catch {
    return 'Invalid Date'
  }
}
</script>