<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
    <div class="bg-white rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-hidden shadow-2xl">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h2 class="text-xl font-semibold text-gray-800">Blocked Users</h2>
        <button 
          @click="$emit('close')"
          class="p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="p-6">
        <!-- Loading State -->
        <div v-if="loading" class="flex items-center justify-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span class="ml-3 text-gray-600">Loading blocked users...</span>
        </div>

        <!-- Empty State -->
        <div v-else-if="blockedUsers.length === 0" class="text-center py-8">
          <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="9" stroke-width="2"></circle>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6"></path>
          </svg>
          <h3 class="text-lg font-medium text-gray-900 mb-2">No blocked users</h3>
          <p class="text-gray-500">You haven't blocked any users yet.</p>
        </div>

        <!-- Blocked Users List -->
        <div v-else class="space-y-3 max-h-[400px] overflow-y-auto">
          <div 
            v-for="blockedUser in blockedUsers" 
            :key="blockedUser.id"
            class="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div class="flex items-center gap-3">
              <img 
                :src="getProfilePictureUrl(blockedUser.blocked_user)"
                alt="Profile"
                class="w-12 h-12 rounded-full object-cover border-2 border-gray-200"
              />
              <div>
                <h4 class="font-medium text-gray-900">
                  {{ blockedUser.blocked_user.first_name }} {{ blockedUser.blocked_user.last_name }}
                </h4>
                <p class="text-sm text-gray-500">@{{ blockedUser.blocked_user.username }}</p>
                <p class="text-xs text-gray-400 mt-1">
                  Blocked {{ formatDate(blockedUser.timestamp) }}
                </p>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <!-- Unblock Button -->
              <button
                @click="handleUnblock(blockedUser)"
                :disabled="unblockingUsers.has(blockedUser.blocked_user.id)"
                class="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <span v-if="unblockingUsers.has(blockedUser.blocked_user.id)">
                  Unblocking...
                </span>
                <span v-else>
                  Unblock
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="border-t border-gray-200 p-6">
        <div class="flex justify-end">
          <button
            @click="$emit('close')"
            class="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import messagingService from '@/services/messaging'

// Props
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['close', 'user-unblocked'])

// State
const loading = ref(false)
const blockedUsers = ref([])
const unblockingUsers = ref(new Set())

// Helper functions
const getProfilePictureUrl = (user) => {
  return messagingService.getProfilePictureUrl(user)
}

const formatDate = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// API functions
const fetchBlockedUsers = async () => {
  loading.value = true
  try {
    const data = await messagingService.getBlockedUsers()
    blockedUsers.value = data
  } catch (error) {
    console.error('Error fetching blocked users:', error)
    alert('Failed to load blocked users. Please try again.')
  } finally {
    loading.value = false
  }
}

const handleUnblock = async (blockedUser) => {
  const userId = blockedUser.blocked_user.id
  
  // Prevent double-clicking
  if (unblockingUsers.value.has(userId)) return
  
  // Confirm action
  const confirmed = confirm(
    `Are you sure you want to unblock ${blockedUser.blocked_user.first_name} ${blockedUser.blocked_user.last_name}?`
  )
  
  if (!confirmed) return

  unblockingUsers.value.add(userId)
  
  try {
    await messagingService.unblockUser(userId)
    
    // Remove from local list
    blockedUsers.value = blockedUsers.value.filter(
      user => user.blocked_user.id !== userId
    )
    
    // Emit event to parent
    emit('user-unblocked', blockedUser.blocked_user)
    
    console.log('User unblocked successfully')
  } catch (error) {
    console.error('Error unblocking user:', error)
    const message = error.response?.data?.error || 'Failed to unblock user'
    alert(message)
  } finally {
    unblockingUsers.value.delete(userId)
  }
}

// Watchers
watch(() => props.show, (newShow) => {
  if (newShow) {
    fetchBlockedUsers()
  }
})

// Lifecycle
onMounted(() => {
  if (props.show) {
    fetchBlockedUsers()
  }
})
</script>

<style scoped>
/* Add any additional styles if needed */
</style>
