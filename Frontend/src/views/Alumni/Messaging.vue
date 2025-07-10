<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <div class="flex h-full">
    <ConversationList
      :users="users"
      :groups="groups"
      :currentTab="currentTab"
      :selectedConversation="selectedConversation"
      @selectConversation="selectConversation"
      @changeTab="currentTab = $event"
      @openGroupModal="showCreateGroup = true"
    />

    <ChatWindow
      :selectedConversation="selectedConversation"
      :selectedConversationName="selectedConversationName"
      :messages="messages"
      :newMessage="newMessage"
      @update:newMessage="newMessage = $event"
      @sendMessage="sendMessage"
      @reactToMessage="reactToMessage"
      @deleteMessage="deleteMessage"
      @handleFile="handleFile"
    />

    <CreateGroupModal
      v-if="showCreateGroup"
      :users="users"
      :groupName="groupName"
      :selectedMembers="selectedMembers"
      @update:groupName="groupName = $event"
      @update:selectedMembers="selectedMembers = $event"
      @close="showCreateGroup = false"
      @createGroup="createGroup"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import api from '@/services/api';
import { websocketService } from '@/services/websocket';

import ConversationList from './../../components/messaging/ConversationList.vue'
import ChatWindow from './../../components/messaging/ChatWindow.vue'
import CreateGroupModal from './../../components/messaging/CreateGroupModal.vue'


const authStore = useAuthStore();
const currentTab = ref('private');
const users = ref([]);
const groups = ref([]);
const selectedConversation = ref(null);
const messages = ref([]);
const newMessage = ref('');
const showCreateGroup = ref(false);
const groupName = ref('');
const selectedMembers = ref([]);
const files = ref([]);

const selectedConversationName = computed(() => {
  if (!selectedConversation.value) return '';
  if (selectedConversation.value.type === 'private') {
    const user = users.value.find(u => u.id === selectedConversation.value.id);
    return user ? user.username : 'Unknown';
  } else {
    const group = groups.value.find(g => g.id === selectedConversation.value.id);
    return group ? group.name : 'Unknown';
  }
});

onMounted(async () => {
  try {
    const usersResponse = await api.get('/user/');
    const data = usersResponse.data;
    users.value = Array.isArray(data) ? data.filter(u => u.id !== authStore.user.id) : [];

    const groupsResponse = await api.get('/group/');
    groups.value = groupsResponse.data;
  } catch (error) {
    console.error('Failed to fetch users or groups:', error);
  }

  websocketService.connect('private');
  websocketService.addListener('private', handleMessage);
});

onUnmounted(() => {
  websocketService.removeListener('private', handleMessage);
  websocketService.disconnect('private');
  groups.value.forEach(group => {
    websocketService.removeListener(`group/${group.id}`, handleMessage);
    websocketService.disconnect(`group/${group.id}`);
  });
});

const handleMessage = (data) => {
  if (data.type === 'chat_message' && selectedConversation.value) {
    const { type, id } = selectedConversation.value;
    if ((type === 'private' && ((data.message.sender.id === authStore.user.id && data.message.receiver.id === id) ||
      (data.message.sender.id === id && data.message.receiver.id === authStore.user.id))) ||
      (type === 'group' && data.message.group === id)) {
      messages.value.push(data.message);
    }
  } else if (data.type === 'reaction_added') {
    const msg = messages.value.find(m => m.id === data.message_id);
    if (msg) {
      msg.reactions = [...(msg.reactions || []), {
        id: Date.now(),
        reaction_type: data.reaction,
        user: { username: data.user }
      }];
    }
  } else if (data.type === 'message_deleted') {
    messages.value = messages.value.filter(m => m.id !== data.message_id);
  }
};

const selectConversation = async (type, id) => {
  selectedConversation.value = { type, id };
  messages.value = [];

  if (type === 'group' && !websocketService.getSocket(`group/${id}`)) {
    websocketService.connect(`group/${id}`);
    websocketService.addListener(`group/${id}`, handleMessage);
  }

  try {
    const endpoint = type === 'private' ? `/messages/private/${id}/` : `/messages/group/${id}/`;
    const response = await api.get(endpoint);
    messages.value = response.data;
  } catch (error) {
    console.error(`Failed to fetch ${type} messages:`, error);
  }
};

const sendMessage = async () => {
  if (!newMessage.value.trim() && !files.value.length) return;

  const { type, id } = selectedConversation.value;
  const messageData = {
    action: 'send_message',
    content: newMessage.value,
    ...(type === 'private' ? { receiver_id: id } : {}),
    ...(files.value.length ? {
      attachments: await Promise.all(files.value.map(async file => {
        const data = await new Promise(resolve => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result.split(',')[1]);
          reader.readAsDataURL(file);
        });
        return { name: file.name, type: file.type.split('/')[0], data };
      }))
    } : {})
  };

  const endpoint = type === 'private' ? 'private' : `group/${id}`;
  const socket = websocketService.getSocket(endpoint);
  if (socket) {
    socket.send(JSON.stringify(messageData));
    messages.value.push({
      id: Date.now(),
      sender: authStore.user,
      content: newMessage.value,
      timestamp: new Date().toISOString(),
      reactions: [],
      attachments: files.value.map(f => ({
        id: Date.now(),
        file: URL.createObjectURL(f),
        file_type: f.type.split('/')[0]
      }))
    });
    newMessage.value = '';
    files.value = [];
  }
};

const reactToMessage = (messageId, reactionType) => {
  const { type, id } = selectedConversation.value;
  const endpoint = type === 'private' ? 'private' : `group/${id}`;
  const socket = websocketService.getSocket(endpoint);
  if (socket) {
    socket.send(JSON.stringify({
      action: 'react',
      message_id: messageId,
      reaction_type: reactionType
    }));
  }
};

const deleteMessage = (messageId) => {
  const { type, id } = selectedConversation.value;
  const endpoint = type === 'private' ? 'private' : `group/${id}`;
  const socket = websocketService.getSocket(endpoint);
  if (socket) {
    socket.send(JSON.stringify({
      action: 'delete',
      message_id: messageId
    }));
  }
};

const handleFile = (event) => {
  files.value = Array.from(event.target.files);
};

const createGroup = async () => {
  if (!groupName.value.trim() || !selectedMembers.value.length) return;

  try {
    const response = await api.post('/group/create/', {
      name: groupName.value,
      members: selectedMembers.value
    });
    groups.value.push(response.data);
    showCreateGroup.value = false;
    groupName.value = '';
    selectedMembers.value = [];
  } catch (error) {
    console.error('Failed to create group:', error);
  }
};
</script>

<style scoped>
.h-full {
  height: calc(100vh - 64px); /* Adjust if navbar exists */
}
</style>
