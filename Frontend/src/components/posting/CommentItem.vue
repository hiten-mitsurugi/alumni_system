<template>
  <div class="comment-item flex space-x-3 py-2 group">
    <!-- User Avatar -->
    <img 
      :src="comment.user?.profile_picture || '/default-avatar.png'"
      :alt="comment.user?.name || 'User'"
      class="comment-avatar"
    />
    
    <!-- Comment Content -->
    <div class="flex-1 min-w-0">
      <!-- Comment Bubble -->
      <div class="relative">
        <div class="bg-gray-100 rounded-2xl px-3 py-2 max-w-xs lg:max-w-md">
          <div class="font-semibold text-sm text-gray-900 mb-1">
            {{ comment.user?.name || 'Anonymous' }}
          </div>
          <div class="text-sm text-gray-800 leading-relaxed">
            {{ comment.content }}
          </div>
        </div>
        
        <!-- Reaction Summary (Facebook-style) -->
        <CommentReactionSummary
          v-if="comment.reactions_summary && comment.reactions_summary.total_count > 0"
          :reactions-summary="comment.reactions_summary"
          :comment-id="comment.id"
          @open-reactions-modal="openReactionsModal"
          class="mt-1"
        />
      </div>
      
      <!-- Comment Actions -->
      <div class="flex items-center space-x-4 mt-1 ml-3">
        <!-- Like Button -->
        <button
          @click="toggleLike"
          :class="[
            'text-xs font-medium transition-colors',
            comment.reactions_summary?.user_reaction === 'like'
              ? 'text-blue-600'
              : 'text-gray-500 hover:text-blue-600'
          ]"
        >
          Like
        </button>
        
        <!-- Reply Button -->
        <button
          @click="toggleReply"
          class="text-xs font-medium text-gray-500 hover:text-blue-600 transition-colors"
        >
          Reply
        </button>
        
        <!-- Time -->
        <span class="text-xs text-gray-400">
          {{ formatTimeAgo(comment.created_at) }}
        </span>
        
        <!-- Reaction Picker Trigger -->
        <button
          @click="toggleReactionPicker"
          class="text-xs text-gray-400 hover:text-gray-600 transition-colors opacity-0 group-hover:opacity-100"
        >
          <span class="text-sm">😊</span>
        </button>
      </div>
      
      <!-- Reaction Picker -->
      <CommentReactionPickerSimple
        :show-picker="showReactionPicker"
        :comment-id="comment.id"
        @reaction-selected="handleReactionSelected"
        @close="showReactionPicker = false"
        class="relative"
      />
      
      <!-- Reply Form -->
      <div v-if="showReplyForm" class="mt-3 ml-3">
        <div class="flex space-x-2">
          <img 
            :src="userProfilePicture || '/default-avatar.png'"
            alt="Your avatar"
            class="reply-avatar"
          />
          <div class="flex-1">
            <input
              v-model="replyText"
              @keypress.enter="submitReply"
              @keypress.escape="cancelReply"
              type="text"
              placeholder="Write a reply..."
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-full focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ref="replyInput"
            />
          </div>
        </div>
      </div>
      
      <!-- Replies -->
      <div v-if="comment.replies && comment.replies.length > 0" class="mt-2 ml-3 space-y-2">
        <CommentItem
          v-for="reply in comment.replies"
          :key="reply.id"
          :comment="reply"
          :user-profile-picture="userProfilePicture"
          :current-user-id="currentUserId"
          @react-to-comment="handleReactionSelected"
          @reply-to-comment="handleReplyToComment"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import CommentReactionPickerSimple from './CommentReactionPickerSimple.vue'
import CommentReactionSummary from './CommentReactionSummary.vue'

// Props
const props = defineProps({
  comment: {
    type: Object,
    required: true
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
const emit = defineEmits(['react-to-comment', 'reply-to-comment'])

// Local state
const showReactionPicker = ref(false)
const showReplyForm = ref(false)
const replyText = ref('')

// Methods
const toggleLike = () => {
  const currentReaction = props.comment.reactions_summary?.user_reaction
  if (currentReaction === 'like') {
    // Remove like
    emit('react-to-comment', {
      commentId: props.comment.id,
      reactionType: null // Remove reaction
    })
  } else {
    // Add like
    emit('react-to-comment', {
      commentId: props.comment.id,
      reactionType: 'like'
    })
  }
}

const toggleReactionPicker = () => {
  showReactionPicker.value = !showReactionPicker.value
}

const handleReactionSelected = (data) => {
  emit('react-to-comment', data)
  showReactionPicker.value = false
}

const toggleReply = () => {
  showReplyForm.value = !showReplyForm.value
  if (showReplyForm.value) {
    nextTick(() => {
      const input = document.querySelector('input[placeholder="Write a reply..."]')
      if (input) input.focus()
    })
  }
}

const submitReply = () => {
  const content = replyText.value.trim()
  if (content) {
    emit('reply-to-comment', {
      commentId: props.comment.id,
      content: content
    })
    replyText.value = ''
    showReplyForm.value = false
  }
}

const cancelReply = () => {
  replyText.value = ''
  showReplyForm.value = false
}

const handleReplyToComment = (data) => {
  emit('reply-to-comment', data)
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

const openReactionsModal = (commentId) => {
  // TODO: Implement reactions modal for comments
  console.log('Open reactions modal for comment:', commentId)
}
</script>

<style scoped>
.comment-item {
  position: relative;
  display: flex;
  gap: 0.75rem;
  padding: 0.5rem 0;
}

.comment-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.reply-avatar {
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.group:hover .group-hover\:opacity-100 {
  opacity: 1;
}
</style>
