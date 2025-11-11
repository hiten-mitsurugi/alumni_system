<template>
  <div :class="[
    'flex items-center justify-between px-4 py-3 transition-colors duration-200 border-b shadow-sm',
    themeStore.isDarkMode 
      ? 'bg-slate-800 border-slate-700' 
      : 'bg-white border-gray-200'
  ]">
    <LogoutLoading v-if="loggingOut" />
    <!-- Left Section: Logo, Menu Button, and Search -->
    <div :class="[
      'flex items-center flex-1 gap-4 transition-all duration-200',
      navbarLeftMargin
    ]">
      <!-- Mobile Menu Button -->
      <button
        class="p-2 mr-2 text-gray-600 transition-colors rounded-lg lg:hidden dark:text-slate-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-slate-700"
        @click="$emit('openSidebar')"
        aria-label="Open menu"
      >
        <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      <img src="@/assets/logo3-removebg-preview.png" alt="Alumni System Logo" class="w-auto h-10" />

      <!-- Search Bar -->
      <div v-if="isHomePage" class="hidden md:flex w-72">
        <div class="relative w-full">
          <input :value="injectedSearchQuery" @input="injectedSearchQuery = $event.target.value" type="text"
            placeholder="Search alumni, posts..."
            class="w-full py-2 pl-10 pr-4 text-gray-900 placeholder-gray-500 bg-white border border-gray-300 rounded-lg dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100 dark:placeholder-slate-400 focus:ring-2 focus:ring-orange-500 focus:border-orange-500">
          <svg class="absolute left-3 top-2.5 h-5 w-5 text-gray-400 dark:text-slate-400" fill="none" stroke="currentColor"
            viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>
    </div>


    <div class="flex items-center gap-3 mr-5">
      <!-- Mobile Search Button -->
            <!-- Mobile Search Button -->
      <button v-if="isHomePage" @click="injectedToggleMobileSearch"
        class="p-2 text-gray-600 transition-colors rounded-lg md:hidden dark:text-slate-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-slate-700"
        title="Search">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </button>

      <!-- Theme Toggle Button (Dark/Light Mode) -->
      <button @click="toggleTheme"
        class="relative p-2 transition-all duration-300 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-700 group"
        title="Toggle Theme">
        <!-- Sun icon (visible in dark mode) -->
        <svg v-if="isDarkMode"
             class="w-6 h-6 text-yellow-400 transition-all duration-500 transform group-hover:rotate-180 group-hover:scale-110"
             fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2.25a.75.75 0 01.75.75v2.25a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM7.5 12a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM18.894 6.166a.75.75 0 00-1.06-1.06l-1.591 1.59a.75.75 0 101.06 1.061l1.591-1.591zM21.75 12a.75.75 0 01-.75.75h-2.25a.75.75 0 010-1.5H21a.75.75 0 01.75.75zM17.834 18.894a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 10-1.061 1.06l1.591 1.591zM12 18a.75.75 0 01.75.75V21a.75.75 0 01-1.5 0v-2.25A.75.75 0 0112 18zM7.758 17.303a.75.75 0 00-1.061-1.06l-1.591 1.59a.75.75 0 001.06 1.061l1.591-1.591zM6 12a.75.75 0 01-.75.75H3a.75.75 0 010-1.5h2.25A.75.75 0 016 12zM6.697 7.757a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 00-1.061 1.06l1.591 1.591z" />
        </svg>

        <!-- Moon icon (visible in light mode) -->
        <svg v-else
             class="w-6 h-6 text-gray-600 transition-all duration-500 transform dark:text-slate-300 group-hover:rotate-12 group-hover:scale-110 group-hover:text-indigo-600 dark:group-hover:text-indigo-400"
             fill="currentColor" viewBox="0 0 24 24">
          <path fill-rule="evenodd" d="M9.528 1.718a.75.75 0 01.162.819A8.97 8.97 0 009 6a9 9 0 009 9 8.97 8.97 0 003.463-.69.75.75 0 01.981.98 10.503 10.503 0 01-9.694 6.46c-5.799 0-10.5-4.701-10.5-10.5 0-4.368 2.667-8.112 6.46-9.694a.75.75 0 01.818.162z" clip-rule="evenodd" />
        </svg>
      </button>

      <!-- Notifications Button -->
      <div class="relative">
        <button @click="notificationOpen = !notificationOpen"
          :class="[
            'relative p-2 transition-colors duration-200 rounded-lg',
            themeStore.isDarkMode 
              ? 'hover:bg-slate-700 text-slate-300' 
              : 'hover:bg-gray-100 text-gray-600'
          ]" 
          title="Notifications">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <!-- Notification Badge -->
          <span v-if="unreadCount > 0" 
                class="absolute top-0 right-0 flex items-center justify-center w-5 h-5 text-xs font-medium text-white bg-red-500 rounded-full">
            {{ unreadCount > 99 ? '99+' : unreadCount }}
          </span>
        </button>

        <!-- Notification Dropdown -->
        <div v-if="notificationOpen"
             :class="[
               'absolute right-0 z-50 w-96 mt-2 rounded-lg shadow-lg border max-h-96 overflow-y-auto',
               themeStore.isDarkMode 
                 ? 'bg-gray-800 border-gray-600' 
                 : 'bg-white border-gray-200'
             ]">
          <!-- Header -->
          <div :class="[
            'px-4 py-3 border-b',
            themeStore.isDarkMode ? 'border-gray-600' : 'border-gray-200'
          ]">
            <div class="flex items-center justify-between">
              <h3 :class="[
                'text-lg font-semibold',
                themeStore.isDarkMode ? 'text-gray-100' : 'text-gray-900'
              ]">Notifications</h3>
              <button @click="markAllAsRead" 
                      class="text-sm text-blue-600 hover:text-blue-700">
                Mark all as read
              </button>
            </div>
          </div>

          <!-- Notification List -->
          <div class="max-h-80 overflow-y-auto">
            <div v-if="notifications.length === 0" 
                 class="px-4 py-8 text-center">
              <svg :class="[
                'w-12 h-12 mx-auto mb-3',
                themeStore.isDarkMode ? 'text-gray-500' : 'text-gray-400'
              ]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
              </svg>
              <p :class="[
                'text-sm',
                themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
              ]">No notifications yet</p>
            </div>

            <div v-else>
              <div v-for="notification in notifications" 
                   :key="notification.id"
                   @click="markAsRead(notification.id)"
                   :class="[
                     'px-4 py-3 border-b cursor-pointer transition-colors',
                     !notification.read ? 'bg-blue-50 dark:bg-blue-900/20' : '',
                     'hover:bg-gray-50 dark:hover:bg-gray-700',
                     themeStore.isDarkMode ? 'border-gray-600' : 'border-gray-100'
                   ]">
                <div class="flex items-start space-x-3">
                  <!-- Notification Icon -->
                  <div :class="[
                    'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center mt-1',
                    getNotificationColor(notification.type)
                  ]">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path v-if="notification.type === 'connection'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                      <path v-else-if="notification.type === 'survey'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      <path v-else-if="notification.type === 'profile'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      <path v-else-if="notification.type === 'message'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                    </svg>
                  </div>

                  <!-- Notification Content -->
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center justify-between">
                      <p :class="[
                        'text-sm font-medium',
                        themeStore.isDarkMode ? 'text-gray-100' : 'text-gray-900'
                      ]">{{ notification.title }}</p>
                      <span v-if="!notification.read" 
                            class="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0"></span>
                    </div>
                    <p :class="[
                      'text-sm mt-1',
                      themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                    ]">{{ notification.message }}</p>
                    <p :class="[
                      'text-xs mt-1',
                      themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
                    ]">{{ notification.time }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div :class="[
            'px-4 py-3 border-t',
            themeStore.isDarkMode ? 'border-gray-600' : 'border-gray-200'
          ]">
            <button class="w-full text-center text-sm text-blue-600 hover:text-blue-700 font-medium">
              View all notifications
            </button>
          </div>
        </div>
      </div>

      <!-- User Profile Dropdown -->
      <div class="relative">
        <button @click="dropdownOpen = !dropdownOpen"
          class="flex items-center gap-2 p-1 transition-colors duration-200 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-700">
          <img :src="profilePictureUrl"
               alt="Profile"
               @error="handleImageError"
               class="object-cover w-10 h-10 border-2 border-gray-200 rounded-full dark:border-slate-600" />
        </button>

        <!-- Dropdown Menu -->
        <div v-if="dropdownOpen"
          class="absolute right-0 z-50 w-48 py-1 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg dark:bg-slate-800 dark:border-slate-700">
          <router-link to="/alumni/my-profile"
            class="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-slate-200 hover:bg-gray-100 dark:hover:bg-slate-700" @click="dropdownOpen = false">
            <svg class="w-5 h-5 mr-3 text-gray-500 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            My Profile
          </router-link>
          <router-link to="/alumni/settings" class="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-slate-200 hover:bg-gray-100 dark:hover:bg-slate-700"
            @click="dropdownOpen = false">
            <svg class="w-5 h-5 mr-3 text-gray-500 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Settings
          </router-link>
          <hr class="my-1 border-gray-200 dark:border-slate-600">
          <button @click="confirmLogout" class="flex items-center w-full px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20">
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
    <div v-if="showLogoutConfirmation" class="fixed z-50 w-full max-w-sm p-4 top-4 right-4">
      <!-- Modal without backdrop -->
      <div class="p-6 text-gray-900 border border-gray-300 shadow-2xl bg-white/98 dark:bg-gray-800/98 rounded-xl dark:text-white dark:border-gray-600 backdrop-blur-sm animate-fade-in">
        <div class="flex items-center mb-4">
          <div class="flex items-center justify-center flex-shrink-0 w-10 h-10 mr-3 bg-red-100 rounded-full dark:bg-red-900/40">
            <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            Confirm Logout
          </h3>
        </div>

        <p class="mb-6 text-sm text-gray-600 dark:text-gray-300">
          Are you sure you want to logout? You will be redirected to the login page.
        </p>

        <div class="flex space-x-3">
          <button
            @click="cancelLogout"
            class="flex-1 px-4 py-2 text-sm font-medium text-gray-700 transition-colors bg-gray-100 border border-gray-300 rounded-lg dark:bg-gray-700/80 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 dark:border-gray-600"
          >
            Cancel
          </button>
          <button
            @click="handleLogout"
            class="flex-1 px-4 py-2 text-sm font-medium text-white transition-colors bg-red-600 border border-red-600 rounded-lg hover:bg-red-700"
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
import { useThemeStore } from '@/stores/theme'
import LogoutLoading from '../common/LogoutLoading.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()
const BASE_URL = `${window.location.protocol}//${window.location.hostname}:8000`;


const dropdownOpen = ref(false)
const notificationOpen = ref(false)
const loggingOut = ref(false)
const showLogoutConfirmation = ref(false)

// Sample notifications data
const notifications = ref([
  {
    id: 1,
    title: 'New Connection Request',
    message: 'John Doe wants to connect with you',
    time: '5 minutes ago',
    type: 'connection',
    read: false
  },
  {
    id: 2,
    title: 'Survey Available',
    message: 'Alumni Career Development Survey is now open',
    time: '1 hour ago',
    type: 'survey',
    read: false
  },
  {
    id: 3,
    title: 'Profile Views',
    message: 'Your profile was viewed 3 times this week',
    time: '2 hours ago',
    type: 'profile',
    read: true
  },
  {
    id: 4,
    title: 'New Message',
    message: 'You have a new message from Sarah Wilson',
    time: '3 hours ago',
    type: 'message',
    read: true
  }
])

// Unread notification count
const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)

// Theme computed property
const isDarkMode = computed(() => themeStore.isDarkMode)

// Inject search functionality from parent (AlumniHome)
const injectedSearchQuery = inject('searchQuery', ref(''))
const injectedToggleMobileSearch = inject('toggleMobileSearch', () => { })

// Define props
const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  },
  sidebarExpanded: {
    type: Boolean,
    default: false
  },
  isMobile: {
    type: Boolean,
    default: false
  }
})

// Define emits
defineEmits(['toggleNotification', 'toggleMobileSearch', 'update:searchQuery'])

// Check if we're on the home page to show search
const isHomePage = computed(() => route.name === 'AlumniHome')

// Compute navbar left margin based on sidebar state
const navbarLeftMargin = computed(() => {
  if (props.isMobile) return 'ml-4'
  return props.sidebarExpanded ? 'ml-48' : 'ml-4'
})

// Compute profile picture URL with cache-busting and better fallback
const profilePictureUrl = computed(() => {
  const user = authStore.user
  const pic = user?.profile_picture

  console.log('User data:', user)
  console.log('Profile picture:', pic)

  if (!pic || pic === '' || pic === 'null') {
    console.log('Using default avatar')
    return '/default-avatar.png'
  }

  try {
    // Handle absolute URLs (already complete)
    if (pic.startsWith('http://') || pic.startsWith('https://')) {
      return pic
    }

    // Handle relative URLs - ensure they start with /
    const relativePath = pic.startsWith('/') ? pic : `/${pic}`
    const fullUrl = `${BASE_URL}${relativePath}`

    console.log('Profile picture URL:', fullUrl)
    return fullUrl
  } catch (error) {
    console.error('Error processing profile picture URL:', error)
    return '/default-avatar.png'
  }
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

// Notification functions
function markAsRead(notificationId) {
  const notification = notifications.value.find(n => n.id === notificationId)
  if (notification) {
    notification.read = true
  }
}

function markAllAsRead() {
  notifications.value.forEach(notification => {
    notification.read = true
  })
}

function getNotificationColor(type) {
  const colorMap = {
    connection: themeStore.isDarkMode ? 'bg-green-900/30 text-green-400' : 'bg-green-100 text-green-600',
    survey: themeStore.isDarkMode ? 'bg-blue-900/30 text-blue-400' : 'bg-blue-100 text-blue-600',
    profile: themeStore.isDarkMode ? 'bg-purple-900/30 text-purple-400' : 'bg-purple-100 text-purple-600',
    message: themeStore.isDarkMode ? 'bg-orange-900/30 text-orange-400' : 'bg-orange-100 text-orange-600',
    system: themeStore.isDarkMode ? 'bg-gray-700 text-gray-400' : 'bg-gray-100 text-gray-600'
  }
  return colorMap[type] || colorMap.system
}

// Close dropdowns when clicking outside
document.addEventListener('click', (e) => {
  const target = e.target
  if (!target.closest('.relative')) {
    dropdownOpen.value = false
    notificationOpen.value = false
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

// Handle image loading errors
function handleImageError(event) {
  console.warn('Profile image failed to load, using default avatar')
  event.target.src = '/default-avatar.png'
}

// Toggle dark/light mode
function toggleTheme() {
  console.log('🌙 Toggle theme clicked')
  console.log('Before:', document.documentElement.classList.contains('dark'))
  themeStore.toggleTheme()
  console.log('After:', document.documentElement.classList.contains('dark'))
  console.log('Store isDarkMode:', themeStore.isDarkMode)
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
