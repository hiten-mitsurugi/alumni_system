<template>
  <div class="flex h-screen bg-gray-100  relative transition-colors duration-200">
    <!-- Transparent overlay when sidebar is expanded on mobile -->
    <div 
      v-if="sidebarExpanded" 
      @click="sidebarExpanded = false"
      class="fixed inset-0 bg-transparent z-40 lg:hidden"
    ></div>
    
    <!-- Sidebar with overlay positioning -->
    <AlumniSidebar 
      :isExpanded="sidebarExpanded" 
      @toggle="sidebarExpanded = !sidebarExpanded"
      class="fixed lg:relative z-50"
    />
    
    <!-- Main content area - adjusted for always visible collapsed sidebar on mobile -->
    <div class="flex flex-col w-full ml-20 lg:ml-0">
      <AlumniNavbar />
      <main class="p-4 overflow-auto flex-1 bg-gray-100  transition-colors duration-200">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AlumniSidebar from '@/components/alumni/AlumniSidebar.vue'
import AlumniNavbar from '@/components/alumni/AlumniNavbar.vue'

const sidebarExpanded = ref(false)
</script>
