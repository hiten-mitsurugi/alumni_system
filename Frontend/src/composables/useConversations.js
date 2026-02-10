/**
 * Conversations Management Composable
 * Handles fetching, selecting, searching conversations
 */
import { ref } from 'vue'
import messagingService from '@/services/messaging'
import api from '@/services/api'
import { getProfilePictureUrl } from '@/utils/imageUrl'

// Helper to get avatar URL for users or groups
function getEntityAvatarUrl(entity) {
  if (!entity) return getProfilePictureUrl(null)
  const pic = entity.profile_picture || entity.group_picture || null
  return getProfilePictureUrl(pic)
}

export function useConversations(currentUser, route) {
  const conversations = ref([])
  const pendingMessages = ref([])
  const availableMates = ref([])
  const searchQuery = ref('')
  const searchResults = ref([])
 const searchInput = ref(null)
  const selectedConversation = ref(null)
  
  /**
   * Fetch all conversations (private + group)
   */
  async function fetchConversations() {
    try {
      const [privateConversations, groupConversations] = await Promise.all([
        messagingService.getConversations().catch(err => {
          console.error('Error fetching private conversations:', err)
          return []
        }),
        messagingService.getGroupConversations().catch(err => {
          console.error('Error fetching group conversations:', err)
          return []
        })
      ])
      
      // Transform private conversations
      const transformedPrivate = (Array.isArray(privateConversations) ? privateConversations : [])
        .map(conv => ({
          ...conv,
          id: conv.id || conv.mate.id,
          type: 'private',
          timestamp: conv.timestamp || conv.lastMessageTime || new Date().toISOString()
        }))
      
      // Transform group conversations
      const transformedGroups = (Array.isArray(groupConversations) ? groupConversations : [])
        .map(group => ({
          id: group.id,
          type: 'group',
          group: group.group || group,
          lastMessage: group.lastMessage || '',
          timestamp: group.timestamp || group.updated_at || group.created_at || new Date().toISOString(),
          unreadCount: group.unreadCount || 0
        }))
      
      // Combine and sort by timestamp
      const allConversations = [...transformedPrivate, ...transformedGroups]
      conversations.value = allConversations.sort((a, b) => 
        new Date(b.timestamp) - new Date(a.timestamp)
      )
      
      console.log('Fetched conversations:', conversations.value.length)
      console.log('Private:', transformedPrivate.length, 'Groups:', transformedGroups.length)
    } catch (e) {
      console.error('Conv fetch error', e)
      if (e.response?.status === 403) {
        console.log('Some conversations may be hidden due to blocking')
      }
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
        avatar: getEntityAvatarUrl(req.sender),
        message: req.content ? truncateMessage(req.content, 50) : 'Message request',
        timestamp: req.timestamp
      }))
    } catch (e) {
      console.error('Pending fetch error', e)
    }
  }
  
  /**
   * Fetch available mates to message
   */
  async function fetchAvailableMates() {
    try {
      const { data } = await api.get('/message/search/')
      availableMates.value = (Array.isArray(data.users) ? data.users : [])
        .map(u => ({
          ...u,
          profile_picture: getEntityAvatarUrl(u)
        }))
    } catch (e) {
      console.error('Mates fetch error', e)
    }
  }
  
  /**
   * Search for users/groups
   */
  async function search() {
    if (!searchQuery.value) {
      searchResults.value = []
      return
    }
    
    try {
      console.log('🔍 Searching for:', searchQuery.value)
      const { data } = await api.get(
        `/message/search/?q=${encodeURIComponent(searchQuery.value)}`
      )
      
      const users = (data.users || []).map(u => ({
        type: 'user',
        ...u,
        profile_picture: getEntityAvatarUrl(u)
      }))
      
      const groups = (data.groups || []).map(g => ({ type: 'group', ...g }))
      
      searchResults.value = [...users, ...groups]
      console.log('🔍 Search results:', searchResults.value.length)
    } catch (e) {
      console.error('🔍 Search error:', e)
      searchResults.value = []
    }
  }
  
  /**
   * Select a conversation
   */
  function selectConversation(conv, options = {}) {
    console.log('Selecting conversation:', conv.id)
    
    selectedConversation.value = conv
    
    // Callback for fetching messages
    if (options.onSelect) {
      options.onSelect(conv)
    }
  }
  
  /**
   * Select search result
   */
  async function selectSearchResult(r, options = {}) {
    if (r.type === 'user') {
      let conv = conversations.value.find(c => c.type === 'private' && c.mate.id === r.id)
      if (!conv) {
        conv = {
          type: 'private',
          id: r.id,
          mate: r,
          lastMessage: '',
          timestamp: null,
          unreadCount: 0
        }
        conversations.value.unshift(conv)
      }
      selectConversation(conv, options)
    } else if (r.type === 'group') {
      let group = conversations.value.find(c => c.type === 'group' && c.group.id === r.id)
      if (!group) {
        const isUserMember = r.members && r.members.some(m => m.id === currentUser.value.id)
        
        if (isUserMember) {
          console.log('User is already a member of this group, fetching conversations')
          await fetchConversations()
          group = conversations.value.find(c => c.type === 'group' && c.group.id === r.id)
        } else {
          console.log('User is not a member, try to join the group')
          // Handle joining logic in parent
          if (options.onGroupJoinNeeded) {
            options.onGroupJoinNeeded(r)
            return
          }
        }
      }
      if (group) {
        selectConversation(group, options)
      }
    }
    
    // Clear search
    searchQuery.value = ''
    searchResults.value = []
  }
  
  /**
   * Auto-select last conversation
   */
  function selectLastConversation(options = {}) {
    if (conversations.value.length > 0) {
      const sorted = [...conversations.value].sort((a, b) => {
        const timestampA = new Date(a.timestamp || 0).getTime()
        const timestampB = new Date(b.timestamp || 0).getTime()
        return timestampB - timestampA
      })
      
      const lastConversation = sorted[0]
      if (lastConversation) {
        console.log('Auto-selecting last conversation:', lastConversation.id)
        selectConversation(lastConversation, options)
      }
    }
  }
  
  /**
   * Handle user from query params
   */
  async function handleUserFromQuery(options = {}) {
    const userId = route.query.userId
    const username = route.query.user
    const userName = route.query.name
    
    if (!userId && !username) return
    
    console.log('🔄 Handling user from query:', { userId, username, userName })
    
    try {
      // Refresh conversations first
      await fetchConversations()
      
      // Try to find existing conversation
      let existingConv = conversations.value.find(c =>
        c.type === 'private' && (
          c.mate.id == userId ||
          c.mate.username === username
        )
      )
      
      if (existingConv) {
        console.log('✅ Found existing conversation')
        selectConversation(existingConv, options)
        return
      }
      
      // Try to find in available mates
      let user = availableMates.value.find(mate =>
        mate.id == userId || mate.username === username
      )
      
      // Search if not found
      if (!user && (userId || username)) {
        try {
          const searchResponse = await api.get(
            `/message/search/?q=${encodeURIComponent(username || userId)}`
          )
          
          if (searchResponse.data && searchResponse.data.length > 0) {
            user = searchResponse.data.find(result =>
              result.type === 'user' && (
                result.id == userId ||
                result.username === username
              )
            )
          }
        } catch (error) {
          console.error('❌ Error searching for user:', error)
        }
      }
      
      // Create minimal user object if still not found
      if (!user && userId) {
        user = {
          id: parseInt(userId),
          username: username || `user_${userId}`,
          first_name: userName ? userName.split(' ')[0] : 'User',
          last_name: userName ? userName.split(' ').slice(1).join(' ') : '',
          profile_picture: null
        }
        console.log('🔧 Created minimal user object')
      }
      
      if (user) {
        const newConversation = {
          type: 'private',
          id: user.id,
          mate: user,
          lastMessage: '',
          timestamp: new Date().toISOString(),
          unreadCount: 0
        }
        
        console.log('✅ Creating new conversation')
        
        if (!conversations.value.find(c => c.type === 'private' && c.mate.id === user.id)) {
          conversations.value.unshift(newConversation)
        }
        
        selectConversation(newConversation, options)
      } else {
        console.warn('⚠️ Could not find or create user for conversation')
      }
    } catch (error) {
      console.error('❌ Error handling user from query:', error)
    }
  }
  
  /**
   * Accept pending message request
   */
  async function acceptPendingMessage(id) {
    try {
      await api.post('/message/requests/', { action: 'accept', request_id: id })
      pendingMessages.value = pendingMessages.value.filter(m => m.id !== id)
      await fetchConversations()
    } catch (e) {
      console.error('Accept error', e)
    }
  }
  
  /**
   * Reject pending message request
   */
  async function rejectPendingMessage(id) {
    try {
      await api.post('/message/requests/', { action: 'decline', request_id: id })
      pendingMessages.value = pendingMessages.value.filter(m => m.id !== id)
      await fetchConversations()
    } catch (e) {
      console.error('Reject error', e)
    }
  }
  
  /**
   * Focus search input
   */
  function focusSearch() {
    if (searchQuery.value) {
      searchQuery.value = ''
      searchResults.value = []
    } else {
      searchInput.value?.focus()
    }
  }
  
  /**
   * Truncate message for preview
   */
  function truncateMessage(message, maxLength = 50) {
    if (!message || message.length <= maxLength) return message || 'Message request'
    return message.substring(0, maxLength).trim() + '...'
  }
  
  return {
    // State
    conversations,
    pendingMessages,
    availableMates,
    searchQuery,
    searchResults,
    searchInput,
    selectedConversation,
    
    // Functions
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
    focusSearch,
    truncateMessage
  }
}
