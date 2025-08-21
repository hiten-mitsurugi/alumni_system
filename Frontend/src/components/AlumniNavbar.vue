<template>
  <div class="flex justify-between items-center px-4 py-3 bg-white dark:bg-slate-800 shadow-sm border-b border-slate-200 dark:border-slate-700 transition-colors duration-200">
    <!-- Left Section: Dynamic Page Title -->
    <div class="flex items-center gap-4">
      <div class="text-lg font-semibold text-slate-800 dark:text-slate-100">{{ currentPageTitle }}</div>
    </div>

    <div class="flex gap-3 items-center">
      <!-- Dark Mode Toggle -->
      <button 
        @click.stop="toggleDarkMode"
        class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors duration-200 cursor-pointer"
        :title="isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
        type="button"
      >
        <!-- Sun Icon (Light Mode) -->
        <svg v-if="isDarkMode" class="w-5 h-5 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2.25a.75.75 0 01.75.75v2.25a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM7.5 12a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM18.894 6.166a.75.75 0 00-1.06-1.06l-1.591 1.59a.75.75 0 101.06 1.061l1.591-1.59zM21.75 12a.75.75 0 01-.75.75h-2.25a.75.75 0 010-1.5H21a.75.75 0 01.75.75zM17.834 18.894a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 10-1.061 1.06l1.59 1.591zM12 18a.75.75 0 01.75.75V21a.75.75 0 01-1.5 0v-2.25A.75.75 0 0112 18zM7.758 17.303a.75.75 0 00-1.061-1.06l-1.591 1.59a.75.75 0 001.06 1.061l1.591-1.59zM6 12a.75.75 0 01-.75.75H3a.75.75 0 010-1.5h2.25A.75.75 0 016 12zM6.697 7.757a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 00-1.061 1.06l1.59 1.591z"/>
        </svg>
        <!-- Moon Icon (Dark Mode) -->
        <svg v-else class="w-5 h-5 text-slate-600 dark:text-slate-300" fill="currentColor" viewBox="0 0 24 24">
          <path fill-rule="evenodd" d="M9.528 1.718a.75.75 0 01.162.819A8.97 8.97 0 009 6a9 9 0 009 9 8.97 8.97 0 003.463-.69.75.75 0 01.981.98 10.503 10.503 0 01-9.694 6.46c-5.799 0-10.5-4.701-10.5-10.5 0-4.368 2.667-8.112 6.46-9.694a.75.75 0 01.818.162z" clip-rule="evenodd"/>
        </svg>
      </button>

      <!-- Notification Icon -->
      <button 
        @click="$emit('toggleNotification')"
        class="relative p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors duration-200"
      >
        <svg class="w-5 h-5 text-slate-600 dark:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5" />
        </svg>
      </button>

      <!-- Profile Dropdown -->
      <div class="relative">
        <button 
          @click="dropdownOpen = !dropdownOpen"
          class="flex items-center gap-2 p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors duration-200"
        >
          <img
            class="w-8 h-8 rounded-full object-cover border-2 border-slate-200 dark:border-slate-600"
            :src="profilePictureUrl"
            alt="Profile"
          />
        </button>
        
        <div v-if="dropdownOpen" class="absolute right-0 mt-2 w-48 bg-white dark:bg-slate-800 shadow-lg rounded-lg border border-slate-200 dark:border-slate-700 py-1 z-50">
          <a href="#" class="block px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors duration-200">Settings & Privacy</a>
          <a href="#" class="block px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors duration-200">Update Profile</a>
          <a href="#" class="block px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors duration-200">Send Feedback</a>
          <hr class="my-1 border-slate-200 dark:border-slate-600">
          <button
            @click.stop="handleLogout"
            class="w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors duration-200"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useDarkModeStore } from '@/stores/darkMode'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const darkModeStore = useDarkModeStore()
const BASE_URL = 'http://127.0.0.1:8000'

const dropdownOpen = ref(false)

// Use the dark mode store
const { isDarkMode } = darkModeStore

// Create a local toggle function for debugging
const toggleDarkMode = () => {
  console.log('🔥 NAVBAR: Button clicked!')
  console.log('🔥 NAVBAR: Current isDarkMode:', isDarkMode.value)
  darkModeStore.toggleDarkMode()
  console.log('🔥 NAVBAR: After toggle isDarkMode:', isDarkMode.value)
}

// Define emits
defineEmits(['toggleNotification'])

// Dynamic page title based on current route
const currentPageTitle = computed(() => {
  const routeName = route.name || route.path
  
  // Map of routes to display names
  const pageTitles = {
    'alumni-home': 'Home',
    'alumni-my-profile': 'My Profile',
    'alumni-my-mates': 'My Mates',
    'alumni-messaging': 'Messages',
    'alumni-survey': 'Survey',
    'alumni-donate': 'Donate',
    'alumni-settings': 'Settings',
    '/alumni/home': 'Home',
    '/alumni/my-profile': 'My Profile',
    '/alumni/my-mates': 'My Mates',
    '/alumni/messaging': 'Messages',
    '/alumni/survey': 'Survey',
    '/alumni/donate': 'Donate',
    '/alumni/settings': 'Settings'
  }
  
  return pageTitles[routeName] || pageTitles[route.path] || 'Alumni Dashboard'
})

// Initialize component
onMounted(async () => {
  // Fetch user if not already present
  if (!authStore.user && authStore.token) {
    try {
      await authStore.fetchUser()
    } catch (error) {
      console.error('Failed to fetch user:', error)
      authStore.logout()
      router.push('/login')
    }
  }
})

// Compute profile picture URL
const profilePictureUrl = computed(() => {
  const user = authStore.user
  const pic = user?.profile_picture
  return pic
    ? (pic.startsWith('http') ? pic : `${BASE_URL}${pic}`)
    : '/default-profile.png'
})

async function handleLogout() {
  console.log('AlumniNavbar: Starting logout process');
  await authStore.logoutWithAPI();
  console.log('AlumniNavbar: Backend logout completed, waiting briefly for status broadcast');
  
  // Wait a bit to ensure status update is broadcast and received
  await new Promise(resolve => setTimeout(resolve, 500));
  
  console.log('AlumniNavbar: Redirecting to login');
  router.push('/login');
}
</script>
