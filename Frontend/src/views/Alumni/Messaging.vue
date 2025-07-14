<template>
  <div class="h-[calc(100vh-120px)] flex bg-white rounded-lg shadow-sm overflow-hidden">
    <!-- Conversations Panel -->
    <div class="w-96 border-r border-gray-200 flex flex-col bg-gray-50">
      <!-- Header with Search and Actions -->
      <div class="p-4 bg-white border-b border-gray-200">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-800">Messages</h2>
          <div class="flex gap-2">
            <!-- Pending Messages Button -->
            <button
              @click="showPendingMessages = true"
              class="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200"
              title="Pending Messages"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              <span v-if="pendingMessages.length > 0" class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {{ pendingMessages.length }}
              </span>
            </button>
            
            <!-- Create Group Button -->
            <button
              @click="showCreateGroup = true"
              class="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-all duration-200"
              title="Create Group"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.196-2.121M17 20H7m10 0v-2c0-5.523-3.582-10-8-10s-8 4.477-8 10v2m8-10a3 3 0 110-6 3 3 0 010 6zm0 10a3 3 0 110-6 3 3 0 010 6z" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Search Bar -->
        <div class="relative">
          <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search mates..."
            class="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:bg-white transition-all duration-200"
          />
        </div>
      </div>

      <!-- Conversations List -->
      <div class="flex-1 overflow-y-auto">
        <div
          v-for="conversation in filteredConversations"
          :key="conversation.id"
          @click="selectConversation(conversation)"
          :class="[
            'flex items-center p-4 cursor-pointer border-b border-gray-100 transition-all duration-200 hover:bg-white',
            selectedConversation?.id === conversation.id 
              ? 'bg-white border-r-4 border-green-500 shadow-sm' 
              : 'hover:shadow-sm'
          ]"
        >
          <!-- Avatar with Status -->
          <div class="relative flex-shrink-0 mr-4">
            <img
              :src="conversation.type === 'private' ? conversation.mate.avatar : conversation.group.avatar"
              :alt="conversation.type === 'private' ? conversation.mate.name : conversation.group.name"
              class="w-14 h-14 rounded-full object-cover border-2 border-white shadow-sm"
            />
            <!-- Online Status for Private Chats -->
            <div
              v-if="conversation.type === 'private'"
              :class="[
                'absolute bottom-0 right-0 w-4 h-4 rounded-full border-2 border-white',
                getStatusColor(conversation.mate.status)
              ]"
            />
            <!-- Group Member Count -->
            <div
              v-if="conversation.type === 'group'"
              class="absolute -bottom-1 -right-1 bg-green-600 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center font-medium"
            >
              {{ conversation.group.memberCount }}
            </div>
          </div>

          <!-- Conversation Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between mb-1">
              <h3 class="font-semibold text-gray-900 truncate text-lg">
                {{ conversation.type === 'private' ? conversation.mate.name : conversation.group.name }}
              </h3>
              <div class="flex items-center gap-2">
                <!-- Muted Icon -->
                <svg
                  v-if="conversation.isMuted"
                  class="w-4 h-4 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
                </svg>
                <!-- Timestamp -->
                <span class="text-xs text-gray-500 font-medium">{{ conversation.timestamp }}</span>
              </div>
            </div>
            
            <div class="flex items-center justify-between">
              <p class="text-sm text-gray-600 truncate pr-2">{{ conversation.lastMessage }}</p>
              <!-- Unread Count -->
              <span
                v-if="conversation.unreadCount > 0"
                class="bg-green-500 text-white text-xs rounded-full px-2 py-1 min-w-[24px] text-center font-medium"
              >
                {{ conversation.unreadCount }}
              </span>
            </div>
          </div>
        </div>

        <!-- Empty State for No Conversations -->
        <div v-if="filteredConversations.length === 0" class="text-center py-12 px-4">
          <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <p class="text-gray-500">No conversations found</p>
          <p class="text-sm text-gray-400 mt-1">Try adjusting your search</p>
        </div>
      </div>
    </div>

    <!-- Chat Area -->
    <div class="flex-1 flex flex-col">
      <ChatArea 
        v-if="selectedConversation"
        :conversation="selectedConversation"
        :messages="messages"
        :current-user="currentUser"
        @send-message="sendMessage"
        @toggle-mute="toggleMute"
        @toggle-block="toggleBlock"
      />
      <EmptyState v-else />
    </div>

    <!-- Modals -->
    <PendingMessagesModal
      v-if="showPendingMessages"
      :pending-messages="pendingMessages"
      @close="showPendingMessages = false"
      @accept="acceptPendingMessage"
      @reject="rejectPendingMessage"
    />

    <CreateGroupModal
      v-if="showCreateGroup"
      :available-mates="availableMates"
      @close="showCreateGroup = false"
      @create-group="createGroup"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import ChatArea from '../../components/messaging/ChatArea.vue'
import EmptyState from '../../components/messaging/EmptyState.vue'
import PendingMessagesModal from '../../components/messaging/PendingMessagesModal.vue'
import CreateGroupModal from '../../components/messaging/CreateGroupModal.vue'

// Reactive data
const selectedConversation = ref(null)
const conversations = ref([])
const messages = ref([])
const showPendingMessages = ref(false)
const showCreateGroup = ref(false)
const searchQuery = ref('')
const currentUser = ref({ id: 1, name: 'You' })

// Mock data
const mockConversations = [
  {
    id: 1,
    type: 'private',
    mate: {
      id: 2,
      name: 'Alice Johnson',
      avatar: '/placeholder.svg?height=56&width=56',
      status: 'online'
    },
    lastMessage: 'Hey! How are you doing?',
    timestamp: '2 min ago',
    unreadCount: 3,
    isMuted: false,
    isBlocked: false
  },
  {
    id: 2,
    type: 'group',
    group: {
      id: 1,
      name: 'Class of 2020',
      avatar: '/placeholder.svg?height=56&width=56',
      memberCount: 25
    },
    lastMessage: 'Meeting tomorrow at 3 PM',
    timestamp: '1 hour ago',
    unreadCount: 5,
    isMuted: false
  },
  {
    id: 3,
    type: 'private',
    mate: {
      id: 3,
      name: 'Bob Smith',
      avatar: '/placeholder.svg?height=56&width=56',
      status: 'away'
    },
    lastMessage: 'Thanks for the help!',
    timestamp: '1 day ago',
    unreadCount: 0,
    isMuted: false,
    isBlocked: false
  }
]

const mockMessages = {
  1: [
    {
      id: 1,
      content: 'Looking forward to it!',
      senderId: 2,
      timestamp: '10:30 AM',
      isRead: true,
      attachments: [],
      reactions: []
    },
    {
      id: 2,
      content: '', // Empty content for attachment-only message
      senderId: 1,
      timestamp: '10:32 AM',
      isRead: true,
      attachments: [
        { name: '3 (1).pdf', size: 150000, type: 'application/pdf', url: null }
      ],
      reactions: []
    },
    {
      id: 3,
      content: '', // Empty content for image-only message
      senderId: 1,
      timestamp: '10:35 AM',
      isRead: false,
      attachments: [
        { name: 'profpic.jpg', size: 500000, type: 'image/jpeg', url: 'https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Screenshot%202025-07-14%20161348-ezsJVJWP84zNkFscZrqHds3JxtD3Bg.png' } // Using your provided image URL
      ],
      reactions: []
    }
  ]
}

const pendingMessages = ref([
  {
    id: 1,
    name: 'David Brown',
    avatar: '/placeholder.svg?height=40&width=40',
    message: 'Hi! I saw we were in the same graduating class.',
    timestamp: '2 hours ago'
  },
  {
    id: 2,
    name: 'Emma Davis',
    avatar: '/placeholder.svg?height=40&width=40',
    message: 'Hello, would love to reconnect!',
    timestamp: '1 day ago'
  }
])

const availableMates = ref([
  {
    id: 2,
    name: 'Alice Johnson',
    avatar: '/placeholder.svg?height=40&width=40',
    status: 'online',
    graduationYear: '2020'
  },
  {
    id: 3,
    name: 'Bob Smith',
    avatar: '/placeholder.svg?height=40&width=40',
    status: 'away',
    graduationYear: '2019'
  }
])

// Computed
const filteredConversations = computed(() => {
  if (!searchQuery.value) return conversations.value
  
  return conversations.value.filter(conv => {
    const name = conv.type === 'private' 
      ? conv.mate.name.toLowerCase()
      : conv.group.name.toLowerCase()
    return name.includes(searchQuery.value.toLowerCase())
  })
})

// Methods
const selectConversation = (conversation) => {
  selectedConversation.value = conversation
  messages.value = mockMessages[conversation.id] || []
}

const sendMessage = (messageData) => {
  if (!selectedConversation.value) return;

  // If there's text content, add it as a separate message
  if (messageData.content.trim()) {
    const newTextMessage = {
      id: Date.now(),
      content: messageData.content.trim(),
      senderId: currentUser.value.id,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isRead: false,
      attachments: [],
      reactions: []
    };
    messages.value.push(newTextMessage);
  }

  // If there are attachments, add each as a separate message
  messageData.attachments.forEach((attachment, index) => {
    const newAttachmentMessage = {
      id: Date.now() + index, // Ensure unique ID for each attachment message
      content: '', // No text content for attachment messages
      senderId: currentUser.value.id,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isRead: false,
      attachments: [{
        name: attachment.name,
        size: attachment.size,
        type: attachment.type,
        url: attachment.url // This will be the previewUrl from MessageInput for new attachments
      }],
      reactions: []
    };
    messages.value.push(newAttachmentMessage);
  });

  // Update last message in conversation
  const conv = conversations.value.find(c => c.id === selectedConversation.value.id);
  if (conv) {
    if (messageData.content.trim() && messageData.attachments.length > 0) {
      conv.lastMessage = `Text + ${messageData.attachments.length} attachment(s)`;
    } else if (messageData.content.trim()) {
      conv.lastMessage = messageData.content.trim();
    } else if (messageData.attachments.length > 0) {
      conv.lastMessage = `Sent ${messageData.attachments.length} attachment(s)`;
    }
    conv.timestamp = 'now';
  }
};

const toggleMute = () => {
  if (selectedConversation.value) {
    selectedConversation.value.isMuted = !selectedConversation.value.isMuted
  }
}

const toggleBlock = () => {
  if (selectedConversation.value && selectedConversation.value.type === 'private') {
    selectedConversation.value.isBlocked = !selectedConversation.value.isBlocked
  }
}

const acceptPendingMessage = (messageId) => {
  pendingMessages.value = pendingMessages.value.filter(msg => msg.id !== messageId)
}

const rejectPendingMessage = (messageId) => {
  pendingMessages.value = pendingMessages.value.filter(msg => msg.id !== messageId)
}

const createGroup = (groupData) => {
  const newGroup = {
    id: Date.now(),
    type: 'group',
    group: {
      id: Date.now(),
      name: groupData.name,
      avatar: '/placeholder.svg?height=56&width=56',
      memberCount: groupData.members.length + 1
    },
    lastMessage: 'Group created',
    timestamp: 'now',
    unreadCount: 0,
    isMuted: false
  }
  
  conversations.value.unshift(newGroup)
  showCreateGroup.value = false
  selectConversation(newGroup)
}

const getStatusColor = (status) => {
  switch (status) {
    case 'online': return 'bg-green-500'
    case 'away': return 'bg-yellow-500'
    case 'busy': return 'bg-red-500'
    default: return 'bg-gray-400'
  }
}

onMounted(() => {
  conversations.value = mockConversations
})
</script>
