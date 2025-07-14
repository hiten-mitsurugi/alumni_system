<template>
  <div class="flex flex-col h-full">
    <!-- Chat Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
      <div class="flex items-center space-x-3">
        <img
          :src="conversation.type === 'private' ? conversation.mate.avatar : conversation.group.avatar"
          :alt="conversation.type === 'private' ? conversation.mate.name : conversation.group.name"
          class="w-10 h-10 rounded-full object-cover"
        />
        <div>
          <h3 class="font-semibold text-gray-900">
            {{ conversation.type === 'private' ? conversation.mate.name : conversation.group.name }}
          </h3>
          <p v-if="conversation.type === 'private'" class="text-sm text-gray-500">
            {{ conversation.mate.status }}
          </p>
          <p v-else class="text-sm text-gray-500">
            {{ conversation.group.memberCount }} members
          </p>
        </div>
      </div>
      <!-- Actions Menu -->
      <div class="relative">
        <button
          @click="showDropdown = !showDropdown"
          class="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-full transition-colors duration-200"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zM12 13a1 1 0 110-2 1 1 0 010 2zM12 20a1 1 0 110-2 1 1 0 010 2z" />
          </svg>
        </button>
        <div
          v-if="showDropdown"
          class="absolute right-0 top-full mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10"
        >
          <button
            @click="handleMuteToggle"
            class="w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center space-x-2 transition-colors duration-200"
          >
            <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
              <path v-if="conversation.isMuted" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
            </svg>
            <span class="text-gray-700">{{ conversation.isMuted ? 'Unmute' : 'Mute' }} notifications</span>
          </button>
          <button
            v-if="conversation.type === 'private'"
            @click="handleBlockToggle"
            :class="[
              'w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center space-x-2 transition-colors duration-200',
              conversation.isBlocked ? 'text-green-600' : 'text-red-600'
            ]"
          >
            <svg v-if="!conversation.isBlocked" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728" />
            </svg>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{{ conversation.isBlocked ? 'Unblock user' : 'Block user' }}</span>
          </button>
        </div>
      </div>
    </div>
    <!-- Messages Area -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4" ref="messagesContainer">
      <MessageBubble
        v-for="message in messages"
        :key="message.id"
        :message="message"
        :current-user-id="currentUser.id"
      />
    </div>
    <!-- Message Input -->
    <MessageInput @send-message="$emit('send-message', $event)" />
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import MessageBubble from './MessageBubble.vue'
import MessageInput from './MessageInput.vue'

const props = defineProps({
  conversation: Object,
  messages: Array,
  currentUser: Object
})

const emit = defineEmits(['send-message', 'toggle-mute', 'toggle-block'])

const showDropdown = ref(false)
const messagesContainer = ref(null)

const handleMuteToggle = () => {
  emit('toggle-mute')
  showDropdown.value = false
}

const handleBlockToggle = () => {
  emit('toggle-block')
  showDropdown.value = false
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

watch(() => props.messages, () => {
  scrollToBottom()
}, { deep: true })
</script>
