<template>
  <div v-if="pinnedMessages.length > 0" class="bg-amber-50 border-b border-amber-200 p-3">
    <!-- Header -->
    <div class="flex items-center justify-between mb-2">
      <div class="flex items-center gap-2">
        <svg class="w-4 h-4 text-amber-600" fill="currentColor" viewBox="0 0 24 24">
          <path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
        </svg>
        <span class="text-sm font-medium text-amber-800">
          {{ pinnedMessages.length }} Pinned Message{{ pinnedMessages.length > 1 ? 's' : '' }}
        </span>
      </div>
      <button 
        @click="toggleExpanded" 
        class="p-1 rounded hover:bg-amber-100 transition-colors"
      >
        <svg 
          :class="['w-4 h-4 text-amber-600 transition-transform', expanded ? 'rotate-180' : '']" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
    </div>

    <!-- Pinned Messages List -->
    <div v-if="expanded" class="space-y-2 max-h-60 overflow-y-auto">
      <div 
        v-for="message in pinnedMessages" 
        :key="message.id"
        class="bg-white rounded-lg p-2 border border-amber-200 cursor-pointer hover:bg-amber-25 transition-colors"
        @click="scrollToMessage(message.id)"
      >
        <!-- Message Header -->
        <div class="flex items-center gap-2 mb-1">
          <img 
            :src="getProfilePictureUrl(message.sender)" 
            :alt="message.sender.first_name"
            class="w-5 h-5 rounded-full object-cover"
          />
          <span class="text-xs font-medium text-gray-700">
            {{ message.sender.first_name }} {{ message.sender.last_name }}
          </span>
          <span class="text-xs text-gray-500">
            {{ formatTimestamp(message.timestamp) }}
          </span>
        </div>

        <!-- Message Content Preview -->
        <div class="text-sm text-gray-800">
          <!-- Image attachment preview -->
          <div v-if="hasImageAttachment(message)" class="flex items-center gap-2 mb-1">
            <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span class="text-gray-600">{{ getImageAttachmentCount(message) }} image{{ getImageAttachmentCount(message) > 1 ? 's' : '' }}</span>
          </div>

          <!-- File attachment preview -->
          <div v-if="hasFileAttachment(message)" class="flex items-center gap-2 mb-1">
            <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span class="text-gray-600">{{ getFileAttachmentCount(message) }} file{{ getFileAttachmentCount(message) > 1 ? 's' : '' }}</span>
          </div>

          <!-- Text content -->
          <p v-if="message.content" class="line-clamp-2">
            {{ message.content }}
          </p>
          <p v-else-if="!hasAttachments(message)" class="text-gray-500 italic">
            No content
          </p>
        </div>
      </div>
    </div>

    <!-- Collapsed view - show only first pinned message -->
    <div v-else-if="pinnedMessages.length > 0" class="bg-white rounded-lg p-2 border border-amber-200 cursor-pointer hover:bg-amber-25 transition-colors" @click="scrollToMessage(pinnedMessages[0].id)">
      <div class="flex items-center gap-2">
        <img 
          :src="getProfilePictureUrl(pinnedMessages[0].sender)" 
          :alt="pinnedMessages[0].sender.first_name"
          class="w-5 h-5 rounded-full object-cover"
        />
        <span class="text-xs font-medium text-gray-700">
          {{ pinnedMessages[0].sender.first_name }}
        </span>
        <span class="text-xs text-gray-800 flex-1 truncate">
          {{ pinnedMessages[0].content || getAttachmentPreview(pinnedMessages[0]) }}
        </span>
        <span v-if="pinnedMessages.length > 1" class="text-xs text-amber-600">
          +{{ pinnedMessages.length - 1 }} more
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  },
  currentUser: {
    type: Object,
    required: true
  },
  conversation: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['scroll-to-message'])

const expanded = ref(false)

// Computed properties
const pinnedMessages = computed(() => {
  return props.messages
    .filter(message => message.is_pinned)
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)) // Most recent first
})

// Methods
const toggleExpanded = () => {
  expanded.value = !expanded.value
}

const scrollToMessage = (messageId) => {
  emit('scroll-to-message', messageId)
}

// Helper methods for profile pictures
const getProfilePictureUrl = (entity) => {
  const BASE_URL = 'http://127.0.0.1:8000'
  const pic = entity?.profile_picture
  return pic
    ? (pic.startsWith('http') ? pic : `${BASE_URL}${pic}`)
    : '/default-avatar.png'
}

// Helper methods for attachments
const hasAttachments = (message) => {
  return message.attachments && message.attachments.length > 0
}

const hasImageAttachment = (message) => {
  return message.attachments?.some(att => 
    att.file_type && att.file_type.startsWith('image/')
  ) || false
}

const hasFileAttachment = (message) => {
  return message.attachments?.some(att => 
    att.file_type && !att.file_type.startsWith('image/')
  ) || false
}

const getImageAttachmentCount = (message) => {
  return message.attachments?.filter(att => 
    att.file_type && att.file_type.startsWith('image/')
  ).length || 0
}

const getFileAttachmentCount = (message) => {
  return message.attachments?.filter(att => 
    att.file_type && !att.file_type.startsWith('image/')
  ).length || 0
}

const getAttachmentPreview = (message) => {
  if (hasImageAttachment(message)) {
    const count = getImageAttachmentCount(message)
    return `📷 ${count} image${count > 1 ? 's' : ''}`
  } else if (hasFileAttachment(message)) {
    const count = getFileAttachmentCount(message)
    return `📎 ${count} file${count > 1 ? 's' : ''}`
  }
  return 'Attachment'
}

// Format timestamp
const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''
  
  const messageDate = new Date(timestamp)
  const now = new Date()
  const diffInMilliseconds = now - messageDate
  const diffInHours = diffInMilliseconds / (1000 * 60 * 60)
  const diffInDays = Math.floor(diffInHours / 24)
  
  // Same day - show just time
  if (diffInDays === 0) {
    return messageDate.toLocaleTimeString([], { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    })
  }
  
  // Yesterday
  if (diffInDays === 1) {
    return 'Yesterday'
  }
  
  // This week
  if (diffInDays < 7) {
    return messageDate.toLocaleDateString([], { weekday: 'short' })
  }
  
  // Older
  return messageDate.toLocaleDateString([], {
    month: 'short',
    day: 'numeric'
  })
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Custom scrollbar for pinned messages */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #fef3c7;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #f59e0b;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #d97706;
}
</style>
