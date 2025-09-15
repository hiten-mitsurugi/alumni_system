<!-- SuperAdminLayout.vue -->
<script setup>
import SuperAdminSidebar from '../sidebar_temp/SuperAdminSidebar.vue'
</script>

<template>

  <div class="min-h-screen bg-gray-50">
    <!-- Fixed sidebar -->
    <div class="fixed top-0 left-0 h-full z-40">
      <SuperAdminSidebar />
    </div>
    <!-- Main content area with left margin -->
    <div class="ml-[350px] p-6 overflow-auto">
      <router-view />
    </div>
  </div>
</template>
