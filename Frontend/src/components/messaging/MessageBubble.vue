<template>
  <div :class="['p-3 rounded-lg mb-2', message.sender.id === currentUser.id ? 'bg-blue-100 ml-auto' : 'bg-gray-200']" style="max-width: 60%;">
    <p>{{ message.content }}</p>
    <div v-if="message.attachments.length" class="mt-2">
      <img v-for="att in message.attachments" :key="att.id" :src="att.file" class="max-w-xs" />
    </div>
    <div v-if="message.reply_to" class="bg-gray-300 p-2 rounded mb-2">{{ message.reply_to.content }}</div>
    <div class="flex space-x-2 mt-1">
      <span v-for="reaction in message.reactions" :key="reaction.id">{{ reaction.reaction_type }}</span>
    </div>
    <div v-if="message.sender.id === currentUser.id" class="flex space-x-2 mt-2">
      <button @click="emit('edit', message.id, prompt('Edit message:', message.content))" class="text-blue-500">Edit</button>
      <button @click="emit('delete', message.id)" class="text-red-500">Delete</button>
    </div>
    <div class="flex space-x-2 mt-2">
      <button @click="emit('react', message.id, '👍')">👍</button>
      <button @click="emit('react', message.id, '❤️')">❤️</button>
    </div>
    <small>{{ message.timestamp }} {{ message.is_read ? '✓✓' : '✓' }}</small>
  </div>
</template>

<script setup>
defineProps(['message', 'currentUser']);
const emit = defineEmits(['react', 'edit', 'delete']);
</script>