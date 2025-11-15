<template>
  <div 
    :class="[
      'whitespace-pre-wrap leading-relaxed',
      className
    ]"
    v-html="formattedContent"
  />
</template>

<script setup>
import { computed } from 'vue'
import { parseMentions, convertMentionsForDisplay } from '@/utils/mentionUtils'

// Props
const props = defineProps({
  content: {
    type: String,
    required: true,
    default: ''
  },
  mentions: {
    type: Array,
    default: () => []
  },
  className: {
    type: String,
    default: ''
  }
})

// Computed formatted content
const formattedContent = computed(() => {
  if (!props.content) return ''
  
  // First convert backend mentions (@username) to display format (@Full Name) if needed
  const displayContent = convertMentionsForDisplay(props.content, props.mentions)
  
  // Then parse and format mentions as bold
  return parseMentions(displayContent)
})
</script>

<style scoped>
/* Global mention styling */
:deep(.mention-text) {
  font-weight: bold;
  color: #2563eb; /* blue-600 */
  transition: color 0.2s ease;
}

/* Dark mode mention styling */
:deep([data-theme="dark"] .mention-text) {
  color: #60a5fa; /* blue-400 */
}

:deep(.mention-text:hover) {
  cursor: pointer;
  color: #1d4ed8; /* blue-700 */
}

:deep([data-theme="dark"] .mention-text:hover) {
  color: #93c5fd; /* blue-300 */
}
</style>