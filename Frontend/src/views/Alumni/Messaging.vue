<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <div class="flex h-screen bg-gray-100">
    <ConversationList @select-conversation="selectConversation" />
    <ChatWindow v-if="selectedConversation" :conversation="selectedConversation" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import ConversationList from '../../components/messaging/ConversationList.vue';
import ChatWindow from '../../components/messaging/ChatWindow.vue';

const selectedConversation = ref(null);

const selectConversation = (conversation) => {
  selectedConversation.value = conversation;
};
</script>