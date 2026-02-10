/**
 * Messaging WebSocket Management Composable
 * Manages privateWs, groupWs, and notificationWs connections with heartbeat
 */
import { ref, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getWebSocketBaseURL } from '@/utils/imageUrl'

const isDev = import.meta.env.DEV
const debugLog = isDev ? console.log : () => {}
const debugError = console.error

export function useMessagingSockets() {
  const authStore = useAuthStore()
  
  // WebSocket refs
  const privateWs = ref(null)
  const groupWs = ref(null)
  const notificationWs = ref(null)
  
  // Heartbeat tracking
  let heartbeatInterval = null
  const heartbeatIntervals = new Set()
  const connectionStates = new Map()
  
  /**
   * Start heartbeat for a single WebSocket
   */
  function startHeartbeat(ws) {
    stopHeartbeat()
    heartbeatInterval = setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        debugLog('Sending heartbeat ping')
        ws.send(JSON.stringify({ action: 'ping' }))
      }
    }, 30000)
  }
  
  /**
   * Start typed heartbeat for specific WebSocket type
   */
  function startTypedHeartbeat(ws, wsType) {
    const intervalId = setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: 'ping' }))
        connectionStates.set(wsType, 'healthy')
      } else {
        connectionStates.set(wsType, 'disconnected')
        debugLog(`${wsType} WebSocket disconnected, stopping heartbeat`)
        clearInterval(intervalId)
        heartbeatIntervals.delete(intervalId)
      }
    }, 30000)
    
    heartbeatIntervals.add(intervalId)
    connectionStates.set(wsType, 'connected')
    debugLog(`Heartbeat setup for ${wsType} WebSocket`)
    return intervalId
  }
  
  /**
   * Stop single heartbeat
   */
  function stopHeartbeat() {
    if (heartbeatInterval) {
      clearInterval(heartbeatInterval)
      heartbeatInterval = null
    }
  }
  
  /**
   * Stop all heartbeats
   */
  function stopAllHeartbeats() {
    stopHeartbeat()
    heartbeatIntervals.forEach(intervalId => clearInterval(intervalId))
    heartbeatIntervals.clear()
    connectionStates.clear()
  }
  
  /**
   * Setup private WebSocket connection
   */
  function setupPrivateWebSocket(onMessage) {
    if (!authStore.token) {
      console.error('Cannot setup private WebSocket: No token')
      return
    }
    
    const token = authStore.token
    const wsBaseUrl = getWebSocketBaseURL()
    privateWs.value = new WebSocket(`${wsBaseUrl}/ws/private/?token=${token}`)
    
    privateWs.value.onopen = () => {
      console.log('Private WS connected')
      startHeartbeat(privateWs.value)
    }
    
    privateWs.value.onclose = () => {
      console.log('Private WS closed')
      stopHeartbeat()
    }
    
    privateWs.value.onerror = (error) => {
      console.error('Private WS error:', error)
      stopHeartbeat()
    }
    
    privateWs.value.onmessage = (e) => {
      const data = JSON.parse(e.data)
      
      // Handle pong
      if (data.action === 'pong') {
        debugLog('Received pong from server')
        return
      }
      
      console.log('🔵 Private WS RECEIVED:', data)
      
      // Special logging for important events
      if (data.type === 'message_read_update') {
        console.log('👁️ Message read update:', data.message_id)
      }
      if (data.type === 'message_edited') {
        console.log('🔴 Message edited:', data.message_id)
      }
      
      if (onMessage) onMessage(data, 'private')
    }
  }
  
  /**
   * Setup group WebSocket connection
   */
  function setupGroupWebSocket(groupId, onMessage) {
    if (!groupId) {
      console.error('Cannot setup group WebSocket: No group ID')
      return
    }
    
    if (groupWs.value) {
      groupWs.value.close()
    }
    
    const token = authStore.token
    const wsBaseUrl = getWebSocketBaseURL()
    groupWs.value = new WebSocket(`${wsBaseUrl}/ws/group/${groupId}/?token=${token}`)
    
    groupWs.value.onopen = () => {
      console.log('Group WS connected')
      startTypedHeartbeat(groupWs.value, 'group')
    }
    
    groupWs.value.onclose = () => {
      console.log('Group WS closed')
    }
    
    groupWs.value.onerror = (error) => {
      console.error('Group WS error:', error)
    }
    
    groupWs.value.onmessage = (e) => {
      const data = JSON.parse(e.data)
      
      if (data.action === 'pong') {
        debugLog('Group WS pong received')
        return
      }
      
      console.log('🟢 Group WS RECEIVED:', data)
      if (onMessage) onMessage(data, 'group')
    }
  }
  
  /**
   * Setup notification WebSocket connection
   */
  function setupNotificationWebSocket(onMessage) {
    if (!authStore.token) {
      console.error('Cannot setup notification WebSocket: No token')
      return
    }
    
    const token = authStore.token
    const wsBaseUrl = getWebSocketBaseURL()
    notificationWs.value = new WebSocket(`${wsBaseUrl}/ws/notifications/?token=${token}`)
    
    notificationWs.value.onopen = () => {
      console.log('🔔 Notification WS connected')
    }
    
    notificationWs.value.onclose = () => {
      console.log('🔔 Notification WS closed')
    }
    
    notificationWs.value.onerror = (error) => {
      console.error('🔔 Notification WS error:', error)
    }
    
    notificationWs.value.onmessage = (e) => {
      const data = JSON.parse(e.data)
      console.log('🔔 Notification WS RECEIVED:', data)
      if (onMessage) onMessage(data, 'notification')
    }
  }
  
  /**
   * Send message through WebSocket
   */
  function sendWsMessage(wsType, payload) {
    const ws = wsType === 'private' ? privateWs.value : 
                wsType === 'group' ? groupWs.value : 
                notificationWs.value
    
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(payload))
      return true
    } else {
      console.error(`Cannot send ${wsType} WS message: Connection not open`)
      return false
    }
  }
  
  /**
   * Close all WebSocket connections
   */
  function closeAllConnections() {
    stopAllHeartbeats()
    
    if (privateWs.value) {
      privateWs.value.close()
      privateWs.value = null
    }
    if (groupWs.value) {
      groupWs.value.close()
      groupWs.value = null
    }
    if (notificationWs.value) {
      notificationWs.value.close()
      notificationWs.value = null
    }
    
    debugLog('All WebSocket connections closed')
  }
  
  // Cleanup on unmount
  onUnmounted(() => {
    closeAllConnections()
  })
  
  return {
    // Refs
    privateWs,
    groupWs,
    notificationWs,
    
    // Setup functions
    setupPrivateWebSocket,
    setupGroupWebSocket,
    setupNotificationWebSocket,
    
    // Heartbeat functions
    startHeartbeat,
    startTypedHeartbeat,
    stopHeartbeat,
    stopAllHeartbeats,
    
    // Utility functions
    sendWsMessage,
    closeAllConnections,
    
    // State tracking
    connectionStates
  }
}
