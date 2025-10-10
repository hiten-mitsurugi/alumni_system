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
      console.log('📊 Messaging Notification Store: Fetching unread counts...')
      const response = await api.get('/message/unread-counts/')
      const data = response.data
      
      // Update values with proper fallbacks
      const newUnreadMessages = parseInt(data.unread_messages || 0)
      const newUnreadRequests = parseInt(data.unread_message_requests || 0)
      
      unreadMessages.value = newUnreadMessages
      unreadMessageRequests.value = newUnreadRequests
      
      console.log('📊 Messaging Notification Store: Fetched unread counts:', {
        messages: unreadMessages.value,
        requests: unreadMessageRequests.value,
        total: totalUnreadCount.value,
        rawData: data
      })
      
    } catch (err) {
      console.error('❌ Failed to fetch messaging unread counts:', err)
      console.error('❌ Error details:', err.response?.data || err.message)
      error.value = err.message
      
      // Set to zero on error to prevent showing stale counts
      unreadMessages.value = 0
      unreadMessageRequests.value = 0
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
      } else if (action === 'refresh') {
        // New action to force refresh from server
        console.log('🔔 Messaging Notification: Refresh action received, fetching latest counts...')
        fetchUnreadCounts()
        return // Don't do delayed refresh if we just refreshed
      }
      
      console.log('🔔 Current counts after update:', { 
        messages: unreadMessages.value, 
        requests: unreadMessageRequests.value,
        total: totalUnreadCount.value
      })
      
      // 🔧 ENHANCEMENT: Immediate refresh for consistency (no delay)
      setTimeout(async () => {
        console.log('🔄 Quick refresh after notification update...')
        await fetchUnreadCounts()
      }, 100) // Minimal delay for better performance
      
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
        // Wait briefly for connection to establish
        await new Promise(resolve => setTimeout(resolve, 200))
      }
      
      // Add our listener to the existing connection
      websocketService.addListener('notifications', handleNotificationUpdate)
      
      wsConnected.value = true
      console.log('🌐 Messaging Notification: Added listener to WebSocket connection')
      
      // 🔧 ENHANCEMENT: Set up periodic refresh to ensure real-time accuracy
      setInterval(async () => {
        if (isInitialized.value) {
          console.log('🔄 Auto-refreshing notification counts...')
          await fetchUnreadCounts()
        }
      }, 10000) // Refresh every 10 seconds for faster updates
      
    } catch (error) {
      console.error('❌ Failed to add messaging notification listener:', error)
    }
  }

  // Initialize store
  async function initialize() {
    if (isInitialized.value) {
      console.log('✅ Messaging notification store already initialized')
      return
    }

    const authStore = useAuthStore()
    if (!authStore.user || !authStore.token) {
      console.log('⚠️ User not authenticated, skipping messaging notification store initialization')
      return
    }

    console.log('🚀 Initializing messaging notification store for user:', authStore.user.id)

    try {
      // First fetch the counts
      await fetchUnreadCounts()
      
      // Then initialize WebSocket
      await initializeWebSocket()
      
      // Mark as initialized
      isInitialized.value = true
      console.log('✅ Messaging notification store initialized successfully')
      
      // Force an immediate refresh to ensure we have latest data
      setTimeout(async () => {
        console.log('🔄 Initial refresh after store initialization...')
        await fetchUnreadCounts()
      }, 100)
      
    } catch (error) {
      console.error('❌ Failed to initialize messaging notification store:', error)
      // Reset state on failure
      isInitialized.value = false
      unreadMessages.value = 0
      unreadMessageRequests.value = 0
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
