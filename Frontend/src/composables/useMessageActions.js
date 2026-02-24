/**
 * Message Actions Composable
 * Handles sending, editing, deleting, reacting to messages
 */
import { ref, nextTick } from 'vue'
import api from '@/services/api'

export function useMessageActions(
  selectedConversation,
  currentUser,
  messages,
  privateWs,
  groupWs,
  messageCache,
  prefetchedConversations
) {
  const uploadProgress = ref(0)
  
  /**
   * Upload attachments and return IDs
   */
  async function uploadAttachments(attachments) {
    if (!attachments || attachments.length === 0) {
      return []
    }
    
    try {
      const uploadPromises = attachments.map(async (file) => {
        const formData = new FormData()
        formData.append('file', file)
        
        const { data } = await api.post('/message/upload-attachment/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (progressEvent) => {
            uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          }
        })
        
        return data.id
      })
      
      const attachmentIds = await Promise.all(uploadPromises)
      uploadProgress.value = 0 // Reset progress
      
      return attachmentIds
    } catch (error) {
      console.error('Error uploading attachments:', error)
      uploadProgress.value = 0
      throw error
    }
  }
  
  /**
   * Send a message
   */
  async function sendMessage(data) {
    console.log('useMessageActions: sendMessage called with:', data)
    
    try {
      // Prevent double sending
      if (data._processing) {
        console.log('Message already processing, skipping')
        return
      }
      data._processing = true
      
      // Upload attachments
      const attachmentIds = await uploadAttachments(data.attachments)
      
      // Validate
      if (!currentUser.value) {
        console.error('Error: currentUser is null')
        return
      }
      if (!selectedConversation.value || !selectedConversation.value.type) {
        console.error('Error: selectedConversation is invalid')
        return
      }
      
      const tempId = `temp-${Date.now()}-${Math.random()}`
      
      // Check if new conversation (no messages)
      const isNewConversation = !selectedConversation.value.isPending &&
                                messages.value.length === 0 &&
                                selectedConversation.value.type === 'private'
      
      if (isNewConversation) {
        console.log('🆕 New conversation - using REST API')
        
        try {
          const response = await api.post('/message/send/', {
            receiver_id: selectedConversation.value.mate.id,
            content: data.content,
            attachment_ids: attachmentIds,
            reply_to_id: data.reply_to_id
          })
          
          console.log('✅ Message request created:', response.data)
          
          // Callback to parent to refresh conversations
          if (data.onConversationCreated) {
            await data.onConversationCreated()
          }
          
          return
        } catch (error) {
          console.error('❌ Error creating message request:', error)
          return
        }
      }
      
      // Create temporary message for optimistic UI
      const newMessage = {
        id: tempId,
        temp_id: tempId,  // Store temp_id for matching server response
        sender: currentUser.value,
        content: data.content,
        attachments: data.attachments.map(file => ({
          url: URL.createObjectURL(file),
          name: file.name,
          type: file.type
        })),
        timestamp: new Date().toISOString(),
        is_read: false,
        reply_to: data.reply_to_id ? messages.value.find(m => m.id === data.reply_to_id) : null,
        reply_to_id: data.reply_to_id || null,
        _isTemporary: true
      }
      
      console.log('Optimistically adding message to UI')
      messages.value.push(newMessage)
      
      // Prepare WebSocket payload
      const payload = {
        action: 'send_message',
        content: data.content,
        attachment_ids: attachmentIds,
        reply_to_id: data.reply_to_id,
        receiver_id: selectedConversation.value.mate?.id,
        temp_id: tempId
      }
      
      // Send via WebSocket
      if (selectedConversation.value.type === 'private') {
        if (!selectedConversation.value.mate?.id) {
          console.error('Error: mate.id is missing')
          messages.value = messages.value.filter(m => m.id !== tempId)
          return
        }
        if (privateWs.value?.readyState === WebSocket.OPEN) {
          console.log('Sending via private WebSocket:', payload)
          privateWs.value.send(JSON.stringify(payload))
        } else {
          console.error('Private WebSocket not open')
          messages.value = messages.value.filter(m => m.id !== tempId)
        }
      } else if (selectedConversation.value.type === 'group') {
        payload.group_id = selectedConversation.value.group.id
        delete payload.receiver_id
        
        console.log('🟢 Preparing to send group message:', {
          groupId: payload.group_id,
          wsState: groupWs.value?.readyState,
          wsOpen: groupWs.value?.readyState === WebSocket.OPEN
        })
        
        if (groupWs.value?.readyState === WebSocket.OPEN) {
          console.log('🟢 Sending via group WebSocket:', payload)
          groupWs.value.send(JSON.stringify(payload))
        } else {
          console.error('🟢 Group WebSocket not open! State:', groupWs.value?.readyState)
          alert('Group chat connection not ready. Please refresh the page.')
          messages.value = messages.value.filter(m => m.id !== tempId)
        }
      }
      
      // Invalidate cache
      const cacheKey = selectedConversation.value.type === 'private'
        ? `private_${selectedConversation.value.mate.id}`
        : `group_${selectedConversation.value.group.id}`
      
      if (messageCache.has(cacheKey)) {
        messageCache.delete(cacheKey)
        prefetchedConversations.delete(cacheKey)
        console.log(`🚀 Cache invalidated for ${cacheKey}`)
      }
      
    } catch (error) {
      console.error('Error sending message:', error)
    }
  }
  
  /**
   * Edit a message
   */
  async function editMessage(message, newContent) {
    try {
      console.log('Editing message:', message.id, 'New content:', newContent)
      
      const payload = {
        action: 'edit_message',
        message_id: message.id,
        new_content: newContent
      }
      
      if (selectedConversation.value?.type === 'private') {
        if (privateWs.value?.readyState === WebSocket.OPEN) {
          privateWs.value.send(JSON.stringify(payload))
        } else {
          console.error('Private WebSocket not open for edit')
        }
      } else if (selectedConversation.value?.type === 'group') {
        if (groupWs.value?.readyState === WebSocket.OPEN) {
          groupWs.value.send(JSON.stringify(payload))
        } else {
          console.error('Group WebSocket not open for edit')
        }
      }
    } catch (error) {
      console.error('Error editing message:', error)
    }
  }
  
  /**
   * Delete a message
   */
  async function deleteMessage(message) {
    try {
      console.log('Deleting message:', message.id)
      
      const payload = {
        action: 'delete_message',
        message_id: message.id
      }
      
      if (selectedConversation.value?.type === 'private') {
        if (privateWs.value?.readyState === WebSocket.OPEN) {
          privateWs.value.send(JSON.stringify(payload))
        } else {
          console.error('Private WebSocket not open for delete')
        }
      } else if (selectedConversation.value?.type === 'group') {
        if (groupWs.value?.readyState === WebSocket.OPEN) {
          groupWs.value.send(JSON.stringify(payload))
        } else {
          console.error('Group WebSocket not open for delete')
        }
      }
    } catch (error) {
      console.error('Error deleting message:', error)
    }
  }
  
  /**
   * Send reaction to message
   */
  function sendReaction(messageId, reactionType, isRemoving = false) {
    try {
      const action = isRemoving ? 'remove_reaction' : 'add_reaction'
      const payload = {
        action: action,
        message_id: messageId,
        reaction_type: reactionType
      }
      
      console.log(`Sending ${action} via WebSocket:`, payload)
      
      if (selectedConversation.value?.type === 'private') {
        if (privateWs.value?.readyState === WebSocket.OPEN) {
          privateWs.value.send(JSON.stringify(payload))
        } else {
          console.error('Private WebSocket not open for reaction')
        }
      } else if (selectedConversation.value?.type === 'group') {
        if (groupWs.value?.readyState === WebSocket.OPEN) {
          groupWs.value.send(JSON.stringify(payload))
        } else {
          console.error('Group WebSocket not open for reaction')
        }
      }
    } catch (error) {
      console.error('Error sending reaction:', error)
    }
  }
  
  /**
   * Handle message action from child components
   */
  async function handleMessageAction(actionData) {
    try {
      // Handle both call signatures: object or individual params
      const { action, message, newContent } = typeof actionData === 'object' && actionData.action
        ? actionData
        : { action: actionData, message: arguments[1], newContent: arguments[2]?.newContent }
      
      console.log('Handling message action:', action, 'for message:', message?.id)
      
      if (!message) {
        console.error('Message is undefined for action:', action)
        alert('Failed to perform action: Message is missing.')
        return
      }
      
      switch (action) {
        case 'edit':
          if (!newContent) {
            console.error('New content is required for edit action')
            return
          }
          await editMessage(message, newContent)
          break
          
        case 'delete':
          await deleteMessage(message)
          break
          
        case 'reaction_added':
        case 'reaction_updated':
        case 'reaction_removed':
          console.log('Handling reaction update for message:', message.id)
          break
          
        case 'select':
          console.log('Selected message:', message.id)
          break
          
        default:
          console.warn('Unknown message action:', action)
      }
    } catch (error) {
      console.error('Error handling message action:', error)
      alert('An error occurred while performing the action.')
    }
  }
  
  /**
   * Handle immediate message read feedback
   */
  function handleMessageRead(data) {
    console.log('📖 Handling immediate message read feedback:', data)
    
    const { messageId, readBy } = data
    
    const messageIndex = messages.value.findIndex(m => m.id === messageId)
    if (messageIndex !== -1) {
      const message = messages.value[messageIndex]
      
      const updatedMessage = {
        ...message,
        read_by: readBy || message.read_by
      }
      
      messages.value[messageIndex] = updatedMessage
      
      nextTick(() => {
        messages.value = [...messages.value]
        console.log('✅ Immediate read feedback: Updated message read status')
      })
    }
  }
  
  return {
    // State
    uploadProgress,
    
    // Functions
    sendMessage,
    editMessage,
    deleteMessage,
    sendReaction,
    uploadAttachments,
    handleMessageAction,
    handleMessageRead
  }
}
