<template>
  <div
    class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
    @click="$emit('close')"
  >
    <div
      class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-96 overflow-hidden"
      @click.stop
    >
      <div class="p-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-800">Pending Messages</h3>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 transition-colors duration-200"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
      
      <div class="p-4 max-h-80 overflow-y-auto">
        <div v-if="pendingMessages.length === 0" class="text-center text-gray-500 py-8">
          <svg class="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
          <p>No pending messages</p>
        </div>
        
        <div v-else class="space-y-3">
          <div
            v-for="pending in pendingMessages"
            :key="pending.id"
            class="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg"
          >
            <img
              :src="pending.avatar"
              :alt="pending.name"
              class="w-10 h-10 rounded-full object-cover"
            />
            <div class="flex-1">
              <p class="font-medium text-gray-800">{{ pending.name }}</p>
              <p class="text-sm text-gray-600 truncate">{{ pending.message }}</p>
              <p class="text-xs text-gray-400">{{ pending.timestamp }}</p>
            </div>
            <div class="flex space-x-2">
              <button
                @click="$emit('accept', pending.id)"
                class="px-3 py-1 bg-green-500 text-white text-sm rounded-full hover:bg-green-600 transition-colors duration-200"
              >
                Accept
              </button>
              <button
                @click="$emit('reject', pending.id)"
                class="px-3 py-1 bg-red-500 text-white text-sm rounded-full hover:bg-red-600 transition-colors duration-200"
              >
                Reject
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  pendingMessages: Array
})

const emit = defineEmits(['close', 'accept', 'reject'])
</script>