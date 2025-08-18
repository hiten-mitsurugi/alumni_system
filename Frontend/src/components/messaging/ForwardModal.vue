<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-96 max-h-[80vh] flex flex-col">
      <!-- Header -->
      <div class="p-4 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-900">Forward Message</h3>
        <button 
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Message Preview -->
      <div class="p-4 border-b border-gray-200 bg-gray-50">
        <div class="text-sm text-gray-600 mb-2">Forwarding message from:</div>
        <div class="bg-white p-3 rounded-lg border">
          <div class="flex items-center gap-2 mb-2">
            <img 
              :src="message.sender.profile_picture || '/default-avatar.png'" 
              alt="Sender" 
              class="w-6 h-6 rounded-full object-cover"
            />
            <span class="text-sm font-medium">{{ message.sender.first_name }} {{ message.sender.last_name }}</span>
          </div>
          <div class="text-sm text-gray-800 truncate">{{ message.content }}</div>
          <div v-if="message.attachments && message.attachments.length > 0" class="text-xs text-gray-500 mt-1">
            📎 {{ message.attachments.length }} attachment(s)
          </div>
        </div>
      </div>

      <!-- Search Bar -->
      <div class="p-4 border-b border-gray-200">
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search conversations..."
            class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <svg class="absolute left-3 top-2.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      <!-- Conversation List -->
      <div class="flex-1 overflow-y-auto">
        <div v-if="loading" class="p-4 text-center text-gray-500">
          Loading conversations...
        </div>
        <div v-else-if="filteredConversations.length === 0" class="p-4 text-center text-gray-500">
          No conversations found
        </div>
        <div v-else class="p-2">
          <div 
            v-for="conversation in filteredConversations" 
            :key="conversation.id"
            @click="toggleSelection(conversation)"
            class="flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors hover:bg-gray-50"
            :class="{ 'bg-blue-50 border border-blue-200': isSelected(conversation) }"
          >
            <!-- Checkbox -->
            <div 
              class="w-5 h-5 rounded border-2 flex items-center justify-center transition-colors"
              :class="isSelected(conversation) ? 'bg-blue-500 border-blue-500' : 'border-gray-300'"
            >
              <svg v-if="isSelected(conversation)" class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </div>

            <!-- Avatar -->
            <img 
              :src="getConversationAvatar(conversation)" 
              alt="Avatar" 
              class="w-10 h-10 rounded-full object-cover"
            />

            <!-- Info -->
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <span class="font-medium text-gray-900">{{ getConversationName(conversation) }}</span>
                <!-- Group or Private indicator -->
                <span 
                  class="text-xs px-2 py-0.5 rounded-full text-white font-medium"
                  :class="conversation.type === 'group' ? 'bg-blue-500' : 'bg-green-500'"
                >
                  {{ conversation.type === 'group' ? 'Group' : 'Private' }}
                </span>
              </div>
              <div class="text-sm text-gray-500">
                {{ getConversationDescription(conversation) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="p-4 border-t border-gray-200 flex justify-between items-center">
        <div class="text-sm text-gray-600">
          {{ selectedConversations.length }} conversation(s) selected
        </div>
        <div class="flex gap-2">
          <button 
            @click="$emit('close')"
            class="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button 
            @click="forwardMessage"
            :disabled="selectedConversations.length === 0 || forwarding"
            class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ forwarding ? 'Forwarding...' : 'Forward' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  message: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'forward'])

const authStore = useAuthStore()
const searchQuery = ref('')
const conversations = ref([])
const selectedConversations = ref([])
const loading = ref(true)
const forwarding = ref(false)

const filteredConversations = computed(() => {
  if (!searchQuery.value.trim()) {
    return conversations.value
  }
  
  const query = searchQuery.value.toLowerCase().trim()
  return conversations.value.filter(conv => {
    const name = getConversationName(conv).toLowerCase()
    
    // For private conversations, also search by username
    if (conv.type === 'private' && conv.mate) {
      const username = conv.mate.username ? conv.mate.username.toLowerCase() : ''
      const firstName = conv.mate.first_name ? conv.mate.first_name.toLowerCase() : ''
      const lastName = conv.mate.last_name ? conv.mate.last_name.toLowerCase() : ''
      
      return name.includes(query) || 
             username.includes(query) || 
             firstName.includes(query) || 
             lastName.includes(query)
    }
    
    // For group conversations, search by group name
    if (conv.type === 'group' && conv.group) {
      const groupName = conv.group.name ? conv.group.name.toLowerCase() : ''
      return groupName.includes(query)
    }
    
    return name.includes(query)
  })
})

function getConversationAvatar(conversation) {
  if (conversation.type === 'private') {
    return conversation.mate?.profile_picture || '/default-avatar.png'
  } else if (conversation.type === 'group') {
    return conversation.group?.group_picture || '/default-avatar.png'
  }
  return '/default-avatar.png'
}

function getConversationName(conversation) {
  if (conversation.type === 'private') {
    const mate = conversation.mate
    if (mate) {
      const firstName = mate.first_name || ''
      const lastName = mate.last_name || ''
      const fullName = `${firstName} ${lastName}`.trim()
      return fullName || mate.username || 'Unknown User'
    }
    return 'Unknown User'
  } else if (conversation.type === 'group') {
    return conversation.group?.name || 'Unnamed Group'
  }
  return 'Unknown Conversation'
}

function getConversationType(conversation) {
  return conversation.type === 'private' ? 'Private chat' : 'Group chat'
}

function getConversationDescription(conversation) {
  if (conversation.type === 'group') {
    const memberCount = conversation.members ? conversation.members.length : 0;
    return `${memberCount} members`;
  } else {
    // For private chat, show if the other user is online/offline if available
    const otherMember = conversation.members?.find(m => m.id !== currentUser.value.id);
    return otherMember ? `@${otherMember.username}` : 'Private chat';
  }
}

function isSelected(conversation) {
  return selectedConversations.value.some(selected => {
    if (conversation.type === 'private' && selected.type === 'private') {
      return selected.mate?.id === conversation.mate?.id
    } else if (conversation.type === 'group' && selected.type === 'group') {
      return selected.group?.id === conversation.group?.id
    }
    return false
  })
}

function toggleSelection(conversation) {
  const index = selectedConversations.value.findIndex(selected => {
    if (conversation.type === 'private' && selected.type === 'private') {
      return selected.mate?.id === conversation.mate?.id
    } else if (conversation.type === 'group' && selected.type === 'group') {
      return selected.group?.id === conversation.group?.id
    }
    return false
  })
  
  if (index === -1) {
    selectedConversations.value.push(conversation)
    console.log('ForwardModal: Selected conversation:', conversation)
  } else {
    selectedConversations.value.splice(index, 1)
    console.log('ForwardModal: Deselected conversation:', conversation)
  }
  
  console.log('ForwardModal: Currently selected conversations:', selectedConversations.value)
}

async function loadConversations() {
  try {
    loading.value = true
    const token = authStore.token

    // Fetch private conversations and group chats in parallel
    const [privateRes, groupRes] = await Promise.all([
      fetch('http://localhost:8000/api/message/conversations/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }),
      fetch('http://localhost:8000/api/message/group/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
    ])

    const privateData = privateRes.ok ? await privateRes.json() : []
    const groupData = groupRes.ok ? await groupRes.json() : []

    // Normalize private conversations and ensure a stable id
    const privateConversations = (privateData || []).map(conv => ({
      // Use mate.id as the unique key for private conversations
      id: conv?.mate?.id ? `private-${conv.mate.id}` : `private-${Math.random().toString(36).slice(2)}`,
      type: 'private',
      ...conv
    }))

    // Map groups into conversation-like objects and ensure a stable id
    const groupConversations = (groupData || []).map(group => ({
      id: `group-${group.id}`,
      type: 'group',
      group,
      // Expose members at the top level for existing helpers (e.g., description)
      members: group.members
    }))

    const merged = [...privateConversations, ...groupConversations]

    console.log('ForwardModal: Loaded private conversations:', privateConversations)
    console.log('ForwardModal: Loaded group conversations:', groupConversations)

    conversations.value = merged
  } catch (error) {
    console.error('Error loading conversations:', error)
  } finally {
    loading.value = false
  }
}

async function forwardMessage() {
  try {
    forwarding.value = true
    
    // Prepare destinations array
    const destinations = selectedConversations.value.map(conv => {
      if (conv.type === 'private') {
        return {
          type: 'private',
          id: conv.mate.id
        }
      } else if (conv.type === 'group') {
        return {
          type: 'group',
          id: conv.group.id
        }
      }
    }).filter(dest => dest !== undefined) // Filter out any undefined entries
    
    console.log('ForwardModal: Prepared destinations:', destinations)
    
    const token = authStore.token
    const response = await fetch('http://localhost:8000/api/message/forward/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message_id: props.message.id,
        destinations: destinations
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      console.log('ForwardModal: Forward successful:', result)
      emit('forward', {
        success: true,
        message: result.status,
        count: result.forwarded_count
      })
    } else {
      const errorText = await response.text()
      console.error('ForwardModal: Forward failed:', response.status, errorText)
      
      let errorMessage = 'Failed to forward message'
      try {
        const errorData = JSON.parse(errorText)
        errorMessage = errorData.error || errorMessage
      } catch (e) {
        // If not JSON, use the text as is or fallback message
        errorMessage = errorText || errorMessage
      }
      
      emit('forward', {
        success: false,
        message: errorMessage
      })
    }
  } catch (error) {
    console.error('Error forwarding message:', error)
    emit('forward', {
      success: false,
      message: 'Network error occurred'
    })
  } finally {
    forwarding.value = false
  }
}

onMounted(() => {
  loadConversations()
})
</script>

<style scoped>
/* Additional styles if needed */
</style>
