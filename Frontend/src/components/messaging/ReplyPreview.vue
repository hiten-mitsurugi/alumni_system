<template>
  <div v-if="replyingTo" class="bg-gray-50 border-l-3 border-blue-400 px-3 py-2 mx-4 mb-1">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2 flex-1 min-w-0">
        <svg class="w-3 h-3 text-blue-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
        </svg>
        <span class="text-xs text-blue-600 font-medium flex-shrink-0">
          {{ replyingTo.sender?.first_name || 'Unknown' }}:
        </span>
        <span class="text-xs text-gray-600 truncate">
          {{ replyingTo.content || 'Attachment' }}
        </span>
      </div>
      
      <!-- Close button -->
      <button
        @click="$emit('cancel-reply')"
        class="ml-2 p-0.5 text-gray-400 hover:text-gray-600 rounded flex-shrink-0"
        title="Cancel reply"
      >
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'

const props = defineProps({
  replyingTo: {
    type: Object,
    default: null
  }
})

defineEmits(['cancel-reply'])

// Debug logging
console.log('ReplyPreview: Initial replyingTo prop:', props.replyingTo)

watch(() => props.replyingTo, (newValue) => {
  console.log('ReplyPreview: replyingTo prop changed to:', newValue)
  console.log('ReplyPreview: Component should be visible:', !!newValue)
}, { immediate: true, deep: true })

const hasImageAttachment = computed(() => {
  return props.replyingTo?.attachments?.some(att => 
    att.file_type && att.file_type.startsWith('image/')
  ) || false
})

const hasFileAttachment = computed(() => {
  return props.replyingTo?.attachments?.some(att => 
    att.file_type && !att.file_type.startsWith('image/')
  ) || false
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
