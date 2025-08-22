<template>
  <div class="flex justify-between items-center px-4 py-3 bg-white shadow-sm border-b border-gray-200">
    <!-- Left Section: Dynamic Page Title -->
    <div class="flex items-center gap-4">
      <div class="text-lg font-semibold text-gray-800">{{ currentPageTitle }}</div>
    </div>

    <div class="flex gap-3 items-center">
      <!-- Notifications Button -->
      <button 
        @click="$emit('toggleNotification')"
        class="relative p-2 rounded-lg hover:bg-gray-100 transition-colors duration-200"
        title="Notifications"
      >
        <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        <!-- Notification Badge -->
        <span class="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-500"></span>
      </button>

      <!-- User Profile Dropdown -->
      <div class="relative">
        <button
          @click="dropdownOpen = !dropdownOpen"
          class="flex items-center gap-2 p-1 rounded-lg hover:bg-gray-100 transition-colors duration-200"
        >
          <img 
            :src="profilePictureUrl"
            alt="Profile" 
            class="w-8 h-8 rounded-full object-cover border-2 border-gray-200"
          />
        </button>

        <!-- Dropdown Menu -->
        <div v-if="dropdownOpen" class="absolute right-0 mt-2 w-48 bg-white shadow-lg rounded-lg border border-gray-200 py-1 z-50">
          <router-link 
            to="/alumni/my-profile" 
            class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
            @click="dropdownOpen = false"
          >
            <svg class="w-4 h-4 mr-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            My Profile
          </router-link>
          <router-link 
            to="/alumni/settings" 
            class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
            @click="dropdownOpen = false"
          >
            <svg class="w-4 h-4 mr-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Settings
          </router-link>
          <hr class="my-1 border-gray-200">
          <button 
            @click="handleLogout" 
            class="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
          >
            <svg class="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
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

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const BASE_URL = 'http://127.0.0.1:8000'

const dropdownOpen = ref(false)

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

// Compute profile picture URL
const profilePictureUrl = computed(() => {
  const user = authStore.user
  const pic = user?.profile_picture
  return pic
    ? (pic.startsWith('http') ? pic : `${BASE_URL}${pic}`)
    : '/default-avatar.png'
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

// Logout function
async function handleLogout() {
  console.log('AlumniNavbar: Starting logout process');
  await authStore.logoutWithAPI();
  console.log('AlumniNavbar: Backend logout completed, waiting briefly for status broadcast');
  
  // Wait a bit to ensure status update is broadcast and received
  await new Promise(resolve => setTimeout(resolve, 500));
  
  console.log('AlumniNavbar: Redirecting to login');
  router.push('/login');
}

// Click outside to close dropdown
const handleClickOutside = (event) => {
  const dropdown = event.target.closest('.relative')
  if (!dropdown) {
    dropdownOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})
</script>
