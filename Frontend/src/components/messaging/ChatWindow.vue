<template>
  <div class="flex-1 flex flex-col">
    <div class="p-4 bg-white border-b flex items-center">
      <img :src="conversation.type === 'private' ? conversation.user.profile.profile_picture : conversation.group.group_picture" class="w-10 h-10 rounded-full mr-3" />
      <h2>{{ conversation.type === 'private' ? `${conversation.user.first_name} ${conversation.user.last_name}` : conversation.group.name }}</h2>
      <span class="ml-2 text-sm" :class="conversation.user?.profile?.status === 'online' ? 'text-green-500' : 'text-gray-500'">
        {{ conversation.user?.profile?.status }}
      </span>
    </div>
    <div class="flex-1 overflow-y-auto p-4">
      <div v-if="typingUsers.length" class="text-gray-500">{{ typingUsers.join(', ') }} is typing...</div>
      <MessageBubble v-for="message in messages" :key="message.id" :message="message" :current-user="currentUser" @react="addReaction" @edit="editMessage" @delete="deleteMessage" />
    </div>
    <MessageInput @send="sendMessage" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import api from '../../services/api';
import { websocketService } from '../../services/websocket';
import MessageBubble from './MessageBubble.vue';
import MessageInput from './MessageInput.vue';

const props = defineProps(['conversation']);
const messages = ref([]);
const typingUsers = ref([]);
const socket = ref(null);
const currentUser = ref({ id: 1 }); // Replace with actual user fetch

const fetchMessages = async () => {
  const url = props.conversation.type === 'private' ? `/message/private/${props.conversation.user.id}/` : `/message/group/${props.conversation.group.id}/`;
  const res = await api.get(url);
  messages.value = res.data;
};

const sendMessage = (data) => {
  const messageData = { action: 'send_message', content: data.content, attachments: data.attachments };
  if (props.conversation.type === 'private') messageData.receiver_id = props.conversation.user.id;
  if (data.replyTo) messageData.reply_to_id = data.replyTo;
  socket.value.send(JSON.stringify(messageData));
};

const addReaction = (messageId, reactionType) => {
  socket.value.send(JSON.stringify({ action: 'react', message_id: messageId, reaction_type: reactionType }));
};

const editMessage = (messageId, newContent) => {
  socket.value.send(JSON.stringify({ action: 'edit_message', message_id: messageId, new_content: newContent }));
};

const deleteMessage = (messageId) => {
  socket.value.send(JSON.stringify({ action: 'delete', message_id: messageId }));
};

onMounted(async () => {
  await fetchMessages();
  const endpoint = props.conversation.type === 'private' ? 'private' : `group/${props.conversation.group.id}`;
  socket.value = await websocketService.connect(endpoint);
  if (props.conversation.type === 'private') {
    socket.value.send(JSON.stringify({ action: 'mark_as_read', receiver_id: props.conversation.user.id }));
  }
  websocketService.addListener(endpoint, (data) => {
    if (data.type === 'chat_message') messages.value.push(data.message);
    else if (data.type === 'reaction_added') {
      const msg = messages.value.find(m => m.id === data.message_id);
      if (msg) msg.reactions.push({ reaction_type: data.reaction, user: { username: data.user } });
    }
    else if (data.type === 'message_deleted') messages.value = messages.value.filter(m => m.id !== data.message_id);
    else if (data.type === 'message_edited') {
      const msg = messages.value.find(m => m.id === data.message_id);
      if (msg) msg.content = data.new_content;
    }
    else if (data.type === 'user_typing') typingUsers.value.push(data.user);
    else if (data.type === 'user_stop_typing') typingUsers.value = typingUsers.value.filter(u => u !== data.user);
    else if (data.type === 'messages_read') messages.value.forEach(m => m.is_read = true);
  });
});

onUnmounted(() => {
  websocketService.disconnect(props.conversation.type === 'private' ? 'private' : `group/${props.conversation.group.id}`);
});
</script>