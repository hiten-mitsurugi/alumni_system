<template>
  <div class="flex h-screen bg-amber-50 relative transition-colors duration-200">
    <!-- Transparent overlay when sidebar is expanded on mobile -->
    <div 
      v-if="sidebarExpanded && isMobile"
      @click="sidebarExpanded = false"
      class="fixed inset-0 bg-black/20 z-40 lg:hidden"
    ></div>

    <!-- Sidebar: Only show on desktop or when expanded on mobile -->
    <AlumniSidebar 
      v-if="!isMobile || sidebarExpanded"
      :isExpanded="sidebarExpanded" 
      @toggle="sidebarExpanded = !sidebarExpanded"
      class="fixed lg:relative z-50"
    />

    <!-- Main content area: no margin when sidebar is hidden on mobile -->
    <div :class="['flex-1 flex flex-col', (!isMobile || sidebarExpanded) ? 'ml-20 lg:ml-0' : 'ml-0']">
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
/* Ensure sidebar overlaps content clearly */
.fixed {
  z-index: 50;
}

/* Optional: Dim content slightly when sidebar is expanded */
div[data-expanded=true] main {
  transition: opacity 0.2s ease;
  opacity: 0.85;
}
</style>