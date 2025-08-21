<template>
  <div v-if="readByUsers && readByUsers.length > 0" class="flex items-center gap-1 mt-1">
    <!-- Show profile pictures of users who have seen the message -->
    <div class="flex -space-x-1">
      <div
        v-for="(user, index) in displayedUsers"
        :key="user.id"
        class="relative"
        :title="`Seen by ${user.first_name} ${user.last_name} at ${formatTime(user.read_at)}`"
      >
        <img
          :src="getProfilePictureUrl(user)"
          :alt="`${user.first_name} ${user.last_name}`"
          class="w-4 h-4 rounded-full border border-white object-cover"
          :style="{ zIndex: readByUsers.length - index }"
        />
      </div>
      
      <!-- Show "+X more" indicator if there are more than 3 users -->
      <div
        v-if="remainingCount > 0"
        class="w-4 h-4 rounded-full bg-gray-400 border border-white flex items-center justify-center text-xs text-white font-medium"
        :title="`+${remainingCount} more`"
      >
        +{{ remainingCount }}
      </div>
    </div>
    
    <!-- Optional: Show "Seen" text for single user -->
    <span v-if="readByUsers.length === 1" class="text-xs text-gray-500 ml-1">
      Seen
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  readBy: {
    type: Array,
    default: () => []
  },
  currentUserId: {
    type: Number,
    required: true
  },
  maxDisplay: {
    type: Number,
    default: 3
  }
})

// Filter out current user from read_by list and get relevant users
const readByUsers = computed(() => {
  if (!props.readBy) return []
  return props.readBy.filter(user => user.id !== props.currentUserId)
})

// Show only the first few users (default 3)
const displayedUsers = computed(() => {
  return readByUsers.value.slice(0, props.maxDisplay)
})

// Count of remaining users not displayed
const remainingCount = computed(() => {
  return Math.max(0, readByUsers.value.length - props.maxDisplay)
})

const getProfilePictureUrl = (user) => {
  if (user.profile_picture) {
    return user.profile_picture
  }
  // Return default avatar
  return '/default-avatar.png'
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
/* Additional styling for the seen indicators */
.seen-indicators {
  transition: opacity 0.2s ease;
}

.seen-indicators:hover {
  opacity: 0.8;
}
</style>
