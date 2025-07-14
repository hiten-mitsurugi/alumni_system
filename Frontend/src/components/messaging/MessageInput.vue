<template>
  <div class="p-4 bg-white border-t flex">
    <input v-model="message" @keyup="handleTyping" @keyup.enter="send" placeholder="Type a message..." class="flex-1 p-2 border rounded mr-2" />
    <input type="file" @change="handleFileUpload" multiple class="mr-2" />
    <button @click="send" class="p-2 bg-blue-500 text-white rounded">Send</button>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { websocketService } from '../../services/websocket';

const emit = defineEmits(['send']);
const message = ref('');
const files = ref([]);
const typingTimeout = ref(null);

const handleTyping = () => {
  const socket = websocketService.getSocket('private') || websocketService.getSocket('group');
  if (!typingTimeout.value) socket.send(JSON.stringify({ action: 'typing' }));
  clearTimeout(typingTimeout.value);
  typingTimeout.value = setTimeout(() => {
    socket.send(JSON.stringify({ action: 'stop_typing' }));
    typingTimeout.value = null;
  }, 1000);
};

const handleFileUpload = (event) => {
  files.value = Array.from(event.target.files);
};

const send = () => {
  if (!message.value && !files.value.length) return;
  const attachments = files.value.map(file => new Promise(resolve => {
    const reader = new FileReader();
    reader.onload = () => resolve({ name: file.name, type: file.type, data: reader.result.split(',')[1] });
    reader.readAsDataURL(file);
  }));
  Promise.all(attachments).then(att => {
    emit('send', { content: message.value, attachments: att });
    message.value = '';
    files.value = [];
  });
};
</script>