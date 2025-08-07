<template>
  <div :class="['flex gap-3', isOwnMessage && 'flex-row-reverse']">
    <!-- Avatar for other user's messages (not shown for own messages) -->
    <div v-if="!isOwnMessage" class="flex-shrink-0">
      <img 
        :src="getProfilePictureUrl(message.sender)" 
        :alt="`${message.sender.first_name} ${message.sender.last_name}`"
        class="w-8 h-8 rounded-full object-cover"
      />
    </div>

    <div :class="['flex flex-col max-w-[70%]', isOwnMessage && 'items-end']">
      <!-- Message Content / Attachment -->
      <div
        :class="[
          'relative shadow-sm',
          isOwnMessage ? 'bg-blue-500 text-white rounded-xl rounded-br-none' : 'bg-gray-100 text-gray-900 rounded-xl rounded-bl-none',
          // No padding for images, normal padding for text/files
          hasImageAttachment ? 'p-0 overflow-hidden' : 'px-4 py-2 break-words'
        ]"
      >
        <!-- Render Image Attachments -->
        <template v-if="hasImageAttachment">
          <div class="space-y-2">
            <div 
              v-for="(attachment, index) in imageAttachments" 
              :key="index"
              class="relative"
            >
              <img
                :src="getAttachmentUrl(attachment)"
                :alt="attachment.name || 'Image'"
                class="max-w-full h-auto object-cover cursor-pointer"
                :class="isOwnMessage ? 'rounded-xl rounded-br-none' : 'rounded-xl rounded-bl-none'"
                style="max-height: 200px; max-width: 250px; min-width: 150px;"
                @click="openImageModal(getAttachmentUrl(attachment))"
              />
              <!-- Image overlay for file name/size if available -->
              <div v-if="attachment.name" class="absolute bottom-2 left-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
                {{ attachment.name }}
              </div>
            </div>
          </div>
          <!-- Text content below image if both exist -->
          <div v-if="message.content && message.content.trim()" class="px-4 py-2">
            <p class="text-sm">{{ message.content }}</p>
          </div>
        </template>

        <!-- Render File Attachments (PDF, DOC, etc.) -->
        <template v-else-if="hasFileAttachment">
          <div class="space-y-2">
            <div 
              v-for="(attachment, index) in fileAttachments" 
              :key="index"
              class="flex items-center space-x-3 p-3 rounded-lg cursor-pointer hover:bg-opacity-80 transition-all"
              :class="isOwnMessage ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'"
              @click="downloadFile(getAttachmentUrl(attachment), attachment.name)"
            >
              <!-- File Icon based on type -->
              <div class="flex-shrink-0">
                <svg v-if="getFileType(attachment) === 'pdf'" class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
                </svg>
                <svg v-else-if="getFileType(attachment) === 'doc'" class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
                </svg>
                <svg v-else class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-medium truncate">{{ attachment.name || 'File' }}</p>
                <p class="text-xs opacity-75">{{ getFileSize(attachment) }} • {{ getFileType(attachment).toUpperCase() }}</p>
              </div>
              <!-- Download icon -->
              <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
          <!-- Text content below files if both exist -->
          <div v-if="message.content && message.content.trim()" class="px-4 py-2 border-t border-gray-300">
            <p class="text-sm">{{ message.content }}</p>
          </div>
        </template>

        <!-- Render Text Content Only -->
        <template v-else>
          <p class="text-sm">{{ message.content }}</p>
        </template>
      </div>

      <!-- Timestamp and Read Status -->
      <div
        :class="[
          'flex items-center gap-1 mt-1 text-xs text-gray-500',
          isOwnMessage && 'flex-row-reverse'
        ]"
      >
        <span>{{ formatTimestamp(message.timestamp) }}</span>
        <span
          v-if="isOwnMessage"
          :class="message.isRead ? 'text-blue-500' : ''"
        >
          {{ message.isRead ? '✓✓' : '✓' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: Object,
  currentUserId: Number
})

const isOwnMessage = computed(() => {
  return props.message.sender?.id === props.currentUserId // ✅ FIX
})

// Helper function to get profile picture URL (same logic as AlumniNavbar)
const getProfilePictureUrl = (entity) => {
  const BASE_URL = 'http://127.0.0.1:8000' // Same as AlumniNavbar
  const pic = entity?.profile_picture
  return pic
    ? (pic.startsWith('http') ? pic : `${BASE_URL}${pic}`)
    : '/default-avatar.png'
};

// Format timestamp like messenger apps
const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''
  
  const messageDate = new Date(timestamp)
  const now = new Date()
  const diffInMilliseconds = now - messageDate
  const diffInHours = diffInMilliseconds / (1000 * 60 * 60)
  const diffInDays = Math.floor(diffInHours / 24)
  
  // Same day - show just time (e.g., "8:44 AM")
  if (diffInDays === 0) {
    return messageDate.toLocaleTimeString([], { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    })
  }
  
  // Yesterday - show "Yesterday" + time
  if (diffInDays === 1) {
    return `Yesterday ${messageDate.toLocaleTimeString([], { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    })}`
  }
  
  // This week (2-6 days ago) - show day + time (e.g., "Mon 10:13 PM")
  if (diffInDays < 7) {
    const dayName = messageDate.toLocaleDateString([], { weekday: 'short' })
    const time = messageDate.toLocaleTimeString([], { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    })
    return `${dayName} ${time}`
  }
  
  // More than a week - show full date + time (e.g., "Jul 26, 2025, 12:18 PM")
  return messageDate.toLocaleDateString([], {
    month: 'short',
    day: 'numeric', 
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  })
};

// Computed properties for attachments
const imageAttachments = computed(() => {
  const images = props.message.attachments?.filter(att => {
    const isImage = att.file && (
      // Check file_type from backend
      (att.file_type && att.file_type.startsWith('image/')) ||
      // Fallback: check file extension in URL
      att.file.toLowerCase().includes('.jpg') ||
      att.file.toLowerCase().includes('.jpeg') ||
      att.file.toLowerCase().includes('.png') ||
      att.file.toLowerCase().includes('.gif') ||
      att.file.toLowerCase().includes('.webp')
    )
    return isImage
  }) || []
  return images
})

const fileAttachments = computed(() => {
  return props.message.attachments?.filter(att => 
    att.file && !imageAttachments.value.includes(att)
  ) || []
})

const hasImageAttachment = computed(() => imageAttachments.value.length > 0)
const hasFileAttachment = computed(() => fileAttachments.value.length > 0)

// Helper methods for attachments (same logic as avatar)
const getAttachmentUrl = (attachment) => {
  // Backend now provides full URLs like avatars, so just return the file URL directly
  const url = attachment.file || '/default-file-icon.png'
  return url
}

const getFileType = (attachment) => {
  // Use file_type from backend first, then fallback to file extension
  if (attachment.file_type) {
    return attachment.file_type.split('/').pop() || 'file'
  }
  if (!attachment.file) return 'file'
  const extension = attachment.file.split('.').pop()?.toLowerCase()
  return extension || 'file'
}

const getFileSize = (attachment) => {
  // If size is available in attachment object
  if (attachment.size) {
    const bytes = attachment.size
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }
  return 'Unknown size'
}

// Image modal functionality
const openImageModal = (imageUrl) => {
  // Create a simple modal to view full-size image
  const modal = document.createElement('div')
  modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75'
  modal.innerHTML = `
    <div class="relative max-w-4xl max-h-full p-4">
      <img src="${imageUrl}" class="max-w-full max-h-full object-contain" />
      <button class="absolute top-4 right-4 text-white hover:text-gray-300 text-3xl">&times;</button>
    </div>
  `
  
  modal.addEventListener('click', (e) => {
    if (e.target === modal || e.target.textContent === '×') {
      document.body.removeChild(modal)
    }
  })
  
  document.body.appendChild(modal)
}

// File download functionality
const downloadFile = (fileUrl, fileName) => {
  const link = document.createElement('a')
  link.href = fileUrl
  link.download = fileName || 'download'
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

