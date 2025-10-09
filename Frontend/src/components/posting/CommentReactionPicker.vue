<template>
  <div
    v-if="showPicker"
    class="comment-reaction-picker absolute bottom-full left-0 mb-2 bg-white rounded-full shadow-lg border border-gray-200 p-1 z-50"
    @click.stop
  >
    <div class="flex items-center space-x-1">
      <button
        v-for="reaction in reactionTypes"
        :key="reaction.type"
        @click="selectReaction(reaction.type)"
        @mouseenter="hoveredReaction = reaction.type"
        @mouseleave="hoveredReaction = null"
        class="reaction-button"
        :class="{ 'scale-125': hoveredReaction === reaction.type }"
        :title="reaction.label"
      >
        <span class="text-lg">{{ reaction.emoji }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Props
const props = defineProps({
  showPicker: {
    type: Boolean,
    default: false
  },
  commentId: {
    type: [String, Number],
    required: true
  }
})

// Emits
const emit = defineEmits(['reaction-selected', 'close'])

// Local state
const hoveredReaction = ref(null)

// Reaction types (Facebook-style)
const reactionTypes = [
  { type: 'like', emoji: '👍', label: 'Like' },
  { type: 'heart', emoji: '❤️', label: 'Love' },
  { type: 'laugh', emoji: '😂', label: 'Haha' },
  { type: 'sad', emoji: '😢', label: 'Sad' },
  { type: 'angry', emoji: '😠', label: 'Angry' },
  { type: 'applaud', emoji: '👏', label: 'Applaud' }
]

// Methods
const selectReaction = (reactionType) => {
  emit('reaction-selected', {
    commentId: props.commentId,
    reactionType: reactionType
  })
  emit('close')
}
</script>

<style scoped>
.comment-reaction-picker {
  animation: slideUp 0.2s ease-out;
}

.reaction-button {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  cursor: pointer;
}

.reaction-button:hover {
  background-color: #f3f4f6;
  transform: scale(1.2);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.8);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>
