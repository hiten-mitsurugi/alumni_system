<template>
  <div 
    ref="chatbotContainer"
    class="fixed z-50"
    :style="{ 
      bottom: position.y + 'px', 
      right: position.x + 'px',
      touchAction: 'none'
    }"
  >
    <!-- Chat Toggle Button -->
    <button
      v-if="!isOpen"
      @click="toggleChat"
      @mousedown="startDrag"
      @touchstart="startDrag"
      :class="[
        'p-4 rounded-full shadow-lg transition-all hover:scale-110 cursor-move',
        themeStore.isDarkMode ? 'bg-orange-600 hover:bg-orange-700' : 'bg-orange-500 hover:bg-orange-600',
        isDragging && 'scale-110'
      ]"
    >
      <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
      </svg>
    </button>

    <!-- Chat Window -->
    <transition name="slide-up">
      <div
        v-if="isOpen"
        :class="[
          'w-96 h-[600px] rounded-lg shadow-2xl flex flex-col',
          themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white'
        ]"
      >
        <!-- Header -->
        <div 
          class="flex items-center justify-between p-4 border-b bg-orange-600 rounded-t-lg cursor-move"
          @mousedown="startDrag"
          @touchstart="startDrag"
        >
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-full bg-white flex items-center justify-center">
              <svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h3 class="font-semibold text-white">ATENDA AI Assistant</h3>
              <p class="text-xs text-orange-100">{{ isTyping ? 'Typing...' : 'Online' }}</p>
            </div>
          </div>
          <button @click="toggleChat" class="text-white hover:bg-orange-700 p-2 rounded">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Messages Container -->
        <div
          ref="messagesContainer"
          :class="[
            'flex-1 overflow-y-auto p-4 space-y-4',
            themeStore.isDarkMode ? 'bg-gray-900' : 'bg-gray-50'
          ]"
        >
          <div v-for="(message, index) in messages" :key="index" :class="['flex', message.sender === 'user' ? 'justify-end' : 'justify-start']">
            <div :class="[
              'max-w-[80%] rounded-lg p-3',
              message.sender === 'user'
                ? 'bg-orange-600 text-white'
                : themeStore.isDarkMode
                  ? 'bg-gray-700 text-gray-100'
                  : 'bg-white text-gray-900 shadow'
            ]">
              <p class="text-sm whitespace-pre-wrap">{{ message.text }}</p>
              <p :class="[
                'text-xs mt-1',
                message.sender === 'user' ? 'text-orange-100' : 'text-gray-500'
              ]">
                {{ formatTime(message.timestamp) }}
              </p>
            </div>
          </div>

          <!-- Typing Indicator -->
          <div v-if="isTyping" class="flex justify-start">
            <div :class="[
              'rounded-lg p-3',
              themeStore.isDarkMode ? 'bg-gray-700' : 'bg-white shadow'
            ]">
              <div class="flex space-x-2">
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div :class="[
          'p-4 border-t',
          themeStore.isDarkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'
        ]">
          <form @submit.prevent="sendMessage" class="flex space-x-2">
            <input
              v-model="inputMessage"
              type="text"
              :disabled="isTyping"
              placeholder="Type your message..."
              :class="[
                'flex-1 px-4 py-2 rounded-lg border focus:outline-none focus:ring-2 focus:ring-orange-500',
                themeStore.isDarkMode
                  ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400'
                  : 'bg-white border-gray-300 text-gray-900',
                isTyping && 'opacity-50 cursor-not-allowed'
              ]"
            />
            <button
              type="submit"
              :disabled="!inputMessage.trim() || isTyping"
              :class="[
                'px-4 py-2 rounded-lg font-medium transition-colors',
                !inputMessage.trim() || isTyping
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-orange-600 hover:bg-orange-700',
                'text-white'
              ]"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import axios from 'axios'

const themeStore = useThemeStore()

const isOpen = ref(false)
const messages = ref([])
const inputMessage = ref('')
const isTyping = ref(false)
const messagesContainer = ref(null)
const sessionId = ref('')
const chatbotContainer = ref(null)

// Dragging state
const isDragging = ref(false)
const position = ref({ x: 16, y: 80 }) // Default position (right: 16px, bottom: 80px on mobile)
const dragStart = ref({ x: 0, y: 0 })

// N8N Webhook Configuration
const N8N_WEBHOOK_URL = 'https://romantik123.app.n8n.cloud/webhook/87db0748-958e-4a67-9ac2-db37f1ff4d71/chat'

onMounted(() => {
  // Generate unique session ID
  sessionId.value = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  
  // Add welcome message
  messages.value.push({
    sender: 'bot',
    text: 'Hello! Welcome to ATENDA. How may I help you today?',
    timestamp: new Date()
  })

  // Set initial position based on screen size
  const isMobile = window.innerWidth < 768
  position.value = { x: 16, y: isMobile ? 80 : 16 }

  // Add event listeners for dragging
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
  document.addEventListener('touchmove', onDrag, { passive: false })
  document.addEventListener('touchend', stopDrag)
})

onUnmounted(() => {
  // Remove event listeners
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('touchend', stopDrag)
})

const startDrag = (e) => {
  // Prevent opening chat when starting drag
  e.stopPropagation()
  
  isDragging.value = true
  
  const clientX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX
  const clientY = e.type.includes('touch') ? e.touches[0].clientY : e.clientY
  
  // Store the starting position
  dragStart.value = {
    x: clientX,
    y: clientY,
    initialX: position.value.x,
    initialY: position.value.y
  }
}

const onDrag = (e) => {
  if (!isDragging.value) return
  
  e.preventDefault()
  
  const clientX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX
  const clientY = e.type.includes('touch') ? e.touches[0].clientY : e.clientY
  
  // Calculate new position (inverted X because we're using right positioning, normal Y for bottom)
  const deltaX = dragStart.value.x - clientX
  const deltaY = dragStart.value.y - clientY
  
  let newX = dragStart.value.initialX + deltaX
  let newY = dragStart.value.initialY + deltaY
  
  // Get viewport dimensions
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight
  const chatbotWidth = chatbotContainer.value?.offsetWidth || 60
  const chatbotHeight = chatbotContainer.value?.offsetHeight || 60
  
  // Constrain position within viewport
  newX = Math.max(0, Math.min(newX, viewportWidth - chatbotWidth))
  newY = Math.max(0, Math.min(newY, viewportHeight - chatbotHeight))
  
  position.value = { x: newX, y: newY }
}

const stopDrag = (e) => {
  if (!isDragging.value) return
  
  const wasJustClick = Math.abs(position.value.x - dragStart.value.initialX) < 5 && 
                        Math.abs(position.value.y - dragStart.value.initialY) < 5
  
  isDragging.value = false
  
  // If it was just a click (not a drag), toggle chat
  if (wasJustClick && !isOpen.value) {
    toggleChat()
  }
}

const toggleChat = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    nextTick(() => {
      scrollToBottom()
    })
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return

  const userMessage = inputMessage.value.trim()
  
  // Add user message to chat
  messages.value.push({
    sender: 'user',
    text: userMessage,
    timestamp: new Date()
  })

  inputMessage.value = ''
  isTyping.value = true

  nextTick(() => {
    scrollToBottom()
  })

  try {
    // Send message to n8n webhook
    const response = await axios.post(N8N_WEBHOOK_URL, {
      action: 'sendMessage',
      chatInput: userMessage,
      sessionId: sessionId.value
    })

    // Add bot response
    messages.value.push({
      sender: 'bot',
      text: response.data.output || 'I apologize, but I encountered an error processing your request.',
      timestamp: new Date()
    })
  } catch (error) {
    console.error('Error sending message to AI:', error)
    messages.value.push({
      sender: 'bot',
      text: 'Sorry, I encountered an error. Please try again later.',
      timestamp: new Date()
    })
  } finally {
    isTyping.value = false
    nextTick(() => {
      scrollToBottom()
    })
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #CBD5E0;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #A0AEC0;
}
</style>
