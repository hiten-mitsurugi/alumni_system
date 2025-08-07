<template>
  <div class="bg-white border-t border-gray-200">
    <!-- Reply Preview -->
    <ReplyPreview
      v-if="replyingTo"
      :replyingTo="replyingTo"
      @cancel-reply="cancelReply"
    />
    
    <div class="p-4">
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

        <!-- Emoji Button -->
        <div class="relative">
          <button
            @click="toggleEmojiPicker"
            class="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
            title="Add emoji"
          >
            😀
          </button>
          
          <!-- Emoji Picker -->
          <EmojiPicker 
            :isVisible="showEmojiPicker"
            @emoji-selected="insertEmoji"
            @close="showEmojiPicker = false"
          />
        </div>

        <!-- Textarea -->
        <textarea
          ref="textareaRef"
          v-model="content"
          placeholder="Type a message..."
          rows="1"
          class="flex-1 p-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-green-500"
          @keydown="handleKeyDown"
          @input="adjustTextareaHeight"
        ></textarea>

        <!-- Send Button -->
        <button
          @click="send"
          :disabled="!canSend"
          :class="[
            'p-2 rounded-lg transition-all duration-200',
            canSend
              ? 'text-green-600 hover:bg-green-50'
              : 'text-gray-400 cursor-not-allowed'
          ]"
          @mousedown="() => console.log('MessageInput: Send button mousedown')"
          @mouseup="() => console.log('MessageInput: Send button mouseup')"
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
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted, computed } from 'vue'
import EmojiPicker from './EmojiPicker.vue'
import ReplyPreview from './ReplyPreview.vue'

const props = defineProps({
  replyingTo: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['send-message', 'cancel-reply'])
const content = ref('')
const attachments = ref([]) // Store selected files
const fileInput = ref(null)
const textareaRef = ref(null)
const showEmojiPicker = ref(false)

// Debug replyingTo prop changes
console.log('MessageInput: Initial replyingTo prop:', props.replyingTo)

// Watch for changes to replyingTo prop
import { watch } from 'vue'
watch(() => props.replyingTo, (newValue, oldValue) => {
  console.log('MessageInput: replyingTo prop changed:')
  console.log('  Old value:', oldValue)
  console.log('  New value:', newValue)
  console.log('  Should show ReplyPreview:', !!newValue)
}, { immediate: true, deep: true })

// Computed property for send button state
const canSend = computed(() => {
  const hasContent = content.value && content.value.trim().length > 0
  const hasAttachments = attachments.value.length > 0
  const result = hasContent || hasAttachments
  
  // Debug logging (can be removed later)
  if (content.value !== undefined) {
    console.log('MessageInput: canSend computed - content:', JSON.stringify(content.value), 'length:', content.value.length, 'trimmed:', content.value.trim().length, 'canSend:', result)
  }
  
  return result
})

// Click outside handler to close emoji picker
function handleClickOutside(event) {
  const emojiPickerEl = event.target.closest('.emoji-picker-container')
  const emojiButtonEl = event.target.closest('[title="Add emoji"]')
  
  if (!emojiPickerEl && !emojiButtonEl && showEmojiPicker.value) {
    showEmojiPicker.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  
  // Add test function to window for debugging
  window.testMessageSend = () => {
    console.log('Window test: Setting test content and sending...')
    content.value = 'Test message 🙂'
    nextTick(() => {
      console.log('Window test: Content set, calling send()')
      send()
    })
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Emoji picker methods
function toggleEmojiPicker() {
  showEmojiPicker.value = !showEmojiPicker.value
}

function insertEmoji(emoji) {
  console.log('MessageInput: Inserting emoji:', emoji)
  const textarea = textareaRef.value
  
  if (!textarea) {
    console.error('MessageInput: Textarea ref not found')
    return
  }
  
  const start = textarea.selectionStart || 0
  const end = textarea.selectionEnd || 0
  
  console.log('MessageInput: Current content before emoji:', JSON.stringify(content.value))
  console.log('MessageInput: Cursor position:', start, 'to', end)
  
  // Insert emoji at cursor position
  const newContent = content.value.substring(0, start) + emoji + content.value.substring(end)
  content.value = newContent
  
  console.log('MessageInput: New content after emoji:', JSON.stringify(content.value))
  
  // Close emoji picker
  showEmojiPicker.value = false
  
  // Focus back on textarea and set cursor position
  nextTick(() => {
    textarea.focus()
    const newCursorPos = start + emoji.length
    textarea.setSelectionRange(newCursorPos, newCursorPos)
    adjustTextareaHeight()
    console.log('MessageInput: Emoji insertion completed, cursor at:', newCursorPos)
  })
}

// Auto-resize textarea
function adjustTextareaHeight() {
  const textarea = textareaRef.value
  if (textarea) {
    textarea.style.height = 'auto'
    const newHeight = Math.min(textarea.scrollHeight, 120) // Max height of ~6 lines
    textarea.style.height = newHeight + 'px'
  }
}

// Handle keyboard shortcuts
function handleKeyDown(event) {
  console.log('MessageInput: Key pressed:', event.key, 'shiftKey:', event.shiftKey)
  
  // Send on Enter (without Shift)
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    console.log('MessageInput: Enter pressed, calling send()')
    send()
  }
  
  // Toggle emoji picker on Ctrl/Cmd + E
  if ((event.ctrlKey || event.metaKey) && event.key === 'e') {
    event.preventDefault()
    toggleEmojiPicker()
  }
  
  // Close emoji picker on Escape
  if (event.key === 'Escape' && showEmojiPicker.value) {
    event.preventDefault()
    showEmojiPicker.value = false
  }
}

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
  console.log('MessageInput: =========================')
  console.log('MessageInput: Send function called')
  console.log('MessageInput: canSend value:', canSend.value)
  console.log('MessageInput: Raw content:', JSON.stringify(content.value))
  console.log('MessageInput: Content type:', typeof content.value)
  console.log('MessageInput: Content length:', content.value?.length)
  console.log('MessageInput: Trimmed content:', JSON.stringify(content.value?.trim()))
  console.log('MessageInput: Trimmed length:', content.value?.trim()?.length)
  console.log('MessageInput: Attachments count:', attachments.value.length)
  console.log('MessageInput: =========================')
  
  if (!canSend.value) {
    console.log('MessageInput: Cannot send - canSend is false')
    return
  }
  
  console.log('MessageInput: Validation passed, emitting send-message event')
  
  try {
    emit('send-message', {
      content: content.value,
      attachments: attachments.value
    })
    console.log('MessageInput: send-message event emitted successfully')
  } catch (error) {
    console.error('MessageInput: Error emitting send-message event:', error)
  }
  
  // Clear form
  console.log('MessageInput: Clearing form...')
  content.value = ''
  attachments.value = []
  if (fileInput.value) {
    fileInput.value.value = '' // Reset input
  }
  
  // Reset textarea height
  nextTick(() => {
    adjustTextareaHeight()
  })
  
  console.log('MessageInput: Message sent and form cleared')
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

// Reply functionality
const cancelReply = () => {
  emit('cancel-reply')
}
</script>