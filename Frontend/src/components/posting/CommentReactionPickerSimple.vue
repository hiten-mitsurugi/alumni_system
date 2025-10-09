<template>
  <div
    v-if="showPicker"
    class="reaction-picker"
    @click.stop
  >
    <div class="reaction-buttons">
      <button
        v-for="reaction in reactionTypes"
        :key="reaction.type"
        @click="selectReaction(reaction.type)"
        class="reaction-btn"
        :title="reaction.label"
      >
        <span class="reaction-emoji">{{ reaction.emoji }}</span>
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
.reaction-picker {
  position: absolute;
  bottom: 100%;
  left: 0;
  margin-bottom: 0.5rem;
  background: white;
  border-radius: 9999px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  padding: 0.25rem;
  z-index: 50;
  animation: slideUp 0.2s ease-out;
}

.reaction-buttons {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.reaction-btn {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
  background: transparent;
}

.reaction-btn:hover {
  background-color: #f3f4f6;
  transform: scale(1.2);
}

.reaction-emoji {
  font-size: 1.125rem;
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

