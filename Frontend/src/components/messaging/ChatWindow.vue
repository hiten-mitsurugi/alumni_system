<template>
  <div class="w-2/3 flex flex-col">
    <!-- Header -->
    <div v-if="selectedConversation" class="bg-green-700 text-white p-3 flex items-center">
      <img
        v-if="selectedConversation.type === 'private'"
        class="w-8 h-8 rounded-full mr-2"
        src="https://via.placeholder.com/32"
        alt="Avatar"
      />
      <span
        v-else
        class="w-8 h-8 rounded-full mr-2 bg-green-500 flex items-center justify-center text-white font-bold"
      >
        {{ selectedConversationName.charAt(0) }}
      </span>
      <span class="text-lg font-semibold">{{ selectedConversationName }}</span>
    </div>

    <!-- Messages -->
    <div v-if="selectedConversation" class="flex-1 overflow-y-auto p-4 bg-gray-50">
      <div
        v-for="message in messages"
        :key="message.id"
        :class="[
          'p-3 rounded-lg mb-2 max-w-[70%]',
          message.sender.id === authStore.user.id ? 'bg-blue-100 ml-auto' : 'bg-white shadow'
        ]"
      >
        <p class="font-semibold">{{ message.sender.username }}</p>
        <p>{{ message.content }}</p>
        <p class="text-xs text-gray-500">{{ new Date(message.timestamp).toLocaleTimeString() }}</p>

        <div v-if="message.reactions" class="mt-1 flex gap-2">
          <span
            v-for="reaction in message.reactions"
            :key="reaction.id"
            class="text-sm"
          >
            {{ reaction.reaction_type }} ({{ reaction.user.username }})
          </span>
        </div>

        <div v-if="message.attachments" class="mt-2">
          <a
            v-for="attachment in message.attachments"
            :key="attachment.id"
            :href="attachment.file"
            target="_blank"
            class="text-blue-500 block"
          >
            {{ attachment.file_type === 'image' ? 'Image' : attachment.file_type.toUpperCase() }}
          </a>
        </div>

        <div class="mt-1 flex gap-2">
          <button @click="$emit('reactToMessage', message.id, 'like')" class="text-sm text-blue-500">Like</button>
          <button
            v-if="message.sender.id === authStore.user.id"
            @click="$emit('deleteMessage', message.id)"
            class="text-sm text-red-500"
          >
            Delete
          </button>
        </div>
      </div>
    </div>

    <div v-else class="flex-1 flex items-center justify-center bg-gray-50">
      <p class="text-gray-500">Select a conversation to start messaging</p>
    </div>

    <!-- Input -->
    <div v-if="selectedConversation" class="p-4 bg-white border-t">
      <div class="flex">
        <input
          :value="newMessage"
          @input="$emit('update:newMessage', $event.target.value)"
          @keyup.enter="$emit('sendMessage')"
          placeholder="Type a message..."
          class="flex-1 p-2 border rounded-l focus:outline-none focus:ring-2 focus:ring-green-500"
        />
        <input type="file" multiple @change="$emit('handleFile', $event)" class="p-2" />
        <button
          @click="$emit('sendMessage')"
          class="bg-green-500 text-white px-4 py-2 rounded-r hover:bg-green-600"
        >
          Send
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
defineProps(['selectedConversation', 'selectedConversationName', 'messages', 'newMessage']);
const authStore = useAuthStore();
</script>
