<template>
  <div :class="themeStore.isDarkMode ? 'flex items-start justify-between p-6 pb-4 bg-gray-700' : 'flex items-start justify-between p-6 pb-4 bg-white'">
    <div class="flex items-start space-x-4">
      <img :src="post.user?.profile_picture || '/default-avatar.png'" alt="Profile"
        :class="themeStore.isDarkMode ? 'w-16 h-16 rounded-full object-cover border-4 border-gray-600 shadow-lg' : 'w-16 h-16 rounded-full object-cover border-4 border-blue-200 shadow-lg'" />
      <div>
        <div class="flex items-center space-x-3">
          <h3 :class="themeStore.isDarkMode ? 'text-lg font-bold text-gray-100' : 'text-lg font-bold text-slate-800'">
            {{ post.user?.first_name }} {{ post.user?.last_name }}
          </h3>

        </div>
        <div :class="themeStore.isDarkMode ? 'flex items-center space-x-3 text-md text-gray-400 mt-1' : 'flex items-center space-x-3 text-md text-slate-600 mt-1'">
          <span class="font-medium">{{ formatTimeAgo(post.created_at) }}</span>
          <span :class="themeStore.isDarkMode ? 'text-gray-500' : 'text-slate-400'">•</span>
          <span
            :class="themeStore.isDarkMode ? 'capitalize font-medium cursor-pointer hover:bg-gray-600 transition-colors flex items-center space-x-1' : 'capitalize font-medium cursor-pointer hover:bg-slate-200 transition-colors flex items-center space-x-1'">
            <span :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-slate-500'" 
                  v-html="getIconSVG(categories.find(c => c.value === post.content_category)?.icon || 'document')"></span>
            <span>{{ post.content_category }}</span>
          </span>
          <span v-if="post.post_type === 'shared'"
            :class="themeStore.isDarkMode ? 'text-gray-300 px-1 py-1 rounded-full font-medium' : 'text-slate-700 px-1 py-1 rounded-full font-medium'">
            🔄 Shared
          </span>
        </div>
      </div>
    </div>

    <!-- Post Menu -->
    <PostMenu 
      :post="post" 
      @deleted="handlePostDeleted"
      @pinned="handlePostPinned"
      @reported="handlePostReported"
    />
  </div>
</template>

<script setup>
import { useThemeStore } from '@/stores/theme'
import PostMenu from './PostMenu.vue'

// Theme store
const themeStore = useThemeStore()

// Props
const props = defineProps({
  post: {
    type: Object,
    required: true
  },
  categories: {
    type: Array,
    required: true
  }
})

// Emits
const emit = defineEmits(['deleted', 'pinned', 'reported'])

// Methods
const formatTimeAgo = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInSeconds = Math.floor((now - date) / 1000)

  if (diffInSeconds < 60) return 'Just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`

  return date.toLocaleDateString()
}

// Icon component mapper - same as AlumniHome
const getIconSVG = (iconName) => {
  const icons = {
    grid: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path></svg>`,
    chat: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>`,
    megaphone: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z"></path></svg>`,
    calendar: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>`,
    newspaper: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"></path></svg>`,
    briefcase: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0H8m8 0v2a2 2 0 002 2v8a2 2 0 01-2 2H6a2 2 0 01-2-2v-8a2 2 0 012-2V8a2 2 0 012-2z"></path></svg>`,
    document: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>`
  };
  return icons[iconName] || icons.document;
}

// Event handlers
const handlePostDeleted = (data) => {
  emit('deleted', data)
}

const handlePostPinned = (data) => {
  emit('pinned', data)
}

const handlePostReported = (data) => {
  emit('reported', data)
}
</script>

<style scoped>
/* Smooth transitions for all interactive elements */
.transition-colors {
  transition: all 0.3s ease;
}
</style>
