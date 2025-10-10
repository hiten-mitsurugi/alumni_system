<template>
  <div class="flex justify-between items-center px-4 py-3 bg-white shadow-sm border-b border-gray-200">
    <LogoutLoading v-if="loggingOut" />
    <!-- Left Section: Logo, Menu Button, and Search -->
    <div class="flex items-center gap-4 flex-1 ml-4">
      <!-- Mobile Menu Button -->
      <button
        class="lg:hidden p-2 mr-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
        @click="$emit('openSidebar')"
        aria-label="Open menu"
      >
        <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      <img src="@/assets/logo3-removebg-preview.png" alt="Alumni System Logo" class="h-10 w-auto" />

      <!-- Search Bar -->
      <div v-if="isHomePage" class="hidden md:flex w-72">
        <div class="relative w-full">
          <input :value="injectedSearchQuery" @input="injectedSearchQuery = $event.target.value" type="text"
            placeholder="Search alumni, posts..."
            class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
          <svg class="absolute left-3 top-2.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor"
            viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>
    </div>


    <div class="flex gap-3 items-center mr-5">
      <!-- Mobile Search Button -->
      <button v-if="isHomePage" @click="injectedToggleMobileSearch"
        class="md:hidden p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
        title="Search">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </button>

      <!-- Notifications Button -->
      <button @click="$emit('toggleNotification')"
        class="relative p-2 rounded-lg hover:bg-gray-100 transition-colors duration-200" title="Notifications">
        <svg class="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        <!-- Notification Badge -->
        <span class="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-500"></span>
      </button>

      <!-- User Profile Dropdown -->
      <div class="relative">
        <button @click="dropdownOpen = !dropdownOpen"
          class="flex items-center gap-2 p-1 rounded-lg hover:bg-gray-100 transition-colors duration-200">
          <img :src="profilePictureUrl" alt="Profile"
            class="w-10 h-10 rounded-full object-cover border-2 border-gray-200" />
        </button>

        <!-- Dropdown Menu -->
        <div v-if="dropdownOpen"
          class="absolute right-0 mt-2 w-48 bg-white shadow-lg rounded-lg border border-gray-200 py-1 z-50">
          <router-link to="/alumni/my-profile"
            class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" @click="dropdownOpen = false">
            <svg class="w-5 h-5 mr-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            My Profile
          </router-link>
          <router-link to="/alumni/settings" class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
            @click="dropdownOpen = false">
            <svg class="w-5 h-5 mr-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Settings
          </router-link>
          <hr class="my-1 border-gray-200">
          <button @click="confirmLogout" class="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50">
            <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Logout
          </button>
        </div>
      </div>
    </div>

    <!-- Logout Confirmation Modal - Positioned like a notification -->
    <div v-if="showLogoutConfirmation" class="fixed top-4 right-4 z-50 max-w-sm w-full p-4">
      <!-- Modal without backdrop -->
      <div class="bg-white/98 dark:bg-gray-800/98 rounded-xl shadow-2xl p-6 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 backdrop-blur-sm animate-fade-in">
        <div class="flex items-center mb-4">
          <div class="flex-shrink-0 w-10 h-10 bg-red-100 dark:bg-red-900/40 rounded-full flex items-center justify-center mr-3">
            <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            Confirm Logout
          </h3>
        </div>
        
        <p class="text-sm text-gray-600 dark:text-gray-300 mb-6">
          Are you sure you want to logout? You will be redirected to the login page.
        </p>
        
        <div class="flex space-x-3">
          <button
            @click="cancelLogout"
            class="flex-1 px-4 py-2 text-sm font-medium bg-gray-100 dark:bg-gray-700/80 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors border border-gray-300 dark:border-gray-600"
          >
            Cancel
          </button>
          <button
            @click="handleLogout"
            class="flex-1 px-4 py-2 text-sm font-medium bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors border border-red-600"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LogoutLoading from '../common/LogoutLoading.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const BASE_URL = `${window.location.protocol}//${window.location.hostname}:8000`;


const dropdownOpen = ref(false)
const loggingOut = ref(false)
const showLogoutConfirmation = ref(false)

// Inject search functionality from parent (AlumniHome)
const injectedSearchQuery = inject('searchQuery', ref(''))
const injectedToggleMobileSearch = inject('toggleMobileSearch', () => { })

// Define props
defineProps({
  searchQuery: {
    type: String,
    default: ''
  }
})

// Define emits
defineEmits(['toggleNotification', 'toggleMobileSearch', 'update:searchQuery'])

// Check if we're on the home page to show search
const isHomePage = computed(() => route.name === 'AlumniHome')

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

// Logout confirmation functions
function confirmLogout() {
  dropdownOpen.value = false; // Close dropdown when showing confirmation
  showLogoutConfirmation.value = true;
}

function cancelLogout() {
  showLogoutConfirmation.value = false;
}

// Logout function
async function handleLogout() {
  showLogoutConfirmation.value = false;
  loggingOut.value = true;
  console.log('AlumniNavbar: Starting logout process');
  await authStore.logoutWithAPI();
  console.log('AlumniNavbar: Backend logout completed, waiting briefly for status broadcast');

  // Wait a bit to ensure status update is broadcast and received
  await new Promise(resolve => setTimeout(resolve, 500));

  console.log('AlumniNavbar: Redirecting to login');
  router.push('/login');
  loggingOut.value = false;
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
