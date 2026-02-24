<template>
 <div :class="[
   'h-full flex rounded-xl shadow-lg overflow-hidden border',
   themeStore.isDarkMode
     ? 'bg-gradient-to-br from-gray-800 to-gray-900 border-gray-700'
     : 'bg-gradient-to-br from-slate-50 to-slate-100 border-slate-200/60'
 ]">

   <!-- Conversations Panel -->
 <div :class="[
 'border-r flex flex-col backdrop-blur-sm',
 'w-full md:w-80 lg:w-96',
 themeStore.isDarkMode
   ? 'border-gray-700 bg-gray-800/90'
   : 'border-slate-300/60 bg-white/80',
 {
 'block': !isMobile || currentMobileView === 'list',
 'hidden': isMobile && currentMobileView !== 'list'
 }
 ]">

 <!-- Conversations Header  -->
 <div :class="[
   'p-4 md:p-6 backdrop-blur-sm border-b shadow-sm',
   themeStore.isDarkMode
     ? 'bg-gray-800/95 border-gray-700'
     : 'bg-white/90 border-slate-200/60'
 ]">
 <div class="flex items-center justify-between mb-4">
 <h2 :class="[
   'text-xl md:text-2xl font-bold',
   themeStore.isDarkMode ? 'text-gray-100' : 'text-slate-800'
 ]">Messages</h2>
 <div class="flex gap-2">
 <button @click="showPendingMessages = true"
 :class="[
 'relative p-2.5 md:p-3 rounded-xl transition-all duration-200 hover:scale-105',
 pendingMessages.length > 0
 ? 'text-amber-600 bg-amber-50 hover:text-amber-700 hover:bg-amber-100 shadow-sm'
 : 'text-slate-500 hover:text-amber-600 hover:bg-amber-50'
 ]"
 title="Pending Message Requests">
 <svg class="w-4 h-4 md:w-5 md:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" :class="pendingMessages.length > 0 ? 'animate-pulse' : ''">
 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
 d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
 </svg>
 <span v-if="pendingMessages.length > 0"
 class="absolute -top-1 -right-1 bg-gradient-to-r from-amber-500 to-orange-500 text-white text-xs rounded-full min-w-[20px] h-5 flex items-center justify-center font-semibold shadow-lg">
 {{ pendingMessages.length > 99 ? '99+' : pendingMessages.length }}
 </span>
 </button>
 <button @click="showBlockedUsers = true"
 class="p-2.5 md:p-3 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all duration-200 hover:scale-105"
 title="Blocked Users">
 <svg class="w-4 h-4 md:w-5 md:h-5" fill="none" stroke="currentColor

" viewBox="0 0 24 24">
 <circle cx="12" cy="12" r="9" stroke-width="2"></circle>
 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6"></path>
 </svg>
 </button>
 <button @click="showCreateGroup = true"
 class="p-2.5 md:p-3 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-xl transition-all duration-200 hover:scale-105"
 title="Create Group">
 <svg class="w-4 h-4 md:w-5 md:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
 d="M17 20h5v-2a3 3 0 00-5.196-2.121M17 20H7m10 0v-2c0-5.523-3.582-10-8-10s-8 4.477-8 10v2m8-10a3 3 0 110-6 3 3 0 010 6zm0 10a3 3 0 110-6 3 3 0 010 6z" />
 </svg>
 </button>
 </div>
 </div>

 <!-- Search Input -->
 <div class="relative">
 <svg @click="focusSearch"
 class="absolute w-4 h-4 transition-colors transform -translate-y-1/2 cursor-pointer left-4 top-1/2 md:w-5 md:h-5 text-slate-400 hover:text-slate-600" fill="none"
 stroke="currentColor" viewBox="0 0 24 24">
 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
 d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
 </svg>
 <input ref="searchInput" v-model="searchQuery" @input="debouncedSearch" type="text"
 placeholder="Search conversations..."
 :class="[
   'w-full pl-10 md:pl-12 pr-4 py-3 md:py-4 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/60 transition-all duration-200 text-sm md:text-base backdrop-blur-sm',
   themeStore.isDarkMode
     ? 'bg-gray-700/80 border-gray-600 text-gray-100 placeholder-gray-400 focus:bg-gray-700'
     : 'bg-slate-50/80 border-slate-200/60 text-gray-900 placeholder-gray-500 focus:bg-white'
 ]" />

 <!-- Search Results Dropdown -->
 <div v-if="searchQuery && searchResults.length"
 :class="[
   'absolute top-full left-0 right-0 mt-2 backdrop-blur-sm border rounded-xl shadow-xl z-10 max-h-80 md:max-h-96 overflow-y-auto',
   themeStore.isDarkMode
     ? 'bg-gray-800/95 border-gray-600'
     : 'bg-white/95 border-slate-200/60'
 ]">
 <div v-for="result in searchResults" :key="result.id" @click="handleSelectSearchResult(result)"
 :class="[
   'flex items-center p-3 md:p-4 cursor-pointer transition-all duration-200',
   themeStore.isDarkMode
     ? 'hover:bg-gray-700'
     : 'hover:bg-slate-50'
 ]">
 <img :src="getEntityAvatarUrl(result)" alt="" class="w-10 h-10 rounded-full mr-3">
 <div>
 <p :class="['font-semibold', themeStore.isDarkMode ? 'text-gray-100' : 'text-slate-800']">
 {{ result.type === 'user' ? `${result.first_name} ${result.last_name}` : result.name }}
 </p>
 <p :class="['text-xs', themeStore.isDarkMode ? 'text-gray-400' : 'text-slate-500']">
 {{ result.type === 'user' ? '@' + result.username : 'Group' }}
 </p>
 </div>
 </div>
 </div>
 </div>
 </div>

 <!-- Conversations List -->
 <ConversationsList
 :conversations="filteredConversations"
 :selected-conversation="selectedConversation"
 :is-mobile="isMobile"
 @select="handleSelectConversation"
 @prefetch="prefetchMessages"
 />
 </div>

 <!-- Chat Area -->
 <div :class="[
 'flex-1 flex flex-col',
 {
 'block': !isMobile || currentMobileView === 'chat',
 'hidden': isMobile && currentMobileView !== 'chat'
 }
 ]">
 <ChatArea
 v-if="selectedConversation"
 :conversation="selectedConversation"
 :messages="messages"
 :current-user="currentUser"
 :private-ws="privateWs"
 :group-ws="groupWs"
 @send-message="handleSendMessage"
 @message-action="handleMessageAction"
 @message-read="handleMessageRead"
 @toggle-chat-info="toggleChatInfo"
 @back-to-conversations="handleBackToConversations"
 />
 <EmptyState v-else />
 </div>

 <!-- Chat Info Panel -->
 <div v-if="showChatInfo && selectedConversation"
 :class="[
 'w-80 border-l',
 themeStore.isDarkMode
   ? 'bg-gray-800 border-gray-700'
   : 'bg-white border-gray-200',
 {
 'block': !isMobile || currentMobileView === 'chat-info',
 'hidden': isMobile && currentMobileView !== 'chat-info'
 }
 ]">
 <ChatInfoPanel
 :conversation="selectedConversation"
 :messages="messages"
 :current-user="currentUser"
 :member-request-notification-trigger="memberRequestNotificationTrigger"
 :group-member-update-trigger="groupMemberUpdateTrigger"
 @close="closeChatInfo"
 @mute="handleMute"
 @unmute="handleUnmute"
 @block="handleBlock"
 @unblock="handleUnblock"
 @scroll-to-message="scrollToMessage"
 @group-photo-updated="handleGroupPhotoUpdated"
 @leave-group="handleLeaveGroup"
 />
 </div>
   <!-- Modals -->
   <PendingMessagesModal
   v-if="showPendingMessages"
   :pending-messages="pendingMessages"
   @close="showPendingMessages = false"
   @accept="acceptPendingMessage"
   @reject="rejectPendingMessage"
   />

   <CreateGroupModal
   v-if="showCreateGroup"
   :available-mates="availableMates"
   @close="showCreateGroup = false"
   @create-group="createGroup"
   />

   <BlockedUsersModal
   v-if="showBlockedUsers"
   :show="showBlockedUsers"
   @close="showBlockedUsers = false"
   @user-unblocked="handleUserUnblocked"
   />

   <ForwardModal
   v-if="showForwardModal"
   :message="messageToForward"
   @close="showForwardModal = false"
   @forward="handleForwardComplete"
   />
 </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import debounce from 'lodash/debounce'
import { useAuthStore } from '@/stores/auth'
import { useMessagingNotificationStore } from '@/stores/messagingNotifications'
import { useThemeStore } from '@/stores/theme'
import { getProfilePictureUrl, getWebSocketBaseURL } from '@/utils/imageUrl'
import api from '@/services/api'

// Composables
import { useMessagingSockets } from '@/composables/useMessagingSockets'
import { useMessages } from '@/composables/useMessages'
import { useMessageActions } from '@/composables/useMessageActions'
import { useConversations } from '@/composables/useConversations'
import { useMessagingUI } from '@/composables/useMessagingUI'

// Components
import ChatArea from '@/components/alumni/messaging/ChatArea.vue'
import EmptyState from '@/components/alumni/messaging/EmptyState.vue'
import PendingMessagesModal from '@/components/alumni/messaging/PendingMessagesModal.vue'
import CreateGroupModal from '@/components/alumni/messaging/CreateGroupModal.vue'
import ChatInfoPanel from '@/components/alumni/messaging/ChatInfoPanel.vue'
import BlockedUsersModal from '@/components/alumni/messaging/BlockedUsersModal.vue'
import ForwardModal from '@/components/alumni/messaging/ForwardModal.vue'
import ConversationsList from '@/components/alumni/messaging/ConversationsList.vue'

// Stores
const authStore = useAuthStore()
const messagingNotificationStore = useMessagingNotificationStore()
const themeStore = useThemeStore()
const route = useRoute()
const router = useRouter()

// State
const isAuthenticated = ref(false)
const currentUser = ref(null)
const userId = computed(() => currentUser.value?.id)

// Initialize composables
const {
  privateWs,
  groupWs,
  notificationWs,
  setupPrivateWebSocket,
  setupGroupWebSocket,
  setupNotificationWebSocket,
  closeAllConnections
} = useMessagingSockets()

const {
  messages,
  messageCache,
  prefetchedConversations,
  fetchMessages,
  prefetchMessages,
  addMessage,
  updateMessage,
  deleteMessage,
  clearCache
} = useMessages()


const {
  conversations,
  pendingMessages,
  availableMates,
  searchQuery,
  searchResults,
  searchInput,
  selectedConversation,
  fetchConversations,
  fetchPendingMessages,
  fetchAvailableMates,
  search,
  selectConversation,
  selectSearchResult,
  selectLastConversation,
  handleUserFromQuery,
  acceptPendingMessage,
  rejectPendingMessage,
  focusSearch
} = useConversations(currentUser, route)

// Initialize message actions AFTER we have the real selectedConversation ref
const {
  sendMessage,
  editMessage,
  deleteMessage: deleteMessageAction,
  sendReaction,
  handleMessageAction,
  handleMessageRead
} = useMessageActions(
  selectedConversation,
  currentUser,
  messages,
  privateWs,
  groupWs,
  messageCache,
  prefetchedConversations
)

const {
  showPendingMessages,
  showCreateGroup,
  showChatInfo,
  showBlockedUsers,
  showForwardModal,
  messageToForward,
  isMobile,
  currentMobileView,
  memberRequestNotificationTrigger,
  groupMemberUpdateTrigger,
  toggleChatInfo,
  closeChatInfo,
  handleBackToConversations: handleBackToConversationsUI,
  scrollToMessage,
  showForward,
  handleForwardComplete,
  triggerMemberRequestNotification,
  triggerGroupMemberUpdate,
  setupResizeListener,
  cleanupResizeListener
} = useMessagingUI()

// Computed
const filteredConversations = computed(() => {
  if (!searchQuery.value) return conversations.value
  return conversations.value.filter(conv => {
    const name = conv.type === 'private'
      ? `${conv.mate.first_name} ${conv.mate.last_name}`
      : conv.group.name
    return name.toLowerCase().includes(searchQuery.value.toLowerCase())
  })
})

// Debounced search
const debouncedSearch = debounce(search, 300)

// Helper to get entity avatar
const getEntityAvatarUrl = (entity) => {
  const pic = entity?.profile_picture || entity?.group_picture || null
  return getProfilePictureUrl(pic)
}

// Auth functions
async function validateToken() {
  if (!authStore.token) {
    isAuthenticated.value = false
    return false
  }
  
  try {
    await api.get('/auth/user/')
    isAuthenticated.value = true
    return true
  } catch (error) {
    if (error.response?.status === 401 && await authStore.tryRefreshToken()) {
      isAuthenticated.value = true
      return true
    }
    isAuthenticated.value = false
    return false
  }
}

async function fetchCurrentUser() {
  try {
    const { data } = await api.get('/auth/user/')
    currentUser.value = data
  } catch (e) {
    console.error('User fetch error', e)
  }
}

// Conversation handlers
async function handleSelectConversation(conv) {
  console.log('Selecting conversation:', conv.id)
  
  selectedConversation.value = conv
  
  if (isMobile.value) {
    currentMobileView.value = 'chat'
  }
  
  messages.value = []
  
  try {
    await fetchMessages(conv)
    
    if (conv.type === 'group') {
      await setupGroupWebSocket(conv.group.id)
    } else {
      if (groupWs.value) {
        groupWs.value.close()
        groupWs.value = null
      }
      
      if (privateWs.value?.readyState === WebSocket.OPEN) {
        privateWs.value.send(JSON.stringify({ 
          action: 'mark_as_read', 
          receiver_id: conv.mate.id 
        }))
      }
    }
    
    if (typeof conv.unreadCount === 'number' && conv.unreadCount > 0) {
      conv.unreadCount = 0
      conversations.value = [...conversations.value]
    }
    
    setTimeout(async () => {
      try {
        await messagingNotificationStore.forceRefresh()
      } catch (error) {
        console.error('Failed to refresh notification counts:', error)
      }
    }, 1)
  } catch (error) {
    console.error('Error selecting conversation:', error)
  }
}

async function handleSelectSearchResult(result) {
  await selectSearchResult(result, {
    onSelect: handleSelectConversation,
    onGroupJoinNeeded: async (group) => {
      // Handle group join logic
      console.log('Need to join group:', group.id)
    }
  })
}

async function handleSendMessage(data) {
  await sendMessage({
    ...data,
    onConversationCreated: async () => {
      await new Promise(resolve => setTimeout(resolve, 500))
      await fetchConversations()
      
      const updatedConv = conversations.value.find(c =>
        c.type === 'private' && c.mate.id === selectedConversation.value.mate.id
      )
      
      if (updatedConv) {
        await handleSelectConversation(updatedConv)
      }
    }
  })
}

function handleBackToConversations() {
  handleBackToConversationsUI(selectedConversation, privateWs, groupWs, messages)
}

async function createGroup(groupData) {
  try {
    let requestData
    let config = {}
    
    if (groupData instanceof FormData) {
      requestData = groupData
      config.headers = {}
    } else {
      requestData = { name: groupData.name, members: groupData.members }
      config.headers = { 'Content-Type': 'application/json' }
    }
    
    const { data } = await api.post('/message/group/create/', requestData, config)
    
    const groupConversation = {
      id: data.id,
      type: 'group',
      group: data,
      lastMessage: '',
      timestamp: data.created_at || new Date().toISOString(),
      unreadCount: 0
    }
    
    conversations.value.unshift(groupConversation)
    showCreateGroup.value = false
    await handleSelectConversation(groupConversation)
  } catch (e) {
    console.error('Group create error', e)
    if (e.response?.data?.error) {
      alert(e.response.data.error)
    } else {
      alert('Failed to create group. Please try again.')
    }
  }
}

function handleUserUnblocked(user) {
  console.log('User unblocked:', user)
  
  if (selectedConversation.value && 
      selectedConversation.value.type === 'private' && 
      selectedConversation.value.mate.id === user.id) {
    selectedConversation.value.isBlockedByMe = false
    selectedConversation.value.canSendMessage = true
  }
  
  fetchConversations()
}

function handleMute() {
  console.log('Mute conversation')
}

function handleUnmute() {
  console.log('Unmute conversation')
}

function handleBlock() {
  console.log('Block user')
}

function handleUnblock() {
  console.log('Unblock user')
}

function handleGroupPhotoUpdated(photoUrl) {
  console.log('Group photo updated:', photoUrl)
  if (selectedConversation.value && selectedConversation.value.type === 'group') {
    selectedConversation.value.group.group_picture = photoUrl
  }
}

async function handleLeaveGroup() {
  console.log('Leave group')
  selectedConversation.value = null
  messages.value = []
  await fetchConversations()
}

// Lifecycle
onMounted(async () => {
  console.log('Messaging.vue: Component mounted')
  
  if (!await validateToken()) {
    router.push('/login')
    return
  }
  
  await fetchCurrentUser()
  
  if (!currentUser.value) {
    console.error('Failed to fetch current user')
    router.push('/login')
    return
  }
  
  await fetchConversations()
  await fetchPendingMessages()
  await fetchAvailableMates()
  
  await setupPrivateWebSocket()
  await setupNotificationWebSocket()
  
  if (route.query.userId || route.query.user) {
    await handleUserFromQuery({ onSelect: handleSelectConversation })
  } else {
    selectLastConversation({ onSelect: handleSelectConversation })
  }
  
  setupResizeListener()
})

onUnmounted(() => {
  console.log('Messaging.vue: Component unmounted')
  closeAllConnections()
  cleanupResizeListener()
})

// Watch for route changes
watch(() => route.query, async (newQuery) => {
  if (newQuery.userId || newQuery.user) {
    await handleUserFromQuery({ onSelect: handleSelectConversation })
  }
})
</script>
