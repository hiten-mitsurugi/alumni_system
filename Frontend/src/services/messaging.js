// services/messaging.js
import api from './api'

class MessagingService {
  // Block/Unblock functionality
  async getBlockedUsers() {
    try {
      const response = await api.get('/message/block/')
      return response.data
    } catch (error) {
      console.error('Error fetching blocked users:', error)
      throw error
    }
  }

  async blockUser(userId) {
    try {
      const response = await api.post('/message/block/', {
        user_id: userId
      })
      return response.data
    } catch (error) {
      console.error('Error blocking user:', error)
      throw error
    }
  }

  async unblockUser(userId) {
    try {
      const response = await api.delete(`/message/block/${userId}/`)
      return response.data
    } catch (error) {
      console.error('Error unblocking user:', error)
      throw error
    }
  }

  // Check if user is blocked
  async isUserBlocked(userId) {
    try {
      const blockedUsers = await this.getBlockedUsers()
      return blockedUsers.some(block => block.blocked_user.id === userId)
    } catch (error) {
      console.error('Error checking if user is blocked:', error)
      return false
    }
  }

  // Conversation functionality
  async getConversations() {
    try {
      const response = await api.get('/message/conversations/')
      return response.data
    } catch (error) {
      console.error('Error fetching conversations:', error)
      throw error
    }
  }

  async getMessages(receiverId) {
    try {
      const response = await api.get(`/message/private/${receiverId}/`)
      return response.data
    } catch (error) {
      console.error('Error fetching messages:', error)
      throw error
    }
  }

  async getGroupMessages(groupId) {
    try {
      const response = await api.get(`/message/group/${groupId}/`)
      return response.data
    } catch (error) {
      console.error('Error fetching group messages:', error)
      throw error
    }
  }

  async sendMessage(receiverId, content, attachmentIds = [], replyToId = null) {
    try {
      const response = await api.post('/message/send/', {
        receiver_id: receiverId,
        content: content,
        attachment_ids: attachmentIds,
        reply_to_id: replyToId
      })
      return response.data
    } catch (error) {
      console.error('Error sending message:', error)
      throw error
    }
  }

  // Search functionality
  async searchUsers(query) {
    try {
      const response = await api.get('/message/search/', {
        params: { q: query }
      })
      return response.data
    } catch (error) {
      console.error('Error searching users:', error)
      throw error
    }
  }

  // Message requests
  async getMessageRequests() {
    try {
      const response = await api.get('/message/requests/')
      return response.data
    } catch (error) {
      console.error('Error fetching message requests:', error)
      throw error
    }
  }

  async respondToMessageRequest(requestId, action) {
    try {
      const response = await api.post('/message/requests/', {
        request_id: requestId,
        action: action // 'accept' or 'decline'
      })
      return response.data
    } catch (error) {
      console.error('Error responding to message request:', error)
      throw error
    }
  }

  // Pin/Unpin messages
  async togglePinMessage(messageId) {
    try {
      const response = await api.post(`/message/pin/${messageId}/`)
      return response.data
    } catch (error) {
      console.error('Error toggling pin message:', error)
      throw error
    }
  }

  // Bump messages
  async bumpMessage(messageId) {
    try {
      const response = await api.post(`/message/bump/${messageId}/`)
      return response.data
    } catch (error) {
      console.error('Error bumping message:', error)
      throw error
    }
  }

  // File upload
  async uploadFile(file) {
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await api.upload('/message/upload/', formData)
      return response.data
    } catch (error) {
      console.error('Error uploading file:', error)
      throw error
    }
  }

  // Utility functions
  getProfilePictureUrl(user) {
    const BASE_URL = 'http://127.0.0.1:8000'
    const pic = user?.profile_picture
    return pic
      ? (pic.startsWith('http') ? pic : `${BASE_URL}${pic}`)
      : '/default-avatar.png'
  }

  formatTimestamp(timestamp) {
    const date = new Date(timestamp)
    const now = new Date()
    const diffInHours = (now - date) / (1000 * 60 * 60)

    if (diffInHours < 1) {
      const minutes = Math.floor(diffInHours * 60)
      return minutes <= 1 ? 'Just now' : `${minutes}m ago`
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`
    } else {
      return date.toLocaleDateString()
    }
  }

  isRecentlyActive(user) {
    if (!user?.profile?.last_seen) return false
    const lastSeen = new Date(user.profile.last_seen)
    const now = new Date()
    const diffMinutes = (now - lastSeen) / (1000 * 60)
    const isRecent = diffMinutes <= 2
    const isOnlineStatus = user.profile.status === 'online'
    return isRecent && isOnlineStatus
  }
}

// Export a singleton instance
export const messagingService = new MessagingService()
export default messagingService
