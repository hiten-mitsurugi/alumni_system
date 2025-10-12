<template>
  <div :class="themeStore.isAdminDark() ? 'flex items-start justify-between p-6 pb-4 bg-gray-700' : 'flex items-start justify-between p-6 pb-4 bg-white'">
    <div class="flex items-start space-x-4">
      <img :src="post.user?.profile_picture || '/default-avatar.png'" alt="Profile"
        :class="themeStore.isAdminDark() ? 'w-16 h-16 rounded-full object-cover border-4 border-gray-600 shadow-lg' : 'w-16 h-16 rounded-full object-cover border-4 border-blue-200 shadow-lg'" />
      <div>
        <div class="flex items-center space-x-3">
          <h3 :class="themeStore.isAdminDark() ? 'text-lg font-bold text-gray-100' : 'text-lg font-bold text-slate-800'">
            {{ post.user?.first_name }} {{ post.user?.last_name }}
          </h3>

        </div>
        <div :class="themeStore.isAdminDark() ? 'flex items-center space-x-3 text-md text-gray-400 mt-1' : 'flex items-center space-x-3 text-md text-slate-600 mt-1'">
          <span class="font-medium">{{ formatTimeAgo(post.created_at) }}</span>
          <span :class="themeStore.isAdminDark() ? 'text-gray-500' : 'text-slate-400'">•</span>
          <span
            :class="themeStore.isAdminDark() ? 'capitalize font-medium cursor-pointer hover:bg-gray-600 transition-colors' : 'capitalize font-medium cursor-pointer hover:bg-slate-200 transition-colors'">
            {{categories.find(c => c.value === post.content_category)?.icon || '📝'}}
            {{ post.content_category }}
          </span>
          <span v-if="post.post_type === 'shared'"
            :class="themeStore.isAdminDark() ? 'text-gray-300 px-1 py-1 rounded-full font-medium' : 'text-slate-700 px-1 py-1 rounded-full font-medium'">
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
