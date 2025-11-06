<template>
  <div class="flex h-screen bg-amber-50 relative transition-colors duration-200">
    <!-- Transparent overlay when sidebar is expanded on mobile -->
    <div 
      v-if="sidebarExpanded && isMobile"
      @click="sidebarExpanded = false"
      class="fixed inset-0 bg-black/20 z-40 lg:hidden"
    ></div>

    <!-- Sidebar: Always fixed overlay, hidden on mobile unless expanded -->
    <AlumniSidebar 
      v-if="!isMobile || sidebarExpanded"
      :isExpanded="sidebarExpanded" 
      @toggle="sidebarExpanded = !sidebarExpanded"
    />

    <!-- Main content area: Offset only on desktop when sidebar is visible -->
    <div :class="['flex-1 flex flex-col w-full transition-all duration-200', !isMobile ? 'ml-20' : '']">
      <AlumniNavbar @openSidebar="sidebarExpanded = true" />
      <main class="p-4 overflow-auto flex-1 bg-amber-50 transition-colors duration-200">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AlumniSidebar from '@/components/alumni/AlumniSidebar.vue'
import AlumniNavbar from '@/components/alumni/AlumniNavbar.vue'

const sidebarExpanded = ref(false)

const isMobile = ref(false)
function checkMobile() {
  isMobile.value = window.innerWidth < 1024;
}
onMounted(() => {
  checkMobile();
  window.addEventListener('resize', checkMobile);
});
</script>

<style scoped>
/* Main content always takes full width */
div[class*="flex-1"] {
  width: 100%;
}
</style>