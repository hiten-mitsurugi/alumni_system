/**
 * Messages Management Composable
 * Handles message fetching, caching, and prefetching
 */
import { ref } from 'vue'
import messagingService from '@/services/messaging'

const isDev = import.meta.env.DEV
const debugLog = isDev ? console.log : () => {}

export function useMessages() {
  const messages = ref([])
  const messageCache = new Map()
  const prefetchedConversations = new Set()
  
  /**
   * Fetch messages for a conversation
   */
  async function fetchMessages(conversation) {
    if (!conversation) {
      console.error('No conversation provided')
      return []
    }
    
    try {
      const cacheKey = conversation.type === 'private'
        ? `private_${conversation.mate.id}`
        : `group_${conversation.group.id}`
      
      // Check cache first
      if (messageCache.has(cacheKey)) {
        const cached = messageCache.get(cacheKey)
        debugLog(`📦 Using cached messages for ${cacheKey}`)
        messages.value = cached
        return cached
      }
      
      // Fetch from API
      debugLog(`🌐 Fetching messages from API for ${cacheKey}`)
      const fetchedMessages = conversation.type === 'private'
        ? await messagingService.getMessages(conversation.mate.id)
        : await messagingService.getGroupMessages(conversation.group?.id)
      
      // Update cache
      messageCache.set(cacheKey, fetchedMessages)
      messages.value = fetchedMessages
      
      debugLog(`✅ Fetched ${fetchedMessages.length} messages for ${cacheKey}`)
      return fetchedMessages
    } catch (error) {
      console.error('Error fetching messages:', error)
      return []
    }
  }
  
  /**
   * Prefetch messages on hover (desktop only)
   */
  async function prefetchMessages(conversation) {
    if (!conversation) return
    
    const cacheKey = conversation.type === 'private'
      ? `private_${conversation.mate.id}`
      : `group_${conversation.group.id}`
    
    // Skip if already prefetched or cached
    if (prefetchedConversations.has(cacheKey) || messageCache.has(cacheKey)) {
      return
    }
    
    try {
      debugLog(`🔮 Prefetching messages for ${cacheKey}`)
      
      const fetchedMessages = conversation.type === 'private'
        ? await messagingService.getMessages(conversation.mate.id)
        : await messagingService.getGroupMessages(conversation.group?.id)
      
      // Cache the prefetched messages
      messageCache.set(cacheKey, fetchedMessages)
      prefetchedConversations.add(cacheKey)
      
      debugLog(`✅ Prefetched ${fetchedMessages.length} messages for ${cacheKey}`)
    } catch (error) {
      console.error('Error prefetching messages:', error)
    }
  }
  
  /**
   * Add message to local state (optimistic update)
   */
  function addMessage(message) {
    if (!message) return
    
    messages.value.push(message)
    
    // Update cache if exists
    const currentConv = messages.value[0]?.receiver || messages.value[0]?.group
    if (currentConv) {
      const cacheKey = message.receiver
        ? `private_${message.receiver.id || message.receiver_id}`
        : `group_${message.group.id || message.group_id}`
      
      if (messageCache.has(cacheKey)) {
        const cached = messageCache.get(cacheKey)
        messageCache.set(cacheKey, [...cached, message])
      }
    }
  }
  
  /**
   * Update message in local state
   */
  function updateMessage(messageId, updates) {
    const index = messages.value.findIndex(m => m.id === messageId)
    if (index !== -1) {
      messages.value[index] = { ...messages.value[index], ...updates }
      
      // Update cache
      messageCache.forEach((cachedMessages, key) => {
        const cacheIndex = cachedMessages.findIndex(m => m.id === messageId)
        if (cacheIndex !== -1) {
          cachedMessages[cacheIndex] = { ...cachedMessages[cacheIndex], ...updates }
          messageCache.set(key, [...cachedMessages])
        }
      })
    }
  }
  
  /**
   * Delete message from local state
   */
  function deleteMessage(messageId) {
    messages.value = messages.value.filter(m => m.id !== messageId)
    
    // Update cache
    messageCache.forEach((cachedMessages, key) => {
      messageCache.set(key, cachedMessages.filter(m => m.id !== messageId))
    })
  }
  
  /**
   * Clear message cache
   */
  function clearCache(cacheKey = null) {
    if (cacheKey) {
      messageCache.delete(cacheKey)
      prefetchedConversations.delete(cacheKey)
      debugLog(`🗑️ Cleared cache for ${cacheKey}`)
    } else {
      messageCache.clear()
      prefetchedConversations.clear()
      debugLog('🗑️ Cleared all message cache')
    }
  }
  
  /**
   * Find message by ID
   */
  function findMessage(messageId) {
    return messages.value.find(m => m.id === messageId)
  }
  
  /**
   * Get unread count for conversation
   */
  function getUnreadCount(conversation) {
    if (!conversation) return 0
    
    const cacheKey = conversation.type === 'private'
      ? `private_${conversation.mate.id}`
      : `group_${conversation.group.id}`
    
    const cachedMessages = messageCache.get(cacheKey) || []
    return cachedMessages.filter(m => !m.is_read).length
  }
  
  return {
    // State
    messages,
    messageCache,
    prefetchedConversations,
    
    // Functions
    fetchMessages,
    prefetchMessages,
    addMessage,
    updateMessage,
    deleteMessage,
    clearCache,
    findMessage,
    getUnreadCount
  }
}
