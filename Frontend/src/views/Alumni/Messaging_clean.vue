<template>
  <div class="h-[calc(100vh-120px)] flex bg-white rounded-lg shadow-sm overflow-hidden">
    <!-- Conversations Sidebar -->
    <ConversationsSidebar 
      :conversations="conversations"
      :selectedConversation="selectedConversation"
      :pendingMessages="pendingMessages"
      :searchResults="searchResults"
      :searchQuery="searchQuery"
      @select-conversation="selectConversation"
      @search="handleSearch"
      @show-pending="showPendingMessages = true"
      @show-create-group="showCreateGroup = true"
      @select-search-result="selectSearchResult"
    />

    <!-- Main Chat Area -->
    <div class="flex-1 flex flex-col">
      <ChatArea 
        v-if="selectedConversation" 
        :conversation="selectedConversation" 
        :messages="messages"
        :current-user="currentUser" 
        @send-message="sendMessage" 
        @message-action="handleMessageAction" 
      />
      <EmptyState v-else />
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
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import debounce from 'lodash/debounce'
import { useAuthStore } from '@/stores/auth'
import api from '../../services/api'

// Components
import ChatArea from '../../components/messaging/ChatArea.vue'
import EmptyState from '../../components/messaging/EmptyState.vue'
import PendingMessagesModal from '../../components/messaging/PendingMessagesModal.vue'
import CreateGroupModal from '../../components/messaging/CreateGroupModal.vue'
import ConversationsSidebar from '../../components/messaging/ConversationsSidebar.vue'

// ===== AUTHENTICATION & STATE =====
const authStore = useAuthStore()
const currentUser = ref(null)
const isAuthenticated = ref(false)

// ===== MESSAGING STATE =====
const conversations = ref([])
const selectedConversation = ref(null)
const messages = ref([])
const pendingMessages = ref([])
const availableMates = ref([])

// ===== UI STATE =====
const showPendingMessages = ref(false)
const showCreateGroup = ref(false)
const searchQuery = ref('')
const searchResults = ref([])

// ===== WEBSOCKETS =====
const privateWs = ref(null)
const groupWs = ref(null)

// ===== AUTHENTICATION =====

/**
 * Validate JWT token and authenticate user
 */
async function validateToken() {
  if (!authStore.token) {
    isAuthenticated.value = false
    return false
  }

  try {
    await api.get('/user/')
    isAuthenticated.value = true
    return true
  } catch (error) {
    if ([401, 403].includes(error.response?.status)) {
      const refreshed = await authStore.tryRefreshToken()
      isAuthenticated.value = refreshed
      return refreshed
    }
    isAuthenticated.value = false
    return false
  }
}

/**
 * Get valid authentication token
 */
async function getValidToken() {
  if (authStore.token) return authStore.token
  
  try {
    const refreshed = await authStore.tryRefreshToken()
    return refreshed ? authStore.token : null
  } catch {
    authStore.logout()
    return null
  }
}

// ===== DATA FETCHING =====

/**
 * Fetch current user data
 */
async function fetchCurrentUser() {
  try {
    const { data } = await api.get('/user/')
    currentUser.value = data
  } catch (error) {
    console.error('Failed to fetch user:', error)
  }
}

/**
 * Fetch conversations with proper sorting
 */
async function fetchConversations() {
  try {
    const { data } = await api.get('/message/conversations/')
    
    conversations.value = (Array.isArray(data) ? data : [])
      .map(conv => ({
        ...conv,
        id: conv.id || (conv.type === 'private' ? conv.mate.id : conv.group.id),
        timestamp: conv.timestamp || conv.lastMessageTime || new Date().toISOString()
      }))
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      
  } catch (error) {
    console.error('Failed to fetch conversations:', error)
  }
}

/**
 * Fetch messages for selected conversation
 */
async function fetchMessages(conversation) {
  try {
    const url = conversation.type === 'private'
      ? `/message/private/${conversation.mate.id}/`
      : `/message/group/${conversation.group.id}/`
      
    const { data } = await api.get(url)
    messages.value = data || []
  } catch (error) {
    console.error('Failed to fetch messages:', error)
  }
}

/**
 * Fetch pending message requests
 */
async function fetchPendingMessages() {
  try {
    const { data } = await api.get('/message/requests/')
    pendingMessages.value = (data || []).map(req => ({
      id: req.id,
      name: `${req.sender.first_name} ${req.sender.last_name}`,
      avatar: getProfilePictureUrl(req.sender),
      message: 'Message request',
      timestamp: req.timestamp
    }))
  } catch (error) {
    console.error('Failed to fetch pending messages:', error)
  }
}

/**
 * Fetch available users for messaging
 */
async function fetchAvailableMates() {
  try {
    const { data } = await api.get('/message/search/')
    availableMates.value = (Array.isArray(data.users) ? data.users : [])
      .map(user => ({
        ...user,
        profile_picture: getProfilePictureUrl(user)
      }))
  } catch (error) {
    console.error('Failed to fetch available mates:', error)
  }
}

// ===== SEARCH FUNCTIONALITY =====

/**
 * Search for users and groups
 */
async function search() {
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    return
  }

  try {
    const { data } = await api.get(`/message/search/?q=${encodeURIComponent(searchQuery.value)}`)
    
    const users = (data.users || []).map(u => ({
      type: 'user',
      ...u,
      profile_picture: getProfilePictureUrl(u)
    }))
    
    const groups = (data.groups || []).map(g => ({ 
      type: 'group', 
      ...g 
    }))
    
    searchResults.value = [...users, ...groups]
  } catch (error) {
    console.error('Search failed:', error)
    searchResults.value = []
  }
}

const debouncedSearch = debounce(search, 300)

function handleSearch(query) {
  searchQuery.value = query
  debouncedSearch()
}

// ===== CONVERSATION MANAGEMENT =====

/**
 * Select and load a conversation
 */
async function selectConversation(conversation) {
  selectedConversation.value = conversation
  
  // Load messages
  await fetchMessages(conversation)
  
  // Setup WebSocket for group chats
  if (conversation.type === 'group') {
    setupGroupWebSocket(conversation)
  } else {
    groupWs.value?.close()
  }
  
  // Mark messages as read for private chats
  if (conversation.type === 'private' && privateWs.value?.readyState === WebSocket.OPEN) {
    privateWs.value.send(JSON.stringify({ 
      action: 'mark_as_read', 
      receiver_id: conversation.mate.id 
    }))
  }
  
  // Reset unread count
  conversation.unreadCount = 0
}

/**
 * Auto-select most recent conversation on load
 */
function selectLastConversation() {
  if (conversations.value.length > 0) {
    const sortedConversations = [...conversations.value]
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    
    if (sortedConversations[0]) {
      selectConversation(sortedConversations[0])
    }
  }
}

/**
 * Handle search result selection
 */
async function selectSearchResult(result) {
  if (result.type === 'user') {
    // Find or create private conversation
    let conversation = conversations.value.find(c => 
      c.type === 'private' && c.mate.id === result.id
    )
    
    if (!conversation) {
      conversation = {
        type: 'private',
        id: result.id,
        mate: result,
        lastMessage: '',
        timestamp: null,
        unreadCount: 0
      }
      conversations.value.unshift(conversation)
    }
    
    selectConversation(conversation)
  } 
  else if (result.type === 'group') {
    // Join group if not already a member
    let groupConv = conversations.value.find(c => 
      c.type === 'group' && c.group.id === result.id
    )
    
    if (!groupConv) {
      try {
        await api.post(`/message/group/${result.id}/manage/`, { 
          action: 'add_member', 
          user_id: currentUser.value.id 
        })
        await fetchConversations()
        groupConv = conversations.value.find(c => 
          c.type === 'group' && c.group.id === result.id
        )
      } catch (error) {
        console.error('Failed to join group:', error)
        return
      }
    }
    
    if (groupConv) {
      selectConversation(groupConv)
    }
  }
  
  // Clear search
  searchQuery.value = ''
  searchResults.value = []
}

// ===== MESSAGE HANDLING =====

/**
 * Send a message via WebSocket
 */
async function sendMessage(data) {
  if (!currentUser.value || !selectedConversation.value) {
    console.error('Missing user or conversation for sending message')
    return
  }

  try {
    // Upload attachments if any
    const attachmentIds = await uploadAttachments(data.attachments || [])
    
    // Create optimistic UI message
    const tempMessage = {
      id: `temp-${Date.now()}`,
      sender: currentUser.value,
      content: data.content,
      attachments: data.attachments?.map(file => ({
        url: URL.createObjectURL(file),
        name: file.name,
        type: file.type
      })) || [],
      timestamp: new Date().toISOString(),
      is_read: false,
      reply_to: data.reply_to_id ? messages.value.find(m => m.id === data.reply_to_id) : null,
      reply_to_id: data.reply_to_id || null
    }
    
    messages.value.push(tempMessage)
    
    // Prepare WebSocket payload
    const payload = {
      action: 'send_message',
      content: data.content,
      attachment_ids: attachmentIds,
      reply_to_id: data.reply_to_id
    }
    
    // Send via appropriate WebSocket
    if (selectedConversation.value.type === 'private') {
      payload.receiver_id = selectedConversation.value.mate.id
      
      if (privateWs.value?.readyState === WebSocket.OPEN) {
        privateWs.value.send(JSON.stringify(payload))
      } else {
        console.error('Private WebSocket not connected')
        messages.value.pop() // Remove optimistic message
      }
    } 
    else if (selectedConversation.value.type === 'group') {
      if (groupWs.value?.readyState === WebSocket.OPEN) {
        groupWs.value.send(JSON.stringify(payload))
      } else {
        console.error('Group WebSocket not connected')
        messages.value.pop() // Remove optimistic message
      }
    }
    
  } catch (error) {
    console.error('Failed to send message:', error)
    messages.value.pop() // Remove optimistic message on error
  }
}

/**
 * Upload message attachments
 */
async function uploadAttachments(attachments) {
  const ids = []
  
  for (const attachment of attachments) {
    const formData = new FormData()
    formData.append('file', attachment)
    
    try {
      const response = await api.post('/message/upload/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      ids.push(response.data.id)
    } catch (error) {
      console.error('Upload failed for:', attachment.name, error)
      throw error
    }
  }
  
  return ids
}

/**
 * Handle message actions (reply, edit, delete, etc.)
 */
async function handleMessageAction(actionData) {
  const { action, message, newContent } = actionData
  
  try {
    switch (action) {
      case 'reply':
        // Reply is handled in ChatArea component
        break
        
      case 'pin':
        await api.post(`/message/${message.id}/pin/`)
        updateMessageInList(message.id, { is_pinned: true })
        break
        
      case 'unpin':
        await api.delete(`/message/${message.id}/pin/`)
        updateMessageInList(message.id, { is_pinned: false })
        break
        
      case 'edit':
        await api.patch(`/message/${message.id}/`, { content: newContent })
        updateMessageInList(message.id, { content: newContent, is_edited: true })
        break
        
      case 'delete':
        await api.delete(`/message/${message.id}/`)
        messages.value = messages.value.filter(m => m.id !== message.id)
        break
        
      case 'bump':
        await api.post(`/message/${message.id}/bump/`)
        break
        
      default:
        console.warn('Unknown message action:', action)
    }
  } catch (error) {
    console.error('Message action failed:', error)
  }
}

/**
 * Update message in messages list
 */
function updateMessageInList(messageId, updates) {
  const index = messages.value.findIndex(m => m.id === messageId)
  if (index !== -1) {
    Object.assign(messages.value[index], updates)
  }
}

/**
 * Update conversation with new message
 */
function updateConversation(message) {
  const conversation = conversations.value.find(conv =>
    (conv.type === 'private' && conv.mate.id === message.sender.id) ||
    (conv.type === 'group' && conv.group.id === message.group)
  )
  
  if (conversation) {
    conversation.lastMessage = message.content
    conversation.timestamp = message.timestamp
    
    if (selectedConversation.value?.id !== conversation.id) {
      conversation.unreadCount = (conversation.unreadCount || 0) + 1
    }
  } else if (message.sender?.id !== currentUser.value.id) {
    // Refresh conversations if new one appears
    fetchConversations()
  }
}

// ===== GROUP MANAGEMENT =====

/**
 * Create a new group
 */
async function createGroup({ name, members }) {
  try {
    const { data } = await api.post('/message/group/create/', { name, members })
    conversations.value.unshift(data)
    showCreateGroup.value = false
    selectConversation(conversations.value[0])
  } catch (error) {
    console.error('Failed to create group:', error)
  }
}

// ===== PENDING MESSAGES =====

/**
 * Accept a pending message request
 */
async function acceptPendingMessage(requestId) {
  try {
    await api.post('/message/requests/', { 
      action: 'accept', 
      request_id: requestId 
    })
    pendingMessages.value = pendingMessages.value.filter(m => m.id !== requestId)
    fetchConversations() // Refresh to show new conversation
  } catch (error) {
    console.error('Failed to accept message request:', error)
  }
}

/**
 * Reject a pending message request
 */
async function rejectPendingMessage(requestId) {
  try {
    await api.post('/message/requests/', { 
      action: 'decline', 
      request_id: requestId 
    })
    pendingMessages.value = pendingMessages.value.filter(m => m.id !== requestId)
  } catch (error) {
    console.error('Failed to reject message request:', error)
  }
}

// ===== WEBSOCKET MANAGEMENT =====

/**
 * Setup private messaging WebSocket
 */
function setupWebSockets() {
  getValidToken().then(token => {
    if (!token) {
      isAuthenticated.value = false
      return
    }
    
    privateWs.value = new WebSocket(`ws://localhost:8000/ws/private/?token=${token}`)
    
    privateWs.value.onopen = () => {
      console.log('Private WebSocket connected')
    }
    
    privateWs.value.onclose = () => {
      console.log('Private WebSocket closed')
    }
    
    privateWs.value.onerror = async (error) => {
      console.error('Private WebSocket error:', error)
      if (await getValidToken()) {
        setupWebSockets() // Retry connection
      } else {
        isAuthenticated.value = false
      }
    }
    
    privateWs.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleWebSocketMessage(data, 'private')
    }
  })
}

/**
 * Setup group messaging WebSocket
 */
function setupGroupWebSocket(conversation) {
  groupWs.value?.close()
  
  getValidToken().then(token => {
    if (!token) return
    
    groupWs.value = new WebSocket(`ws://localhost:8000/ws/group/${conversation.group.id}/?token=${token}`)
    
    groupWs.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleWebSocketMessage(data, 'group')
    }
    
    groupWs.value.onerror = async (error) => {
      console.error('Group WebSocket error:', error)
      if (await getValidToken()) {
        setupGroupWebSocket(conversation) // Retry
      } else {
        isAuthenticated.value = false
      }
    }
  })
}

/**
 * Handle incoming WebSocket messages
 */
function handleWebSocketMessage(data, scope) {
  const handlers = {
    chat_message: handleChatMessage,
    status_update: handleStatusUpdate,
    reaction_added: handleReactionAdded,
    message_edited: handleMessageEdited,
    message_deleted: handleMessageDeleted,
    messages_read: handleMessagesRead,
    message_request: handleMessageRequest,
    request_accepted: handleRequestAccepted,
    user_typing: handleUserTyping,
    user_stop_typing: handleUserStopTyping,
    error: handleWebSocketError,
    status: handleWebSocketStatus
  }
  
  const handler = handlers[data.type || data.status]
  if (handler) {
    handler(data, scope)
  } else {
    console.warn('Unknown WebSocket message type:', data.type || data.status)
  }
}

/**
 * Handle incoming chat messages
 */
function handleChatMessage(data, scope) {
  const message = data.message
  
  // Remove optimistic message if it exists
  messages.value = messages.value.filter(m => !m.id.startsWith('temp-'))
  
  // Add message if it belongs to current conversation
  const shouldAddMessage = 
    (scope === 'private' && selectedConversation.value?.type === 'private' &&
     ((message.sender.id === currentUser.value.id && message.receiver.id === selectedConversation.value.mate.id) ||
      (message.sender.id === selectedConversation.value.mate.id && message.receiver.id === currentUser.value.id))) ||
    (scope === 'group' && selectedConversation.value?.type === 'group' && 
     selectedConversation.value.group.id === message.group)
  
  if (shouldAddMessage) {
    // Create deep copy to ensure reactivity
    const newMessage = JSON.parse(JSON.stringify(message))
    messages.value.push(newMessage)
    
    // Auto-scroll to bottom
    nextTick(() => {
      const chatArea = document.querySelector('.chat-messages-container')
      if (chatArea) {
        chatArea.scrollTop = chatArea.scrollHeight
      }
    })
  }
  
  // Update conversation list
  updateConversation(message)
}

/**
 * Handle user status updates
 */
function handleStatusUpdate(data) {
  const { user_id, status, last_seen } = data
  
  // Update conversations
  conversations.value.forEach(conv => {
    if (conv.type === 'private' && conv.mate.id === user_id) {
      if (!conv.mate.profile) conv.mate.profile = {}
      conv.mate.profile.status = status
      if (last_seen) conv.mate.profile.last_seen = last_seen
    }
  })
  
  // Update selected conversation
  if (selectedConversation.value?.type === 'private' && 
      selectedConversation.value.mate.id === user_id) {
    if (!selectedConversation.value.mate.profile) {
      selectedConversation.value.mate.profile = {}
    }
    selectedConversation.value.mate.profile.status = status
    if (last_seen) selectedConversation.value.mate.profile.last_seen = last_seen
  }
}

// Additional WebSocket handlers (simplified for brevity)
function handleReactionAdded(data) {
  const messageIndex = messages.value.findIndex(m => m.id === data.message_id)
  if (messageIndex !== -1) {
    if (!messages.value[messageIndex].reactions) {
      messages.value[messageIndex].reactions = []
    }
    messages.value[messageIndex].reactions.push({
      user: { id: data.user_id },
      emoji: data.emoji
    })
  }
}

function handleMessageEdited(data) {
  updateMessageInList(data.message_id, { 
    content: data.new_content, 
    is_edited: true 
  })
}

function handleMessageDeleted(data) {
  messages.value = messages.value.filter(m => m.id !== data.message_id)
}

function handleMessagesRead(data) {
  messages.value.forEach(m => {
    if (m.sender.id === selectedConversation.value?.mate.id) {
      m.is_read = true
    }
  })
}

function handleMessageRequest(data) {
  fetchPendingMessages()
}

function handleRequestAccepted(data) {
  fetchConversations()
}

function handleUserTyping(data) {
  // Handle typing indicators
}

function handleUserStopTyping(data) {
  // Handle stop typing indicators
}

function handleWebSocketError(data) {
  console.error('WebSocket error:', data)
  messages.value = messages.value.filter(m => !m.id.startsWith('temp-'))
}

function handleWebSocketStatus(data) {
  console.log('WebSocket status:', data.status)
}

// ===== UTILITY FUNCTIONS =====

/**
 * Get profile picture URL with fallback
 */
function getProfilePictureUrl(entity) {
  const BASE_URL = 'http://127.0.0.1:8000'
  const pic = entity?.profile_picture
  return pic?.startsWith('http') ? pic : pic ? `${BASE_URL}${pic}` : '/default-avatar.png'
}

// ===== LIFECYCLE =====

/**
 * Initialize application
 */
onMounted(async () => {
  const authenticated = await validateToken()
  
  if (authenticated) {
    // Fetch initial data
    await Promise.all([
      fetchCurrentUser(),
      fetchConversations(),
      fetchPendingMessages(),
      fetchAvailableMates()
    ])
    
    // Setup WebSocket connection
    setupWebSockets()
    
    // Auto-select most recent conversation
    selectLastConversation()
    
    // Listen for global status updates
    window.addEventListener('userStatusUpdate', handleGlobalStatusUpdate)
  }
})

/**
 * Cleanup on unmount
 */
onUnmounted(() => {
  privateWs.value?.close()
  groupWs.value?.close()
  window.removeEventListener('userStatusUpdate', handleGlobalStatusUpdate)
})

/**
 * Handle global status updates from other components
 */
function handleGlobalStatusUpdate(event) {
  if (event.detail?.type === 'status_update') {
    handleStatusUpdate(event.detail)
  }
}
</script>
