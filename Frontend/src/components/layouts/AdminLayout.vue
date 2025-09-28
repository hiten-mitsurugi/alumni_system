<!-- AdminLayout.vue -->
<script setup>
import AdminSidebar from '../sidebar_temp/AdminSidebar.vue';
import { useThemeStore } from '@/stores/theme';
import { onMounted } from 'vue';

const themeStore = useThemeStore();

onMounted(() => {
  // Initialize theme when layout mounts
  themeStore.initializeTheme();
});
</script>

<template>
  <div class="min-h-screen flex transition-colors duration-200"
       :class="themeStore.isDarkMode ? 'bg-gray-900' : 'bg-gray-50'">
    <!-- Sidebar - Sticky positioning -->
    <div class="sticky top-0 h-screen">
      <AdminSidebar />
    </div>

    <!-- Main content area -->
    <div class="flex-1 transition-colors duration-200"
         :class="themeStore.isDarkMode ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'">
      <router-view />
    </div>
  </div>
</template>
