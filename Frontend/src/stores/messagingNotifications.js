import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { websocketService } from '@/services/websocket'

export const useMessagingNotificationStore = defineStore('messagingNotifications', () => {
  // State
  const unreadMessages = ref(0)
  const unreadMessageRequests = ref(0)
  const isLoading = ref(false)
  const error = ref(null)
  const isInitialized = ref(false)
  const wsConnected = ref(false)

  // Computed
  const totalUnreadCount = computed(() => {
    return unreadMessages.value + unreadMessageRequests.value
  })

  const hasUnreadMessages = computed(() => {
    return totalUnreadCount.value > 0
  })

  // Actions
  async function fetchUnreadCounts() {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.get('/message/unread-counts/')
      const data = response.data
      
      unreadMessages.value = data.unread_messages || 0
      unreadMessageRequests.value = data.unread_message_requests || 0
      
      console.log('📊 Messaging Notification Store: Fetched unread counts:', {
        messages: unreadMessages.value,
        requests: unreadMessageRequests.value,
        total: totalUnreadCount.value
      })
      
    } catch (err) {
      console.error('❌ Failed to fetch messaging unread counts:', err)
      error.value = err.message
    } finally {
      isLoading.value = false
    }
  }

  function incrementMessages(count = 1) {
    unreadMessages.value += count
    console.log('📈 Messaging Notification: Incremented messages by', count, 'Total:', unreadMessages.value)
  }

  function decrementMessages(count = 1) {
    unreadMessages.value = Math.max(0, unreadMessages.value - count)
    console.log('📉 Messaging Notification: Decremented messages by', count, 'Total:', unreadMessages.value)
  }

  function incrementRequests(count = 1) {
    unreadMessageRequests.value += count
    console.log('📈 Messaging Notification: Incremented requests by', count, 'Total:', unreadMessageRequests.value)
  }

  function decrementRequests(count = 1) {
    unreadMessageRequests.value = Math.max(0, unreadMessageRequests.value - count)
    console.log('📉 Messaging Notification: Decremented requests by', count, 'Total:', unreadMessageRequests.value)
  }

  function markAllMessagesAsRead() {
    console.log('✅ Messaging Notification: Marking all messages as read')
    unreadMessages.value = 0
  }

  function markAllRequestsAsRead() {
    console.log('✅ Messaging Notification: Marking all requests as read')
    unreadMessageRequests.value = 0
  }

  function clearAllCounts() {
    console.log('🧹 Messaging Notification: Clearing all counts')
    unreadMessages.value = 0
    unreadMessageRequests.value = 0
  }

  // WebSocket event handler
  function handleNotificationUpdate(data) {
    console.log('🔔 Messaging Notification: Received WebSocket event:', data)
    
    // Only handle notification_update events, ignore status_update and other events
    if (data.type === 'notification_update' && data.data) {
      const { action, type, count = 1 } = data.data
      
      console.log('🔔 Messaging Notification: Processing notification update:', { action, type, count })
      console.log('🔔 Current counts before update:', { 
        messages: unreadMessages.value, 
        requests: unreadMessageRequests.value 
      })
      
      if (action === 'increment') {
        if (type === 'message') {
          incrementMessages(count)
        } else if (type === 'request') {
          incrementRequests(count)
        }
      } else if (action === 'decrement') {
        if (type === 'message') {
          decrementMessages(count)
        } else if (type === 'request') {
          decrementRequests(count)
        }
      } else if (action === 'reset') {
        if (type === 'message') {
          markAllMessagesAsRead()
        } else if (type === 'request') {
          markAllRequestsAsRead()
        } else if (type === 'all') {
          clearAllCounts()
        }
      }
      
      console.log('🔔 Current counts after update:', { 
        messages: unreadMessages.value, 
        requests: unreadMessageRequests.value,
        total: totalUnreadCount.value
      })
      
    } else if (data.type === 'status_update') {
      // Ignore status updates - these are handled by App.vue and other components
      console.log('🔔 Messaging Notification: Ignoring status update event')
    } else {
      // Log other events but don't process them
      console.log('🔔 Messaging Notification: Ignoring non-notification event:', data.type)
    }
  }

  // Initialize WebSocket connection
  async function initializeWebSocket() {
    if (wsConnected.value) return

    try {
      // Ensure the main WebSocket connection exists first
      const socket = websocketService.getSocket('notifications')
      if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.log('🌐 Messaging Notification: Main WebSocket not ready, connecting...')
        await websocketService.connect('notifications')
        // Wait a bit for connection to establish
        await new Promise(resolve => setTimeout(resolve, 500))
      }
      
      // Add our listener to the existing connection
      websocketService.addListener('notifications', handleNotificationUpdate)
      
      wsConnected.value = true
      console.log('🌐 Messaging Notification: Added listener to WebSocket connection')
    } catch (error) {
      console.error('❌ Failed to add messaging notification listener:', error)
    }
  }

  // Initialize store
  async function initialize() {
    if (isInitialized.value) return

    const authStore = useAuthStore()
    if (!authStore.user) {
      console.log('⚠️ User not authenticated, skipping messaging notification store initialization')
      return
    }

    try {
      await fetchUnreadCounts()
      await initializeWebSocket()
      isInitialized.value = true
      console.log('✅ Messaging notification store initialized')
    } catch (error) {
      console.error('❌ Failed to initialize messaging notification store:', error)
    }
  }

  // Cleanup
  function cleanup() {
    websocketService.removeListener('notifications', handleNotificationUpdate)
    wsConnected.value = false
    isInitialized.value = false
    clearAllCounts()
    console.log('🧹 Messaging notification store cleaned up')
  }

  // Test method to manually trigger updates (for debugging)
  function testIncrement() {
    console.log('🧪 Testing increment...')
    incrementMessages(1)
  }

  function testDecrement() {
    console.log('🧪 Testing decrement...')
    decrementMessages(1)
  }

  // Force refresh counts from server
  async function forceRefresh() {
    console.log('🔄 Force refreshing notification counts...')
    await fetchUnreadCounts()
  }

  return {
    // State
    unreadMessages,
    unreadMessageRequests,
    isLoading,
    error,
    isInitialized,
    wsConnected,
    
    // Computed
    totalUnreadCount,
    hasUnreadMessages,
    
    // Actions
    fetchUnreadCounts,
    incrementMessages,
    decrementMessages,
    incrementRequests,
    decrementRequests,
    markAllMessagesAsRead,
    markAllRequestsAsRead,
    clearAllCounts,
    initialize,
    cleanup,
    forceRefresh,
    testIncrement,
    testDecrement,
    
    // WebSocket handlers
    handleNotificationUpdate
  }
})
