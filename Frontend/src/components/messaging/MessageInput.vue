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

    <!-- Show Selected Files with Previews -->
    <div v-if="attachments.length" class="mt-3 space-y-2">
      <div class="flex flex-wrap gap-3">
        <div
          v-for="(file, index) in attachments"
          :key="index"
          class="relative group"
        >
          <!-- Image Preview -->
          <div v-if="isImageFile(file)" class="relative">
            <img
              :src="getFilePreviewUrl(file)"
              :alt="file.name"
              class="w-20 h-20 object-cover rounded-lg border border-gray-200"
            />
            <button
              @click="removeAttachment(index)"
              class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs hover:bg-red-600"
            >
              ✕
            </button>
            <div class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-xs p-1 rounded-b-lg truncate">
              {{ file.name }}
            </div>
          </div>

          <!-- File Preview -->
          <div v-else class="flex items-center bg-gray-100 px-3 py-2 rounded-lg border border-gray-200 min-w-[200px]">
            <div class="flex-shrink-0 mr-2">
              <!-- File type icon -->
              <svg v-if="getFileType(file) === 'pdf'" class="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 24 24">
                <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
              </svg>
              <svg v-else-if="getFileType(file) === 'doc'" class="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
              </svg>
              <svg v-else class="w-6 h-6 text-gray-600" fill="currentColor" viewBox="0 0 24 24">
                <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-sm truncate">{{ file.name }}</p>
              <p class="text-xs text-gray-500">{{ getFileSize(file) }} • {{ getFileType(file).toUpperCase() }}</p>
            </div>
            <button
              @click="removeAttachment(index)"
              class="ml-2 text-red-500 hover:text-red-700 text-sm"
            >
              ✕
            </button>
          </div>
        </div>
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

// Helper methods for file handling
const isImageFile = (file) => {
  return file.type && file.type.startsWith('image/')
}

const getFilePreviewUrl = (file) => {
  return URL.createObjectURL(file)
}

const getFileType = (file) => {
  if (!file.name) return 'file'
  const extension = file.name.split('.').pop()?.toLowerCase()
  return extension || 'file'
}

const getFileSize = (file) => {
  const bytes = file.size
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>