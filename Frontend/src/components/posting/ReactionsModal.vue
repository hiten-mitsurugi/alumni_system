<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm"
    @click.self="closeModal"
  >
    <div
      class="bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[80vh] overflow-hidden flex flex-col"
      @click.stop
    >
      <!-- Modal Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h3 class="text-xl font-semibold text-gray-900">Reactions</h3>
        <button
          @click="closeModal"
          class="p-2 hover:bg-gray-100 rounded-full transition-colors"
        >
          <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Reaction Filter Tabs -->
      <div class="flex border-b border-gray-200 bg-gray-50">
        <button
          @click="selectedFilter = 'all'"
          :class="[
            'flex-1 px-4 py-3 text-sm font-medium transition-colors relative',
            selectedFilter === 'all'
              ? 'text-blue-600 bg-white border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
          ]"
        >
          <span class="flex items-center justify-center space-x-2">
            <span>All</span>
            <span class="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded-full">{{ totalReactions }}</span>
          </span>
        </button>
        
        <button
          v-for="(count, reactionType) in reactionCounts"
          :key="reactionType"
          @click="selectedFilter = reactionType"
          :class="[
            'flex-1 px-4 py-3 text-sm font-medium transition-colors relative',
            selectedFilter === reactionType
              ? 'text-blue-600 bg-white border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
          ]"
        >
          <span class="flex items-center justify-center space-x-2">
            <span class="text-lg">{{ getReactionEmoji(reactionType) }}</span>
            <span class="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded-full">{{ count.count }}</span>
          </span>
        </button>
      </div>

      <!-- Reactions List -->
      <div class="flex-1 overflow-y-auto">
        <div v-if="loading" class="flex justify-center items-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else-if="filteredReactions.length === 0" class="text-center py-8 text-gray-500">
          <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
          </svg>
          <p>No reactions yet</p>
        </div>
        
        <div v-else class="divide-y divide-gray-100">
          <div
            v-for="reaction in filteredReactions"
            :key="`${reaction.user.id}-${reaction.reaction_type}`"
            class="p-4 flex items-center space-x-3 hover:bg-gray-50 transition-colors"
          >
            <!-- User Avatar -->
            <img
              :src="reaction.user.profile_picture || '/default-avatar.png'"
              :alt="reaction.user.full_name"
              class="w-12 h-12 rounded-full object-cover border border-gray-200"
            />
            
            <!-- User Info -->
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-900 truncate">
                {{ reaction.user.full_name }}
                <span v-if="reaction.user.id === currentUserId" class="text-blue-600">(You)</span>
              </p>
              <p class="text-xs text-gray-500">{{ formatTimeAgo(reaction.created_at) }}</p>
            </div>
            
            <!-- Reaction -->
            <div class="flex items-center space-x-2">
              <span class="text-2xl">{{ getReactionEmoji(reaction.reaction_type) }}</span>
              
              <!-- Reaction Options for Current User -->
              <div v-if="reaction.user.id === currentUserId" class="relative">
                <button
                  @click="toggleReactionOptions(reaction)"
                  class="p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
                >
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                  </svg>
                </button>
                
                <!-- Reaction Options Dropdown -->
                <div
                  v-if="showReactionOptions && selectedReaction?.user.id === reaction.user.id"
                  class="absolute right-0 top-8 bg-white border border-gray-200 rounded-lg shadow-lg py-2 z-10 min-w-[200px]"
                >
                  <!-- Change Reaction Options -->
                  <div class="px-3 py-2 text-xs font-medium text-gray-500 uppercase tracking-wide border-b border-gray-100">
                    Change Reaction
                  </div>
                  <div class="flex space-x-2 p-3 border-b border-gray-100">
                    <button
                      v-for="(reactionInfo, type) in reactionTypes"
                      :key="type"
                      @click="changeReaction(reaction, type)"
                      :class="[
                        'p-2 rounded-lg hover:bg-gray-100 transition-colors',
                        reaction.reaction_type === type ? 'bg-blue-100 ring-2 ring-blue-500' : ''
                      ]"
                      :title="reactionInfo.label"
                    >
                      <span class="text-xl">{{ reactionInfo.emoji }}</span>
                    </button>
                  </div>
                  
                  <!-- Remove Reaction -->
                  <button
                    @click="removeReaction(reaction)"
                    class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                  >
                    Remove Reaction
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { postsService } from '@/services/postsService'

// Props
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  postId: {
    type: [String, Number],
    required: true
  },
  currentUserId: {
    type: Number,
    required: true
  }
})

// Emits
const emit = defineEmits(['close', 'reaction-updated'])

// Local state
const loading = ref(false)
const reactions = ref([])
const selectedFilter = ref('all')
const showReactionOptions = ref(false)
const selectedReaction = ref(null)

// Reaction types
const reactionTypes = {
  like: { emoji: '👍', label: 'Like' },
  applaud: { emoji: '👏', label: 'Applaud' },
  heart: { emoji: '❤️', label: 'Heart' },
  support: { emoji: '🤝', label: 'Support' },
  laugh: { emoji: '😂', label: 'Laugh' },
  sad: { emoji: '😢', label: 'Sad' }
}

// Computed properties
const reactionCounts = computed(() => {
  const counts = {}
  reactions.value.forEach(reaction => {
    if (!counts[reaction.reaction_type]) {
      counts[reaction.reaction_type] = { count: 0 }
    }
    counts[reaction.reaction_type].count++
  })
  return counts
})

const totalReactions = computed(() => {
  return reactions.value.length
})

const filteredReactions = computed(() => {
  if (selectedFilter.value === 'all') {
    return reactions.value
  }
  return reactions.value.filter(reaction => reaction.reaction_type === selectedFilter.value)
})

// Methods
const closeModal = () => {
  showReactionOptions.value = false
  selectedReaction.value = null
  emit('close')
}

const loadReactions = async () => {
  if (!props.postId) return
  
  loading.value = true
  try {
    const response = await postsService.getPostReactions(props.postId)
    reactions.value = response.data.reactions || []
  } catch (error) {
    console.error('Error loading reactions:', error)
    reactions.value = []
  } finally {
    loading.value = false
  }
}

const getReactionEmoji = (type) => {
  return reactionTypes[type]?.emoji || '👍'
}

const formatTimeAgo = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInSeconds = Math.floor((now - date) / 1000)

  if (diffInSeconds < 60) return 'Just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h`
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d`

  return date.toLocaleDateString()
}

const toggleReactionOptions = (reaction) => {
  if (selectedReaction.value?.user.id === reaction.user.id) {
    showReactionOptions.value = !showReactionOptions.value
  } else {
    selectedReaction.value = reaction
    showReactionOptions.value = true
  }
}

const changeReaction = async (reaction, newReactionType) => {
  if (reaction.reaction_type === newReactionType) {
    showReactionOptions.value = false
    return
  }

  try {
    await postsService.reactToPost(props.postId, newReactionType)
    
    // Update local reaction
    const reactionIndex = reactions.value.findIndex(r => r.user.id === reaction.user.id)
    if (reactionIndex !== -1) {
      reactions.value[reactionIndex].reaction_type = newReactionType
    }
    
    showReactionOptions.value = false
    selectedReaction.value = null
    
    emit('reaction-updated')
  } catch (error) {
    console.error('Error changing reaction:', error)
  }
}

const removeReaction = async (reaction) => {
  try {
    await postsService.removeReaction(props.postId)
    
    // Remove from local list
    reactions.value = reactions.value.filter(r => r.user.id !== reaction.user.id)
    
    showReactionOptions.value = false
    selectedReaction.value = null
    
    emit('reaction-updated')
  } catch (error) {
    console.error('Error removing reaction:', error)
  }
}

const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    showReactionOptions.value = false
    selectedReaction.value = null
  }
}

// Watchers
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    loadReactions()
    selectedFilter.value = 'all'
  } else {
    showReactionOptions.value = false
    selectedReaction.value = null
  }
})

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Smooth transitions */
.transition-colors {
  transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

/* Modal animation */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { 
    opacity: 0; 
    transform: scale(0.9) translateY(20px); 
  }
  to { 
    opacity: 1; 
    transform: scale(1) translateY(0); 
  }
}

.fixed {
  animation: fadeIn 0.2s ease-out;
}

.bg-white {
  animation: slideIn 0.3s ease-out;
}
</style>
