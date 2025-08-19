<template>
  <div class="message-reactions" v-if="hasReactions">
    <div class="reaction-summary">
      <button
        v-for="(reactionData, reactionType) in reactionStats.reactions_by_type"
        :key="reactionType"
        @click="toggleReaction(reactionType)"
        class="reaction-summary-btn"
        :class="{ 'user-reacted': userHasReacted(reactionType) }"
        :title="getReactionTooltip(reactionData)"
      >
        <span class="reaction-emoji">{{ reactionData.emoji }}</span>
        <span class="reaction-count">{{ reactionData.count }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, computed } from 'vue'

const props = defineProps({
  reactionStats: {
    type: Object,
    default: () => ({
      total_reactions: 0,
      reactions_by_type: {}
    })
  },
  currentUserId: {
    type: Number,
    required: true
  },
  messageId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['toggle-reaction'])

const hasReactions = computed(() => {
  return props.reactionStats.total_reactions > 0
})

const userHasReacted = (reactionType) => {
  const reactionData = props.reactionStats.reactions_by_type[reactionType]
  if (!reactionData || !reactionData.users) return false
  
  return reactionData.users.some(user => user.id === props.currentUserId)
}

const getReactionTooltip = (reactionData) => {
  if (!reactionData.users || reactionData.users.length === 0) return ''
  
  const names = reactionData.users.map(user => user.name)
  if (names.length === 1) return names[0]
  if (names.length === 2) return `${names[0]} and ${names[1]}`
  if (names.length === 3) return `${names[0]}, ${names[1]} and ${names[2]}`
  return `${names[0]}, ${names[1]} and ${names.length - 2} others`
}

const toggleReaction = (reactionType) => {
  emit('toggle-reaction', {
    messageId: props.messageId,
    reactionType: reactionType,
    isRemoving: userHasReacted(reactionType)
  })
}
</script>

<style scoped>
.message-reactions {
  margin-top: 6px;
}

.reaction-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.reaction-summary-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 24px;
}

.reaction-summary-btn:hover {
  background: #e5e7eb;
  transform: scale(1.05);
}

.reaction-summary-btn.user-reacted {
  background: #dbeafe;
  border-color: #3b82f6;
  color: #1e40af;
}

.reaction-emoji {
  font-size: 14px;
  line-height: 1;
}

.reaction-count {
  font-weight: 500;
  font-size: 11px;
}
</style>
