// Notification System Test Utility
// Use this in browser console to test the messaging notification system

export function testNotificationSystem() {
  console.log('🧪 Starting Notification System Test...')
  
  // Get the messaging notification store
  const messagingStore = useMessagingNotificationStore()
  
  console.log('Current state:', {
    initialized: messagingStore.isInitialized,
    messages: messagingStore.unreadMessages,
    requests: messagingStore.unreadMessageRequests,
    total: messagingStore.totalUnreadCount,
    wsConnected: messagingStore.wsConnected
  })
  
  // Test manual increment
  console.log('Testing increment...')
  messagingStore.testIncrement()
  
  setTimeout(() => {
    console.log('State after increment:', {
      messages: messagingStore.unreadMessages,
      requests: messagingStore.unreadMessageRequests,
      total: messagingStore.totalUnreadCount
    })
    
    // Test force refresh
    console.log('Testing force refresh...')
    messagingStore.forceRefresh()
  }, 1000)
}

// Make it globally available for console testing
if (typeof window !== 'undefined') {
  window.testNotificationSystem = testNotificationSystem
}