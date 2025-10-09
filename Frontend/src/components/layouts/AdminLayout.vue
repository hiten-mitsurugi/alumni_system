<!-- AdminLayout.vue -->
<script setup>
import AdminSidebar from '../sidebar_temp/AdminSidebar.vue'
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
themeStore.initializeAdminTheme && themeStore.initializeAdminTheme()

const adminDark = computed(() => (themeStore.isAdminDark ? themeStore.isAdminDark() : false))
</script>

<template>
  <div :class="['min-h-screen flex', adminDark ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900']">
    <!-- Fixed sidebar -->
    <div class="fixed top-0 left-0 h-full z-40">
      <AdminSidebar />
    </div>
    <!-- Main content area with proper left margin based on sidebar width -->
    <div class="flex-1 ml-[220px] sm:ml-[220px] md:ml-[240px] lg:ml-[260px] p-3 sm:p-4 md:p-6 overflow-auto min-h-screen">
      <router-view />
    </div>
  </div>
</template>
