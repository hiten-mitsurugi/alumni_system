<template>
  <div :class="['flex gap-3', isSystemMessage ? 'justify-center' : isOwnMessage && 'flex-row-reverse']" :data-message-id="message.id">
    <!-- Avatar for other user's messages (not shown for own messages or system messages) -->
    <div v-if="!isOwnMessage && !isSystemMessage" class="flex-shrink-0">
      <img 
        :src="getProfilePictureUrl(message.sender)" 
        :alt="`${message.sender.first_name} ${message.sender.last_name}`"
        class="w-8 h-8 rounded-full object-cover"
      />
    </div>

    <div :class="['flex flex-col max-w-[70%] relative group', isSystemMessage ? 'items-center' : isOwnMessage && 'items-end']">
      <!-- Pin indicator -->
      <div v-if="message.is_pinned" class="flex items-center gap-1 mb-1 text-xs text-amber-600">
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
          <path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
        </svg>
        <span>Pinned</span>
      </div>

      <!-- Forward indicator -->
      <div v-if="message.is_forwarded" class="flex items-center gap-1 mb-1 text-xs text-green-600">
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M13 5l7 7-7 7M5 5l7 7-7 7" />
        </svg>
        <span>Forwarded</span>
      </div>

      <!-- Reply indicator with enhanced threading - REMOVED standalone version -->
      <!-- This will now be integrated inside the main message bubble -->

      <!-- Message Container with Menu Button -->
      <div class="relative flex items-start gap-2">
        <!-- Message Content / Attachment -->
        <div
          :class="[
            'relative shadow-sm flex-1',
            isSystemMessage ? 'bg-yellow-100 rounded-xl border-l-4 border-yellow-400 italic text-center super-tiny-system-msg' :
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
              class="relative group"
            >
              <img
                :src="getAttachmentUrl(attachment)"
                :alt="attachment.file_name || attachment.name || 'Image'"
                class="max-w-full h-auto object-cover cursor-pointer transition-opacity group-hover:opacity-90"
                :class="isOwnMessage ? 'rounded-xl rounded-br-none' : 'rounded-xl rounded-bl-none'"
                style="max-height: 200px; max-width: 250px; min-width: 150px; cursor: pointer;"
                @click.stop="openImageModal(getAttachmentUrl(attachment))"
              />
              <!-- Enhanced image overlay with filename and size -->
              <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent p-3 transition-opacity"
                   :class="isOwnMessage ? 'rounded-br-none rounded-bl-xl' : 'rounded-bl-none rounded-br-xl'">
                <div class="text-white text-xs">
                  <p class="font-medium truncate" v-if="attachment.file_name || attachment.name">
                    {{ attachment.file_name || attachment.name }}
                  </p>
                  <p class="text-white/80 text-xs" v-if="attachment.file_size">
                    {{ getFileSize(attachment) }}
                  </p>
                </div>
              </div>
              <!-- View full size indicator on hover -->
              <div class="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center cursor-pointer"
                   :class="isOwnMessage ? 'rounded-xl rounded-br-none' : 'rounded-xl rounded-bl-none'"
                   @click.stop="openImageModal(getAttachmentUrl(attachment))">
                <div class="bg-black/60 text-white px-3 py-1 rounded-full text-sm font-medium pointer-events-none">
                  Click to view
                </div>
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
              @click="downloadFile(getAttachmentUrl(attachment), attachment.file_name || attachment.name)"
            >
              <!-- File Icon based on type -->
              <div class="flex-shrink-0">
                <svg v-if="getFileType(attachment) === 'pdf'" class="w-8 h-8 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
                </svg>
                <svg v-else-if="getFileType(attachment).includes('doc')" class="w-8 h-8 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
                </svg>
                <svg v-else-if="getFileType(attachment).includes('sheet') || getFileType(attachment).includes('excel')" class="w-8 h-8 text-green-500" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
                </svg>
                <svg v-else-if="getFileType(attachment).includes('ppt') || getFileType(attachment).includes('presentation')" class="w-8 h-8 text-orange-500" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
                </svg>
                <svg v-else-if="getFileType(attachment).includes('video') || getFileType(attachment) === 'mp4'" class="w-8 h-8 text-purple-500" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M17,10.5V7A1,1 0 0,0 16,6H4A1,1 0 0,0 3,7V17A1,1 0 0,0 4,18H16A1,1 0 0,0 17,17V13.5L21,17.5V6.5L17,10.5Z" />
                </svg>
                <svg v-else class="w-8 h-8" :class="isOwnMessage ? 'text-white' : 'text-gray-600'" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-semibold text-sm truncate" :title="attachment.file_name || attachment.name || 'File'">
                  {{ attachment.file_name || attachment.name || 'Unnamed file' }}
                </p>
                <p class="text-xs" :class="isOwnMessage ? 'text-white text-opacity-80' : 'text-gray-500'">
                  {{ getFileSize(attachment) }}{{ getFileType(attachment) ? ' • ' + getFileType(attachment).toUpperCase() : '' }}
                </p>
              </div>
              <!-- Download icon -->
              <svg class="w-5 h-5 flex-shrink-0" :class="isOwnMessage ? 'text-white' : 'text-gray-500'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
          <!-- Text content below files if both exist -->
          <div v-if="message.content && message.content.trim()" class="px-4 py-2 border-t" :class="isOwnMessage ? 'border-blue-400' : 'border-gray-300'">
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
            <!-- Special styling for bump messages - show original content cleanly -->
            <div v-if="isBumpMessage && replyMessage" @click="scrollToOriginalMessage" class="cursor-pointer">
              <!-- Small bump indicator at top -->
              <div class="flex items-center gap-2 text-xs text-amber-600 mb-2 opacity-80">
                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M7 11l5-5m0 0l5 5m-5-5v12" />
                </svg>
                <span>Bumped</span>
              </div>
              
              <!-- Display original message content directly (clean style) -->
              <div v-if="replyMessage && /^[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\s]*$/u.test(replyMessage.content)" class="text-4xl p-2">
                {{ replyMessage.content }}
              </div>
              <p v-else-if="replyMessage" class="text-sm" v-html="formatMessageContent(replyMessage.content)"></p>
            </div>
            
            <!-- Regular message content (non-bump) -->
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

              <!-- Forwarded from preview (similar to reply) -->
              <div v-if="message.forwarded_from" class="mb-3">
                <div :class="[
                  'border-l-4 pl-3 py-2 rounded-r-md transition-all duration-200',
                  isOwnMessage 
                    ? 'border-green-300 bg-green-100 bg-opacity-30' 
                    : 'border-green-500 bg-green-50'
                ]">
                  <div class="flex items-center gap-2 mb-1">
                    <svg class="w-3 h-3 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                            d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                    </svg>
                    <span :class="[
                      'font-medium text-xs',
                      isOwnMessage ? 'text-white text-opacity-90' : 'text-green-600'
                    ]">
                      Forwarded from {{ message.forwarded_from.sender.first_name }} {{ message.forwarded_from.sender.last_name }}
                    </span>
                  </div>
                  <p :class="[
                    'text-xs line-clamp-2 leading-tight',
                    isOwnMessage ? 'text-white text-opacity-80' : 'text-gray-700'
                  ]">
                    {{ message.forwarded_from.content || 'Attachment' }}
                  </p>
                  <span :class="[
                    'text-xs opacity-75',
                    isOwnMessage ? 'text-white text-opacity-60' : 'text-gray-500'
                  ]">
                    {{ formatTimestamp(message.forwarded_from.timestamp) }}
                    {{ message.forwarded_from.was_group_message ? `• ${message.forwarded_from.original_group_name}` : '' }}
                  </span>
                </div>
              </div>

              <!-- Main message content -->
              <div v-if="isEmojiOnlyMessage" class="text-4xl p-2">
                {{ message.content }}
              </div>
              <p v-else class="text-sm" v-html="formatMessageContent(message.content)"></p>
              <!-- Edit indicator -->
              <span v-if="message.edited_at" class="text-xs opacity-75 ml-1">(edited)</span>
              
              <!-- Link Previews -->
              <div v-if="message.link_previews && message.link_previews.length > 0" class="mt-3 space-y-2">
                <div 
                  v-for="preview in message.link_previews" 
                  :key="preview.id"
                  class="border rounded-lg overflow-hidden cursor-pointer hover:bg-opacity-90 transition-all"
                  :class="isOwnMessage ? 'border-blue-300 bg-blue-50' : 'border-gray-300 bg-white'"
                  @click="openLink(preview.url)"
                >
                  <!-- Link preview header with image -->
                  <div v-if="preview.image_url" class="aspect-video bg-gray-100 overflow-hidden">
                    <img 
                      :src="preview.image_url" 
                      :alt="preview.title"
                      class="w-full h-full object-cover"
                      @error="handleImageError"
                    />
                  </div>
                  
                  <!-- Link preview content -->
                  <div class="p-3">
                    <div class="flex items-start justify-between">
                      <div class="flex-1 min-w-0">
                        <h4 v-if="preview.title" 
                            class="font-medium text-sm line-clamp-2 mb-1"
                            :class="isOwnMessage ? 'text-blue-900' : 'text-gray-900'">
                          {{ preview.title }}
                        </h4>
                        <p v-if="preview.description" 
                           class="text-xs line-clamp-2 mb-2"
                           :class="isOwnMessage ? 'text-blue-700' : 'text-gray-600'">
                          {{ preview.description }}
                        </p>
                        <div class="flex items-center gap-2">
                          <svg class="w-3 h-3" :class="isOwnMessage ? 'text-blue-600' : 'text-gray-500'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                          <span class="text-xs font-medium truncate" 
                                :class="isOwnMessage ? 'text-blue-700' : 'text-gray-700'">
                            {{ preview.domain }}
                          </span>
                        </div>
                      </div>
                      <svg class="w-4 h-4 flex-shrink-0 ml-2" :class="isOwnMessage ? 'text-blue-600' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
            </div>
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
      :visible="showContextMenu"
      :message="message"
      :position="contextMenuPosition"
      :currentUser="currentUser"
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
  currentUser: Object, // Changed from currentUserId to full user object
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
  const result = props.message.sender?.id === props.currentUser?.id
  console.log('MessageBubble isOwnMessage check:', {
    messageId: props.message.id,
    senderId: props.message.sender?.id,
    currentUserId: props.currentUser?.id,
    senderIdType: typeof props.message.sender?.id,
    currentUserIdType: typeof props.currentUser?.id,
    isOwnMessage: result
  })
  return result
})

// Check if this is a system message
const isSystemMessage = computed(() => {
  const result = props.message.isSystemMessage || 
         props.message.sender?.id === 'system' ||
         props.message.message_type === 'system' ||
         props.message.sender === null ||
         // Detect system messages by content pattern
         (props.message.content && (
           props.message.content.includes(' left the group') ||
           props.message.content.includes(' joined the group') ||
           props.message.content.includes(' was added to the group') ||
           props.message.content.includes(' was removed from the group')
         ))
  
  if (result) {
    console.log('🔍 System message detected:', props.message.content, props.message);
  }
  
  return result;
})

// Check if this is a bump message
const isBumpMessage = computed(() => {
  return props.message.content === "🔔 Bumped message" && props.message.reply_to
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
  // For bump messages, check the original message content
  const contentToCheck = isBumpMessage.value && replyMessage.value 
    ? replyMessage.value.content 
    : props.message.content
    
  if (!contentToCheck) return false
  
  // Remove all emoji characters and check if anything remains
  const textWithoutEmojis = contentToCheck.replace(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu, '').trim()
  
  // Consider it emoji-only if no text remains and original message has content
  return textWithoutEmojis.length === 0 && contentToCheck.trim().length > 0
})

// Format message content with enhanced emoji rendering and link detection
const formatMessageContent = (content) => {
  if (!content) return ''
  
  // Enhanced URL regex pattern to match various URL formats
  const urlRegex = /(https?:\/\/(?:[-\w.])+(?:\.[a-zA-Z]{2,})+(?:\/[^\s]*)?)/gi
  
  // Replace URLs with clickable links - different colors for sender vs receiver
  let formattedContent = content.replace(urlRegex, (url) => {
    const linkClasses = isOwnMessage.value 
      ? "text-white hover:text-gray-200 underline break-all" // White for sender (blue bubble)
      : "text-blue-600 hover:text-blue-800 underline break-all" // Blue for receiver (gray bubble)
    return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="${linkClasses}">${url}</a>`
  })
  
  // Enhanced emoji regex to match more emoji ranges
  const emojiRegex = /([\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}])/gu
  
  // Replace emojis with larger styled versions
  formattedContent = formattedContent.replace(emojiRegex, '<span class="inline-block text-lg">$1</span>')
  
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
    // Return the subtype (e.g., 'pdf' from 'application/pdf')
    return attachment.file_type.split('/').pop() || 'file'
  }
  
  // Fallback: extract from filename
  const fileName = attachment.file_name || attachment.name || attachment.file || ''
  if (!fileName) return 'file'
  
  const extension = fileName.split('.').pop()?.toLowerCase()
  return extension || 'file'
}

const getFileSize = (attachment) => {
  // Use file_size from backend first
  const bytes = attachment.file_size || attachment.size || 0
  
  if (bytes === 0) return 'Unknown size'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Image modal functionality
const openImageModal = (imageUrl) => {
  console.log('Opening image modal for:', imageUrl)
  
  // Create a simple modal to view full-size image
  const modal = document.createElement('div')
  modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm'
  modal.style.zIndex = '9999'
  modal.innerHTML = `
    <div class="relative max-w-4xl max-h-full p-4 flex items-center justify-center">
      <img src="${imageUrl}" class="max-w-full max-h-full object-contain" style="max-height: 90vh; max-width: 90vw;" />
      <button class="absolute top-4 right-4 text-white hover:text-gray-300 text-3xl font-bold bg-black bg-opacity-50 rounded-full w-10 h-10 flex items-center justify-center">&times;</button>
    </div>
  `
  
  // Close modal on click
  modal.addEventListener('click', (e) => {
    if (e.target === modal || e.target.textContent === '×' || e.target.tagName === 'BUTTON') {
      document.body.removeChild(modal)
    }
  })
  
  // Close modal on Escape key
  const handleEscape = (e) => {
    if (e.key === 'Escape') {
      document.body.removeChild(modal)
      document.removeEventListener('keydown', handleEscape)
    }
  }
  document.addEventListener('keydown', handleEscape)
  
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
    case 'delete':
      confirmDelete()
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

// Delete functionality with confirmation
const confirmDelete = () => {
  if (!isOwnMessage.value) return
  
  const confirmed = window.confirm('Are you sure you want to delete this message? This action cannot be undone.')
  if (confirmed) {
    console.log('MessageBubble: Deleting message', props.message.id)
    emit('message-action', {
      action: 'delete',
      message: props.message
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

// Link functionality
const openLink = (url) => {
  window.open(url, '_blank', 'noopener,noreferrer')
}

// Handle image loading errors for link previews
const handleImageError = (event) => {
  event.target.style.display = 'none'
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

.break-all {
  word-break: break-all;
}

.aspect-video {
  aspect-ratio: 16 / 9;
}

/* Super small font for system messages */
.system-message-tiny {
  font-size: 10px !important;
  line-height: 1.2 !important;
  opacity: 0.8;
}

/* Even more specific selector for super tiny system messages */
.super-tiny-system-msg,
.super-tiny-system-msg * {
  font-size: 9px !important;
  line-height: 1.2 !important;
  color: #000000 !important;
  font-weight: normal !important;
}

.super-tiny-system-msg {
  opacity: 0.9 !important;
}
</style>

