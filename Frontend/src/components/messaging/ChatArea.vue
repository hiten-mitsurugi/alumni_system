<template>
  <div class="flex-1 flex flex-col">
    <!-- Header with user/group info -->
    <div class="p-4 bg-white border-b border-gray-200 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <!-- Safe avatar with status indicator -->
        <div class="relative">
          <img :src="conversation.type === 'private'
              ? getProfilePictureUrl(conversation.mate)
              : conversation.group?.group_picture || '/default-group.png'
            " alt="Avatar" class="w-10 h-10 rounded-full object-cover" />
          <!-- Online/Offline status indicator for private chats -->
          <div v-if="conversation.type === 'private'" 
               :class="['absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-white', getStatusColor(conversation.mate)]">
          </div>
        </div>
        <div>
          <!-- Safe name -->
          <h3 class="font-semibold text-gray-900">
            {{
              conversation.type === 'private'
                ? `${conversation.mate.first_name} ${conversation.mate.last_name}`
                : conversation.group?.name || 'Group'
            }}
          </h3>
          <!-- Safe status text -->
          <p v-if="conversation.type === 'private'" :class="['text-sm', getStatusTextColor(conversation.mate)]">
            {{ getStatusText(conversation.mate) }}
          </p>
        </div>
      </div>
      
      <!-- Chat Info Toggle Button -->
      <div class="flex items-center gap-2">
        <button 
          @click="$emit('toggle-chat-info')"
          class="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200"
          title="Chat Info"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Messages -->
    <div 
      ref="messagesContainer"
      class="flex-1 overflow-y-auto p-4 chat-messages-container bg-gray-50"
      style="min-height: 0; max-height: calc(100vh - 300px);"
    >
      <!-- Messages Display -->
      <div>
        <div
          v-for="(message, index) in messages"
          :key="message.id"
          :class="[
            // Reduce spacing for reply threads
            isReplyMessage(message, index) ? 'mb-2' : 'mb-4'
          ]"
        >
          <MessageBubble
            :message="message"
            :messages="messages"
            :currentUser="currentUser"
            @message-action="handleMessageAction"
            @scroll-to-message="scrollToMessage"
          />
        </div>

        <!-- Individual Pinned Message Indicators (inside messages container) -->
        <div 
          v-if="pinnedMessages.length > 0" 
          class="pinned-indicators-container"
        >
          <div 
            v-for="pinnedMessage in pinnedMessages"
            :key="pinnedMessage.id"
            class="pinned-indicator-container"
            @click="scrollToMessage(pinnedMessage.id)"
          >
            <div class="pinned-indicator">
              <svg class="w-3 h-3 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M4 3a2 2 0 100 4h12a2 2 0 100-4H4z"/>
                <path fill-rule="evenodd" d="M3 8a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"/>
                <path d="M9 11H7v5a1 1 0 001 1h4a1 1 0 001-1v-5h-2V9H9v2z"/>
              </svg>
              <span class="pinned-text">pinned message</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Message input -->
    <div class="flex-shrink-0 border-t border-gray-200 bg-white p-2">
      <MessageInput 
        :replyingTo="replyingTo"
        @send-message="sendMessage" 
        @cancel-reply="cancelReply"
      />
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, watch, ref, nextTick, computed } from 'vue'
import MessageBubble from './MessageBubble.vue'
import MessageInput from './MessageInput.vue'

const props = defineProps({
  conversation: Object,
  messages: Array,
  currentUser: Object
})

const emit = defineEmits(['send-message', 'message-action', 'toggle-chat-info'])
const messagesContainer = ref(null)

// Reply state
const replyingTo = ref(null)

// Computed property for pinned messages
const pinnedMessages = computed(() => {
  return props.messages?.filter(message => message.is_pinned) || []
})

// Safe profile picture helper (same logic as AlumniNavbar)
const getProfilePictureUrl = (entity) => {
  const BASE_URL = 'http://127.0.0.1:8000'
  const pic = entity?.profile_picture
  return pic
    ? (pic.startsWith('http') ? pic : `${BASE_URL}${pic}`)
    : '/default-avatar.png'
}

// Online/Offline status helpers
const getStatusColor = (user) => {
  if (!user?.profile?.last_seen) return 'bg-gray-400'; // Default offline color
  return isRecentlyActive(user) ? 'bg-green-500' : 'bg-gray-400';
}

const getStatusTextColor = (user) => {
  return isRecentlyActive(user) ? 'text-green-600' : 'text-gray-500';
}

const getStatusText = (user) => {
  if (!user?.profile?.last_seen) return 'Offline';
  return isRecentlyActive(user) ? 'Online' : 'Offline';
}

const isRecentlyActive = (user) => {
  if (!user?.profile?.last_seen) return false;
  const lastSeen = new Date(user.profile.last_seen);
  const now = new Date();
  const diffMinutes = (now - lastSeen) / (1000 * 60);
  // Consider active if seen within last 2 minutes AND status is online
  const isRecent = diffMinutes <= 2;
  const isOnlineStatus = user.profile.status === 'online';
  console.log(`ChatArea isRecentlyActive for user ${user.id}: lastSeen=${lastSeen.toISOString()}, diffMinutes=${diffMinutes.toFixed(2)}, status=${user.profile.status}, isRecent=${isRecent}, isOnlineStatus=${isOnlineStatus}`);
  return isRecent && isOnlineStatus;
};

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
    );
    
    if (newMessagesWithReplies.length > 0) {
      console.log('✅ ChatArea: New messages with reply data detected:', newMessagesWithReplies.length)
      newMessagesWithReplies.forEach(msg => {
        console.log(`✅ ChatArea: Message ${msg.id} has reply_to:`, msg.reply_to ? 'YES' : 'NO')
      });
    }
  }
  
  // Auto-scroll to bottom when new messages arrive
  nextTick(() => {
    scrollToBottom()
  })
}, { immediate: true, deep: true })

// Scroll to bottom when conversation changes
watch(() => props.conversation, () => {
  setTimeout(scrollToBottom, 100)
}, { immediate: true })
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