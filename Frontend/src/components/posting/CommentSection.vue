<template>
  <div v-if="showComments" class="border-t border-gray-200 bg-white">
    <!-- Add Comment -->
    <div class="px-4 py-2 border-b border-gray-200">
      <div class="flex space-x-2 items-center">
        <img 
          :src="userProfilePicture || '/default-avatar.png'"
          alt="Your Profile"
          class="w-6 h-6 rounded-full object-cover flex-shrink-0"
        />
        <div class="flex-1 flex space-x-2 items-center">
          <input
            v-model="localComment"
            type="text"
            placeholder="Write a comment..."
            @keypress.enter="addComment"
            class="flex-1 px-3 py-1.5 text-sm border border-gray-300 rounded-full focus:ring-1 focus:ring-orange-500 focus:border-orange-500 transition-all"
          />
          <button
            @click="addComment"
            :disabled="!localComment?.trim()"
            class="px-3 py-1.5 bg-orange-600 text-white rounded-full hover:bg-orange-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all text-xs font-medium"
          >
            Post
          </button>
        </div>
      </div>
    </div>
    
    <!-- Comments List -->
    <div v-if="comments && comments.length > 0" class="px-4 py-2 space-y-2">
      <CommentItem
        v-for="comment in comments"
        :key="comment.id"
        :comment="comment"
        :user-profile-picture="userProfilePicture"
        :current-user-id="currentUserId"
        @react-to-comment="handleReactToComment"
        @reply-to-comment="handleReplyToComment"
        @delete-comment="handleDeleteComment"
      />
    </div>
    
    <!-- Empty Comments State -->
    <div v-else class="px-4 py-6 text-center text-gray-500">
      <svg class="mx-auto h-8 w-8 text-gray-300 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
      <p class="text-sm">No comments yet</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import CommentItem from '@/components/posting/CommentItem.vue'

// Props
const props = defineProps({
  postId: {
    type: [String, Number],
    required: true
  },
  showComments: {
    type: Boolean,
    default: false
  },
  comments: {
    type: Array,
    default: () => []
  },
  userProfilePicture: {
    type: String,
    default: ''
  },
  currentUserId: {
    type: Number,
    required: true
  }
})

// Emits
const emit = defineEmits(['add-comment', 'react-to-comment', 'reply-to-comment', 'delete-comment'])

// Local state
const localComment = ref('')

// Methods
const addComment = () => {
  const content = localComment.value?.trim()
  if (!content) return
  
  emit('add-comment', props.postId, content)
  localComment.value = ''
}

const handleReactToComment = (data) => {
  emit('react-to-comment', data)
}

const handleReplyToComment = (data) => {
  emit('reply-to-comment', data)
}

const handleDeleteComment = (commentId) => {
  emit('delete-comment', commentId)
}
</script>

<style scoped>
/* Clean desktop-focused styles */
input:focus {
  outline: none;
}

button:hover:not(:disabled) {
  transform: translateY(-0.5px);
}

.transition-all {
  transition: all 0.2s ease;
}

/* Subtle shadows for desktop */
.border {
  border-width: 1px;
}

/* Compact, clean layout for desktop */
.rounded-full {
  border-radius: 9999px;
}

.rounded-lg {
  border-radius: 0.5rem;
}
</style>
