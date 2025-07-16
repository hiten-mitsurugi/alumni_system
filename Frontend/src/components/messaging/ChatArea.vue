<template>
  <div class="flex-1 flex flex-col">
    <!-- Header with user/group info -->
    <div class="p-4 bg-white border-b border-gray-200 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <!-- ✅ Safe avatar -->
        <img :src="conversation.type === 'private'
            ? getProfilePictureUrl(conversation.mate)
            : conversation.group?.group_picture || '/default-group.png'
          " alt="Avatar" class="w-10 h-10 rounded-full object-cover" />
        <div>
          <!-- ✅ Safe name -->
          <h3 class="font-semibold text-gray-900">
            {{
              conversation.type === 'private'
                ? `${conversation.mate.first_name} ${conversation.mate.last_name}`
                : conversation.group?.name || 'Group'
            }}
          </h3>
          <!-- ✅ Safe status -->
          <p v-if="conversation.type === 'private'" class="text-sm text-gray-500">
            {{ conversation.mate?.profile?.status ?? 'online' }}
          </p>

        </div>
      </div>
    </div>

    <!-- Messages -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4">
      <div v-for="message in messages" :key="message.id" :class="[
        'flex',
        message.sender?.id === currentUser?.id ? 'justify-end' : 'justify-start'
      ]">
        <div :class="[
          'max-w-xs p-3 rounded-lg',
          message.sender?.id === currentUser?.id ? 'bg-green-100' : 'bg-gray-100'
        ]">
          <p class="text-sm">{{ message.content }}</p>
          <span class="text-xs text-gray-500">
            {{ formatTimestamp(message.timestamp) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Message input -->
    <MessageInput @send-message="sendMessage" />
  </div>
</template>

<script setup>
import { defineProps } from 'vue'
import MessageInput from './MessageInput.vue'

// ✅ Props
defineProps({
  conversation: Object,
  messages: Array,
  currentUser: Object
})

// ✅ Safe profile picture helper
const getProfilePictureUrl = (entity) => {
  return (
    entity?.profile_picture || // direct user field
    entity?.profile?.profile_picture || // nested profile model
    '/default-avatar.png' // fallback
  )
}

// ✅ Safe timestamp
function formatTimestamp(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// ✅ Dummy send handler (kept if needed)
function sendMessage(data) {
  // Will be emitted to parent
}
</script>
