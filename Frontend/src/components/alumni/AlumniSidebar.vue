<template>
  <div :class="[
    'h-full transition-all duration-200 shadow-xl border-r',
    'fixed top-0 left-0 z-50',
    // Mobile: Always show collapsed (w-20), expand to w-64 when toggled
    isExpanded ? 'w-64' : 'w-20',
    // Theme-aware classes
    themeStore.isDarkMode
      ? 'bg-gray-800 text-white border-gray-700'
      : 'bg-white text-gray-800 border-gray-200'
  ]">
    <div :class="[
      'flex items-center justify-between p-4 border-b',
      themeStore.isDarkMode
        ? 'bg-gray-800 border-gray-700'
        : 'bg-white border-gray-200'
    ]">
      <span v-if="isExpanded" :class="[
        'text-xl font-semibold',
        themeStore.isDarkMode ? 'text-white' : 'text-gray-800'
      ]">Alumni System</span>
      <button
        @click="$emit('toggle')"
        class="p-2 transition-colors duration-200 rounded-lg"
        :class="themeStore.isDarkMode 
          ? 'text-gray-300 hover:bg-gray-700 hover:text-white'
          : 'text-gray-800 hover:bg-gray-100 hover:text-gray-900'"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
    </div>
    <nav class="px-3 mt-6" :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-800'">
      <SidebarItem :icon="Home" label="Home" to="/alumni/home" :expanded="isExpanded" />
      <SidebarItem :icon="User" label="My Profile" to="/alumni/my-profile" :expanded="isExpanded" />
      <SidebarItem :icon="Users" label="My Mates" to="/alumni/my-mates" :expanded="isExpanded" />
      <SidebarItem :icon="MessageCircle" label="Messaging" to="/alumni/messaging" :expanded="isExpanded" :badge="messagingBadgeCount" />
      <SidebarItem :icon="FileText" label="Survey" to="/alumni/survey" :expanded="isExpanded" />
    </nav>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import SidebarItem from './SidebarItem.vue'
import { useMessagingNotificationStore } from '@/stores/messagingNotifications'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

// Lucide icon components
import {
  Home,
  User,
  Users,
  MessageCircle,
  FileText,
  //Settings
} from 'lucide-vue-next'

const messagingNotificationStore = useMessagingNotificationStore()
const authStore = useAuthStore()
const themeStore = useThemeStore()

defineProps(['isExpanded'])

// Computed property for messaging badge count
const messagingBadgeCount = computed(() => {
  const count = messagingNotificationStore.totalUnreadCount
  console.log('🔧 AlumniSidebar: Badge count computed:', {
    messages: messagingNotificationStore.unreadMessages,
    requests: messagingNotificationStore.unreadMessageRequests,
    total: count,
    display: count > 0 ? count.toString() : null
  })
  return count > 0 ? count.toString() : null
})

// Initialize messaging notification store when component mounts
onMounted(async () => {
  console.log('🔧 AlumniSidebar: Component mounted, checking initialization...')
  console.log('🔧 AlumniSidebar: Auth user:', authStore.user?.id)
  console.log('🔧 AlumniSidebar: Store initialized:', messagingNotificationStore.isInitialized)

  if (authStore.user && !messagingNotificationStore.isInitialized) {
    console.log('🔧 AlumniSidebar: Initializing messaging notification store...')
    await messagingNotificationStore.initialize()
    console.log('🔧 AlumniSidebar: Store initialization complete')
  } else if (!authStore.user) {
    console.log('🔧 AlumniSidebar: No user found, skipping store initialization')
  } else {
    console.log('🔧 AlumniSidebar: Store already initialized')
  }

  // 🔧 ENHANCEMENT: Force refresh counts to ensure real-time accuracy
  if (authStore.user) {
    console.log('🔄 AlumniSidebar: Force refreshing notification counts...')
    await messagingNotificationStore.forceRefresh()
  }
})
</script>
