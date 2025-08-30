<template>
  <div class="flex-1 flex flex-col">
    <!-- Header with user/group info - Enhanced styling -->
    <div class="p-4 md:p-6 bg-white/90 backdrop-blur-sm border-b border-gray-200/60 flex items-center justify-between transition-all duration-200 shadow-sm">
      <div class="flex items-center gap-3 md:gap-4">
        <!-- Safe avatar with enhanced status indicator -->
        <div class="relative">
          <img 
            :src="avatarUrl" 
            :key="conversation?.group?.group_picture || conversation?.mate?.profile_picture || Date.now()"
            alt="Avatar" 
            class="w-12 h-12 md:w-14 md:h-14 rounded-full object-cover shadow-md ring-2 ring-white hover:ring-slate-200 transition-all duration-200" 
          />
          <!-- Online/Offline status indicator for private chats -->
          <div v-if="conversation.type === 'private'" 
               :class="['absolute bottom-0 right-0 w-4 h-4 md:w-5 md:h-5 rounded-full border-2 md:border-3 border-white shadow-sm', getStatusColor(conversation.mate)]">
          </div>
        </div>
        <div>
          <!-- Safe name with improved typography -->
          <h3 class="font-bold text-gray-900 text-lg md:text-xl leading-tight">
            {{
              conversation.type === 'private'
                ? `${conversation.mate.first_name} ${conversation.mate.last_name}`
                : conversation.group?.name || 'Group'
            }}
          </h3>
          <!-- Safe status text with better styling -->
          <p v-if="conversation.type === 'private'" :class="['text-sm md:text-base font-medium', getStatusTextColor(conversation.mate)]">
            {{ getStatusText(conversation.mate) }}
          </p>
          <p v-else class="text-sm md:text-base text-gray-500 font-medium">
            {{ conversation.group?.members?.length || 0 }} members
          </p>
        </div>
      </div>
      
      <!-- Chat Info Toggle Button with better styling -->
      <div class="flex items-center gap-2">
        <button 
          @click="$emit('toggle-chat-info')"
          class="p-2.5 md:p-3 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-xl transition-all duration-200 hover:scale-105"
          title="Chat Info"
        >
          <svg class="w-5 h-5 md:w-6 md:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Messages with improved background and spacing -->
    <div 
      ref="messagesContainer"
      class="flex-1 overflow-y-auto p-4 md:p-6 chat-messages-container bg-gradient-to-br from-gray-50/80 to-slate-50/60 transition-all duration-200"
      style="min-height: 0; max-height: calc(100vh - 300px);"
    >
      <!-- Messages Display with enhanced spacing -->
      <div>
        <div
          v-for="(message, index) in messages"
          :key="message.id"
          :data-message-id="message.id"
          :class="[
            // Better spacing for reply threads and regular messages
            isReplyMessage(message, index) ? 'mb-2 md:mb-3' : 'mb-4 md:mb-6'
          ]"
        >
          <MessageBubble
            :message="message"
            :messages="messages"
            :currentUser="currentUser"
            :conversation="conversation"
            @message-action="handleMessageAction"
            @scroll-to-message="scrollToMessage"
            @mentionClick="handleMentionClick"
          />
        </div>

        <!-- Enhanced Pinned Message Indicators -->
        <div 
          v-if="pinnedMessages && pinnedMessages.length > 0" 
          class="pinned-indicators-container"
        >
          <div 
            v-for="pinnedMessage in pinnedMessages"
            :key="pinnedMessage.id"
            class="pinned-indicator-container"
            @click="scrollToMessage(pinnedMessage.id)"
          >
            <div class="pinned-indicator bg-amber-50 hover:bg-amber-100 border border-amber-200 rounded-lg p-2 transition-all duration-200 cursor-pointer">
              <svg class="w-4 h-4 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M4 3a2 2 0 100 4h12a2 2 0 100-4H4z"/>
                <path fill-rule="evenodd" d="M3 8a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"/>
                <path d="M9 11H7v5a1 1 0 001 1h4a1 1 0 001-1v-5h-2V9H9v2z"/>
              </svg>
              <span class="pinned-text text-amber-700 font-medium ml-2">Pinned message</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Message input or blocked indicator -->
    <div class="flex-shrink-0 border-t border-gray-200  bg-white  p-2 transition-colors duration-200">
      <!-- Show blocked message if conversation is blocked -->
      <div v-if="conversation.isBlockedByMe || conversation.isBlockedByThem" 
           class="p-4 text-center">
        <div v-if="conversation.isBlockedByMe" 
             class="bg-red-50 border border-red-200 rounded-lg p-4">
          <div class="flex items-center justify-center space-x-2 text-red-600">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M13.477 14.89A6 6 0 015.11 6.524l8.367 8.368zm1.414-1.414L6.524 5.11a6 6 0 018.367 8.367zM18 10a8 8 0 11-16 0 8 8 0 0116 0z" clip-rule="evenodd"/>
            </svg>
            <span class="font-medium">You have blocked this user</span>
          </div>
          <p class="text-sm text-red-500 mt-2">
            You cannot send messages to blocked users. Unblock them to continue messaging.
          </p>
        </div>
        <div v-else-if="conversation.isBlockedByThem" 
             class="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <div class="flex items-center justify-center space-x-2 text-orange-600">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M13.477 14.89A6 6 0 015.11 6.524l8.367 8.368zm1.414-1.414L6.524 5.11a6 6 0 018.367 8.367zM18 10a8 8 0 11-16 0 8 8 0 0116 0z" clip-rule="evenodd"/>
            </svg>
            <span class="font-medium">You are blocked by this user</span>
          </div>
          <p class="text-sm text-orange-500 mt-2">
            This user has blocked you. You cannot send messages to them.
          </p>
        </div>
      </div>
      <!-- Normal message input for non-blocked conversations -->
      <MessageInput 
        v-else
        :replyingTo="replyingTo"
        :conversation="conversation"
        @send-message="sendMessage" 
        @cancel-reply="cancelReply"
      />
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, watch, ref, nextTick, computed, onMounted, onUnmounted } from 'vue'
import MessageBubble from './MessageBubble.vue'
import MessageInput from './MessageInput.vue'
import api from '@/services/api'

const props = defineProps({
  conversation: Object,
  messages: Array,
  currentUser: Object,
  privateWs: Object, // WebSocket for private chats
  groupWs: Object,   // WebSocket for group chats
})

const emit = defineEmits(['send-message', 'message-action', 'toggle-chat-info', 'message-read'])
const messagesContainer = ref(null)

// Reply state
const replyingTo = ref(null)

// Intersection observer for marking messages as read
let intersectionObserver = null
const readMessageIds = new Set()

// Safe profile picture helper
const getProfilePictureUrl = (entity) => {
  const BASE_URL = 'http://127.0.0.1:8000'
  const pic = entity?.profile_picture || entity?.group_picture
  return pic
    ? (pic.startsWith('http') ? pic : `${BASE_URL}${pic}`)
    : '/default-avatar.png'
}

// Computed property for avatar URL
const avatarUrl = computed(() => {
  return props.conversation.type === 'private'
    ? getProfilePictureUrl(props.conversation.mate)
    : getProfilePictureUrl(props.conversation.group)
})

// Computed property for pinned messages
const pinnedMessages = computed(() => {
  return props.messages?.filter(message => message.is_pinned) || []
})

// Online/Offline status helpers
const getStatusColor = (user) => {
  if (!user?.profile?.last_seen) return 'bg-gray-400' // Default offline color
  return isRecentlyActive(user) ? 'bg-green-500' : 'bg-gray-400'
}

const getStatusTextColor = (user) => {
  return isRecentlyActive(user) ? 'text-green-600' : 'text-gray-500'
}

const getStatusText = (user) => {
  if (!user?.profile?.last_seen) return 'Offline'
  return isRecentlyActive(user) ? 'Online' : 'Offline'
}

const isRecentlyActive = (user) => {
  if (!user?.profile?.last_seen) return false
  const lastSeen = new Date(user.profile.last_seen)
  const now = new Date()
  const diffMinutes = (now - lastSeen) / (1000 * 60)
  // Consider active if seen within last 2 minutes AND status is online
  const isRecent = diffMinutes <= 2
  const isOnlineStatus = user.profile.status === 'online'
  console.log(`ChatArea isRecentlyActive for user ${user.id}: lastSeen=${lastSeen.toISOString()}, diffMinutes=${diffMinutes.toFixed(2)}, status=${user.profile.status}, isRecent=${isRecent}, isOnlineStatus=${isOnlineStatus}`)
  return isRecent && isOnlineStatus
}

const formatLastSeen = (lastSeen) => {
  if (!lastSeen) return ''
  
  const now = new Date()
  const lastSeenDate = new Date(lastSeen)
  const diffInMilliseconds = now - lastSeenDate
  const diffInMinutes = Math.floor(diffInMilliseconds / (1000 * 60))
  const diffInHours = Math.floor(diffInMinutes / 60)
  const diffInDays = Math.floor(diffInHours / 24)
  
  if (diffInMinutes < 1) return 'just now'
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`
  if (diffInHours < 24) return `${diffInHours}h ago`
  if (diffInDays === 1) return 'yesterday'
  if (diffInDays < 7) return `${diffInDays}d ago`
  
  return lastSeenDate.toLocaleDateString()
}

// Safe timestamp
function formatTimestamp(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// Auto-scroll to bottom
function scrollToBottom() {
  if (messagesContainer.value) {
    nextTick(() => {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    })
  }
}

// Mark message as read function
const markMessageAsRead = async (messageId) => {
  // Avoid duplicate API calls
  if (readMessageIds.has(messageId)) return
  
  try {
    readMessageIds.add(messageId)
    console.log('📖 Marking message as read:', messageId)
    
    // Make the API call - Fixed URL path
    const response = await api.post(`/message/mark-read/${messageId}/`)
    console.log('✅ Marked message as read:', messageId, 'Response:', response.data)
    
    // Emit an event to parent to trigger immediate UI update
    emit('message-read', { messageId, readBy: response.data.read_by })
    
  } catch (error) {
    console.error('❌ Failed to mark message as read:', error)
    readMessageIds.delete(messageId) // Remove from set if API call failed
  }
}

// Setup intersection observer to detect when messages are visible
const setupIntersectionObserver = () => {
  if (intersectionObserver) {
    intersectionObserver.disconnect()
  }
  
  intersectionObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const messageElement = entry.target
          const messageId = messageElement.dataset.messageId
          const messageData = props.messages?.find(m => m.id === messageId)
          
          // Only mark as read if:
          // 1. Message exists
          // 2. Current user is not the sender
          // 3. Message hasn't been read yet (for private messages) or user hasn't read it (for group messages)
          if (messageData && messageData.sender?.id !== props.currentUser?.id) {
            // For private messages, check is_read field
            if (props.conversation?.type === 'private' && !messageData.is_read) {
              markMessageAsRead(messageId)
            }
            // For group messages, check if current user is in read_by array
            else if (props.conversation?.type === 'group') {
              const hasRead = messageData.read_by?.some(user => user.id === props.currentUser?.id)
              if (!hasRead) {
                markMessageAsRead(messageId)
              }
            }
          }
        }
      })
    },
    {
      root: messagesContainer.value,
      rootMargin: '0px',
      threshold: 0.5 // Message needs to be 50% visible
    }
  )
  
  // Observe all message elements
  if (messagesContainer.value) {
    const messageElements = messagesContainer.value.querySelectorAll('[data-message-id]')
    messageElements.forEach(element => {
      intersectionObserver.observe(element)
    })
  }
}

// Cleanup intersection observer
onUnmounted(() => {
  if (intersectionObserver) {
    intersectionObserver.disconnect()
  }
})

// Setup observer when component mounts and when messages change
onMounted(() => {
  nextTick(() => {
    setupIntersectionObserver()
  })
})

// Re-setup observer when messages change
watch(() => props.messages, () => {
  nextTick(() => {
    setupIntersectionObserver()
  })
}, { deep: true })

// WebSocket listener for real-time read status updates
function handleWebSocketMessage(event) {
  try {
    const data = JSON.parse(event.data)
    
    if (data.type === 'message_read_update') {
      console.log('🔥 Received message_read_update:', data)
      
      // Find the message and update its read_by status
      const messageIndex = props.messages?.findIndex(m => m.id === data.message_id)
      if (messageIndex !== -1 && props.messages[messageIndex]) {
        // Force reactivity by updating the message object
        const updatedMessage = { ...props.messages[messageIndex] }
        updatedMessage.read_by = data.read_by || []
        
        // Update the message in the array to trigger reactivity
        props.messages.splice(messageIndex, 1, updatedMessage)
        
        console.log('✅ Updated message read status:', {
          messageId: data.message_id,
          readBy: updatedMessage.read_by
        })
      }
    }
  } catch (error) {
    console.error('❌ Error handling WebSocket message:', error)
  }
}

// Set up WebSocket listeners for real-time updates
watch(() => props.privateWs, (newWs, oldWs) => {
  if (oldWs) {
    oldWs.removeEventListener('message', handleWebSocketMessage)
  }
  if (newWs) {
    newWs.addEventListener('message', handleWebSocketMessage)
  }
}, { immediate: true })

watch(() => props.groupWs, (newWs, oldWs) => {
  if (oldWs) {
    oldWs.removeEventListener('message', handleWebSocketMessage)
  }
  if (newWs) {
    newWs.addEventListener('message', handleWebSocketMessage)
  }
}, { immediate: true })

// Cleanup WebSocket listeners on unmount
onUnmounted(() => {
  if (intersectionObserver) {
    intersectionObserver.disconnect()
  }
  if (props.privateWs) {
    props.privateWs.removeEventListener('message', handleWebSocketMessage)
  }
  if (props.groupWs) {
    props.groupWs.removeEventListener('message', handleWebSocketMessage)
  }
})

// Handle message actions from MessageBubble
function handleMessageAction(actionData) {
  console.log('ChatArea: Message action received:', actionData)
  const { action, message, newContent } = actionData
  
  switch (action) {
    case 'reply':
      // Set reply state for MessageInput
      replyingTo.value = message
      console.log('ChatArea: Set reply target to message:', message.id)
      console.log('ChatArea: replyingTo.value is now:', replyingTo.value)
      console.log('ChatArea: Will pass to MessageInput:', !!replyingTo.value)
      break
    case 'forward':
      // Forward to parent to handle forwarding
      emit('message-action', actionData)
      break
    case 'pin':
    case 'unpin':
      // Forward to parent to handle pin/unpin
      emit('message-action', actionData)
      break
    case 'bump':
      // Forward to parent to handle bump
      emit('message-action', actionData)
      break
    case 'edit':
      // Forward to parent to handle edit
      emit('message-action', actionData)
      break
    case 'delete':
      // Forward to parent to handle delete
      emit('message-action', actionData)
      break
    case 'select':
      // Forward to parent to handle selection
      emit('message-action', actionData)
      break
    default:
      console.warn('ChatArea: Unknown message action:', action)
  }
}

// 🔔 MENTIONS: Handle mention clicks from MessageBubble
function handleMentionClick({ userId, username }) {
  console.log('ChatArea: Mention clicked:', { userId, username })
  // You can implement various actions here:
  // - Show user profile modal
  // - Highlight the mentioned user in the members list
  // - Scroll to the user in members sidebar
  // - Start a private chat with the mentioned user
  
  // For now, we'll just log it - you can extend this based on your needs
  // Example: emit an event to show user profile
  // emit('show-user-profile', { userId, username })
}

// Reply functionality
const cancelReply = () => {
  replyingTo.value = null
  console.log('ChatArea: Cancelled reply')
}

// Scroll to specific message by ID
function scrollToMessage(messageId) {
  console.log('ChatArea: Scrolling to message:', messageId)
  nextTick(() => {
    const messageElement = document.querySelector(`[data-message-id="${messageId}"]`)
    if (messageElement) {
      messageElement.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
      })
      // Add highlight effect
      messageElement.classList.add('highlight-pinned-message')
      setTimeout(() => {
        messageElement.classList.remove('highlight-pinned-message')
      }, 3000)
    } else {
      console.warn('ChatArea: Message element not found for ID:', messageId)
    }
  })
}

// Check if message is a reply to create threaded layout
function isReplyMessage(message, index) {
  // Check if this message is a reply
  const isReply = !!(message.reply_to || message.reply_to_id)
  
  // Check if previous message is related (same conversation thread)
  if (index > 0) {
    const prevMessage = props.messages[index - 1]
    const isReplyToPrevious = message.reply_to === prevMessage.id || message.reply_to_id === prevMessage.id
    const sameAuthorAsReply = message.reply_to && props.messages.find(m => m.id === message.reply_to)?.sender?.id === prevMessage.sender?.id
    
    return isReply || isReplyToPrevious || sameAuthorAsReply
  }
  
  return isReply
}

// Forward sendMessage to parent
function sendMessage(data) {
  console.log('ChatArea: =========================')
  console.log('ChatArea: sendMessage function called!')
  console.log('ChatArea: Received data:', data)
  
  // Add reply information if replying to a message
  if (replyingTo.value) {
    data.reply_to_id = replyingTo.value.id
    console.log('ChatArea: Adding reply_to_id:', data.reply_to_id)
  }
  
  console.log('ChatArea: Forwarding to parent Messaging.vue')
  console.log('ChatArea: =========================')
  
  emit('send-message', data)
  
  // Clear reply state after sending
  if (replyingTo.value) {
    replyingTo.value = null
    console.log('ChatArea: Cleared reply state after sending')
  }
  
  // Auto-scroll to bottom after sending message
  setTimeout(scrollToBottom, 100)
}

// Watch messages for debugging and auto-scroll
watch(() => props.messages, (newMessages, oldMessages) => {
  console.log('🔄 ChatArea: Messages updated - count:', newMessages?.length || 0)
  
  // Debug: Check for new messages with reply_to data
  if (newMessages && oldMessages) {
    const newMessagesWithReplies = newMessages.filter(m => 
      m.reply_to || m.reply_to_id && 
      !oldMessages.find(old => old.id === m.id)
    )
    
    if (newMessagesWithReplies.length > 0) {
      console.log('✅ ChatArea: New messages with reply data detected:', newMessagesWithReplies.length)
      newMessagesWithReplies.forEach(msg => {
        console.log(`✅ ChatArea: Message ${msg.id} has reply_to:`, msg.reply_to ? 'YES' : 'NO')
      })
    }
  }
  
  // Auto-scroll to bottom when new messages arrive
  nextTick(() => {
    scrollToBottom()
  })
}, { immediate: true, deep: true })
</script>

<style scoped>
.chat-messages-container {
  scroll-behavior: smooth;
}

/* Custom scrollbar for webkit browsers */
.chat-messages-container::-webkit-scrollbar {
  width: 6px;
}

.chat-messages-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-messages-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages-container::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* Highlight effect for scrolled-to messages */
:deep(.highlight-message) {
  animation: messageHighlight 2s ease-in-out;
}

/* Special highlight for pinned messages */
:deep(.highlight-pinned-message) {
  animation: pinnedMessageHighlight 3s ease-in-out;
}

@keyframes messageHighlight {
  0% { 
    background-color: rgba(59, 130, 246, 0.2);
    transform: scale(1.02);
  }
  50% { 
    background-color: rgba(59, 130, 246, 0.1);
    transform: scale(1.01);
  }
  100% { 
    background-color: transparent;
    transform: scale(1);
  }
}

@keyframes pinnedMessageHighlight {
  0% { 
    background-color: rgba(245, 158, 11, 0.3);
    transform: scale(1.02);
    box-shadow: 0 0 20px rgba(245, 158, 11, 0.4);
  }
  50% { 
    background-color: rgba(245, 158, 11, 0.2);
    transform: scale(1.01);
    box-shadow: 0 0 15px rgba(245, 158, 11, 0.3);
  }
  100% { 
    background-color: transparent;
    transform: scale(1);
    box-shadow: none;
  }
}

/* Pinned Message Indicators Styles */
.pinned-indicators-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px 0;
  border-top: 1px solid rgba(245, 158, 11, 0.1);
  margin-top: 16px;
}

.pinned-indicator-container {
  display: flex;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pinned-indicator-container:hover {
  transform: translateY(-1px);
}

.pinned-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: 16px;
  transition: all 0.2s ease;
}

.pinned-indicator:hover {
  background: rgba(245, 158, 11, 0.15);
  border-color: rgba(245, 158, 11, 0.3);
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.2);
}

.pinned-text {
  font-size: 11px;
  font-weight: 500;
  color: #92400e;
  letter-spacing: 0.025em;
}
</style>