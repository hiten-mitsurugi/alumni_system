<template>
  <div :class="['rounded-lg shadow-sm border', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
    <!-- Header -->
    <div :class="['p-6 border-b', themeStore.isAdminDark() ? 'border-gray-700' : 'border-gray-200']">
      <div class="flex items-center space-x-3">
        <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-blue-900' : 'bg-blue-100']">
          <Zap :class="['w-6 h-6', themeStore.isAdminDark() ? 'text-blue-400' : 'text-blue-600']" />
        </div>
        <div>
          <h3 :class="['text-lg font-semibold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
            Quick Actions
          </h3>
          <p :class="['text-sm', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
            Survey management tasks
          </p>
        </div>
      </div>
    </div>

    <!-- Navigation Actions -->
    <div class="p-6">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

        <!-- Survey Management -->
        <router-link 
          to="/super-admin/survey-management"
          :class="[
            'group block p-4 rounded-xl border-2 border-dashed transition-all duration-200',
            themeStore.isAdminDark() 
              ? 'border-gray-600 hover:border-orange-400 hover:bg-orange-900/20' 
              : 'border-gray-300 hover:border-orange-500 hover:bg-orange-50'
          ]"
        >
          <div class="flex items-center space-x-3">
            <div :class="[
              'p-3 rounded-lg transition-colors',
              themeStore.isAdminDark() 
                ? 'bg-orange-900 group-hover:bg-orange-800' 
                : 'bg-orange-100 group-hover:bg-orange-200'
            ]">
              <FileText :class="['w-5 h-5', themeStore.isAdminDark() ? 'text-orange-400' : 'text-orange-600']" />
            </div>
            <div>
              <p :class="[
                'text-sm font-semibold',
                themeStore.isAdminDark() 
                  ? 'text-white group-hover:text-orange-300' 
                  : 'text-gray-900 group-hover:text-orange-700'
              ]">
                Manage Surveys
              </p>
              <p :class="['text-xs', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
                Create, edit & publish
              </p>
            </div>
          </div>
        </router-link>

        <!-- Alumni Directory -->
        <router-link 
          to="/super-admin/alumni-directory"
          :class="[
            'group block p-4 rounded-xl border-2 border-dashed transition-all duration-200',
            themeStore.isAdminDark() 
              ? 'border-gray-600 hover:border-blue-400 hover:bg-blue-900/20' 
              : 'border-gray-300 hover:border-blue-500 hover:bg-blue-50'
          ]"
        >
          <div class="flex items-center space-x-3">
            <div :class="[
              'p-3 rounded-lg transition-colors',
              themeStore.isAdminDark() 
                ? 'bg-blue-900 group-hover:bg-blue-800' 
                : 'bg-blue-100 group-hover:bg-blue-200'
            ]">
              <Users :class="['w-5 h-5', themeStore.isAdminDark() ? 'text-blue-400' : 'text-blue-600']" />
            </div>
            <div>
              <p :class="[
                'text-sm font-semibold',
                themeStore.isAdminDark() 
                  ? 'text-white group-hover:text-blue-300' 
                  : 'text-gray-900 group-hover:text-blue-700'
              ]">
                Alumni Directory
              </p>
              <p :class="['text-xs', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
                View all alumni
              </p>
            </div>
          </div>
        </router-link>

        <!-- User Management -->
        <router-link 
          to="/super-admin/user-management"
          :class="[
            'group block p-4 rounded-xl border-2 border-dashed transition-all duration-200',
            themeStore.isAdminDark() 
              ? 'border-gray-600 hover:border-green-400 hover:bg-green-900/20' 
              : 'border-gray-300 hover:border-green-500 hover:bg-green-50'
          ]"
        >
          <div class="flex items-center space-x-3">
            <div :class="[
              'p-3 rounded-lg transition-colors',
              themeStore.isAdminDark() 
                ? 'bg-green-900 group-hover:bg-green-800' 
                : 'bg-green-100 group-hover:bg-green-200'
            ]">
              <Users :class="['w-5 h-5', themeStore.isAdminDark() ? 'text-green-400' : 'text-green-600']" />
            </div>
            <div>
              <p :class="[
                'text-sm font-semibold',
                themeStore.isAdminDark() 
                  ? 'text-white group-hover:text-green-300' 
                  : 'text-gray-900 group-hover:text-green-700'
              ]">
                Manage Users
              </p>
              <p :class="['text-xs', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
                Alumni approvals
              </p>
            </div>
          </div>
        </router-link>

        <!-- System Refresh -->
        <button 
          @click="$emit('refresh')"
          :disabled="loading"
          :class="[
            'group block p-4 rounded-xl border-2 border-dashed transition-all duration-200 disabled:opacity-50',
            themeStore.isAdminDark() 
              ? 'border-gray-600 hover:border-purple-400 hover:bg-purple-900/20' 
              : 'border-gray-300 hover:border-purple-500 hover:bg-purple-50'
          ]"
        >
          <div class="flex items-center space-x-3">
            <div :class="[
              'p-3 rounded-lg transition-colors',
              themeStore.isAdminDark() 
                ? 'bg-purple-900 group-hover:bg-purple-800' 
                : 'bg-purple-100 group-hover:bg-purple-200'
            ]">
              <RefreshCw :class="['w-5 h-5', themeStore.isAdminDark() ? 'text-purple-400' : 'text-purple-600', { 'animate-spin': loading }]" />
            </div>
            <div>
              <p :class="[
                'text-sm font-semibold',
                themeStore.isAdminDark() 
                  ? 'text-white group-hover:text-purple-300' 
                  : 'text-gray-900 group-hover:text-purple-700'
              ]">
                Refresh Data
              </p>
              <p :class="['text-xs', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
                Update dashboard
              </p>
            </div>
          </div>
        </button>
      </div>

      <!-- System Status -->
      <div :class="[
        'mt-6 p-4 rounded-xl border',
        themeStore.isAdminDark() 
          ? 'bg-gray-900 border-gray-700' 
          : 'bg-gray-50 border-gray-200'
      ]">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="shrink-0">
              <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            </div>
            <div>
              <p :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
                System Online
              </p>
              <p :class="['text-xs', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
                Last updated: {{ formatDateTime(lastUpdated) }}
              </p>
            </div>
          </div>
          <button 
            @click="$emit('refresh')"
            :disabled="loading"
            :class="[
              'text-sm disabled:opacity-50 transition-colors',
              themeStore.isAdminDark() 
                ? 'text-orange-400 hover:text-orange-300' 
                : 'text-orange-600 hover:text-orange-700'
            ]"
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
  Zap, FileText, Users, RefreshCw 
} from 'lucide-vue-next'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

defineProps({
  loading: {
    type: Boolean,
    default: false
  },
  lastUpdated: {
    type: Date,
    default: null
  }
})

defineEmits(['refresh'])

const formatDateTime = (date) => {
  if (!date) return 'Never'
  try {
    return new Date(date).toLocaleString()
  } catch {
    return 'Invalid Date'
  }
}
</script>
