<template>
  <!-- Template remains unchanged -->
  <div class="h-[calc(100vh-120px)] flex bg-white rounded-lg shadow-sm overflow-hidden">
    <!-- Conversations Panel -->
    <div class="w-96 border-r border-gray-200 flex flex-col bg-gray-50">
      <div class="p-4 bg-white border-b border-gray-200">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-800">Messages</h2>
          <div class="flex gap-2">
            <button @click="showPendingMessages = true"
              class="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200"
              title="Pending Messages">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              <span v-if="pendingMessages.length > 0"
                class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {{ pendingMessages.length }}
              </span>
            </button>
            <button @click="showCreateGroup = true"
              class="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-all duration-200"
              title="Create Group">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M17 20h5v-2a3 3 0 00-5.196-2.121M17 20H7m10 0v-2c0-5.523-3.582-10-8-10s-8 4.477-8 10v2m8-10a3 3 0 110-6 3 3 0 010 6zm0 10a3 3 0 110-6 3 3 0 010 6z" />
              </svg>
            </button>
          </div>
        </div>
        <div class="relative">
          <svg @click="focusSearch"
            class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 cursor-pointer" fill="none"
            stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input ref="searchInput" v-model="searchQuery" @input="debouncedSearch" type="text"
            placeholder="Search mates or groups..."
            class="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:bg-white transition-all duration-200" />
          <div v-if="searchQuery && searchResults.length"
            class="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-96 overflow-y-auto">
            <div v-for="result in searchResults" :key="result.id" @click="selectSearchResult(result)"
              class="flex items-center p-3 hover:bg-gray-50 cursor-pointer">
              <img :src="getProfilePictureUrl(result)" class="w-10 h-10 rounded-full object-cover" />

              <div>
                <p class="font-semibold text-gray-800">{{ result.type === 'user' ? `${result.first_name}
                  ${result.last_name}` : result.name }}</p>
                <p class="text-sm text-gray-500">{{ result.type === 'user' ? result.username : 'Group' }}</p>
              </div>
            </div>
            <div v-if="searchQuery && searchResults.length === 0" class="p-3 text-gray-500">No results found</div>
          </div>
        </div>
      </div>
      <div class="flex-1 overflow-y-auto">
        <div v-for="conversation in filteredConversations" :key="conversation.id"
          @click="selectConversation(conversation)"
          :class="['flex items-center p-4 cursor-pointer border-b border-gray-100 transition-all duration-200 hover:bg-white', selectedConversation?.id === conversation.id ? 'bg-white border-r-4 border-green-500 shadow-sm' : 'hover:shadow-sm']">
          <div v-if="conversation.type === 'private'" class="relative flex-shrink-0 mr-4">
            <img :src="getProfilePictureUrl(conversation.mate)" class="w-10 h-10 rounded-full object-cover" />
            <div
              :class="['absolute bottom-0 right-0 w-4 h-4 rounded-full border-2 border-white', getStatusColor(conversation.mate.profile?.status)]" />
          </div>

          <div v-else class="relative flex-shrink-0 mr-4">
            <img :src="conversation.group.group_picture || '/default-group.png'" alt="Group Avatar"
              class="w-14 h-14 rounded-full object-cover border-2 border-white shadow-sm" />
            <div
              class="absolute -bottom-1 -right-1 bg-green-600 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center font-medium">
              {{ conversation.group.members.length }}</div>
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between mb-1">
              <h3 class="font-semibold text-gray-900 truncate text-lg">{{ conversation.type === 'private' ?
                `${conversation.mate.first_name} ${conversation.mate.last_name}` : conversation.group.name }}</h3>
              <div class="flex items-center gap-2">
                <svg v-if="conversation.isMuted" class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor"
                  viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
                </svg>
                <span class="text-xs text-gray-500 font-medium">{{ formatTimestamp(conversation.timestamp) }}</span>
              </div>
            </div>
            <div class="flex items-center justify-between">
              <p class="text-sm text-gray-600 truncate pr-2">{{ conversation.lastMessage }}</p>
              <span v-if="conversation.unreadCount > 0"
                class="bg-green-500 text-white text-xs rounded-full px-2 py-1 min-w-[24px] text-center font-medium">{{
                  conversation.unreadCount }}</span>
            </div>
          </div>
        </div>
        <div v-if="filteredConversations.length === 0 && !searchQuery" class="text-center py-12 px-4">
          <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <p class="text-gray-500">No conversations found</p>
        </div>
      </div>
    </div>
    <div class="flex-1 flex flex-col">
      <ChatArea v-if="selectedConversation" :conversation="selectedConversation" :messages="messages"
        :current-user="currentUser" @send-message="sendMessage" />
      <EmptyState v-else />
    </div>
    <PendingMessagesModal v-if="showPendingMessages" :pending-messages="pendingMessages"
      @close="showPendingMessages = false" @accept="acceptPendingMessage" @reject="rejectPendingMessage" />
    <CreateGroupModal v-if="showCreateGroup" :available-mates="availableMates" @close="showCreateGroup = false"
      @create-group="createGroup" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import debounce from 'lodash/debounce';
import { useAuthStore } from '@/stores/auth';
import api from '../../services/api';
import ChatArea from '../../components/messaging/ChatArea.vue';
import EmptyState from '../../components/messaging/EmptyState.vue';
import PendingMessagesModal from '../../components/messaging/PendingMessagesModal.vue';
import CreateGroupModal from '../../components/messaging/CreateGroupModal.vue';

// === STATE ===
const authStore = useAuthStore();
const isAuthenticated = ref(false);
const currentUser = ref(null);
const conversations = ref([]);
const selectedConversation = ref(null);
const messages = ref([]);
const pendingMessages = ref([]);
const availableMates = ref([]);

const showPendingMessages = ref(false);
const showCreateGroup = ref(false);
const searchQuery = ref('');
const searchResults = ref([]);
const searchInput = ref(null);

const privateWs = ref(null);
const groupWs = ref(null);

// === Helper to always return correct avatar URL for user/group
const getProfilePictureUrl = (entity) => {
  return (
    entity?.profile_picture ||              // direct CustomUser profile_picture
    entity?.profile?.profile_picture ||     // nested Profile model
    entity?.group_picture ||                // group chat avatar
    '/default-avatar.png'                   // fallback
  );
};

// === COMPUTED ===
const filteredConversations = computed(() => {
  if (!searchQuery.value) return conversations.value;
  return conversations.value.filter(conv => {
    const name = conv.type === 'private'
      ? `${conv.mate.first_name} ${conv.mate.last_name}`
      : conv.group.name;
    return name.toLowerCase().includes(searchQuery.value.toLowerCase());
  });
});

// === AUTH & TOKEN ===
async function validateToken() {
  if (!authStore.token) return (isAuthenticated.value = false);
  try {
    await api.get('/user/');
    return (isAuthenticated.value = true);
  } catch (error) {
    if ([401, 403].includes(error.response?.status) && await authStore.tryRefreshToken()) {
      return (isAuthenticated.value = true);
    }
    isAuthenticated.value = false;
  }
}

async function refreshToken() {
  try {
    if (!authStore.refreshToken) return null;
    const { data } = await api.post('/token/refresh/');
    authStore.setToken(data.access, authStore.refreshToken);
    return data.access;
  } catch (e) {
    authStore.logout();
    return null;
  }
}

const getValidToken = async () => authStore.token || await refreshToken();

// === FETCH DATA ===
const fetchCurrentUser = async () => {
  try { currentUser.value = (await api.get('/user/')).data; } catch (e) { console.error('User fetch error', e); }
};

const fetchConversations = async () => {
  try {
    const { data } = await api.get('/message/conversations/');
    conversations.value = (Array.isArray(data) ? data : []).map(conv => ({
      ...conv,
      id: conv.id || (conv.type === 'private' ? conv.mate.id : conv.group.id)
    }));
  } catch (e) { console.error('Conv fetch error', e); }
};

const fetchMessages = async conv => {
  try {
    const url = conv.type === 'private'
      ? `/message/private/${conv.mate.id}/`
      : `/message/group/${conv.group.id}/`;
    messages.value = (await api.get(url)).data;
  } catch (e) { console.error('Msg fetch error', e); }
};

const fetchPendingMessages = async () => {
  try {
    const { data } = await api.get('/message/requests/');
    pendingMessages.value = (data || []).map(req => ({
      id: req.id,
      name: `${req.sender.first_name} ${req.sender.last_name}`,
      avatar: getProfilePictureUrl(req.sender),
      message: 'Message request',
      timestamp: req.timestamp
    }));
  } catch (e) { console.error('Pending fetch error', e); }
};

const fetchAvailableMates = async () => {
  try {
    const { data } = await api.get('/message/search/');
    availableMates.value = (Array.isArray(data.users) ? data.users : []).map(u => ({
      ...u,
      profile_picture: getProfilePictureUrl(u)
    }));
  } catch (e) { console.error('Mates fetch error', e); }
};

// === SEARCH ===
async function search() {
  if (!searchQuery.value) return (searchResults.value = []);
  try {
    const { data } = await api.get(`/message/search/?q=${encodeURIComponent(searchQuery.value)}`);
    const users = (data.users || []).map(u => ({
      type: 'user',
      ...u,
      profile_picture: getProfilePictureUrl(u)
    }));
    const groups = (data.groups || []).map(g => ({ type: 'group', ...g }));
    searchResults.value = [...users, ...groups];
  } catch (e) { searchResults.value = []; }
}
const debouncedSearch = debounce(search, 300);

const focusSearch = () => searchQuery.value ? (searchQuery.value = searchResults.value = '') : searchInput.value?.focus();

// === CONVERSATION HANDLERS ===
async function selectSearchResult(r) {
  if (r.type === 'user') {
    let conv = conversations.value.find(c => c.type === 'private' && c.mate.id === r.id);
    if (!conv) {
      conv = { type: 'private', id: r.id, mate: r, lastMessage: '', timestamp: null, unreadCount: 0 };
      conversations.value.unshift(conv);
    }
    selectConversation(conv);
  } else if (r.type === 'group') {
    let group = conversations.value.find(c => c.type === 'group' && c.group.id === r.id);
    if (!group) {
      try {
        await api.post(`/message/group/${r.id}/manage/`, { action: 'add_member', user_id: currentUser.value.id });
        await fetchConversations();
        group = conversations.value.find(c => c.type === 'group' && c.group.id === r.id);
      } catch (e) { console.error('Join group error', e); }
    }
    if (group) selectConversation(group);
  }
  searchQuery.value = '';
  searchResults.value = [];
}

function updateConversation(msg) {
  const conv = conversations.value.find(c =>
    (c.type === 'private' && c.mate.id === msg.sender.id) ||
    (c.type === 'group' && c.group.id === msg.group)
  );
  if (conv) {
    conv.lastMessage = msg.content;
    conv.timestamp = msg.timestamp;
    if (selectedConversation.value?.id !== conv.id) conv.unreadCount++;
  } else if (msg.sender?.id !== currentUser.value.id) fetchConversations();
}

async function selectConversation(conv) {
  selectedConversation.value = conv;
  await fetchMessages(conv);
  conv.type === 'group' ? setupGroupWebSocket(conv) : groupWs.value?.close();

  if (conv.type === 'private' && privateWs.value?.readyState === WebSocket.OPEN) {
    privateWs.value.send(JSON.stringify({ action: 'mark_as_read', receiver_id: conv.mate.id }));
  }
}

// === MESSAGE ACTIONS ===
async function sendMessage(data) {
  console.log('Messaging.vue: sendMessage called with:', data);
  try {
    // Upload attachments
    const attachmentIds = await uploadAttachments(data.attachments);
    console.log('Messaging.vue: Attachment IDs:', attachmentIds);

    // Validate required data
    if (!currentUser.value) {
      console.error('Messaging.vue: Error: currentUser is null');
      return;
    }
    if (!selectedConversation.value || !selectedConversation.value.type) {
      console.error('Messaging.vue: Error: selectedConversation is invalid:', selectedConversation.value);
      return;
    }

    // Create temporary message for UI
    const newMessage = {
      id: `temp-${Date.now()}`,
      sender: currentUser.value,
      content: data.content,
      attachments: data.attachments.map(file => ({
        url: URL.createObjectURL(file),
        name: file.name,
        type: file.type
      })),
      timestamp: new Date().toISOString(),
      is_read: false
    };
    console.log('Messaging.vue: Optimistically adding message to UI:', newMessage);
    messages.value.push(newMessage);

    // Prepare WebSocket payload
    const payload = {
      action: 'send_message',
      content: data.content,
      attachment_ids: attachmentIds,
      reply_to_id: data.reply_to_id,
      receiver_id: selectedConversation.value.mate?.id
    };

    // Send via WebSocket
    if (selectedConversation.value.type === 'private') {
      if (!selectedConversation.value.mate?.id) {
        console.error('Messaging.vue: Error: mate.id is missing');
        messages.value.pop();
        return;
      }
      if (privateWs.value?.readyState === WebSocket.OPEN) {
        console.log('Messaging.vue: Sending private WS payload:', payload);
        privateWs.value.send(JSON.stringify(payload));
      } else {
        console.error('Messaging.vue: Private WebSocket not open:', privateWs.value?.readyState);
        messages.value.pop();
      }
    } else if (selectedConversation.value.type === 'group') {
      if (!selectedConversation.value.group?.id) {
        console.error('Messaging.vue: Error: group.id is missing');
        messages.value.pop();
        return;
      }
      if (groupWs.value?.readyState === WebSocket.OPEN) {
        console.log('Messaging.vue: Sending group WS payload:', payload);
        groupWs.value.send(JSON.stringify(payload));
      } else {
        console.error('Messaging.vue: Group WebSocket not open:', groupWs.value?.readyState);
        messages.value.pop();
      }
    } else {
      console.error('Messaging.vue: Invalid conversation type:', selectedConversation.value.type);
      messages.value.pop();
    }
  } catch (e) {
    console.error('Messaging.vue: Error in sendMessage:', e);
    messages.value.pop();
  }
}

async function uploadAttachments(attachments) {
  console.log('Messaging.vue: Uploading attachments:', attachments);
  const ids = [];
  for (const att of attachments) {
    const formData = new FormData();
    formData.append('file', att);
    try {
      const response = await api.post('/message/upload/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      console.log('Messaging.vue: Uploaded file:', att.name, 'ID:', response.data.id);
      ids.push(response.data.id);
    } catch (e) {
      console.error('Messaging.vue: Upload error for file:', att.name, e);
      throw e;
    }
  }
  return ids;
}

const createGroup = async ({ name, members }) => {
  try {
    const { data } = await api.post('/message/group/create/', { name, members });
    conversations.value.unshift(data);
    showCreateGroup.value = false;
    selectConversation(conversations.value[0]);
  } catch (e) { console.error('Group create error', e); }
};

const acceptPendingMessage = async (id) => {
  try {
    await api.post('/message/requests/', { action: 'accept', request_id: id });
    pendingMessages.value = pendingMessages.value.filter(m => m.id !== id);
    fetchConversations();
  } catch (e) { console.error('Accept error', e); }
};

const rejectPendingMessage = async (id) => {
  try {
    await api.post('/message/requests/', { action: 'decline', request_id: id });
    pendingMessages.value = pendingMessages.value.filter(m => m.id !== id);
    fetchConversations();
  } catch (e) { console.error('Reject error', e); }
};

// === WEBSOCKETS ===
function setupWebSockets() {
  getValidToken().then(token => {
    if (!token) return (isAuthenticated.value = false);
    privateWs.value = new WebSocket(`ws://localhost:8000/ws/private/?token=${token}`);

    privateWs.value.onopen = () => console.log('Messaging.vue: Private WS connected');
    privateWs.value.onclose = () => console.log('Messaging.vue: Private WS closed');
    privateWs.value.onerror = async (error) => {
      console.error('Messaging.vue: Private WS error:', error);
      if (await refreshToken()) setupWebSockets();
      else isAuthenticated.value = false;
    };
    privateWs.value.onmessage = (e) => {
      const data = JSON.parse(e.data);
      console.log('Messaging.vue: Received WebSocket message:', data);
      handleWsMessage(data, 'private');
    };
  });
}

function setupGroupWebSocket(conv) {
  groupWs.value?.close();
  getValidToken().then(token => {
    if (!token) return;
    groupWs.value = new WebSocket(`ws://localhost:8000/ws/group/${conv.group.id}/?token=${token}`);
    groupWs.value.onmessage = e => {
      const data = JSON.parse(e.data);
      console.log('Messaging.vue: Received group WebSocket message:', data);
      handleWsMessage(data, 'group');
    };
    groupWs.value.onerror = async (error) => {
      console.error('Messaging.vue: Group WS error:', error);
      if (await refreshToken()) setupGroupWebSocket(conv);
      else isAuthenticated.value = false;
    };
  });
}

function handleWsMessage(data, scope) {
  console.log('Messaging.vue: Handling WebSocket message:', data, 'scope:', scope);
  const actions = {
    chat_message: (data) => {
      console.log('Messaging.vue: Processing chat_message:', data);
      // Add message to current conversation if it's selected
      if (scope === 'private' && selectedConversation.value?.type === 'private') {
        const senderId = data.message.sender.id;
        const receiverId = data.message.receiver.id;
        const currentUserId = authStore.user.id;
        const selectedUserId = selectedConversation.value.mate.id;
        
        console.log('Messaging.vue: Message participants - sender:', senderId, 'receiver:', receiverId, 'current:', currentUserId, 'selected:', selectedUserId);
        
        // Show message if it's between current user and selected conversation partner
        if ((senderId === currentUserId && receiverId === selectedUserId) || 
            (senderId === selectedUserId && receiverId === currentUserId)) {
          console.log('Messaging.vue: Adding message to conversation');
          messages.value = messages.value.filter(m => !m.id.startsWith('temp-')); // Remove temp message
          messages.value.push(data.message);
          // Auto-scroll to bottom
          nextTick(() => {
            const chatArea = document.querySelector('.chat-messages-container');
            if (chatArea) chatArea.scrollTop = chatArea.scrollHeight;
          });
        } else {
          console.log('Messaging.vue: Message not for current conversation');
        }
      }
      
      if (scope === 'group' && selectedConversation.value?.type === 'group' && 
          selectedConversation.value?.group.id === data.message.group) {
        console.log('Messaging.vue: Adding group message to conversation');
        messages.value = messages.value.filter(m => !m.id.startsWith('temp-')); // Remove temp message
        messages.value.push(data.message);
        // Auto-scroll to bottom
        nextTick(() => {
          const chatArea = document.querySelector('.chat-messages-container');
          if (chatArea) chatArea.scrollTop = chatArea.scrollHeight;
        });
      }
      
      // Always update conversation list with latest message
      updateConversation(data.message);
    },
    reaction_added: (data) => {
      const m = messages.value.find(m => m.id === data.message_id);
      if (m) (m.reactions ||= []).push({ user: { id: data.user_id }, emoji: data.emoji });
    },
    message_edited: (data) => {
      const m = messages.value.find(m => m.id === data.message_id);
      if (m) m.content = data.new_content;
    },
    message_deleted: (data) => messages.value = messages.value.filter(m => m.id !== data.message_id),
    messages_read: (data) => messages.value.forEach(m => { if (m.sender.id === selectedConversation.value?.mate.id) m.is_read = true; }),
    message_request: (data) => {
      console.log('Messaging.vue: Received message request:', data);
      fetchPendingMessages(); // Refresh pending messages
      // Also add to conversations if not exists
      updateConversationWithRequest(data.message);
    },
    request_accepted: (data) => {
      console.log('Messaging.vue: Message request was accepted:', data);
      fetchConversations(); // Refresh conversations
      // If this user sent the request, the conversation should now be available
    },
    pending: () => fetchPendingMessages(),
    error: (data) => {
      console.error('Messaging.vue: WebSocket error received:', data);
      // Remove the temporary message if there was an error
      messages.value = messages.value.filter(m => !m.id.startsWith('temp-'));
    },
    status: (data) => {
      console.log('Messaging.vue: WebSocket status:', data);
      if (data.status === 'connected') {
        console.log('Messaging.vue: WebSocket connected successfully');
      } else if (data.status === 'success' && data.message) {
        // Message was sent successfully, temp message will be replaced by real-time message
        console.log('Messaging.vue: Message sent successfully');
      } else if (data.status === 'pending') {
        console.log('Messaging.vue: Message request sent, waiting for acceptance');
      }
    },
    connected: (data) => {
      console.log('Messaging.vue: WebSocket connection established');
    }
  };
  
  const action = actions[data.type || data.status];
  if (action) {
    action(data);
  } else {
    console.warn('Messaging.vue: Unknown WebSocket message type:', data.type || data.status, data);
  }
}

// Function to update conversations when a new message request is received
function updateConversationWithRequest(messageRequest) {
  // This function can be expanded to add new conversations from message requests
  console.log('Updating conversation with request:', messageRequest);
}

// === UTILS ===
const formatTimestamp = ts => ts ? new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';
const getStatusColor = s => ({ online: 'bg-green-500', offline: 'bg-gray-400' }[s] || 'bg-gray-400');

// === LIFECYCLE ===
onMounted(async () => {
  if (await validateToken()) {
    await Promise.all([fetchCurrentUser(), fetchConversations(), fetchPendingMessages(), fetchAvailableMates()]);
    setupWebSockets();
  }
});

onUnmounted(() => {
  privateWs.value?.close();
  groupWs.value?.close();
});
</script>