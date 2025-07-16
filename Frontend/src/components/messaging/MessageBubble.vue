<template>
  <div :class="['flex gap-3', isOwnMessage && 'flex-row-reverse']">
    <div :class="['flex flex-col max-w-[70%]', isOwnMessage && 'items-end']">
      <!-- Message Content / Attachment -->
      <div
        :class="[
          'relative shadow-sm',
          isOwnMessage ? 'bg-blue-500 text-white rounded-xl rounded-br-none' : 'bg-gray-100 text-gray-900 rounded-xl rounded-bl-none',
          // Conditional padding and overflow for images
          message.attachments && message.attachments.length > 0 && message.attachments[0].type && message.attachments[0].type.startsWith('image/') ? 'p-0 overflow-hidden' : 'px-4 py-2 break-words'
        ]"
      >
        <!-- Render Image Attachment -->
        <template v-if="message.attachments && message.attachments.length > 0 && message.attachments[0].type && message.attachments[0].type.startsWith('image/') && message.attachments[0].url">
          <img
            :src="message.attachments[0].url"
            :alt="message.attachments[0].name"
            class="max-w-full h-auto object-cover rounded-xl"
            :class="isOwnMessage ? 'rounded-br-none' : 'rounded-bl-none'"
            style="max-height: 300px;"
          />
        </template>
        <!-- Render File Attachment (PDF, etc.) -->
        <template v-else-if="message.attachments && message.attachments.length > 0">
          <a href="#" class="flex items-center space-x-2 p-2 rounded-lg"
             :class="isOwnMessage ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'">
            <!-- Replaced PaperclipIcon with direct SVG for robustness -->
            <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.414a4 4 0 00-5.656-5.656l-6.415 6.415a6 6 0 108.486 8.485L20.5 13.5" />
            </svg>
            <span class="truncate font-medium">{{ message.attachments[0].name }}</span>
          </a>
        </template>
        <!-- Render Text Content -->
        <template v-else>
          <p class="text-sm">{{ message.content }}</p>
        </template>
      </div>

      <!-- Timestamp and Read Status -->
      <div
        :class="[
          'flex items-center gap-1 mt-1 text-xs text-gray-500',
          isOwnMessage && 'flex-row-reverse'
        ]"
      >
        <span>{{ message.timestamp }}</span>
        <span
          v-if="isOwnMessage"
          :class="message.isRead ? 'text-blue-500' : ''"
        >
          {{ message.isRead ? '✓✓' : '✓' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: Object,
  currentUserId: Number
})

const isOwnMessage = computed(() => {
  return props.message.sender?.id === props.currentUserId // ✅ FIX
})
</script>

