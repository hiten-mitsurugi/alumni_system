<template>
  <div class="flex-1 flex flex-col">
    <!-- Header with user/group info -->
    <div class="p-4 bg-white border-b border-gray-200 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <!-- Safe avatar -->
        <img :src="conversation.type === 'private'
            ? getProfilePictureUrl(conversation.mate)
            : conversation.group?.group_picture || '/default-group.png'
          " alt="Avatar" class="w-10 h-10 rounded-full object-cover" />
        <div>
          <!-- Safe name -->
          <h3 class="font-semibold text-gray-900">
            {{
              conversation.type === 'private'
                ? `${conversation.mate.first_name} ${conversation.mate.last_name}`
                : conversation.group?.name || 'Group'
            }}
          </h3>
          <!-- Safe status -->
          <p v-if="conversation.type === 'private'" class="text-sm text-gray-500">
            {{ conversation.mate?.profile?.status ?? 'online' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Messages -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4 chat-messages-container">
      <MessageBubble
        v-for="message in messages"
        :key="message.id"
        :message="message"
        :currentUserId="currentUser.id"
      />
    </div>

    <!-- Message input -->
    <MessageInput @send-message="sendMessage" />
  </div>
</template>

<script setup>
import { defineProps, defineEmits, watch } from 'vue'
import MessageBubble from './MessageBubble.vue'
import MessageInput from './MessageInput.vue'

const props = defineProps({
  conversation: Object,
  messages: Array,
  currentUser: Object
})

const emit = defineEmits(['send-message'])

// Safe profile picture helper
const getProfilePictureUrl = (entity) => {
  return (
    entity?.profile_picture ||
    entity?.profile?.profile_picture ||
    '/default-avatar.png'
  )
}

// Safe timestamp
function formatTimestamp(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// Forward sendMessage to parent
function sendMessage(data) {
  console.log('ChatArea: Forwarding sendMessage to parent with:', data)
  emit('send-message', data)
}

// Watch messages for debugging
watch(() => props.messages, (newMessages) => {
  console.log('ChatArea: Messages updated:', newMessages)
}, { immediate: true })
</script>