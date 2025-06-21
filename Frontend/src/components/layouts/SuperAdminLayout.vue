<!-- SuperAdminLayout.vue -->
<script setup>
import SuperAdminSidebar from '../sidebar_temp/SuperAdminSidebar.vue'
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex">
    <!-- Correct sidebar component -->
    <SuperAdminSidebar />

    <!-- Main content area -->
    <div class="flex-1 p-6 overflow-auto">
      <router-view />
    </div>
  </div>
</template>
