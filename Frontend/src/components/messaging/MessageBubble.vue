<template>
  <div :class="['flex gap-3', isOwnMessage && 'flex-row-reverse']" :data-message-id="message.id">
    <!-- Avatar for other user's messages (not shown for own messages) -->
    <div v-if="!isOwnMessage" class="flex-shrink-0">
      <img 
        :src="getProfilePictureUrl(message.sender)" 
        :alt="`${message.sender.first_name} ${message.sender.last_name}`"
        class="w-8 h-8 rounded-full object-cover"
      />
    </div>

    <div :class="['flex flex-col max-w-[70%] relative group', isOwnMessage && 'items-end']">
      <!-- Pin indicator -->
      <div v-if="message.isPinned" class="flex items-center gap-1 mb-1 text-xs text-amber-600">
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
          <path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
        </svg>
        <span>Pinned</span>
      </div>

      <!-- Reply indicator with enhanced threading - REMOVED standalone version -->
      <!-- This will now be integrated inside the main message bubble -->

      <!-- Message Container with Menu Button -->
      <div class="relative flex items-start gap-2">
        <!-- Message Content / Attachment -->
        <div
          :class="[
            'relative shadow-sm flex-1',
            isOwnMessage ? 'bg-blue-500 text-white rounded-xl rounded-br-none' : 'bg-gray-100 text-gray-900 rounded-xl rounded-bl-none',
            // No padding for images, normal padding for text/files
            hasImageAttachment ? 'p-0 overflow-hidden' : 'px-4 py-2 break-words'
          ]"
          @contextmenu.prevent="handleRightClick"
          @click="handleClick"
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
          <!-- Edit mode -->
          <div v-if="isEditing" class="p-2">
            <textarea 
              v-model="editContent"
              class="w-full bg-transparent border border-gray-300 rounded p-2 text-sm resize-none"
              rows="2"
              @keydown.enter.ctrl="saveEdit"
              @keydown.escape="cancelEdit"
            ></textarea>
            <div class="flex gap-2 mt-2">
              <button 
                @click="saveEdit"
                class="px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600"
              >
                Save
              </button>
              <button 
                @click="cancelEdit"
                class="px-3 py-1 bg-gray-300 text-gray-700 text-xs rounded hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
          <!-- Normal display -->
          <div v-else>
            <!-- Reply preview inside the message bubble (WhatsApp/Telegram style) -->
            <div v-if="replyMessage" class="mb-3">
              <div :class="[
                'border-l-4 pl-3 py-2 rounded-r-md cursor-pointer transition-all duration-200 hover:bg-opacity-80',
                isOwnMessage 
                  ? 'border-white bg-white bg-opacity-20' 
                  : 'border-blue-500 bg-blue-50'
              ]" @click="scrollToOriginalMessage">
                <div class="flex items-center gap-2 mb-1">
                  <img 
                    :src="getProfilePictureUrl(replyMessage.sender)" 
                    :alt="replyMessage.sender.first_name"
                    class="w-4 h-4 rounded-full object-cover flex-shrink-0"
                  />
                  <span :class="[
                    'font-medium text-xs',
                    isOwnMessage ? 'text-white text-opacity-90' : 'text-blue-600'
                  ]">{{ replyMessage.sender.first_name }} {{ replyMessage.sender.last_name }}</span>
                </div>
                <!-- ✅ FIX: Always show the message content, not just for non-senders -->
                <p :class="[
                  'text-xs line-clamp-2 leading-tight',
                  isOwnMessage ? 'text-white text-opacity-80' : 'text-gray-700'
                ]">
                  {{ replyMessage.content || 'Attachment' }}
                </p>
              </div>
            </div>

            <!-- Main message content -->
            <div v-if="isEmojiOnlyMessage" class="text-4xl p-2">
              {{ message.content }}
            </div>
            <p v-else class="text-sm" v-html="formatMessageContent(message.content)"></p>
            <!-- Edit indicator -->
            <span v-if="message.isEdited" class="text-xs opacity-75 ml-1">(edited)</span>
          </div>
        </template>
        </div>

        <!-- Action Buttons Container -->
        <div :class="[
          'flex-shrink-0 flex items-center gap-1 transition-all duration-200',
          'opacity-0 group-hover:opacity-100',
          isOwnMessage ? 'order-first mr-2 flex-row-reverse' : 'order-last ml-2'
        ]">
          <!-- Reply Button -->
          <button
            @click="handleReply"
            class="w-6 h-6 rounded-full flex items-center justify-center hover:bg-blue-100 transition-all duration-200"
            title="Reply to message"
          >
            <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
            </svg>
          </button>

          <!-- Menu Button (Three Dots) -->
          <button
            @click="toggleMenu"
            class="w-6 h-6 rounded-full flex items-center justify-center hover:bg-gray-200 transition-all duration-200"
            title="Message options"
          >
            <svg class="w-4 h-4 text-gray-600" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
            </svg>
          </button>
        </div>
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

    <!-- Context Menu -->
    <MessageContextMenu
      :isVisible="showContextMenu"
      :message="message"
      :position="contextMenuPosition"
      :isOwnMessage="isOwnMessage"
      @close="showContextMenu = false"
      @action="handleAction"
    />
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import MessageContextMenu from './MessageContextMenu.vue'

const props = defineProps({
  message: Object,
  currentUserId: Number,
  messages: Array // Add this to access all messages for reply lookups
})

const emit = defineEmits(['message-action', 'scroll-to-message'])

// State for context menu
const showContextMenu = ref(false)
const contextMenuPosition = ref({ x: 0, y: 0 })

// State for editing
const isEditing = ref(false)
const editContent = ref('')

const isOwnMessage = computed(() => {
  return props.message.sender?.id === props.currentUserId // ✅ FIX
})

// Get the original message being replied to
const replyMessage = computed(() => {
  const message = props.message;
  const messagesArray = props.messages;
  
  if (!message) return null;
  
  // STEP 1: Check if the message has reply_to object directly from backend (most reliable)
  if (message.reply_to && typeof message.reply_to === 'object' && message.reply_to.id) {
    return message.reply_to
  }
  
  // STEP 2: Check for reply_to_id field and look it up in messages array
  const replyId = message.reply_to_id || (typeof message.reply_to === 'string' ? message.reply_to : null)
  if (replyId && messagesArray && Array.isArray(messagesArray) && messagesArray.length > 0) {
    // Try both exact match and string conversion
    const foundMessage = messagesArray.find(msg => {
      if (!msg || !msg.id) return false;
      return msg.id === replyId || 
             msg.id === String(replyId) || 
             String(msg.id) === String(replyId);
    });
    
    if (foundMessage) {
      return foundMessage
    }
  }
  
  return null
})

// Debug: Watch for message changes to see the structure (reduced logging)
watch(() => props.message, (newMessage) => {
  if (!newMessage) return
  
  if (newMessage.reply_to || newMessage.reply_to_id) {
    console.log('MessageBubble: Message with reply detected:', {
      id: newMessage.id,
      reply_to_exists: !!newMessage.reply_to,
      reply_to_id: newMessage.reply_to_id
    })
  }
}, { immediate: true })

// Format time display  
const formatTime = computed(() => {
  if (!props.message.timestamp) return ''
  return formatTimestamp(props.message.timestamp)
})

// Check if message contains only emojis for special styling
const isEmojiOnly = computed(() => {
  return isEmojiOnlyMessage.value
})

// Message classes for styling
const messageClasses = computed(() => {
  return [
    'message-bubble',
    'max-w-xs md:max-w-md lg:max-w-lg xl:max-w-xl',
    'p-3 rounded-lg shadow-sm',
    'break-words',
    isOwnMessage.value ? 'bg-blue-500 text-white ml-auto' : 'bg-gray-100 text-gray-800',
    props.message.is_pinned ? 'ring-2 ring-yellow-400' : '',
    isEmojiOnly.value ? 'text-3xl bg-transparent shadow-none p-1' : ''
  ]
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

// Check if message contains only emojis (for special large rendering)
const isEmojiOnlyMessage = computed(() => {
  if (!props.message.content) return false
  
  // Remove all emoji characters and check if anything remains
  const textWithoutEmojis = props.message.content.replace(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu, '').trim()
  
  // Consider it emoji-only if no text remains and original message has content
  return textWithoutEmojis.length === 0 && props.message.content.trim().length > 0
})

// Format message content with enhanced emoji rendering
const formatMessageContent = (content) => {
  if (!content) return ''
  
  // Enhanced emoji regex to match more emoji ranges
  const emojiRegex = /([\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}])/gu
  
  // Replace emojis with larger styled versions
  const formattedContent = content.replace(emojiRegex, '<span class="inline-block text-lg">$1</span>')
  
  // Replace line breaks with <br> tags
  return formattedContent.replace(/\n/g, '<br>')
}

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

// Context menu handlers
const handleRightClick = (event) => {
  event.preventDefault()
  contextMenuPosition.value = {
    x: event.clientX,
    y: event.clientY
  }
  showContextMenu.value = true
  console.log('MessageBubble: Context menu opened for message', props.message.id)
}

const handleClick = () => {
  if (showContextMenu.value) {
    showContextMenu.value = false
  }
}

const toggleMenu = (event) => {
  event.preventDefault()
  event.stopPropagation()
  
  const rect = event.currentTarget.getBoundingClientRect()
  contextMenuPosition.value = {
    x: rect.left + rect.width / 2,
    y: rect.bottom + 5
  }
  showContextMenu.value = !showContextMenu.value
  console.log('MessageBubble: Menu toggled via button for message', props.message.id)
}

const handleReply = (event) => {
  event.preventDefault()
  event.stopPropagation()
  
  console.log('MessageBubble: Reply button clicked for message', props.message.id)
  emit('message-action', {
    action: 'reply',
    message: props.message
  })
}

const handleAction = (actionData) => {
  console.log('MessageBubble: Action triggered:', actionData)
  const { action, message } = actionData
  
  switch (action) {
    case 'edit':
      startEdit()
      break
    case 'copy':
      copyMessage()
      break
    default:
      // Forward all other actions to parent
      emit('message-action', actionData)
      break
  }
}

// Edit functionality
const startEdit = () => {
  if (!isOwnMessage.value) return
  isEditing.value = true
  editContent.value = props.message.content
  console.log('MessageBubble: Started editing message', props.message.id)
}

const saveEdit = () => {
  if (editContent.value.trim() === props.message.content) {
    cancelEdit()
    return
  }
  
  console.log('MessageBubble: Saving edit for message', props.message.id, 'new content:', editContent.value)
  emit('message-action', {
    action: 'edit',
    message: props.message,
    newContent: editContent.value.trim()
  })
  isEditing.value = false
}

const cancelEdit = () => {
  isEditing.value = false
  editContent.value = ''
  console.log('MessageBubble: Cancelled editing message', props.message.id)
}

// Copy functionality
const copyMessage = () => {
  if (props.message.content) {
    navigator.clipboard.writeText(props.message.content).then(() => {
      console.log('MessageBubble: Message content copied to clipboard')
      // Could show a toast notification here
    }).catch(err => {
      console.error('MessageBubble: Failed to copy message:', err)
    })
  }
}

// Scroll to original message functionality
const scrollToOriginalMessage = () => {
  if (replyMessage.value) {
    console.log('MessageBubble: Scrolling to original message', replyMessage.value.id)
    emit('scroll-to-message', replyMessage.value.id)
  }
}
</script>

