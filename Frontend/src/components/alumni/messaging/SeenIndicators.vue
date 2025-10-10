<template>
  <div v-if="readByUsers && readByUsers.length > 0" class="flex items-center gap-1 mt-1">
    <!-- Show profile pictures of users who have seen the message -->
    <div class="flex -space-x-1 relative">
      <div
        v-for="(user, index) in displayedUsers"
        :key="user.id"
        class="relative group"
        @mouseenter="showTooltip(user, $event)"
        @mouseleave="hideTooltip"
      >
        <img
          :src="getProfilePictureUrl(user)"
          :alt="`${user.first_name} ${user.last_name}`"
          class="w-4 h-4 rounded-full border border-white object-cover cursor-pointer hover:scale-110 transition-transform duration-200"
          :style="{ zIndex: readByUsers.length - index }"
        />
      </div>
      
      <!-- Show "+X more" indicator if there are more than 3 users -->
      <div
        v-if="remainingCount > 0"
        class="w-4 h-4 rounded-full bg-gray-400 border border-white flex items-center justify-center text-xs text-white font-medium cursor-pointer hover:scale-110 transition-transform duration-200"
        @mouseenter="showAllTooltip($event)"
        @mouseleave="hideTooltip"
      >
        +{{ remainingCount }}
      </div>
    </div>
    
    <!-- Optional: Show "Seen" text for single user -->
    <span v-if="readByUsers.length === 1" class="text-xs text-gray-500 ml-1">
      Seen
    </span>

    <!-- Custom Tooltip -->
    <div
      v-if="tooltipVisible"
      :style="tooltipPosition"
      class="fixed z-[9999] bg-gray-900 text-white text-xs rounded-md px-2 py-1.5 shadow-lg pointer-events-none max-w-[140px]"
    >
      <!-- Single user tooltip -->
      <div v-if="tooltipUser" class="text-xs leading-tight">
        <div class="font-medium">{{ tooltipUser.first_name }} {{ tooltipUser.last_name }}</div>
        <div class="text-gray-300 text-[10px]">{{ formatDateTime(tooltipUser.read_at) }}</div>
      </div>
      
      <!-- Multiple users tooltip -->
      <div v-else-if="showingAll" class="text-xs">
        <div class="text-center mb-1 text-[10px] text-gray-300">{{ readByUsers.length }} people</div>
        <div class="max-h-24 overflow-y-auto space-y-0.5">
          <div v-for="user in readByUsers" :key="user.id" class="text-[10px] leading-tight">
            <div class="font-medium">{{ user.first_name }} {{ user.last_name }}</div>
            <div class="text-gray-400">{{ formatTime(user.read_at) }}</div>
          </div>
        </div>
      </div>
      
      <!-- Tooltip arrow -->
      <div class="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-3 border-r-3 border-t-3 border-transparent border-t-gray-900"></div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, reactive } from 'vue'

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

// Tooltip state
const tooltipVisible = ref(false)
const tooltipUser = ref(null)
const showingAll = ref(false)
const tooltipPosition = reactive({
  left: '0px',
  top: '0px'
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

const formatDateTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffInHours = (now - date) / (1000 * 60 * 60)
  
  if (diffInHours < 24) {
    // Same day - show time only
    return `Today at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
  } else if (diffInHours < 48) {
    // Yesterday
    return `Yesterday at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
  } else if (diffInHours < 168) { // Less than a week
    // Show day of week
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    return `${days[date.getDay()]} at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
  } else {
    // Show full date
    return `${date.toLocaleDateString()} at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
  }
}

const showTooltip = (user, event) => {
  tooltipUser.value = user
  showingAll.value = false
  positionTooltip(event)
  tooltipVisible.value = true
}

const showAllTooltip = (event) => {
  tooltipUser.value = null
  showingAll.value = true
  positionTooltip(event)
  tooltipVisible.value = true
}

const hideTooltip = () => {
  // Add small delay to prevent flickering when moving between elements
  setTimeout(() => {
    tooltipVisible.value = false
    tooltipUser.value = null
    showingAll.value = false
  }, 100)
}

const positionTooltip = (event) => {
  const rect = event.target.getBoundingClientRect()
  const tooltipWidth = 140 // Narrow width
  const tooltipHeight = showingAll.value ? Math.min(100, readByUsers.value.length * 25 + 35) : 35 // Compact height
  
  // Calculate horizontal position (center on element)
  let left = rect.left + (rect.width / 2) - (tooltipWidth / 2)
  
  // Keep tooltip within screen bounds
  const padding = 10
  if (left < padding) {
    left = padding
  } else if (left + tooltipWidth > window.innerWidth - padding) {
    left = window.innerWidth - tooltipWidth - padding
  }
  
  // Calculate vertical position (prefer showing above)
  let top = rect.top - tooltipHeight - 8
  
  // If not enough space above, show below
  if (top < padding) {
    top = rect.bottom + 8
  }
  
  tooltipPosition.left = `${left}px`
  tooltipPosition.top = `${top}px`
}
</script>

<style scoped>
/* Seen indicators styling */
.seen-indicators {
  transition: opacity 0.2s ease;
}

.seen-indicators:hover {
  opacity: 0.8;
}

/* Tooltip styling - ensure no overflow issues */
.fixed {
  animation: fadeIn 0.2s ease-out;
  box-sizing: border-box;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

/* Custom scrollbar for multiple users list */
.max-h-48::-webkit-scrollbar {
  width: 4px;
}

.max-h-48::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.max-h-48::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
}

.max-h-48::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Hover effects for profile pictures */
img:hover {
  filter: brightness(1.1);
}

/* Smooth transitions */
.group img,
.group div {
  transition: all 0.2s ease;
}

/* Ensure tooltip doesn't cause page overflow */
.fixed {
  max-height: 50vh;
  overflow: hidden;
}
</style>
