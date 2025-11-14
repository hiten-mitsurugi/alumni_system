<template>
  <div :class="[
    'flex h-screen relative transition-colors duration-200',
    themeStore.isDarkMode ? 'bg-gray-900' : 'bg-white'
  ]">
    <!-- Transparent overlay when sidebar is expanded on mobile/tablet -->
    <div
      v-if="sidebarExpanded && (isMobile || isTablet)"
      @click="sidebarExpanded = false"
      class="fixed inset-0 z-40 bg-black/20"
    ></div>

    <!-- Desktop & Tablet Sidebar: Show when not mobile -->
    <AlumniSidebar
      v-if="!isMobile && (!isTablet || sidebarExpanded)"
      :isExpanded="sidebarExpanded"
      @toggle="sidebarExpanded = !sidebarExpanded"
    />

    <!-- Main content area: Responsive margins and padding -->
    <div :class="[
      'flex-1 flex flex-col w-full transition-all duration-200',
      // Desktop margins
      isDesktop ? (sidebarExpanded ? 'ml-64' : 'ml-20') : '',
      // Mobile: Add bottom padding for bottom nav
      isMobile ? 'pb-20' : ''
    ]">
      <!-- Navbar: Hide burger menu on mobile -->
      <AlumniNavbar
        :sidebar-expanded="sidebarExpanded"
        :is-mobile="isMobile"
        :is-tablet="isTablet"
        :show-burger-menu="!isMobile"
        @openSidebar="sidebarExpanded = true"
      />

      <!-- Main content -->
      <main :class="[
        'overflow-auto flex-1 transition-colors duration-200',
        // Responsive padding
        isMobile ? 'p-3 main-content-mobile' : 'p-4',
        themeStore.isDarkMode ? 'bg-gray-900' : 'bg-white'
      ]">
        <router-view :sidebar-expanded="sidebarExpanded" />
      </main>
    </div>

    <!-- Mobile Bottom Navigation: Show only on mobile -->
    <AlumniBottomNav v-if="isMobile" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import AlumniSidebar from '@/components/alumni/AlumniSidebar.vue'
import AlumniNavbar from '@/components/alumni/AlumniNavbar.vue'
import AlumniBottomNav from '@/components/alumni/AlumniBottomNav.vue'

const themeStore = useThemeStore()

const sidebarExpanded = ref(false)

// More granular mobile/tablet detection
const isMobile = ref(false)      // iPhone SE to iPhone Pro Max
const isTablet = ref(false)      // iPad Mini to iPad Pro
const isDesktop = ref(false)     // Desktop and larger

function checkScreenSize() {
  const width = window.innerWidth;

  // Mobile: 0-767px (hide sidebar, show bottom nav)
  isMobile.value = width < 768;

  // Tablet: 768-1023px (show collapsed sidebar)
  isTablet.value = width >= 768 && width < 1024;

  // Desktop: 1024px+ (show full sidebar functionality)
  isDesktop.value = width >= 1024;
}
onMounted(() => {
  checkScreenSize();
  window.addEventListener('resize', checkScreenSize);
});
</script>

<style scoped>
/* Main content always takes full width */
div[class*="flex-1"] {
  width: 100%;
}
</style>
