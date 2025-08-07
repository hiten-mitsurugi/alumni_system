<template>
  <div :class="['flex gap-3', isOwnMessage && 'flex-row-reverse']" :data-message-id="message.id">
    <!-- Avatar (for other user's messages only) -->
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

      <!-- Message Container -->
      <div class="relative flex items-start gap-2">
        <!-- Main Message Bubble -->
        <div
          :class="messageClasses"
          @contextmenu.prevent="handleRightClick"
          @click="handleClick"
        >
          <!-- Image Attachments -->
          <template v-if="hasImageAttachment">
            <div class="space-y-2">
              <div v-for="(attachment, index) in imageAttachments" :key="index" class="relative">
                <img
                  :src="getAttachmentUrl(attachment)"
                  :alt="attachment.name || 'Image'"
                  class="max-w-full h-auto object-cover cursor-pointer rounded-lg"
                  style="max-height: 200px; max-width: 250px; min-width: 150px;"
                  @click="openImageModal(getAttachmentUrl(attachment))"
                />
                <div v-if="attachment.name" class="absolute bottom-2 left-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
                  {{ attachment.name }}
                </div>
              </div>
            </div>
            <!-- Text content below image -->
            <div v-if="message.content?.trim()" class="px-4 py-2">
              <p class="text-sm">{{ message.content }}</p>
            </div>
          </template>

          <!-- File Attachments -->
          <template v-else-if="hasFileAttachment">
            <div class="space-y-2">
              <div 
                v-for="(attachment, index) in fileAttachments" 
                :key="index"
                class="flex items-center space-x-3 p-3 rounded-lg cursor-pointer hover:bg-opacity-80 transition-all"
                :class="isOwnMessage ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'"
                @click="downloadFile(getAttachmentUrl(attachment), attachment.name)"
              >
                <FileIcon :fileType="getFileType(attachment)" />
                <div class="flex-1 min-w-0">
                  <p class="font-medium truncate">{{ attachment.name || 'File' }}</p>
                  <p class="text-xs opacity-75">{{ getFileSize(attachment) }} • {{ getFileType(attachment).toUpperCase() }}</p>
                </div>
                <DownloadIcon />
              </div>
            </div>
            <!-- Text content below files -->
            <div v-if="message.content?.trim()" class="px-4 py-2 border-t border-gray-300">
              <p class="text-sm">{{ message.content }}</p>
            </div>
          </template>

          <!-- Text Content Only -->
          <template v-else>
            <!-- Edit Mode -->
            <div v-if="isEditing" class="p-2">
              <textarea 
                v-model="editContent"
                class="w-full bg-transparent border border-gray-300 rounded p-2 text-sm resize-none"
                rows="2"
                @keydown.enter.ctrl="saveEdit"
                @keydown.escape="cancelEdit"
              />
              <div class="flex gap-2 mt-2">
                <button @click="saveEdit" class="px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600">
                  Save
                </button>
                <button @click="cancelEdit" class="px-3 py-1 bg-gray-300 text-gray-700 text-xs rounded hover:bg-gray-400">
                  Cancel
                </button>
              </div>
            </div>
            
            <!-- Normal Display -->
            <div v-else>
              <!-- Reply Preview (WhatsApp style) -->
              <ReplyPreview 
                v-if="replyMessage" 
                :replyMessage="replyMessage"
                :isOwnMessage="isOwnMessage"
                @click="scrollToOriginalMessage"
              />

              <!-- Main Content -->
              <div v-if="isEmojiOnlyMessage" class="text-4xl p-2">
                {{ message.content }}
              </div>
              <p v-else class="text-sm" v-html="formatMessageContent(message.content)" />
              
              <!-- Edit Indicator -->
              <span v-if="message.isEdited" class="text-xs opacity-75 ml-1">(edited)</span>
            </div>
          </template>
        </div>

        <!-- Action Buttons -->
        <MessageActions 
          :isOwnMessage="isOwnMessage"
          @reply="handleReply"
          @menu="toggleMenu"
        />
      </div>

      <!-- Timestamp and Read Status -->
      <MessageTimestamp 
        :message="message"
        :isOwnMessage="isOwnMessage"
      />
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

// ===== PROPS & EMITS =====
const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  currentUserId: {
    type: Number,
    required: true
  },
  messages: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['message-action', 'scroll-to-message'])

// ===== REACTIVE STATE =====
const showContextMenu = ref(false)
const contextMenuPosition = ref({ x: 0, y: 0 })
const isEditing = ref(false)
const editContent = ref('')

// ===== COMPUTED PROPERTIES =====

/**
 * Check if this message belongs to the current user
 */
const isOwnMessage = computed(() => {
  return props.message.sender?.id === props.currentUserId
})

/**
 * Find the original message being replied to
 */
const replyMessage = computed(() => {
  const { message, messages } = props
  
  if (!message) return null
  
  // First check if message has reply_to object from backend
  if (message.reply_to?.id) {
    return message.reply_to
  }
  
  // Then look up reply_to_id in messages array
  const replyId = message.reply_to_id
  if (replyId && messages?.length) {
    return messages.find(msg => 
      msg?.id === replyId || 
      String(msg?.id) === String(replyId)
    ) || null
  }
  
  return null
})

/**
 * CSS classes for the message bubble
 */
const messageClasses = computed(() => [
  'relative shadow-sm flex-1',
  isOwnMessage.value 
    ? 'bg-blue-500 text-white rounded-xl rounded-br-none' 
    : 'bg-gray-100 text-gray-900 rounded-xl rounded-bl-none',
  hasImageAttachment.value ? 'p-0 overflow-hidden' : 'px-4 py-2 break-words'
])

/**
 * Filter image attachments
 */
const imageAttachments = computed(() => {
  return props.message.attachments?.filter(att => {
    const isImage = att.file && (
      (att.file_type?.startsWith('image/')) ||
      /\.(jpg|jpeg|png|gif|webp)$/i.test(att.file)
    )
    return isImage
  }) || []
})

/**
 * Filter file attachments (non-images)
 */
const fileAttachments = computed(() => {
  return props.message.attachments?.filter(att => 
    att.file && !imageAttachments.value.includes(att)
  ) || []
})

const hasImageAttachment = computed(() => imageAttachments.value.length > 0)
const hasFileAttachment = computed(() => fileAttachments.value.length > 0)

/**
 * Check if message contains only emojis
 */
const isEmojiOnlyMessage = computed(() => {
  if (!props.message.content) return false
  
  const textWithoutEmojis = props.message.content.replace(
    /[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu, 
    ''
  ).trim()
  
  return textWithoutEmojis.length === 0 && props.message.content.trim().length > 0
})

// ===== UTILITY FUNCTIONS =====

/**
 * Get profile picture URL with fallback
 */
const getProfilePictureUrl = (entity) => {
  const BASE_URL = 'http://127.0.0.1:8000'
  const pic = entity?.profile_picture
  return pic?.startsWith('http') ? pic : pic ? `${BASE_URL}${pic}` : '/default-avatar.png'
}

/**
 * Get attachment URL
 */
const getAttachmentUrl = (attachment) => {
  return attachment.file || '/default-file-icon.png'
}

/**
 * Get file type from attachment
 */
const getFileType = (attachment) => {
  if (attachment.file_type) {
    return attachment.file_type.split('/').pop() || 'file'
  }
  const extension = attachment.file?.split('.').pop()?.toLowerCase()
  return extension || 'file'
}

/**
 * Format file size for display
 */
const getFileSize = (attachment) => {
  if (!attachment.size) return 'Unknown size'
  
  const bytes = attachment.size
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * Format message content with emoji enhancement
 */
const formatMessageContent = (content) => {
  if (!content) return ''
  
  const emojiRegex = /([\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}])/gu
  
  return content
    .replace(emojiRegex, '<span class="inline-block text-lg">$1</span>')
    .replace(/\n/g, '<br>')
}

// ===== EVENT HANDLERS =====

/**
 * Handle right-click context menu
 */
const handleRightClick = (event) => {
  event.preventDefault()
  contextMenuPosition.value = { x: event.clientX, y: event.clientY }
  showContextMenu.value = true
}

/**
 * Handle click to close context menu
 */
const handleClick = () => {
  if (showContextMenu.value) {
    showContextMenu.value = false
  }
}

/**
 * Toggle action menu
 */
const toggleMenu = (event) => {
  event.preventDefault()
  event.stopPropagation()
  
  const rect = event.currentTarget.getBoundingClientRect()
  contextMenuPosition.value = {
    x: rect.left + rect.width / 2,
    y: rect.bottom + 5
  }
  showContextMenu.value = !showContextMenu.value
}

/**
 * Handle reply button click
 */
const handleReply = (event) => {
  event.preventDefault()
  event.stopPropagation()
  
  emit('message-action', {
    action: 'reply',
    message: props.message
  })
}

/**
 * Handle various message actions
 */
const handleAction = (actionData) => {
  const { action } = actionData
  
  switch (action) {
    case 'edit':
      startEdit()
      break
    case 'copy':
      copyMessage()
      break
    default:
      emit('message-action', actionData)
      break
  }
}

/**
 * Start editing message
 */
const startEdit = () => {
  if (!isOwnMessage.value) return
  
  isEditing.value = true
  editContent.value = props.message.content
}

/**
 * Save edited message
 */
const saveEdit = () => {
  const trimmedContent = editContent.value.trim()
  
  if (trimmedContent === props.message.content) {
    cancelEdit()
    return
  }
  
  emit('message-action', {
    action: 'edit',
    message: props.message,
    newContent: trimmedContent
  })
  
  isEditing.value = false
}

/**
 * Cancel editing
 */
const cancelEdit = () => {
  isEditing.value = false
  editContent.value = ''
}

/**
 * Copy message content to clipboard
 */
const copyMessage = () => {
  if (props.message.content) {
    navigator.clipboard.writeText(props.message.content).catch(err => {
      console.error('Failed to copy message:', err)
    })
  }
}

/**
 * Open image in modal
 */
const openImageModal = (imageUrl) => {
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

/**
 * Download file
 */
const downloadFile = (fileUrl, fileName) => {
  const link = document.createElement('a')
  link.href = fileUrl
  link.download = fileName || 'download'
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * Scroll to original message
 */
const scrollToOriginalMessage = () => {
  if (replyMessage.value) {
    emit('scroll-to-message', replyMessage.value.id)
  }
}

// ===== WATCHERS =====

/**
 * Debug watch for messages with replies
 */
watch(() => props.message, (newMessage) => {
  if (newMessage?.reply_to || newMessage?.reply_to_id) {
    console.log('MessageBubble: Message with reply detected:', {
      id: newMessage.id,
      hasReplyObject: !!newMessage.reply_to,
      hasReplyId: !!newMessage.reply_to_id
    })
  }
}, { immediate: true })
</script>

<!-- Separate component files for better organization -->
<script>
// File Icon Component
const FileIcon = {
  props: ['fileType'],
  template: `
    <div class="flex-shrink-0">
      <svg v-if="fileType === 'pdf'" class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
        <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
      </svg>
      <svg v-else class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
        <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
      </svg>
    </div>
  `
}

// Download Icon Component
const DownloadIcon = {
  template: `
    <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  `
}

// Reply Preview Component
const ReplyPreview = {
  props: ['replyMessage', 'isOwnMessage'],
  emits: ['click'],
  template: `
    <div class="mb-3">
      <div 
        :class="[
          'border-l-4 pl-3 py-2 rounded-r-md cursor-pointer transition-all duration-200 hover:bg-opacity-80',
          isOwnMessage 
            ? 'border-white bg-white bg-opacity-20' 
            : 'border-blue-500 bg-blue-50'
        ]" 
        @click="$emit('click')"
      >
        <div class="flex items-center gap-2 mb-1">
          <img 
            :src="getProfilePictureUrl(replyMessage.sender)" 
            :alt="replyMessage.sender.first_name"
            class="w-4 h-4 rounded-full object-cover flex-shrink-0"
          />
          <span :class="[
            'font-medium text-xs',
            isOwnMessage ? 'text-white text-opacity-90' : 'text-blue-600'
          ]">
            {{ replyMessage.sender.first_name }} {{ replyMessage.sender.last_name }}
          </span>
        </div>
        <p :class="[
          'text-xs line-clamp-2 leading-tight',
          isOwnMessage ? 'text-white text-opacity-80' : 'text-gray-700'
        ]">
          {{ replyMessage.content || 'Attachment' }}
        </p>
      </div>
    </div>
  `,
  methods: {
    getProfilePictureUrl(entity) {
      const BASE_URL = 'http://127.0.0.1:8000'
      const pic = entity?.profile_picture
      return pic?.startsWith('http') ? pic : pic ? `${BASE_URL}${pic}` : '/default-avatar.png'
    }
  }
}

// Message Actions Component
const MessageActions = {
  props: ['isOwnMessage'],
  emits: ['reply', 'menu'],
  template: `
    <div :class="[
      'flex-shrink-0 flex items-center gap-1 transition-all duration-200',
      'opacity-0 group-hover:opacity-100',
      isOwnMessage ? 'order-first mr-2 flex-row-reverse' : 'order-last ml-2'
    ]">
      <!-- Reply Button -->
      <button
        @click="$emit('reply')"
        class="w-6 h-6 rounded-full flex items-center justify-center hover:bg-blue-100 transition-all duration-200"
        title="Reply to message"
      >
        <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
        </svg>
      </button>

      <!-- Menu Button -->
      <button
        @click="$emit('menu')"
        class="w-6 h-6 rounded-full flex items-center justify-center hover:bg-gray-200 transition-all duration-200"
        title="Message options"
      >
        <svg class="w-4 h-4 text-gray-600" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
        </svg>
      </button>
    </div>
  `
}

// Message Timestamp Component
const MessageTimestamp = {
  props: ['message', 'isOwnMessage'],
  template: `
    <div :class="[
      'flex items-center gap-1 mt-1 text-xs text-gray-500',
      isOwnMessage && 'flex-row-reverse'
    ]">
      <span>{{ formatTimestamp(message.timestamp) }}</span>
      <span
        v-if="isOwnMessage"
        :class="message.isRead ? 'text-blue-500' : ''"
      >
        {{ message.isRead ? '✓✓' : '✓' }}
      </span>
    </div>
  `,
  methods: {
    formatTimestamp(timestamp) {
      if (!timestamp) return ''
      
      const messageDate = new Date(timestamp)
      const now = new Date()
      const diffInHours = (now - messageDate) / (1000 * 60 * 60)
      const diffInDays = Math.floor(diffInHours / 24)
      
      if (diffInDays === 0) {
        return messageDate.toLocaleTimeString([], { 
          hour: 'numeric', 
          minute: '2-digit',
          hour12: true 
        })
      }
      
      if (diffInDays === 1) {
        return `Yesterday ${messageDate.toLocaleTimeString([], { 
          hour: 'numeric', 
          minute: '2-digit',
          hour12: true 
        })}`
      }
      
      if (diffInDays < 7) {
        const dayName = messageDate.toLocaleDateString([], { weekday: 'short' })
        const time = messageDate.toLocaleTimeString([], { 
          hour: 'numeric', 
          minute: '2-digit',
          hour12: true 
        })
        return `${dayName} ${time}`
      }
      
      return messageDate.toLocaleDateString([], {
        month: 'short',
        day: 'numeric', 
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      })
    }
  }
}

export default {
  components: {
    FileIcon,
    DownloadIcon,
    ReplyPreview,
    MessageActions,
    MessageTimestamp,
    MessageContextMenu
  }
}
</script>
