<template>
  <div class="reaction-picker" v-if="showPicker" @click.stop>
    <div class="reaction-buttons">
      <button
        v-for="reaction in reactionTypes"
        :key="reaction.type"
        @click="addReaction(reaction.type)"
        class="reaction-btn"
        :title="reaction.label"
      >
        {{ reaction.emoji }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  showPicker: {
    type: Boolean,
    default: false
  },
  messageId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['reaction-selected', 'close'])

const reactionTypes = [
  { type: 'like', emoji: '👍', label: 'Like' },
  { type: 'heart', emoji: '❤️', label: 'Love' },
  { type: 'haha', emoji: '😂', label: 'Haha' },
  { type: 'sad', emoji: '😢', label: 'Sad' },
  { type: 'angry', emoji: '😠', label: 'Angry' },
  { type: 'care', emoji: '🤗', label: 'Care' },
  { type: 'dislike', emoji: '👎', label: 'Dislike' }
]

const addReaction = (reactionType) => {
  emit('reaction-selected', {
    messageId: props.messageId,
    reactionType: reactionType
  })
  emit('close')
}
</script>

<style scoped>
.reaction-picker {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 25px;
  padding: 8px 16px; /* Increased horizontal padding */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  margin-bottom: 5px;
  white-space: nowrap; /* Prevent wrapping */
  min-width: 380px; /* Ensure enough width for all 7 reactions */
}

.reaction-buttons {
  display: flex;
  gap: 6px; /* Slightly reduced gap to fit better */
  align-items: center;
  justify-content: center;
}

.reaction-btn {
  background: none;
  border: none;
  font-size: 20px;
  padding: 6px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  flex-shrink: 0; /* Prevent buttons from shrinking */
}

.reaction-btn:hover {
  background-color: #f3f4f6;
  transform: scale(1.2);
}

.reaction-btn:active {
  transform: scale(1.1);
}
</style>
