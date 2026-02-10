<template>
 <div class="flex-1 overflow-y-auto">
 <div v-if="conversations.length === 0"
 :class="[
   'p-8 text-center',
   $root && $root.$refs.themeStore?.isDarkMode ? 'text-gray-400' : 'text-slate-500'
 ]">
 <p class="text-lg">No conversations yet</p>
 <p class="text-sm mt-2">Start a new conversation by clicking the search bar above</p>
 </div>
 
 <div v-for="conv in conversations" :key="conv.id"
 @click="$emit('select', conv)"
 @mouseenter="!isMobile && $emit('prefetch', conv)"
 :class="[
   'flex items-center p-3 md:p-4 cursor-pointer transition-all duration-200 border-b',
   selectedConversation && selectedConversation.id === conv.id
     ? isDarkMode
       ? 'bg-blue-900/30 border-blue-700'
       : 'bg-blue-50 border-blue-200'
     : isDarkMode
       ? 'hover:bg-gray-700/50 border-gray-700'
       : 'hover:bg-slate-50 border-slate-200/60'
 ]">
 
 <!-- Avatar -->
 <div class="relative mr-3 flex-shrink-0">
 <img
 :src="getConversationAvatar(conv)"
 alt=""
 class="w-12 h-12 md:w-14 md:h-14 rounded-full object-cover ring-2"
 :class="selectedConversation && selectedConversation.id === conv.id
   ? 'ring-blue-500'
   : isDarkMode ? 'ring-gray-700' : 'ring-slate-200'"
 />
 <span
 v-if="conv.unreadCount > 0"
 class="absolute -top-1 -right-1 bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs rounded-full min-w-[20px] h-5 flex items-center justify-center font-semibold shadow-lg"
 >
 {{ conv.unreadCount > 99 ? '99+' : conv.unreadCount }}
 </span>
 </div>
 
 <!-- Content -->
 <div class="flex-1 min-w-0">
 <div class="flex items-center justify-between mb-1">
 <p :class="[
   'font-semibold truncate',
   isDarkMode ? 'text-gray-100' : 'text-slate-800'
 ]">
 {{ getConversationName(conv) }}
 </p>
 <span :class="[
   'text-xs whitespace-nowrap ml-2',
   isDarkMode ? 'text-gray-400' : 'text-slate-500'
 ]">
 {{ formatTimestamp(conv.timestamp) }}
 </span>
 </div>
 
 <!-- Last Message Preview -->
 <div class="flex items-center">
 <p :class="[
   'text-sm truncate',
   conv.unreadCount > 0
     ? isDarkMode ? 'text-gray-200 font-medium' : 'text-slate-700 font-medium'
     : isDarkMode ? 'text-gray-400' : 'text-slate-500'
 ]">
 {{ getLastMessagePreview(conv) }}
 </p>
 </div>
 
 <!-- Status Indicators -->
 <div v-if="conv.isPending" class="flex items-center gap-1 mt-1">
 <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800">
 <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
 <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
 </svg>
 Pending
 </span>
 </div>
 </div>
 </div>
 </div>
</template>

<script setup>
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { getProfilePictureUrl } from '@/utils/imageUrl'

const props = defineProps({
  conversations: {
    type: Array,
    required: true
  },
  selectedConversation: {
    type: Object,
    default: null
  },
  isMobile: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select', 'prefetch'])

const themeStore = useThemeStore()
const isDarkMode = computed(() => themeStore.isDarkMode)

function getConversationAvatar(conv) {
  if (conv.type === 'private') {
    return getProfilePictureUrl(conv.mate?.profile_picture)
  } else {
    return getProfilePictureUrl(conv.group?.group_picture)
  }
}

function getConversationName(conv) {
  if (conv.type === 'private') {
    return `${conv.mate?.first_name || ''} ${conv.mate?.last_name || ''}`.trim() || 'Unknown User'
  } else {
    return conv.group?.name || 'Unnamed Group'
  }
}

function getLastMessagePreview(conv) {
  if (!conv.lastMessage) return 'No messages yet'
  
  const maxLength = 40
  let message = conv.lastMessage
  
  // Remove [Pending] prefix if exists
  message = message.replace('[Pending] ', '')
  
  if (message.length > maxLength) {
    return message.substring(0, maxLength) + '...'
  }
  
  return message
}

function formatTimestamp(timestamp) {
  if (!timestamp) return ''
  
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  // Less than 1 minute
  if (diff < 60000) {
    return 'Just now'
  }
  
  // Less than 1 hour
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000)
    return `${minutes}m ago`
  }
  
  // Less than 24 hours
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000)
    return `${hours}h ago`
  }
  
  // Less than 7 days
  if (diff < 604800000) {
    const days = Math.floor(diff / 86400000)
    return `${days}d ago`
  }
  
  // Older than 7 days
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}
</script>
