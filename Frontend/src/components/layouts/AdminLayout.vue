<!-- AdminLayout.vue -->
<script setup>
import AdminSidebar from '../sidebar_temp/AdminSidebar.vue';
</script>

<template>

  <div class="min-h-screen bg-gray-50">
    <!-- Fixed sidebar -->
    <div class="fixed top-0 left-0 h-full z-40">
      <AdminSidebar />
    </div>
    <!-- Main content area with left margin -->
    <div class="ml-[280px] p-6 overflow-auto">
      <router-view />
    </div>
  </div>
</template>
