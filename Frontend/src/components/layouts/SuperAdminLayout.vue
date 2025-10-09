<!-- SuperAdminLayout.vue -->
<script setup>
import SuperAdminSidebar from '../sidebar_temp/SuperAdminSidebar.vue'
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex">
    <!-- Fixed sidebar -->
    <div class="fixed top-0 left-0 h-full z-40">
      <SuperAdminSidebar />
    </div>
    <!-- Main content area with proper left margin based on sidebar width -->
    <div class="flex-1 ml-[220px] sm:ml-[220px] md:ml-[240px] lg:ml-[260px] p-3 sm:p-4 md:p-6 overflow-auto min-h-screen">
      <router-view />
    </div>
  </div>
</template>
