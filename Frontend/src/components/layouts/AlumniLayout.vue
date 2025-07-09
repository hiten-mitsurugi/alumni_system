<template>
  <div class="flex h-screen bg-gray-100">
    <AlumniSidebar :isExpanded="sidebarExpanded" @toggle="sidebarExpanded = !sidebarExpanded" />
    <div class="flex flex-col flex-1">
      <AlumniNavbar />
      <main class="p-4 overflow-auto">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AlumniSidebar from '../AlumniSidebar.vue'
import AlumniNavbar from '../AlumniNavbar.vue'

const sidebarExpanded = ref(false)
</script>
