<template>
  <div class="w-80 bg-white border-l border-gray-200 flex flex-col">
    <!-- Header -->
    <div class="p-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-800">Chat Info</h3>
        <button @click="$emit('close')" class="p-1 rounded-lg hover:bg-gray-100 transition-colors">
          <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto">
      <!-- User/Group Profile Section -->
      <div class="p-4 border-b border-gray-200">
        <div class="text-center">
          <div class="relative inline-block">
            <img 
              :src="conversation.type === 'private' 
                ? getProfilePictureUrl(conversation.mate) 
                : conversation.group?.group_picture || '/default-group.png'"
              alt="Profile"
              class="w-20 h-20 rounded-full object-cover mx-auto mb-3"
            />
            <!-- Online status for private chats -->
            <div v-if="conversation.type === 'private'" 
                 :class="['absolute bottom-2 right-2 w-4 h-4 rounded-full border-2 border-white', getStatusColor(conversation.mate)]">
            </div>
          </div>
          <h4 class="font-semibold text-gray-900 text-lg">
            {{ conversation.type === 'private' 
                ? `${conversation.mate.first_name} ${conversation.mate.last_name}` 
                : conversation.group?.name || 'Group' }}
          </h4>
          <p v-if="conversation.type === 'private'" class="text-sm text-gray-500">
            @{{ conversation.mate.username }}
          </p>
          <p v-if="conversation.type === 'private'" :class="['text-sm mt-1', getStatusTextColor(conversation.mate)]">
            {{ getStatusText(conversation.mate) }}
          </p>
          <p v-else class="text-sm text-gray-500 mt-1">
            {{ conversation.group?.members?.length || 0 }} members
          </p>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="p-4 border-b border-gray-200">
        <div class="grid grid-cols-2 gap-3">
          <!-- Block/Unblock (only for private chats) -->
          <button 
            v-if="conversation.type === 'private'"
            @click="toggleBlock"
            :class="[
              'flex flex-col items-center p-3 rounded-lg transition-all duration-200',
              isBlocked 
                ? 'bg-red-50 text-red-600 hover:bg-red-100' 
                : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
            ]"
          >
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="9" stroke-width="2"></circle>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6"></path>
            </svg>
            <span class="text-xs font-medium">{{ isBlocked ? 'Unblock' : 'Block' }}</span>
          </button>

          <!-- Search Messages -->
          <button 
            @click="showSearchMessages = true"
            class="flex flex-col items-center p-3 rounded-lg bg-gray-50 text-gray-600 hover:bg-gray-100 transition-all duration-200"
          >
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span class="text-xs font-medium">Search</span>
          </button>

          <!-- Group Info (only for groups) -->
          <button 
            v-if="conversation.type === 'group'"
            @click="showGroupInfo = true"
            class="flex flex-col items-center p-3 rounded-lg bg-gray-50 text-gray-600 hover:bg-gray-100 transition-all duration-200"
          >
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M17 20h5v-2a3 3 0 00-5.196-2.121M17 20H7m10 0v-2c0-5.523-3.582-10-8-10s-8 4.477-8 10v2m8-10a3 3 0 110-6 3 3 0 010 6zm0 10a3 3 0 110-6 3 3 0 010 6z" />
            </svg>
            <span class="text-xs font-medium">Members</span>
          </button>
        </div>
      </div>

      <!-- Pinned Messages -->
      <div class="border-b border-gray-200">
        <button 
          @click="showPinnedMessages = !showPinnedMessages"
          class="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-amber-600" fill="currentColor" viewBox="0 0 24 24">
              <path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
            </svg>
            <span class="font-medium text-gray-900">Pinned Messages</span>
            <span class="bg-amber-100 text-amber-800 text-xs px-2 py-1 rounded-full">
              {{ pinnedMessages.length }}
            </span>
          </div>
          <svg 
            :class="['w-4 h-4 text-gray-400 transition-transform', showPinnedMessages ? 'rotate-180' : '']" 
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        
        <!-- Pinned Messages List -->
        <div v-if="showPinnedMessages" class="max-h-48 overflow-y-auto">
          <div v-if="pinnedMessages.length === 0" class="p-4 text-center text-gray-500 text-sm">
            No pinned messages
          </div>
          <div 
            v-for="message in pinnedMessages" 
            :key="message.id"
            class="p-3 mx-3 mb-2 bg-amber-50 rounded-lg cursor-pointer hover:bg-amber-100 transition-all duration-200 border border-amber-200 group relative"
            @click="scrollToMessage(message.id)"
          >
            <!-- Pin icon indicator -->
            <div class="absolute top-2 right-2">
              <svg class="w-3 h-3 text-amber-600 opacity-70 group-hover:opacity-100 transition-opacity" fill="currentColor" viewBox="0 0 24 24">
                <path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
            </div>
            <div class="flex items-start gap-2 pr-6">
              <img :src="getProfilePictureUrl(message.sender)" class="w-6 h-6 rounded-full object-cover" />
              <div class="flex-1 min-w-0">
                <p class="text-xs text-amber-700 font-medium">{{ message.sender.first_name }}</p>
                <p class="text-sm text-gray-800 line-clamp-2">{{ message.content }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ formatDate(message.timestamp) }}</p>
              </div>
            </div>
            <!-- Click indicator -->
            <div class="text-center mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <p class="text-xs text-amber-600 font-medium">Click to jump to message</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Shared Images -->
      <div class="border-b border-gray-200">
        <button 
          @click="showSharedImages = !showSharedImages"
          class="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span class="font-medium text-gray-900">Shared Images</span>
            <span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
              {{ sharedImages.length }}
            </span>
          </div>
          <svg 
            :class="['w-4 h-4 text-gray-400 transition-transform', showSharedImages ? 'rotate-180' : '']" 
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <!-- Shared Images Grid -->
        <div v-if="showSharedImages" class="p-3">
          <div v-if="sharedImages.length === 0" class="text-center text-gray-500 text-sm py-4">
            No shared images
          </div>
          <div class="grid grid-cols-3 gap-2">
            <div 
              v-for="image in sharedImages.slice(0, 9)" 
              :key="image.id"
              class="aspect-square bg-gray-100 rounded-lg overflow-hidden cursor-pointer hover:opacity-80 transition-opacity"
              @click="openMedia(image)"
            >
              <img 
                :src="image.url" 
                :alt="image.name"
                class="w-full h-full object-cover"
              />
            </div>
          </div>
          <button 
            v-if="sharedImages.length > 9" 
            class="w-full mt-3 p-2 text-sm text-blue-600 hover:text-blue-700 transition-colors"
            @click="showAllImages = true"
          >
            View All ({{ sharedImages.length }})
          </button>
        </div>
      </div>

      <!-- Shared Links -->
      <div class="border-b border-gray-200">
        <button 
          @click="showSharedLinks = !showSharedLinks"
          class="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <span class="font-medium text-gray-900">Shared Links</span>
            <span class="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full">
              {{ sharedLinks.length }}
            </span>
          </div>
          <svg 
            :class="['w-4 h-4 text-gray-400 transition-transform', showSharedLinks ? 'rotate-180' : '']" 
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <!-- Shared Links List -->
        <div v-if="showSharedLinks" class="max-h-48 overflow-y-auto">
          <div v-if="sharedLinks.length === 0" class="p-4 text-center text-gray-500 text-sm">
            No shared links
          </div>
          <a 
            v-for="link in sharedLinks" 
            :key="link.id"
            :href="link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="block p-3 mx-3 mb-2 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
          >
            <div class="flex items-start gap-3">
              <!-- Link preview image if available -->
              <div v-if="link.image_url" class="w-12 h-8 flex-shrink-0 rounded overflow-hidden bg-gray-200">
                <img 
                  :src="link.image_url" 
                  :alt="link.title"
                  class="w-full h-full object-cover"
                  @error="handleImageError"
                />
              </div>
              <!-- Default icon if no image -->
              <svg v-else class="w-4 h-4 text-purple-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-800 truncate">{{ link.title || link.url }}</p>
                <p v-if="link.description" class="text-xs text-gray-600 line-clamp-2 mt-1">{{ link.description }}</p>
                <div class="flex items-center gap-2 mt-1">
                  <p class="text-xs text-gray-500">{{ link.domain }}</p>
                  <span class="text-xs text-gray-400">•</span>
                  <p class="text-xs text-gray-400">{{ formatDate(link.timestamp) }}</p>
                </div>
              </div>
            </div>
          </a>
        </div>
      </div>

      <!-- Shared Files -->
      <div>
        <button 
          @click="showSharedFiles = !showSharedFiles"
          class="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span class="font-medium text-gray-900">Shared Files</span>
            <span class="bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded-full">
              {{ sharedFiles.length }}
            </span>
          </div>
          <svg 
            :class="['w-4 h-4 text-gray-400 transition-transform', showSharedFiles ? 'rotate-180' : '']" 
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <!-- Shared Files List -->
        <div v-if="showSharedFiles" class="max-h-48 overflow-y-auto">
          <div v-if="sharedFiles.length === 0" class="p-4 text-center text-gray-500 text-sm">
            No shared files
          </div>
          <div 
            v-for="file in sharedFiles" 
            :key="file.id"
            class="p-3 mx-3 mb-2 bg-orange-50 rounded-lg cursor-pointer hover:bg-orange-100 transition-colors"
            @click="downloadFile(file)"
          >
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-orange-200 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-orange-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-800 truncate">{{ file.name }}</p>
                <p class="text-xs text-gray-500">{{ formatFileSize(file.size) }} • {{ formatDate(file.timestamp) }}</p>
              </div>
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../../services/api'
import messagingService from '../../services/messaging'

// Props
const props = defineProps({
  conversation: {
    type: Object,
    required: true
  },
  messages: {
    type: Array,
    default: () => []
  },
  currentUser: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['close', 'block', 'unblock', 'scroll-to-message'])

// State
const isBlocked = ref(false)
const pinnedMessages = ref([])
const sharedImages = ref([])
const sharedLinks = ref([])
const sharedFiles = ref([])

// UI State
const showPinnedMessages = ref(true) // Start expanded for better UX
const showSharedImages = ref(false)
const showSharedLinks = ref(false)
const showSharedFiles = ref(false)
const showSearchMessages = ref(false)
const showGroupInfo = ref(false)
const showAllImages = ref(false)

// Helper functions
const getProfilePictureUrl = (entity) => {
  const BASE_URL = 'http://127.0.0.1:8000'
  const pic = entity?.profile_picture || entity?.group_picture
  return pic
    ? (pic.startsWith('http') ? pic : `${BASE_URL}${pic}`)
    : '/default-avatar.png'
}

const getStatusColor = (user) => {
  if (!user?.profile?.last_seen) return 'bg-gray-400'
  return isRecentlyActive(user) ? 'bg-green-500' : 'bg-gray-400'
}

const getStatusTextColor = (user) => {
  return isRecentlyActive(user) ? 'text-green-600' : 'text-gray-500'
}

const getStatusText = (user) => {
  if (!user?.profile?.last_seen) return 'Offline'
  return isRecentlyActive(user) ? 'Online' : 'Offline'
}

const isRecentlyActive = (user) => {
  if (!user?.profile?.last_seen) return false
  const lastSeen = new Date(user.profile.last_seen)
  const now = new Date()
  const diffMinutes = (now - lastSeen) / (1000 * 60)
  const isRecent = diffMinutes <= 2
  const isOnlineStatus = user.profile.status === 'online'
  return isRecent && isOnlineStatus
}

const formatDate = (timestamp) => {
  return new Date(timestamp).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// API functions
const fetchChatInfo = async () => {
  try {
    // Check if user is blocked (only for private chats)
    if (props.conversation.type === 'private') {
      isBlocked.value = await messagingService.isUserBlocked(props.conversation.mate.id)
    }

    // Fetch pinned messages
    await fetchPinnedMessages()

    // Process shared content from messages
    processSharedContent()
  } catch (error) {
    console.error('Error fetching chat info:', error)
  }
}

const fetchPinnedMessages = async () => {
  try {
    // Filter pinned messages from current conversation and sort by newest first
    pinnedMessages.value = props.messages
      .filter(message => message.is_pinned)
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    console.log('ChatInfoPanel: Found pinned messages:', pinnedMessages.value.length)
  } catch (error) {
    console.error('Error fetching pinned messages:', error)
  }
}

const processSharedContent = () => {
  const images = []
  const links = []
  const files = []

  console.log('ChatInfoPanel: Processing shared content from messages:', props.messages.length)

  props.messages.forEach(message => {
    // Process attachments
    if (message.attachments && message.attachments.length > 0) {
      console.log('ChatInfoPanel: Processing attachments for message:', message.id, message.attachments)
      
      message.attachments.forEach(attachment => {
        console.log('ChatInfoPanel: Processing attachment:', attachment)
        
        // Build the attachment data
        const attachmentData = {
          id: attachment.id,
          url: attachment.file, // This comes from the serializer
          name: attachment.file_name || 'Unnamed file',
          type: attachment.file_type || 'application/octet-stream',
          size: attachment.file_size || 0,
          timestamp: message.timestamp,
          messageId: message.id
        }
        
        console.log('ChatInfoPanel: Built attachment data:', attachmentData)
        
        // Only images go to shared images
        if (attachment.file_type?.startsWith('image/')) {
          images.push(attachmentData)
          console.log('ChatInfoPanel: Added to images')
        } else {
          // All non-image files (PDFs, Word docs, videos, etc.) go to shared files
          files.push(attachmentData)
          console.log('ChatInfoPanel: Added to files')
        }
      })
    }

    // Extract links from message content and link previews
    const urlRegex = /(https?:\/\/[^\s]+)/g
    const matches = message.content.match(urlRegex)
    if (matches) {
      matches.forEach(url => {
        try {
          const urlObj = new URL(url)
          links.push({
            id: `${message.id}-${url}`,
            url: url,
            title: url,
            domain: urlObj.hostname,
            timestamp: message.timestamp,
            messageId: message.id
          })
        } catch (e) {
          // Invalid URL, ignore
        }
      })
    }

    // Also extract from link previews if available
    if (message.link_previews && message.link_previews.length > 0) {
      message.link_previews.forEach(preview => {
        // Check if we already added this URL from regex extraction
        const existingLink = links.find(link => link.url === preview.url)
        if (existingLink) {
          // Update existing link with richer data from preview
          existingLink.title = preview.title || preview.url
          existingLink.description = preview.description
          existingLink.image_url = preview.image_url
          existingLink.domain = preview.domain
        } else {
          // Add new link from preview
          links.push({
            id: preview.id,
            url: preview.url,
            title: preview.title || preview.url,
            description: preview.description,
            image_url: preview.image_url,
            domain: preview.domain,
            timestamp: message.timestamp,
            messageId: message.id
          })
        }
      })
    }
  })

  console.log('ChatInfoPanel: Final results - Images:', images.length, 'Files:', files.length, 'Links:', links.length)

  sharedImages.value = images.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
  sharedLinks.value = links.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
  sharedFiles.value = files.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
  
  console.log('ChatInfoPanel: sharedImages:', sharedImages.value)
  console.log('ChatInfoPanel: sharedFiles:', sharedFiles.value)
}

// Actions
const toggleBlock = async () => {
  if (props.conversation.type !== 'private') return

  try {
    if (isBlocked.value) {
      // Unblock
      await messagingService.unblockUser(props.conversation.mate.id)
      isBlocked.value = false
      emit('unblock')
      console.log('User unblocked successfully')
    } else {
      // Block
      await messagingService.blockUser(props.conversation.mate.id)
      isBlocked.value = true
      emit('block')
      console.log('User blocked successfully')
    }
  } catch (error) {
    console.error('Error toggling block:', error)
    // Show user-friendly error message
    const message = error.response?.data?.error || 'Failed to update block status'
    alert(message) // You can replace this with a toast notification
  }
}

const scrollToMessage = (messageId) => {
  // Emit event to parent to scroll to message
  console.log('ChatInfoPanel: Emitting scroll-to-message for:', messageId)
  emit('scroll-to-message', messageId)
}

const openMedia = (media) => {
  // Open media in full screen or new tab
  window.open(media.url, '_blank')
}

const downloadFile = (file) => {
  // Download file
  const link = document.createElement('a')
  link.href = file.url
  link.download = file.name
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Watchers
watch(() => props.conversation, (newConversation) => {
  if (newConversation) {
    fetchChatInfo()
  }
}, { immediate: true })

watch(() => props.messages, () => {
  processSharedContent()
  fetchPinnedMessages()
}, { deep: true })

// Handle image loading errors for link previews
const handleImageError = (event) => {
  event.target.style.display = 'none'
}

// Lifecycle
onMounted(() => {
  fetchChatInfo()
})
</script>

<style scoped>
.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
}
</style>