<template>
  <div class="flex-1 flex flex-col">
    <!-- Chat Header -->
    <ChatHeader :conversation="conversation" />

    <!-- Messages Area -->
    <div 
      ref="messagesContainer"
      class="flex-1 overflow-y-auto p-4 chat-messages-container bg-gray-50"
      style="min-height: 0; max-height: calc(100vh - 300px);"
    >
      <div
        v-for="(message, index) in messages"
        :key="message.id"
        :class="getMessageSpacing(message, index)"
      >
        <MessageBubble
          :message="message"
          :messages="messages"
          :currentUserId="currentUser.id"
          @message-action="handleMessageAction"
          @scroll-to-message="scrollToMessage"
        />
      </div>
    </div>

    <!-- Message Input -->
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
import { ref, watch, nextTick } from 'vue'
import MessageBubble from './MessageBubble.vue'
import MessageInput from './MessageInput.vue'

// ===== PROPS & EMITS =====
const props = defineProps({
  conversation: {
    type: Object,
    required: true
  },
  messages: {
    type: Array,
    default: () => []
  },
  currentUser: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['send-message', 'message-action'])

// ===== STATE =====
const messagesContainer = ref(null)
const replyingTo = ref(null)

// ===== COMPUTED =====

/**
 * Get appropriate spacing for message based on threading
 */
function getMessageSpacing(message, index) {
  const isReply = !!(message.reply_to || message.reply_to_id)
  
  if (index > 0) {
    const prevMessage = props.messages[index - 1]
    const isReplyToPrevious = message.reply_to === prevMessage.id || message.reply_to_id === prevMessage.id
    const sameAuthorAsReply = message.reply_to && 
      props.messages.find(m => m.id === message.reply_to)?.sender?.id === prevMessage.sender?.id
    
    const isThreaded = isReply || isReplyToPrevious || sameAuthorAsReply
    return isThreaded ? 'mb-2' : 'mb-4'
  }
  
  return isReply ? 'mb-2' : 'mb-4'
}

// ===== FUNCTIONS =====

/**
 * Auto-scroll to bottom of messages
 */
function scrollToBottom() {
  if (messagesContainer.value) {
    nextTick(() => {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    })
  }
}

/**
 * Scroll to specific message by ID with highlight effect
 */
function scrollToMessage(messageId) {
  nextTick(() => {
    const messageElement = document.querySelector(`[data-message-id="${messageId}"]`)
    if (messageElement) {
      messageElement.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
      })
      
      // Add highlight effect
      messageElement.classList.add('highlight-message')
      setTimeout(() => {
        messageElement.classList.remove('highlight-message')
      }, 2000)
    } else {
      console.warn('Message element not found for ID:', messageId)
    }
  })
}

/**
 * Handle message actions from MessageBubble
 */
function handleMessageAction(actionData) {
  const { action, message } = actionData
  
  if (action === 'reply') {
    // Set reply state for MessageInput
    replyingTo.value = message
  } else {
    // Forward other actions to parent
    emit('message-action', actionData)
  }
}

/**
 * Cancel reply
 */
function cancelReply() {
  replyingTo.value = null
}

/**
 * Send message with reply data
 */
function sendMessage(data) {
  // Add reply information if replying
  if (replyingTo.value) {
    data.reply_to_id = replyingTo.value.id
  }
  
  // Forward to parent
  emit('send-message', data)
  
  // Clear reply state and auto-scroll
  if (replyingTo.value) {
    replyingTo.value = null
  }
  
  setTimeout(scrollToBottom, 100)
}

// ===== WATCHERS =====

/**
 * Auto-scroll when messages change
 */
watch(() => props.messages, (newMessages) => {
  nextTick(scrollToBottom)
}, { immediate: true, deep: true })

/**
 * Auto-scroll when conversation changes
 */
watch(() => props.conversation, () => {
  setTimeout(scrollToBottom, 100)
}, { immediate: true })
</script>

<!-- Chat Header Component -->
<script>
const ChatHeader = {
  props: ['conversation'],
  template: `
    <div class="p-4 bg-white border-b border-gray-200 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <!-- Avatar with status indicator -->
        <div class="relative">
          <img 
            :src="getAvatarUrl()" 
            alt="Avatar" 
            class="w-10 h-10 rounded-full object-cover" 
          />
          <!-- Status indicator for private chats -->
          <div 
            v-if="conversation.type === 'private'" 
            :class="['absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-white', getStatusColor()]"
          />
        </div>
        
        <div>
          <!-- Name -->
          <h3 class="font-semibold text-gray-900">
            {{ getDisplayName() }}
          </h3>
          
          <!-- Status text for private chats -->
          <p 
            v-if="conversation.type === 'private'" 
            :class="['text-sm', getStatusTextColor()]"
          >
            {{ getStatusText() }}
          </p>
        </div>
      </div>
    </div>
  `,
  methods: {
    getAvatarUrl() {
      const BASE_URL = 'http://127.0.0.1:8000'
      
      if (this.conversation.type === 'private') {
        const pic = this.conversation.mate?.profile_picture
        return pic?.startsWith('http') ? pic : pic ? `${BASE_URL}${pic}` : '/default-avatar.png'
      } else {
        return this.conversation.group?.group_picture || '/default-group.png'
      }
    },
    
    getDisplayName() {
      if (this.conversation.type === 'private') {
        const mate = this.conversation.mate
        return `${mate?.first_name || ''} ${mate?.last_name || ''}`.trim() || 'Unknown User'
      } else {
        return this.conversation.group?.name || 'Group'
      }
    },
    
    getStatusColor() {
      const user = this.conversation.mate
      if (!user?.profile?.last_seen) return 'bg-gray-400'
      
      const lastSeen = new Date(user.profile.last_seen)
      const now = new Date()
      const diffMinutes = (now - lastSeen) / (1000 * 60)
      const isRecent = diffMinutes <= 2
      const isOnline = user.profile.status === 'online'
      
      return isRecent && isOnline ? 'bg-green-500' : 'bg-gray-400'
    },
    
    getStatusTextColor() {
      const user = this.conversation.mate
      if (!user?.profile?.last_seen) return 'text-gray-500'
      
      const lastSeen = new Date(user.profile.last_seen)
      const now = new Date()
      const diffMinutes = (now - lastSeen) / (1000 * 60)
      const isRecent = diffMinutes <= 2
      const isOnline = user.profile.status === 'online'
      
      return isRecent && isOnline ? 'text-green-600' : 'text-gray-500'
    },
    
    getStatusText() {
      const user = this.conversation.mate
      if (!user?.profile?.last_seen) return 'Offline'
      
      const lastSeen = new Date(user.profile.last_seen)
      const now = new Date()
      const diffMinutes = (now - lastSeen) / (1000 * 60)
      const isRecent = diffMinutes <= 2
      const isOnline = user.profile.status === 'online'
      
      return isRecent && isOnline ? 'Online' : 'Offline'
    }
  }
}

export default {
  components: {
    ChatHeader,
    MessageBubble,
    MessageInput
  }
}
</script>

<style scoped>
.chat-messages-container {
  scroll-behavior: smooth;
}

/* Custom scrollbar */
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

/* Highlight animation for scrolled-to messages */
:deep(.highlight-message) {
  animation: messageHighlight 2s ease-in-out;
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
</style>
