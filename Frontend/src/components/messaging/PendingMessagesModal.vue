<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-96 overflow-hidden" @click.stop>
      <div class="p-4 border-b border-gray-200">
        <h3 class="text-lg font-semibold text-gray-800">Pending Messages</h3>
      </div>
      <div class="p-4 max-h-80 overflow-y-auto">
        <div v-if="pendingMessages.length === 0" class="text-center text-gray-500 py-8">
          <p>No pending messages</p>
        </div>
        <div v-else class="space-y-3">
          <div v-for="pending in pendingMessages" :key="pending.id" class="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <img :src="pending.avatar" alt="Avatar" class="w-10 h-10 rounded-full object-cover" />
            <div class="flex-1">
              <p class="font-medium text-gray-800">{{ pending.name }}</p>
              <p class="text-sm text-gray-600">{{ pending.message }}</p>
            </div>
            <div class="flex space-x-2">
              <button @click="$emit('accept', pending.id)" class="px-3 py-1 bg-green-500 text-white rounded-full hover:bg-green-600">Accept</button>
              <button @click="$emit('reject', pending.id)" class="px-3 py-1 bg-red-500 text-white rounded-full hover:bg-red-600">Reject</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  pendingMessages: Array,
});
</script>