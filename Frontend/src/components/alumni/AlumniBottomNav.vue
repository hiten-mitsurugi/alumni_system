<template>
  <nav :class="[
    'fixed bottom-0 left-0 right-0 z-50 border-t backdrop-blur-lg transition-colors duration-200',
    'safe-area-pb', // Add safe area padding for devices with home indicator
    themeStore.isDarkMode
      ? 'bg-gray-800/95 border-gray-700 text-white'
      : 'bg-white/95 border-gray-200 text-gray-800'
  ]">
    <div class="flex items-center justify-around px-2 py-1">
      <BottomNavItem
        v-for="item in navItems"
        :key="item.path"
        :icon="item.icon"
        :label="item.label"
        :to="item.path"
        :badge="item.badge"
        :is-active="isActive(item.path)"
      />
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { useMessagingNotificationStore } from '@/stores/messagingNotifications'
import BottomNavItem from './BottomNavItem.vue'

// Lucide icon components
import {
  Home,
  User,
  Users,
  MessageCircle,
  FileText,
} from 'lucide-vue-next'

const route = useRoute()
const themeStore = useThemeStore()
const messagingNotificationStore = useMessagingNotificationStore()

// Computed property for messaging badge count
const messagingBadgeCount = computed(() => {
  const count = messagingNotificationStore.totalUnreadCount
  return count > 0 ? count.toString() : null
})

// Navigation items
const navItems = computed(() => [
  {
    icon: Home,
    label: 'Home',
    path: '/alumni/home',
    badge: null
  },
  {
    icon: User,
    label: 'Profile',
    path: '/alumni/my-profile',
    badge: null
  },
  {
    icon: Users,
    label: 'Mates',
    path: '/alumni/my-mates',
    badge: null
  },
  {
    icon: MessageCircle,
    label: 'Messages',
    path: '/alumni/messaging',
    badge: messagingBadgeCount.value
  },
  {
    icon: FileText,
    label: 'Survey',
    path: '/alumni/survey',
    badge: '2'
  }
])

// Check if route is active
const isActive = (path) => {
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

<style scoped>
/* Safe area padding for devices with home indicator */
.safe-area-pb {
  padding-bottom: env(safe-area-inset-bottom, 0);
  min-height: calc(60px + env(safe-area-inset-bottom, 0));
}

/* Backdrop blur fallback */
@supports not (backdrop-filter: blur(12px)) {
  nav {
    background-color: rgba(255, 255, 255, 0.98);
  }

  .dark nav {
    background-color: rgba(31, 41, 55, 0.98);
  }
}
</style>
