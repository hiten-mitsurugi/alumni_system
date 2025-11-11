<template>
  <div :class="[
    'flex h-screen relative transition-colors duration-200',
    themeStore.isDarkMode ? 'bg-gray-900' : 'bg-white'
  ]">
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
      <AlumniNavbar 
        :sidebar-expanded="sidebarExpanded"
        :is-mobile="isMobile"
        @openSidebar="sidebarExpanded = true" 
      />
      <main :class="[
        'p-4 overflow-auto flex-1 transition-colors duration-200',
        themeStore.isDarkMode ? 'bg-gray-900' : 'bg-white'
      ]">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import AlumniSidebar from '@/components/alumni/AlumniSidebar.vue'
import AlumniNavbar from '@/components/alumni/AlumniNavbar.vue'

const themeStore = useThemeStore()

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