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
          <!-- Mute/Unmute -->
          <button 
            @click="toggleMute"
            :class="[
              'flex flex-col items-center p-3 rounded-lg transition-all duration-200',
              isMuted 
                ? 'bg-orange-50 text-orange-600 hover:bg-orange-100' 
                : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
            ]"
          >
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="!isMuted" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M6 10H4a2 2 0 00-2 2v0a2 2 0 002 2h2l6 6V4l-6 6z" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
            </svg>
            <span class="text-xs font-medium">{{ isMuted ? 'Unmute' : 'Mute' }}</span>
          </button>

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
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636" />
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

      <!-- Shared Media -->
      <div class="border-b border-gray-200">
        <button 
          @click="showSharedMedia = !showSharedMedia"
          class="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span class="font-medium text-gray-900">Shared Media</span>
            <span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
              {{ sharedMedia.length }}
            </span>
          </div>
          <svg 
            :class="['w-4 h-4 text-gray-400 transition-transform', showSharedMedia ? 'rotate-180' : '']" 
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <!-- Shared Media Grid -->
        <div v-if="showSharedMedia" class="p-3">
          <div v-if="sharedMedia.length === 0" class="text-center text-gray-500 text-sm py-4">
            No shared media
          </div>
          <div class="grid grid-cols-3 gap-2">
            <div 
              v-for="media in sharedMedia.slice(0, 9)" 
              :key="media.id"
              class="aspect-square bg-gray-100 rounded-lg overflow-hidden cursor-pointer hover:opacity-80 transition-opacity"
              @click="openMedia(media)"
            >
              <img 
                v-if="media.type?.startsWith('image')"
                :src="media.url" 
                :alt="media.name"
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full flex items-center justify-center">
                <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
          </div>
          <button 
            v-if="sharedMedia.length > 9" 
            class="w-full mt-3 p-2 text-sm text-blue-600 hover:text-blue-700 transition-colors"
            @click="showAllMedia = true"
          >
            View All ({{ sharedMedia.length }})
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
            <div class="flex items-start gap-2">
              <svg class="w-4 h-4 text-purple-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              <div class="flex-1 min-w-0">
                <p class="text-sm text-gray-800 truncate">{{ link.title || link.url }}</p>
                <p class="text-xs text-gray-500">{{ link.domain }}</p>
                <p class="text-xs text-gray-400">{{ formatDate(link.timestamp) }}</p>
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
const emit = defineEmits(['close', 'mute', 'unmute', 'block', 'unblock', 'scroll-to-message'])

// State
const isMuted = ref(false)
const isBlocked = ref(false)
const pinnedMessages = ref([])
const sharedMedia = ref([])
const sharedLinks = ref([])
const sharedFiles = ref([])

// UI State
const showPinnedMessages = ref(true) // Start expanded for better UX
const showSharedMedia = ref(false)
const showSharedLinks = ref(false)
const showSharedFiles = ref(false)
const showSearchMessages = ref(false)
const showGroupInfo = ref(false)
const showAllMedia = ref(false)

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
    // Check if conversation is muted
    const muteResponse = await api.get('/message/mute/')
    isMuted.value = muteResponse.data.some(mute => 
      (props.conversation.type === 'private' && mute.receiver?.id === props.conversation.mate.id) ||
      (props.conversation.type === 'group' && mute.group?.id === props.conversation.group.id)
    )

    // Check if user is blocked (only for private chats)
    if (props.conversation.type === 'private') {
      const blockResponse = await api.get('/message/block/')
      isBlocked.value = blockResponse.data.some(block => 
        block.blocked_user.id === props.conversation.mate.id
      )
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
  const media = []
  const links = []
  const files = []

  props.messages.forEach(message => {
    // Process attachments
    if (message.attachments && message.attachments.length > 0) {
      message.attachments.forEach(attachment => {
        if (attachment.type?.startsWith('image/') || attachment.type?.startsWith('video/')) {
          media.push({
            id: attachment.id,
            url: attachment.url,
            name: attachment.name,
            type: attachment.type,
            timestamp: message.timestamp,
            messageId: message.id
          })
        } else {
          files.push({
            id: attachment.id,
            url: attachment.url,
            name: attachment.name,
            size: attachment.size || 0,
            type: attachment.type,
            timestamp: message.timestamp,
            messageId: message.id
          })
        }
      })
    }

    // Extract links from message content
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
  })

  sharedMedia.value = media.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
  sharedLinks.value = links.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
  sharedFiles.value = files.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
}

// Actions
const toggleMute = async () => {
  try {
    if (isMuted.value) {
      // Unmute
      await api.delete('/message/mute/', {
        data: {
          receiver_id: props.conversation.type === 'private' ? props.conversation.mate.id : null,
          group_id: props.conversation.type === 'group' ? props.conversation.group.id : null
        }
      })
      isMuted.value = false
      emit('unmute')
    } else {
      // Mute
      await api.post('/message/mute/', {
        receiver_id: props.conversation.type === 'private' ? props.conversation.mate.id : null,
        group_id: props.conversation.type === 'group' ? props.conversation.group.id : null
      })
      isMuted.value = true
      emit('mute')
    }
  } catch (error) {
    console.error('Error toggling mute:', error)
  }
}

const toggleBlock = async () => {
  if (props.conversation.type !== 'private') return

  try {
    if (isBlocked.value) {
      // Unblock
      await api.delete(`/message/block/${props.conversation.mate.id}/`)
      isBlocked.value = false
      emit('unblock')
    } else {
      // Block
      await api.post('/message/block/', {
        user_id: props.conversation.mate.id
      })
      isBlocked.value = true
      emit('block')
    }
  } catch (error) {
    console.error('Error toggling block:', error)
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