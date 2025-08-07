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
    </div>

    <!-- Messages -->
    <div 
      ref="messagesContainer"
      class="flex-1 overflow-y-auto p-4 space-y-4 chat-messages-container bg-gray-50"
      style="min-height: 0; max-height: calc(100vh - 300px);"
    >
      <MessageBubble
        v-for="message in messages"
        :key="message.id"
        :message="message"
        :currentUserId="currentUser.id"
      />
    </div>

    <!-- Message input -->
    <div class="flex-shrink-0 border-t border-gray-200 bg-white p-2">
      <MessageInput @send-message="sendMessage" />
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, watch, ref, nextTick } from 'vue'
import MessageBubble from './MessageBubble.vue'
import MessageInput from './MessageInput.vue'

const props = defineProps({
  conversation: Object,
  messages: Array,
  currentUser: Object
})

const emit = defineEmits(['send-message'])
const messagesContainer = ref(null)

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

// Forward sendMessage to parent
function sendMessage(data) {
  console.log('ChatArea: Forwarding sendMessage to parent with:', data)
  emit('send-message', data)
  // Auto-scroll to bottom after sending message
  setTimeout(scrollToBottom, 100)
}

// Watch messages for debugging and auto-scroll
watch(() => props.messages, (newMessages) => {
  console.log('ChatArea: Messages updated:', newMessages)
  // Auto-scroll to bottom when new messages arrive
  scrollToBottom()
}, { immediate: true })

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
</style>