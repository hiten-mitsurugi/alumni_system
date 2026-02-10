/**
 * Messaging UI State Composable
 * Handles mobile view, modals, chat info, and other UI states
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'

export function useMessagingUI() {
  // Modal states
  const showPendingMessages = ref(false)
  const showCreateGroup = ref(false)
  const showChatInfo = ref(false)
  const showBlockedUsers = ref(false)
  const showForwardModal = ref(false)
  const messageToForward = ref(null)
  
  // Mobile state
  const isMobile = ref(typeof window !== 'undefined' ? window.innerWidth < 768 : false)
  const currentMobileView = ref('list') // 'list', 'chat', 'chat-info'
  
  // Real-time notification triggers
  const memberRequestNotificationTrigger = ref(0)
  const groupMemberUpdateTrigger = ref(0)
  
  /**
   * Update mobile state on window resize
   */
  function handleResize() {
    isMobile.value = window.innerWidth < 768
  }
  
  /**
   * Toggle chat info panel
   */
  function toggleChatInfo() {
    showChatInfo.value = !showChatInfo.value
    
    // 📱 Mobile: Switch to chat-info view
    if (isMobile.value && showChatInfo.value) {
      currentMobileView.value = 'chat-info'
    } else if (isMobile.value && !showChatInfo.value) {
      currentMobileView.value = 'chat'
    }
    
    console.log('Chat info toggled:', showChatInfo.value)
  }
  
  /**
   * Close chat info panel
   */
  function closeChatInfo() {
    showChatInfo.value = false
    
    // 📱 Mobile: Return to chat view
    if (isMobile.value) {
      currentMobileView.value = 'chat'
    }
    
    console.log('Chat info closed')
  }
  
  /**
   * Handle back to conversations (mobile)
   */
  function handleBackToConversations(selectedConversation, privateWs, groupWs, messages) {
    console.log('📱 Back to conversations button clicked')
    
    if (currentMobileView.value === 'chat-info') {
      currentMobileView.value = 'chat'
    } else if (currentMobileView.value === 'chat') {
      // Clear selected conversation
      selectedConversation.value = null
      
      // Reset to list view
      currentMobileView.value = 'list'
      
      // Close chat info
      showChatInfo.value = false
      
      // Clear messages
      messages.value = []
      
      // Close WebSocket connections
      if (privateWs.value) {
        console.log('🔌 Closing private WebSocket connection')
        privateWs.value.close()
        privateWs.value = null
      }
      
      if (groupWs.value) {
        console.log('🔌 Closing group WebSocket connection')
        groupWs.value.close()
        groupWs.value = null
      }
      
      console.log('📱 Successfully returned to conversation list')
    }
  }
  
  /**
   * Scroll to specific message
   */
  function scrollToMessage(messageId) {
    console.log('Scrolling to message:', messageId)
    
    // Wait for next tick to ensure message is rendered
    setTimeout(() => {
      const messageElement = document.querySelector(`[data-message-id="${messageId}"]`)
      if (messageElement) {
        messageElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
        
        // Highlight the message briefly
        messageElement.classList.add('highlight-message')
        setTimeout(() => {
          messageElement.classList.remove('highlight-message')
        }, 2000)
      } else {
        console.warn('Message element not found:', messageId)
      }
    }, 100)
  }
  
  /**
   * Show forward modal
   */
  function showForward(message) {
    messageToForward.value = message
    showForwardModal.value = true
    console.log('Showing forward modal for message:', message.id)
  }
  
  /**
   * Handle forward complete
   */
  function handleForwardComplete() {
    showForwardModal.value = false
    messageToForward.value = null
    console.log('Forward completed')
  }
  
  /**
   * Trigger member request notification
   */
  function triggerMemberRequestNotification() {
    memberRequestNotificationTrigger.value++
    console.log('Member request notification triggered:', memberRequestNotificationTrigger.value)
  }
  
  /**
   * Trigger group member update
   */
  function triggerGroupMemberUpdate() {
    groupMemberUpdateTrigger.value++
    console.log('Group member update triggered:', groupMemberUpdateTrigger.value)
  }
  
  /**
   * Setup resize listener
   */
  function setupResizeListener() {
    if (typeof window !== 'undefined') {
      window.addEventListener('resize', handleResize)
    }
  }
  
  /**
   * Cleanup resize listener
   */
  function cleanupResizeListener() {
    if (typeof window !== 'undefined') {
      window.removeEventListener('resize', handleResize)
    }
  }
  
  return {
    // Modal states
    showPendingMessages,
    showCreateGroup,
    showChatInfo,
    showBlockedUsers,
    showForwardModal,
    messageToForward,
    
    // Mobile state
    isMobile,
    currentMobileView,
    
    // Notification triggers
    memberRequestNotificationTrigger,
    groupMemberUpdateTrigger,
    
    // Functions
    toggleChatInfo,
    closeChatInfo,
    handleBackToConversations,
    scrollToMessage,
    showForward,
    handleForwardComplete,
    triggerMemberRequestNotification,
    triggerGroupMemberUpdate,
    setupResizeListener,
    cleanupResizeListener,
    handleResize
  }
}
