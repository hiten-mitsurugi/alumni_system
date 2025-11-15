<template>
  <div class="mention-wrapper" ref="mentionWrapper">
    <!-- Textarea with mention detection -->
    <div class="relative">
      <textarea
        ref="textarea"
        v-model="internalText"
        @input="handleInput"
        @keydown="handleKeydown"
        :placeholder="placeholder"
        :class="[
          'w-full p-3 border rounded-lg resize-none transition-colors duration-200',
          themeStore.isDark 
            ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
            : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
        ]"
        :rows="rows"
      ></textarea>
      
      <!-- Mention dropdown -->
      <div
        v-if="showMentionDropdown"
        ref="mentionDropdown"
        :class="[
          'absolute z-50 w-80 max-h-60 overflow-y-auto shadow-lg rounded-lg border',
          themeStore.isDark 
            ? 'bg-gray-800 border-gray-600' 
            : 'bg-white border-gray-200'
        ]"
        :style="dropdownStyle"
      >
        <!-- Loading state -->
        <div v-if="loading" class="p-4 text-center">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto"></div>
          <p class="mt-2 text-sm text-gray-500">Searching users...</p>
        </div>
        
        <!-- No results -->
        <div v-else-if="mentionUsers.length === 0 && currentMentionQuery.length >= 2" class="p-4 text-center">
          <p :class="themeStore.isDark ? 'text-gray-400' : 'text-gray-500'">
            No users found for "{{ currentMentionQuery }}"
          </p>
        </div>
        
        <!-- User list -->
        <div v-else>
          <div
            v-for="(user, index) in mentionUsers"
            :key="user.id"
            :class="[
              'flex items-center p-3 cursor-pointer transition-colors duration-150',
              index === selectedMentionIndex
                ? (themeStore.isDark ? 'bg-gray-700' : 'bg-blue-50')
                : (themeStore.isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-50')
            ]"
            @click="selectMention(user)"
          >
            <!-- User avatar -->
            <div class="flex-shrink-0 w-10 h-10 rounded-full overflow-hidden bg-gray-300 mr-3">
              <img
                v-if="user.profile_picture"
                :src="user.profile_picture"
                :alt="user.full_name"
                class="w-full h-full object-cover"
              />
              <div
                v-else
                :class="[
                  'w-full h-full flex items-center justify-center text-sm font-medium',
                  themeStore.isDark ? 'bg-gray-600 text-gray-300' : 'bg-gray-400 text-white'
                ]"
              >
                {{ user.first_name?.[0] }}{{ user.last_name?.[0] }}
              </div>
            </div>
            
            <!-- User info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center">
                <p :class="[
                  'text-sm font-medium truncate',
                  themeStore.isDark ? 'text-white' : 'text-gray-900'
                ]">
                  {{ user.full_name }}
                </p>
                <span
                  v-if="user.is_connection"
                  class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                >
                  Connection
                </span>
              </div>
              <p :class="[
                'text-xs truncate',
                themeStore.isDark ? 'text-gray-400' : 'text-gray-500'
              ]">
                @{{ user.username }} • {{ user.program }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useThemeStore } from '@/stores/theme'
import api from '@/services/api'

// Props
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Type your message... Use @ to mention someone'
  },
  rows: {
    type: Number,
    default: 3
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'mention', 'submit'])

// Stores
const themeStore = useThemeStore()

// Refs
const textarea = ref(null)
const mentionWrapper = ref(null)
const mentionDropdown = ref(null)

// Reactive data
const internalText = ref(props.modelValue)
const showMentionDropdown = ref(false)
const mentionUsers = ref([])
const currentMentionQuery = ref('')
const mentionStartPosition = ref(-1)
const selectedMentionIndex = ref(0)
const loading = ref(false)
const dropdownStyle = ref({})

// Watch for prop changes
watch(() => props.modelValue, (newValue) => {
  if (newValue !== internalText.value) {
    internalText.value = newValue
  }
})

// Watch for internal text changes
watch(internalText, (newValue) => {
  emit('update:modelValue', newValue)
})

// Methods
const handleInput = (event) => {
  const text = event.target.value
  const cursorPosition = event.target.selectionStart
  
  // Check if we're typing after an @ symbol
  const beforeCursor = text.substring(0, cursorPosition)
  const mentionMatch = beforeCursor.match(/@(\w*)$/)
  
  if (mentionMatch) {
    const mentionQuery = mentionMatch[1]
    mentionStartPosition.value = beforeCursor.lastIndexOf('@')
    currentMentionQuery.value = mentionQuery
    
    if (mentionQuery.length >= 0) {
      showMentionDropdown.value = true
      selectedMentionIndex.value = 0
      searchUsers(mentionQuery)
      positionDropdown()
    }
  } else {
    hideMentionDropdown()
  }
}

const handleKeydown = (event) => {
  if (showMentionDropdown.value) {
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault()
        selectedMentionIndex.value = Math.min(
          selectedMentionIndex.value + 1,
          mentionUsers.value.length - 1
        )
        break
        
      case 'ArrowUp':
        event.preventDefault()
        selectedMentionIndex.value = Math.max(selectedMentionIndex.value - 1, 0)
        break
        
      case 'Enter':
      case 'Tab':
        if (mentionUsers.value.length > 0) {
          event.preventDefault()
          selectMention(mentionUsers.value[selectedMentionIndex.value])
        }
        break
        
      case 'Escape':
        event.preventDefault()
        hideMentionDropdown()
        break
    }
  } else if (event.key === 'Enter' && event.ctrlKey) {
    // Ctrl+Enter to submit
    emit('submit', internalText.value)
  }
}

const searchUsers = async (query) => {
  if (query.length < 2 && query.length > 0) {
    return
  }
  
  try {
    loading.value = true
    
    const response = await api.get('/auth/mention-search/', {
      params: {
        q: query,
        limit: 8
      }
    })
    
    mentionUsers.value = response.data.users || []
    selectedMentionIndex.value = 0
    
  } catch (error) {
    console.error('❌ Error searching users for mentions:', error)
    console.error('❌ Error details:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      config: error.config
    })
    mentionUsers.value = []
  } finally {
    loading.value = false
  }
}

const selectMention = (user) => {
  const beforeMention = internalText.value.substring(0, mentionStartPosition.value)
  const afterCursor = internalText.value.substring(textarea.value.selectionStart)
  
  // Insert the mention using full name instead of username
  const mentionText = `@${user.full_name} `
  internalText.value = beforeMention + mentionText + afterCursor
  
  // Position cursor after the mention
  const newCursorPosition = beforeMention.length + mentionText.length
  
  nextTick(() => {
    textarea.value.focus()
    textarea.value.setSelectionRange(newCursorPosition, newCursorPosition)
  })
  
  // Emit mention event with full user data
  emit('mention', {
    user,
    mentionText: `@${user.full_name}`,
    username: user.username, // Keep username for backend processing
    position: {
      start: mentionStartPosition.value,
      end: beforeMention.length + mentionText.length - 1
    }
  })
  
  hideMentionDropdown()
}

const hideMentionDropdown = () => {
  showMentionDropdown.value = false
  mentionUsers.value = []
  currentMentionQuery.value = ''
  mentionStartPosition.value = -1
}

const positionDropdown = async () => {
  await nextTick()
  
  if (!textarea.value || !mentionDropdown.value) return
  
  const textMetrics = getTextMetrics()
  
  dropdownStyle.value = {
    top: `${textMetrics.lineHeight + 5}px`,
    left: `${textMetrics.characterWidth}px`
  }
}

const getTextMetrics = () => {
  // Simple approximation - in a real implementation, you might want more precise positioning
  const lineHeight = 24 // Approximate line height
  const characterWidth = mentionStartPosition.value * 8 // Approximate character width
  
  return {
    lineHeight,
    characterWidth: Math.min(characterWidth, 200) // Don't go too far right
  }
}

// Handle clicks outside to close dropdown
const handleClickOutside = (event) => {
  if (mentionWrapper.value && !mentionWrapper.value.contains(event.target)) {
    hideMentionDropdown()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.mention-wrapper {
  position: relative;
}

/* Custom scrollbar for mention dropdown */
.mention-dropdown::-webkit-scrollbar {
  width: 6px;
}

.mention-dropdown::-webkit-scrollbar-track {
  background-color: #f3f4f6;
}

.mention-dropdown::-webkit-scrollbar-thumb {
  background-color: #d1d5db;
  border-radius: 9999px;
}

.mention-dropdown::-webkit-scrollbar-thumb:hover {
  background-color: #9ca3af;
}

/* Dark mode scrollbar */
[data-theme="dark"] .mention-dropdown::-webkit-scrollbar-track {
  background-color: #1f2937;
}

[data-theme="dark"] .mention-dropdown::-webkit-scrollbar-thumb {
  background-color: #4b5563;
}

[data-theme="dark"] .mention-dropdown::-webkit-scrollbar-thumb:hover {
  background-color: #6b7280;
}
</style>