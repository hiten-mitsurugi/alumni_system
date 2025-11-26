<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm bg-opacity-50 backdrop-blur-sm"
    @click.self="closeModal"
  >
    <!-- Mobile Layout -->
    <div
      class="flex flex-col w-full h-full overflow-hidden bg-white lg:hidden"
      style="height: calc(100vh - 80px); max-height: calc(100vh - 80px);"
      @click.stop
    >
      <!-- Mobile Header -->
      <div class="flex items-center justify-between shrink-0 p-4 bg-white border-b border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900 truncate">
          {{ post.user.full_name }}'s Post
        </h3>
        <button
          @click="closeModal"
          class="flex-shrink-0 p-2 transition-colors rounded-full hover:bg-gray-100"
        >
          <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Scrollable Content Area -->
      <div class="flex-1 min-h-0 overflow-y-auto">
        <!-- Mobile Media Section -->
        <div
          v-if="hasMedia"
          class="flex items-center justify-center shrink-0 bg-gray-900"
          style="height: 35vh; min-height: 200px;"
        >
        <div class="relative flex items-center justify-center w-full h-full p-2">
          <!-- Image Display -->
          <div v-if="currentMediaType === 'image'" class="relative flex items-center justify-center w-full h-full">
            <img
              :src="getMediaUrl(currentMediaUrl)"
              :alt="post.title"
              class="object-contain w-full h-full max-w-full max-h-full rounded"
              loading="lazy"
              @load="onImageLoad"
              @error="onImageError"
            />
          </div>

          <!-- Video Display -->
          <div v-else-if="currentMediaType === 'video'" class="relative flex items-center justify-center w-full h-full">
            <video
              :src="getMediaUrl(currentMediaUrl)"
              controls
              class="object-contain w-full h-full max-w-full max-h-full rounded"
              @error="onVideoError"
            />
          </div>

          <!-- Navigation for multiple media -->
          <div v-if="mediaFiles.length > 1" class="absolute inset-0 flex items-center justify-between p-2 pointer-events-none">
            <button
              v-if="currentMediaIndex > 0"
              @click="previousMedia"
              class="p-2 text-white transition-all bg-black bg-opacity-50 rounded-full pointer-events-auto hover:bg-opacity-75"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div class="flex-1"></div>
            <button
              v-if="currentMediaIndex < mediaFiles.length - 1"
              @click="nextMedia"
              class="p-2 text-white transition-all bg-black bg-opacity-50 rounded-full pointer-events-auto hover:bg-opacity-75"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          <!-- Media Counter -->
          <div v-if="mediaFiles.length > 1" class="absolute px-2 py-1 text-xs text-white bg-black bg-opacity-50 rounded-full bottom-2 right-2">
            {{ currentMediaIndex + 1 }} / {{ mediaFiles.length }}
          </div>
        </div>
      </div>

      <!-- Mobile Content Area -->
      <div class="flex flex-col flex-1 min-h-0 overflow-hidden">
        <!-- Post Content -->
        <div class="flex-shrink-0 p-4 bg-white border-b border-gray-200">
          <PostHeader
            :post="post"
            :categories="categories"
            :user-profile-picture="userProfilePicture"
            :show-menu="false"
          />
          <h3 v-if="post.title" class="mt-3 mb-2 text-base font-semibold text-gray-900">
            {{ post.title }}
          </h3>
          <p v-if="post.content" class="text-sm leading-relaxed text-gray-700 whitespace-pre-wrap">
            {{ post.content }}
          </p>
        </div>

        <!-- Engagement Summary -->
        <div v-if="hasEngagement" class="shrink-0 px-4 py-3 bg-white border-b border-gray-200">
          <ReactionSummary
            :reactions-summary="post.reactions_summary"
            :post-id="post.id"
            @open-reactions-modal="openReactionsModal"
          />
        </div>

        <!-- Post Actions -->
        <div class="shrink-0 px-4 py-3 border-b border-gray-200 bg-gray-50">
          <PostActions
            :post-id="post.id"
            :selected-reaction="selectedReaction"
            size="small"
            @react-to-post="handleReaction"
            @comment-clicked="() => {}"
            @share-post="handleShare"
            @copy-link="handleCopyLink"
          />
        </div>

        <!-- Comments Header -->
        <div class="shrink-0 px-4 py-2 border-b border-gray-200 bg-gray-50">
          <h4 class="text-sm font-semibold text-gray-900">
            Comments ({{ comments.length || 0 }})
          </h4>
        </div>

        <!-- Comments List -->
        <div class="flex-1 min-h-0 px-4 py-3 overflow-y-auto bg-gray-50">
          <div v-if="comments.length === 0" class="py-8 text-center text-gray-500">
            <svg class="w-8 h-8 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <p class="text-sm">No comments yet</p>
            <p class="text-xs">Be the first to comment!</p>
          </div>

          <div v-for="comment in comments" :key="comment.id" class="mb-3">
            <CommentItem
              :comment="comment"
              :user-profile-picture="userProfilePicture"
              :current-user-id="currentUserId"
              @react-to-comment="handleReactToComment"
              @reply-to-comment="handleReplyToComment"
              @delete-comment="handleDeleteComment"
            />
          </div>
        </div>
      </div>

      <!-- Mobile Comment Input - Fixed at bottom -->
      <div class="shrink-0 px-4 py-3 bg-white border-t border-gray-200" style="padding-bottom: calc(env(safe-area-inset-bottom) + 16px);">
        <!-- Reply indicator -->
          <div v-if="isReplying" class="px-3 py-2 mb-2 text-sm border border-blue-200 rounded-lg bg-blue-50">
            <span class="text-blue-600">📝 Replying to {{ replyContext?.authorName }}</span>
            <button
              @click="cancelReply"
              class="ml-2 font-medium text-blue-500 hover:text-blue-700"
            >
              Cancel
            </button>
          </div>

          <div class="flex items-center space-x-3">
            <img
              :src="getProfilePictureUrl(userProfilePicture)"
              alt="Your avatar"
              class="flex-shrink-0 object-cover w-8 h-8 rounded-full"
            />
            <!-- Emoji Button -->
            <button
              @click="toggleEmojiPicker"
              class="flex-shrink-0 p-2 text-lg text-gray-500 transition-all duration-200 rounded-full emoji-button hover:text-orange-600 hover:bg-orange-100 focus:outline-none focus:ring-2 focus:ring-orange-500"
              title="Add emoji"
            >
              😀
            </button>
            <div class="flex-1">
              <MentionTextarea
                v-model="newComment"
                @mention="handleMention"
                @submit="addComment"
                :placeholder="isReplying ? `Reply to ${replyContext?.authorName}... Use @ to mention someone` : 'Write a comment... Use @ to mention someone'"
                :rows="1"
                class="w-full text-sm transition-all duration-200 border border-gray-300 rounded-full mobile-comment-input focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                ref="commentInputRef"
              />
            </div>
            <button
              @click="addComment"
              :disabled="!newComment.trim() || isSubmittingComment"
              class="flex items-center justify-center flex-shrink-0 w-8 h-8 font-medium text-white transition-all duration-200 bg-orange-600 rounded-full hover:bg-orange-500 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>

          <!-- Emoji Picker -->
          <EmojiPicker
            :isVisible="showEmojiPicker"
            @emoji-selected="insertEmoji"
            @close="closeEmojiPicker"
          />
        </div>
      </div>
    </div>

    <!-- Desktop Layout -->
    <div 
      :class="[
        'hidden h-full mx-auto overflow-hidden bg-white rounded-lg shadow-2xl lg:flex',
        hasMedia ? 'max-w-6xl' : 'max-w-3xl w-full'
      ]"
    >
      <!-- Desktop Media Section -->
      <div
        v-if="hasMedia"
        class="flex items-center justify-center h-full bg-gray-900 basis-2/3"
      >
        <div class="relative flex items-center justify-center w-full h-full p-4">
          <!-- Image Display -->
          <div v-if="currentMediaType === 'image'" class="relative flex items-center justify-center w-full h-full">
            <img
              :src="getMediaUrl(currentMediaUrl)"
              :alt="post.title"
              class="object-contain w-full h-full max-w-full max-h-full rounded-lg"
              style="max-height: calc(100vh - 80px); max-width: calc(100vw - 40px);"
              loading="lazy"
              @load="onImageLoad"
              @error="onImageError"
            />
          </div>

          <!-- Video Display -->
          <div v-else-if="currentMediaType === 'video'" class="relative flex items-center justify-center w-full h-full">
            <video
              :src="getMediaUrl(currentMediaUrl)"
              controls
              class="object-contain w-full h-full max-w-full max-h-full rounded-lg"
              style="max-height: calc(100vh - 80px); max-width: calc(100vw - 40px);"
              @error="onVideoError"
            />
          </div>

          <!-- Navigation for multiple media -->
          <div v-if="mediaFiles.length > 1" class="absolute inset-0 flex items-center justify-between p-2 pointer-events-none">
            <button
              v-if="currentMediaIndex > 0"
              @click="previousMedia"
              class="p-3 text-white transition-all bg-black bg-opacity-50 rounded-full pointer-events-auto hover:bg-opacity-75"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div class="flex-1"></div>
            <button
              v-if="currentMediaIndex < mediaFiles.length - 1"
              @click="nextMedia"
              class="p-3 text-white transition-all bg-black bg-opacity-50 rounded-full pointer-events-auto hover:bg-opacity-75"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          <!-- Media Counter -->
          <div v-if="mediaFiles.length > 1" class="absolute px-3 py-1 text-sm text-white bg-black bg-opacity-50 rounded-full bottom-4 right-4">
            {{ currentMediaIndex + 1 }} / {{ mediaFiles.length }}
          </div>
        </div>
      </div>

      <!-- Desktop Content Section -->
      <div 
        :class="[
          'flex flex-col h-full bg-white border-l border-gray-200',
          hasMedia ? 'basis-1/3 min-w-[400px]' : 'w-full'
        ]"
      >
        <!-- Desktop Header -->
        <div class="flex items-center justify-between p-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900 truncate">
            {{ post.user.full_name }}'s Post
          </h3>
          <button
            @click="closeModal"
            class="p-2 transition-colors rounded-full hover:bg-gray-100"
          >
            <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Desktop Content Area -->
        <div class="flex flex-col flex-1 overflow-hidden">
          <!-- Post Header -->
          <div class="p-4 border-b border-gray-200">
            <PostHeader
              :post="post"
              :categories="categories"
              :user-profile-picture="userProfilePicture"
              :show-menu="false"
            />
          </div>

          <!-- Post Content -->
          <div class="p-4 border-b border-gray-200">
            <h3 v-if="post.title" class="mb-3 text-lg font-semibold text-gray-900">
              {{ post.title }}
            </h3>
            <p v-if="post.content" class="text-base leading-relaxed text-gray-700 whitespace-pre-wrap">
              {{ post.content }}
            </p>
          </div>

          <!-- Engagement Summary -->
          <div v-if="hasEngagement" class="px-4 py-3 border-b border-gray-200">
            <ReactionSummary
              :reactions-summary="post.reactions_summary"
              :post-id="post.id"
              :current-user-id="currentUserId"
              @show-reactions-modal="showReactionsModal = true"
            />
          </div>

          <!-- Post Actions -->
          <div class="px-4 py-3 border-b border-gray-200">
            <PostActions
              :post-id="post.id"
              :post="post"
              :current-user-id="currentUserId"
              @reaction-updated="handleReactionUpdated"
              @save-updated="handleSave"
              @edit-post="handleEdit"
              @delete-post="handleDelete"
            />
          </div>

          <!-- Comments Section -->
          <div class="flex-1 px-4 pt-3 overflow-y-auto">
            <div v-if="comments.length > 0" class="mb-4 space-y-4">
              <CommentItem
                v-for="comment in comments"
                :key="comment.id"
                :comment="comment"
                :current-user-id="currentUserId"
                :is-replying="replyContext?.commentId === comment.id"
                @reply="handleReplyToComment"
                @reply-to-comment="handleReplyToComment"
                @like="handleCommentLike"
                @edit="handleCommentEdit"
                @delete="handleCommentDelete"
                @delete-comment="handleDeleteComment"
                @cancel-reply="cancelReply"
              />
            </div>
            <div v-else class="py-8 text-center text-gray-500">
              <svg class="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <p class="mb-1 text-lg font-medium text-gray-400">No comments yet</p>
              <p class="text-sm text-gray-400">Be the first to share your thoughts!</p>
            </div>
          </div>

          <!-- Comment Input -->
          <div class="p-4 border-t border-gray-200">
            <!-- Reply Context -->
            <div v-if="isReplying" class="p-3 mb-3 border-l-4 border-orange-500 rounded-lg bg-gray-50">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-2">
                  <span class="text-sm text-gray-600">Replying to</span>
                  <span class="text-sm font-medium text-gray-900">{{ replyContext.authorName }}</span>
                </div>
                <button
                  @click="cancelReply"
                  class="text-gray-400 transition-colors hover:text-gray-600"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <p class="mt-1 text-sm text-gray-700 line-clamp-2">{{ replyContext.content }}</p>
            </div>

            <div class="flex items-end space-x-3">
              <img
                :src="getProfilePictureUrl(userProfilePicture)"
                alt="Your avatar"
                class="flex-shrink-0 object-cover w-10 h-10 rounded-full"
              />
              <button
                @click="toggleEmojiPicker"
                class="flex-shrink-0 p-3 text-sm text-gray-500 transition-all duration-200 rounded-full emoji-button hover:text-orange-600 hover:bg-orange-100 focus:outline-none focus:ring-2 focus:ring-orange-500"
                title="Add emoji"
              >
                😀
              </button>
              <div class="flex-1">
                <MentionTextarea
                  v-model="newComment"
                  @mention="handleMention"
                  @submit="addComment"
                  :placeholder="isReplying ? `Reply to ${replyContext?.authorName}... Use @ to mention someone` : 'Write a comment... Use @ to mention someone'"
                  :rows="1"
                  class="w-full text-sm transition-all duration-200 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  ref="commentInputRef"
                />
              </div>
              <button
                @click="addComment"
                :disabled="!newComment.trim() || isSubmittingComment"
                class="flex-shrink-0 px-4 py-2 font-medium text-white transition-all duration-200 bg-orange-600 rounded-full hover:bg-orange-500 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>

            <!-- Desktop Emoji Picker -->
            <EmojiPicker
              :isVisible="showEmojiPicker"
              @emoji-selected="insertEmoji"
              @close="closeEmojiPicker"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Reactions Modal -->
    <ReactionsModal
      v-if="showReactionsModal"
      :post-id="post.id"
      :current-user-id="currentUserId"
      @close="showReactionsModal = false"
      @reaction-updated="handleReactionUpdated"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import PostHeader from './PostHeader.vue'
import PostActions from './PostActions.vue'
import ReactionSummary from './ReactionSummary.vue'
import ReactionsModal from './ReactionsModal.vue'
import EmojiPicker from './EmojiPicker.vue'
import CommentItem from './CommentItem.vue'
import MentionTextarea from '@/components/common/MentionTextarea.vue'
import '@/components/css/PostModal.css'

// Props
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  post: {
    type: Object,
    required: true
  },
  comments: {
    type: Array,
    default: () => []
  },
  userProfilePicture: {
    type: String,
    default: null
  },
  currentIndex: {
    type: Number,
    default: 0
  },
  totalPosts: {
    type: Number,
    default: 0
  },
  categories: {
    type: Array,
    default: () => []
  },
  selectedReaction: {
    type: String,
    default: null
  },
  currentUserId: {
    type: Number,
    required: true
  }
})

// Emits
const emit = defineEmits([
  'close',
  'add-comment',
  'react-to-post',
  'share-post',
  'save-post',
  'copy-link',
  'load-comments',
  'navigate',
  'reaction-updated',
  'react-to-comment',
  'reply-to-comment',
  'delete-comment',
  'edit-post',
  'delete-post'
])

// Local state
const newComment = ref('')
const currentMediaIndex = ref(0)
// const focusCommentInput = ref(false) // Add missing property to prevent Vue warning
const showReactionsModal = ref(false)
const showEmojiPicker = ref(false)
const isSubmittingComment = ref(false)
const commentInputRef = ref(null)
const mentionedUsers = ref([])

// Reply context state
const replyContext = ref(null) // { commentId: number, authorName: string }
const isReplying = ref(false)

// Methods
const handleMention = (mentionData) => {
  const existingUser = mentionedUsers.value.find(u => u.id === mentionData.user.id)
  if (!existingUser) {
    mentionedUsers.value.push(mentionData.user)
  }
}

// Computed properties
const mediaFiles = computed(() => {
  const files = []

  // Add main image if exists
  if (props.post.image_url) {
    files.push({
      type: 'image',
      url: props.post.image_url,
      caption: props.post.title
    })
  }

  // Add media files if exists
  if (props.post.media_files && props.post.media_files.length > 0) {
    props.post.media_files.forEach(media => {
      files.push({
        type: media.media_type,
        url: media.file_url,
        caption: media.caption
      })
    })
  }

  return files
})

const hasMedia = computed(() => mediaFiles.value.length > 0)

const currentMediaUrl = computed(() => {
  if (mediaFiles.value.length > 0) {
    return mediaFiles.value[currentMediaIndex.value]?.url
  }
  return null
})

const currentMediaType = computed(() => {
  if (mediaFiles.value.length > 0) {
    return mediaFiles.value[currentMediaIndex.value]?.type
  }
  return null
})

const hasEngagement = computed(() => {
  return props.post.likes_count > 0 ||
         props.post.comments_count > 0 ||
         props.post.shares_count > 0 ||
         (props.post.reactions_summary && props.post.reactions_summary.total_count > 0)
})

// Methods
const closeModal = () => {
  emit('close')
}

const extractMentions = (content) => {
  const mentionPattern = /@(\w+)/g
  const mentions = []
  let match

  while ((match = mentionPattern.exec(content)) !== null) {
    const username = match[1]
    const user = mentionedUsers.value.find(u => u.username === username)
    if (user) {
      mentions.push({
        user_id: user.id,
        username: user.username,
        start_position: match.index,
        end_position: match.index + match[0].length
      })
    }
  }

  return mentions
}

const clearReplyContext = () => {
  replyContext.value = null
  isReplying.value = false
}

const cancelReply = () => {
  clearReplyContext()
  newComment.value = ''
  mentionedUsers.value = []
}

const addComment = () => {
  if (isSubmittingComment.value) {
    return;
  }
  
  const content = newComment.value?.trim()
  if (!content) {
    return;
  }

  try {
    isSubmittingComment.value = true;
    
    // Extract mentions from the comment
    const mentions = extractMentions(content)

    if (isReplying.value && replyContext.value) {
      // This is a reply to a specific comment
      emit('reply-to-comment', {
        commentId: replyContext.value.commentId,
        content: content,
        mentions: mentions
      })
    } else {
      // This is a new top-level comment - emit with same signature as expected by AlumniHome
      emit('add-comment', props.post.id, content, null, mentions)
    }

    // Reset form
    newComment.value = ''
    mentionedUsers.value = []
    clearReplyContext()
  } finally {
    // Reset loading state after a short delay to prevent rapid clicking
    setTimeout(() => {
      isSubmittingComment.value = false;
    }, 500);
  }
}

const handleReaction = (postId, reactionType) => {
  emit('react-to-post', postId, reactionType)
}

const handleShare = (postId) => {
  emit('share-post', postId)
}

const handleSave = (postId) => {
  emit('save-post', postId)
}

const handleCopyLink = (postId) => {
  emit('copy-link', postId)
}

const openReactionsModal = () => {
  showReactionsModal.value = true
}

const handleReactionUpdated = () => {
  // Emit event to parent to refresh post data
  emit('reaction-updated', props.post.id)
  showReactionsModal.value = false
}

const previousMedia = () => {
  if (currentMediaIndex.value > 0) {
    currentMediaIndex.value--
  }
}

const nextMedia = () => {
  if (currentMediaIndex.value < mediaFiles.value.length - 1) {
    currentMediaIndex.value++
  }
}

const onImageLoad = () => {
  // Handle successful image load
}

const onImageError = (event) => {
  console.error('Failed to load image:', currentMediaUrl.value);
  event.target.src = '/default-placeholder.png'; // Fallback image
}

const onVideoError = () => {
  console.error('Failed to load video:', currentMediaUrl.value)
  // Could show error message or try different format
}

// Comment handlers
const handleReactToComment = (data) => {
  emit('react-to-comment', data)
}

const handleReplyToComment = (data) => {
  // Set reply context
  replyContext.value = {
    commentId: data.commentId,
    authorName: data.authorName
  }
  isReplying.value = true

  // Focus the main comment input safely
  nextTick(() => {
    try {
      if (commentInputRef.value) {
        // Try to focus the MentionTextarea component
        if (commentInputRef.value.focus) {
          commentInputRef.value.focus()
        } else if (commentInputRef.value.$el) {
          // Try to focus the underlying element
          const inputElement = commentInputRef.value.$el.querySelector('textarea') || commentInputRef.value.$el.querySelector('input')
          if (inputElement && inputElement.focus) {
            inputElement.focus()
          }
        }
      }
    } catch (error) {
      console.warn('Could not focus comment input:', error)
    }
  })
}

const handleDeleteComment = (commentId) => {
  emit('delete-comment', commentId)
}

const handleEdit = (postId) => {
  emit('edit-post', postId)
}

const handleDelete = (postId) => {
  emit('delete-post', postId)
}

const handleCommentLike = (data) => {
  emit('react-to-comment', data)
}

const handleCommentEdit = (commentId) => {
  // Handle comment edit - could open edit modal or inline edit
  console.log('Edit comment:', commentId)
}

const handleCommentDelete = (commentId) => {
  emit('delete-comment', commentId)
}

const insertEmoji = (emoji) => {
  const input = commentInputRef.value
  if (input) {
    const start = input.selectionStart
    const end = input.selectionEnd
    const currentValue = newComment.value

    newComment.value = currentValue.slice(0, start) + emoji + currentValue.slice(end)

    // Set cursor position after emoji
    setTimeout(() => {
      input.focus()
      input.setSelectionRange(start + emoji.length, start + emoji.length)
    }, 0)
  } else {
    newComment.value += emoji
  }

  // Don't close picker automatically - let user pick multiple emojis
}

const toggleEmojiPicker = () => {
  showEmojiPicker.value = !showEmojiPicker.value
}

const closeEmojiPicker = () => {
  showEmojiPicker.value = false
}

const getBackendBaseUrl = () => {
  const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
  const hostname = window.location.hostname;
  return `${protocol}//${hostname}:8000`;
};

const getProfilePictureUrl = (profilePicture) => {
  if (!profilePicture) return '/default-avatar.png';
  // If already a full URL, return as is
  if (profilePicture.startsWith('http://') || profilePicture.startsWith('https://')) {
    return profilePicture;
  }
  // If relative path, prepend dynamic base URL
  const BASE_URL = getBackendBaseUrl();
  return profilePicture.startsWith('/') ? `${BASE_URL}${profilePicture}` : `${BASE_URL}/${profilePicture}`;
};

const getMediaUrl = (url) => {
  if (!url) return '/default-placeholder.png'; // Fallback if null

  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }

  const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
  return url.startsWith('/') ? `${BASE_URL}${url}` : `${BASE_URL}/${url}`;
}

// Handle escape key
const handleEscape = (event) => {
  if (event.key === 'Escape') {
    if (showEmojiPicker.value) {
      closeEmojiPicker()
    } else if (props.isOpen) {
      closeModal()
    }
  }
}

// Handle click outside emoji picker
const handleClickOutside = (event) => {
  if (showEmojiPicker.value && !event.target.closest('.emoji-picker-container') && !event.target.closest('.emoji-button')) {
    closeEmojiPicker()
  }
}

// Watch for modal open/close
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    // Reset media index when opening
    currentMediaIndex.value = 0

    // Load comments if not already loaded
    if (props.comments.length === 0) {
      emit('load-comments', props.post.id)
    }

    // Prevent body scroll
    document.body.style.overflow = 'hidden'
  } else {
    // Restore body scroll
    document.body.style.overflow = ''
  }
})

// Lifecycle
onMounted(() => {
  document.addEventListener('keydown', handleEscape)
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
  document.removeEventListener('click', handleClickOutside)
  // Ensure body scroll is restored
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* Ensure mobile layout is always shown on mobile devices */
@media (max-width: 1023px) {
  .lg\:hidden {
    display: flex !important;
    flex-direction: column !important;
    width: 100vw !important;
    height: 100vh !important;
    max-width: none !important;
    max-height: none !important;
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    border-radius: 0 !important;
  }

  .hidden.lg\:flex {
    display: none !important;
  }
}

/* Mobile-specific improvements for comment section */
@media (max-width: 640px) {
  /* Override MentionTextarea default padding for mobile */
  .mobile-comment-input :deep(textarea) {
    padding: 10px 16px !important;
    min-height: 40px !important;
    max-height: 100px !important;
    font-size: 16px !important; /* Prevent zoom on iOS */
    line-height: 1.4 !important;
    border-radius: 20px !important;
    background-color: #ffffff !important;
    border: 2px solid #d1d5db !important;
    color: #374151 !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 1 !important;
  }

  .mobile-comment-input :deep(textarea):focus {
    border-color: #f97316 !important;
    box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.1) !important;
    outline: none !important;
  }

  .emoji-button {
    min-width: 36px;
    min-height: 36px;
    font-size: 18px;
    padding: 8px !important;
    background-color: transparent;
  }

  /* Ensure proper avatar sizing and aspect ratio on mobile */
  img[alt="Your avatar"] {
    width: 36px !important;
    height: 36px !important;
    aspect-ratio: 1 / 1;
    object-fit: cover;
  }

  /* Ensure send button is properly sized and centered */
  button[class*="bg-orange-600"] {
    min-width: 36px !important;
    min-height: 36px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 10px !important;
  }

  /* Better container spacing */
  .mobile-comment-input {
    min-height: 40px !important;
  }
}

/* Touch-friendly interactions */
@media (hover: none) and (pointer: coarse) {
  button {
    min-height: 44px; /* iOS accessibility guidelines */
    touch-action: manipulation;
  }

  /* Better touch targets for mobile */
  .emoji-button,
  button[class*="bg-orange-600"] {
    min-width: 44px;
    min-height: 44px;
  }
}

/* Additional specificity for mobile textarea overrides */
@media (max-width: 640px) {
  .mobile-comment-input :deep(.mention-wrapper) {
    width: 100% !important;
    position: relative !important;
    display: block !important;
  }

  .mobile-comment-input :deep(.mention-wrapper textarea) {
    width: 100% !important;
    padding: 10px 16px !important;
    height: 40px !important;
    min-height: 40px !important;
    max-height: 100px !important;
    font-size: 16px !important;
    line-height: 1.4 !important;
    resize: none !important;
    background: white !important;
    border: 2px solid #d1d5db !important;
    border-radius: 20px !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: relative !important;
    z-index: 1 !important;
  }

  .mobile-comment-input :deep(.mention-wrapper textarea):focus {
    border-color: #f97316 !important;
    outline: none !important;
  }
}
</style>
