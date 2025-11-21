<template>
  <div>
    <div class="comment-item flex space-x-2 sm:space-x-3 py-1 sm:py-2 group items-start">
    <!-- User Avatar -->
    <img
      :src="comment.user?.profile_picture || '/default-avatar.png'"
      :alt="comment.user?.full_name || `${comment.user?.first_name} ${comment.user?.last_name}`.trim() || 'User'"
      class="comment-avatar"
    />

    <!-- Comment Content -->
    <div class="flex-1 min-w-0">
      <!-- Comment Bubble -->
      <div class="relative">
        <div class="bg-gray-100 rounded-lg sm:rounded-xl md:rounded-2xl px-3 py-2 sm:px-3 sm:py-2 md:px-4 md:py-3 max-w-[85%] sm:max-w-[80%] md:max-w-md lg:max-w-lg xl:max-w-xl">
          <div class="font-semibold text-xs sm:text-sm md:text-base text-gray-900 mb-1">
            {{ comment.user?.full_name || `${comment.user?.first_name} ${comment.user?.last_name}`.trim() || 'Anonymous' }}
          </div>
          <MentionText
            :content="comment.content"
            :mentions="comment.mentions || []"
            :available-users="comment.mentioned_users || {}"
            className="text-xs sm:text-sm md:text-base text-gray-800 leading-relaxed break-words"
          />
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
      <div class="flex items-center flex-wrap gap-2 sm:gap-3 md:gap-4 mt-1 sm:mt-2 ml-2 sm:ml-3">
        <!-- Like Button -->
        <button
          @click="toggleLike"
          :class="[
            'text-xs sm:text-sm font-medium transition-colors py-1 px-1 sm:px-2 rounded hover:bg-gray-100 touch-manipulation',
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
          class="text-xs sm:text-sm font-medium text-gray-500 hover:text-blue-600 transition-colors py-1 px-1 sm:px-2 rounded hover:bg-gray-100 touch-manipulation"
        >
          Reply
        </button>

        <!-- Delete Button (Facebook-style permissions) -->
        <button
          v-if="comment.can_delete"
          @click="showDeleteConfirmation"
          class="text-xs sm:text-sm font-medium text-gray-500 hover:text-red-600 transition-colors py-1 px-1 sm:px-2 rounded hover:bg-gray-100 touch-manipulation sm:opacity-0 sm:group-hover:opacity-100"
        >
          Delete
        </button>

        <!-- Time -->
        <span class="text-xs sm:text-sm text-gray-400 flex-shrink-0">
          {{ formatTimeAgo(comment.created_at) }}
        </span>

        <!-- Reaction Picker Trigger -->
        <button
          @click="toggleReactionPicker"
          class="text-xs sm:text-sm text-gray-400 hover:text-gray-600 transition-colors py-1 px-1 sm:px-2 rounded hover:bg-gray-100 touch-manipulation sm:opacity-0 sm:group-hover:opacity-100"
        >
          <span class="text-base sm:text-lg">😊</span>
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

      <!-- Replies -->
      <div v-if="comment.replies && comment.replies.length > 0" class="mt-2 ml-2 sm:ml-3 md:ml-4 pl-2 sm:pl-3 border-l-2 border-gray-200 space-y-1 sm:space-y-2">
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

  <!-- Delete Confirmation Modal -->
  <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Delete Comment</h3>
      <p class="text-gray-600 mb-6">Are you sure you want to delete this comment? This action cannot be undone.</p>
      <div class="flex justify-end space-x-3">
        <button
          @click="hideDeleteConfirmation"
          class="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
        <button
          @click="confirmDelete"
          class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
        >
          Delete
        </button>
      </div>
    </div>
  </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import CommentReactionPickerSimple from './CommentReactionPickerSimple.vue'
import CommentReactionSummary from './CommentReactionSummary.vue'
import MentionText from '@/components/common/MentionText.vue'

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
  },
  isReplying: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['react-to-comment', 'reply-to-comment', 'delete-comment', 'reply', 'like', 'edit', 'delete', 'cancelReply'])

// Local state
const showReactionPicker = ref(false)

// Methods
const toggleReply = () => {
  const data = {
    commentId: props.comment.id,
    authorName: props.comment.user?.full_name || 'Someone'
  }
  
  // Emit both event names for compatibility
  emit('reply-to-comment', data)
  emit('reply', data)
}

const handleReplyToComment = (data) => {
  emit('reply-to-comment', data)
  emit('reply', data)
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

// Delete confirmation modal
const showDeleteModal = ref(false)

const showDeleteConfirmation = () => {
  showDeleteModal.value = true
}

const hideDeleteConfirmation = () => {
  showDeleteModal.value = false
}

const confirmDelete = () => {
  // Emit both event names for compatibility
  emit('delete-comment', props.comment.id)
  emit('delete', props.comment.id)
  hideDeleteConfirmation()
}

// Missing methods
const toggleLike = () => {
  const currentReaction = props.comment.reactions_summary?.user_reaction
  const data = {
    commentId: props.comment.id,
    reactionType: currentReaction === 'like' ? null : 'like'
  }
  
  // Emit both event names for compatibility
  emit('react-to-comment', data)
  emit('like', data)
}

const toggleReactionPicker = () => {
  showReactionPicker.value = !showReactionPicker.value
}

const handleReactionSelected = (data) => {
  emit('react-to-comment', data)
  showReactionPicker.value = false
}
</script>

<style scoped>
.comment-item {
  position: relative;
  display: flex;
  gap: 0.5rem;
  padding: 0.25rem 0;
  align-items: flex-start;
}

@media (min-width: 640px) {
  .comment-item {
    gap: 0.75rem;
    padding: 0.5rem 0;
  }
}

.comment-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
  aspect-ratio: 1 / 1;
}

@media (min-width: 640px) {
  .comment-avatar {
    width: 2.25rem;
    height: 2.25rem;
  }
}

@media (min-width: 768px) {
  .comment-avatar {
    width: 2.5rem;
    height: 2.5rem;
  }
}

.group:hover .group-hover\:opacity-100 {
  opacity: 1;
}

/* Touch-friendly interactions for mobile */
@media (hover: none) and (pointer: coarse) {
  .sm\:opacity-0.sm\:group-hover\:opacity-100 {
    opacity: 1 !important;
  }
}

/* Better word breaking for long text on mobile */
.break-words {
  word-wrap: break-word;
  word-break: break-word;
  hyphens: auto;
}

/* Touch manipulation for better mobile performance */
.touch-manipulation {
  touch-action: manipulation;
}
</style>
