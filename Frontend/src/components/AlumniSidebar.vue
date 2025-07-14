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
      <SidebarItem :icon="MessageSquare" label="Messaging" to="/alumni/messaging" :expanded="isExpanded" badge="10" />
      <SidebarItem :icon="ClipboardList" label="Survey" to="/alumni/survey" :expanded="isExpanded" badge="2" />
      <SidebarItem :icon="Heart" label="Donate" to="/alumni/donate" :expanded="isExpanded" />
      <SidebarItem :icon="Settings" label="Settings" to="/alumni/settings" :expanded="isExpanded" />
    </nav>
  </div>
</template>

<script setup>
import SidebarItem from './SidebarItem.vue'

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

defineProps(['isExpanded'])
</script>
