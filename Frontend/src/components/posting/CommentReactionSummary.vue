<template>
  <div 
    v-if="totalReactions > 0" 
    class="comment-reaction-summary flex items-center space-x-1 cursor-pointer hover:bg-gray-50 rounded-lg px-2 py-1 transition-colors mb-1 relative"
    @click="openReactionsModal"
  >
    <!-- Reaction Icons (Facebook-style) -->
    <div class="flex -space-x-1">
      <div
        v-for="(reactionType, index) in topReactions"
        :key="reactionType"
        class="reaction-icon"
        :class="{ 'z-10': index === 0, 'z-5': index === 1, 'z-0': index === 2 }"
        :title="`${getReactionLabel(reactionType)} reactions`"
      >
        <span class="reaction-emoji">{{ getReactionEmoji(reactionType) }}</span>
      </div>
    </div>

    <!-- Reaction Count -->
    <span 
      class="text-xs text-gray-600 font-medium hover:underline ml-1"
    >
      {{ formatReactionCount(totalReactions) }}
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// Props
const props = defineProps({
  reactionsSummary: {
    type: Object,
    default: () => ({
      total_count: 0,
      reaction_counts: {},
      user_reaction: null,
      recent_reactions: []
    })
  },
  commentId: {
    type: [String, Number],
    required: true
  }
})

// Emits
const emit = defineEmits(['open-reactions-modal'])

// Reaction type mappings
const reactionTypes = {
  like: { emoji: '👍', label: 'Like' },
  heart: { emoji: '❤️', label: 'Love' },
  laugh: { emoji: '😂', label: 'Haha' },
  sad: { emoji: '😢', label: 'Sad' },
  angry: { emoji: '😠', label: 'Angry' },
  applaud: { emoji: '👏', label: 'Applaud' }
}

// Computed properties
const totalReactions = computed(() => {
  return props.reactionsSummary?.total_count || 0;
})

const topReactions = computed(() => {
  const reactionCounts = props.reactionsSummary?.reaction_counts || {}
  
  // Sort reactions by count (most popular first)
  const sortedReactions = Object.entries(reactionCounts)
    .sort(([,a], [,b]) => b.count - a.count)
    .slice(0, 3) // Show top 3 reactions
  
  return sortedReactions.map(([type]) => type)
})

// Methods
const getReactionEmoji = (type) => {
  return reactionTypes[type]?.emoji || '👍'
}

const getReactionLabel = (type) => {
  return reactionTypes[type]?.label || 'Like'
}

const formatReactionCount = (count) => {
  if (count === 0) return ''
  if (count === 1) return '1'
  if (count < 1000) return count.toString()
  if (count < 1000000) return `${Math.floor(count / 1000)}K`
  return `${Math.floor(count / 1000000)}M`
}

const openReactionsModal = () => {
  emit('open-reactions-modal', props.commentId)
}
</script>

<style scoped>
.comment-reaction-summary {
  max-width: fit-content;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  cursor: pointer;
  border-radius: 0.5rem;
  padding: 0.25rem 0.5rem;
  transition: background-color 0.2s ease;
}

.comment-reaction-summary:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.reaction-icon {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.25rem;
  height: 1.25rem;
  background-color: white;
  border-radius: 50%;
  border: 1px solid #e5e7eb;
}

.reaction-emoji {
  font-size: 0.75rem;
}

.z-10 { z-index: 10; }
.z-5 { z-index: 5; }
.z-0 { z-index: 0; }
</style>
