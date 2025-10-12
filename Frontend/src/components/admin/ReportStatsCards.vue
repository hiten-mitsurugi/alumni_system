<script setup>
import { useThemeStore } from '@/stores/theme'

// Stores
const themeStore = useThemeStore()

defineProps({
  totalReports: {
    type: Number,
    default: 0
  },
  pendingReports: {
    type: Number,
    default: 0
  },
  resolvedToday: {
    type: Number,
    default: 0
  },
  dismissedToday: {
    type: Number,
    default: 0
  }
})
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
    <div :class="['rounded-lg p-4 shadow-sm border', 
                  themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <div class="flex items-center">
        <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-red-900' : 'bg-red-100']">
          <svg :class="['h-6 w-6', themeStore.isAdminDark() ? 'text-red-400' : 'text-red-600']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.865-.833-2.635 0L4.179 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
          </svg>
        </div>
        <div class="ml-3">
          <p :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">Total Reports</p>
          <p :class="['text-2xl font-semibold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">{{ totalReports }}</p>
        </div>
      </div>
    </div>

    <div :class="['rounded-lg p-4 shadow-sm border', 
                  themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <div class="flex items-center">
        <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-yellow-900' : 'bg-yellow-100']">
          <svg :class="['h-6 w-6', themeStore.isAdminDark() ? 'text-yellow-400' : 'text-yellow-600']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <div class="ml-3">
          <p :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">Pending</p>
          <p :class="['text-2xl font-semibold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">{{ pendingReports }}</p>
        </div>
      </div>
    </div>

    <div :class="['rounded-lg p-4 shadow-sm border', 
                  themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <div class="flex items-center">
        <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-green-900' : 'bg-green-100']">
          <svg :class="['h-6 w-6', themeStore.isAdminDark() ? 'text-green-400' : 'text-green-600']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <div class="ml-3">
          <p :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">Resolved Today</p>
          <p :class="['text-2xl font-semibold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">{{ resolvedToday }}</p>
        </div>
      </div>
    </div>

    <div :class="['rounded-lg p-4 shadow-sm border', 
                  themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <div class="flex items-center">
        <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-gray-700' : 'bg-gray-100']">
          <svg :class="['h-6 w-6', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728"></path>
          </svg>
        </div>
        <div class="ml-3">
          <p :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">Dismissed Today</p>
          <p :class="['text-2xl font-semibold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">{{ dismissedToday }}</p>
        </div>
      </div>
    </div>
  </div>
</template>