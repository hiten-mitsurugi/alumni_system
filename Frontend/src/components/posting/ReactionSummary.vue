<template>
  <div 
    v-if="totalReactions > 0" 
    class="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 rounded-lg px-3 py-2 transition-colors mb-3 relative z-10"
    @click="openReactionsModal"
    @mouseenter.stop
    @mouseover.stop
    @mouseleave.stop
  >
    <!-- Top Reaction Icons -->
    <div class="flex -space-x-1 relative" @mouseenter.stop @mouseover.stop>
      <div
        v-for="(reactionType, index) in topReactions"
        :key="reactionType"
        class="relative flex items-center justify-center w-8 h-8 bg-white rounded-full border border-gray-200 hover:scale-110 transition-transform"
        :class="{ 'z-10': index === 0, 'z-5': index === 1, 'z-0': index === 2 }"
        :title="`${getReactionLabel(reactionType)} reactions`"
        @mouseenter.stop
        @mouseover.stop
      >
        <span class="text-base">{{ getReactionEmoji(reactionType) }}</span>
      </div>
    </div>

    <!-- Reaction Count -->
    <span 
      class="text-sm text-gray-600 font-medium hover:underline"
      @mouseenter.stop
      @mouseover.stop
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
  postId: {
    type: [String, Number],
    required: true
  }
})

// Emits
const emit = defineEmits(['open-reactions-modal'])

// Reaction type mappings
const reactionTypes = {
  like: { emoji: '👍', label: 'Like' },
  applaud: { emoji: '👏', label: 'Applaud' },
  heart: { emoji: '❤️', label: 'Heart' },
  support: { emoji: '🤝', label: 'Support' },
  laugh: { emoji: '😂', label: 'Laugh' },
  sad: { emoji: '😢', label: 'Sad' }
}

// Computed properties
const totalReactions = computed(() => {
  return props.reactionsSummary?.total_count || 0;
})

const topReactions = computed(() => {
  const reactionCounts = props.reactionsSummary?.reaction_counts || {}
  
  // Sort reactions by count and get top 3
  return Object.entries(reactionCounts)
    .sort(([, a], [, b]) => (b?.count || 0) - (a?.count || 0))
    .slice(0, 3)
    .map(([type]) => type)
    .filter(type => reactionCounts[type]?.count > 0)
})

// Methods
const getReactionEmoji = (type) => {
  return reactionTypes[type]?.emoji || '👍'
}

const getReactionLabel = (type) => {
  return reactionTypes[type]?.label || 'React'
}

const formatReactionCount = (count) => {
  if (count === 1) return '1'
  if (count < 1000) return count.toString()
  if (count < 1000000) return `${(count / 1000).toFixed(1)}K`
  return `${(count / 1000000).toFixed(1)}M`
}

const openReactionsModal = () => {
  emit('open-reactions-modal', props.postId)
}
</script>

<style scoped>
.transition-transform {
  transition: transform 0.2s ease;
}

.transition-colors {
  transition: background-color 0.2s ease, color 0.2s ease;
}
</style>
