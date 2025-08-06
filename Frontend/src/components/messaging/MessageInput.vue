<template>
  <div class="p-4 bg-white border-t border-gray-200">
    <div class="flex items-center gap-2">
      <!-- Hidden File Input -->
      <input
        type="file"
        ref="fileInput"
        multiple
        class="hidden"
        @change="handleFileSelect"
      />

      <!-- Attach Button -->
      <button
        @click="triggerFilePicker"
        class="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
        title="Attach files"
      >
        📎
      </button>

      <!-- Textarea -->
      <textarea
        v-model="content"
        placeholder="Type a message..."
        rows="1"
        class="flex-1 p-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-green-500"
        @keydown.enter.prevent="send"
      ></textarea>

      <!-- Send Button -->
      <button
        @click="send"
        class="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-all duration-200"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9-7-9-7v14z" />
        </svg>
      </button>
    </div>

    <!-- Show Selected Files -->
    <div v-if="attachments.length" class="mt-2 flex flex-wrap gap-2">
      <div
        v-for="(file, index) in attachments"
        :key="index"
        class="flex items-center bg-gray-100 px-2 py-1 rounded text-sm"
      >
        {{ file.name }}
        <button @click="removeAttachment(index)" class="ml-2 text-red-500">✕</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['send-message'])
const content = ref('')
const attachments = ref([]) // Store selected files
const fileInput = ref(null)

// Open file picker
function triggerFilePicker() {
  fileInput.value.click()
}

// Handle selected files
function handleFileSelect(event) {
  const files = Array.from(event.target.files)
  attachments.value.push(...files)
}

// Remove selected attachment before sending
function removeAttachment(index) {
  attachments.value.splice(index, 1)
}

// Send message with attachments
function send() {
  if (!content.value.trim() && attachments.value.length === 0) {
    console.log('MessageInput: No content or attachments, aborting')
    return
  }
  console.log('MessageInput: Emitting send-message with:', { content: content.value, attachments: attachments.value })
  emit('send-message', {
    content: content.value,
    attachments: attachments.value
  })
  content.value = ''
  attachments.value = []
  fileInput.value.value = '' // Reset input
}
</script>