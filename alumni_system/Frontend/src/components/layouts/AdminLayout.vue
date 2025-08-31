<!-- AdminLayout.vue -->
<script setup>
import AdminSidebar from '../sidebar_temp/AdminSidebar.vue';
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex">
    <!-- Correct sidebar component -->
    <AdminSidebar />

    <!-- Main content area -->
    <div class="flex-1 p-6 overflow-auto">
      <router-view />
    </div>
  </div>
</template>
