<template>
  <div :class="['bg-green-700 text-white h-full transition-all duration-300', isExpanded ? 'w-64' : 'w-20']">
    <div class="p-4 flex justify-between items-center">
      <span v-if="isExpanded" class="text-xl font-bold">Alumni</span>
      <button @click="$emit('toggle')">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
    </div>
    <nav class="mt-4">
      <SidebarItem :icon="Home" label="Home" to="/alumni/home" :expanded="isExpanded" />
      <SidebarItem :icon="User" label="My Profile" to="/alumni/my-profile" :expanded="isExpanded" />
      <SidebarItem :icon="Users" label="My Mates" to="/alumni/my-mates" :expanded="isExpanded" />
      <SidebarItem :icon="MessageSquare" label="Messaging" to="/alumni/messaging" :expanded="isExpanded" :badge="messagingBadgeCount" />
      <SidebarItem :icon="ClipboardList" label="Survey" to="/alumni/survey" :expanded="isExpanded" badge="2" />
      <SidebarItem :icon="Heart" label="Donate" to="/alumni/donate" :expanded="isExpanded" />
      <SidebarItem :icon="Settings" label="Settings" to="/alumni/settings" :expanded="isExpanded" />
    </nav>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import SidebarItem from './SidebarItem.vue'
import { useMessagingNotificationStore } from '@/stores/messagingNotifications'
import { useAuthStore } from '@/stores/auth'

// Lucide icon components
import {
  Home,
  User,
  Users,
  MessageSquare,
  ClipboardList,
  Heart,
  Settings
} from 'lucide-vue-next'

const messagingNotificationStore = useMessagingNotificationStore()
const authStore = useAuthStore()

defineProps(['isExpanded'])

// Computed property for messaging badge count
const messagingBadgeCount = computed(() => {
  const count = messagingNotificationStore.totalUnreadCount
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
})
</script>
