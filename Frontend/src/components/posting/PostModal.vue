<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-opacity-50 backdrop-blur-sm p-2 sm:p-4"
    @click.self="closeModal"
  >
    <div
      class="bg-white rounded-lg sm:rounded-2xl shadow-2xl w-full h-full sm:max-w-[70vw] sm:w-full sm:max-h-[95vh] overflow-hidden flex flex-col"
      @click.stop
    >
      <!-- Mobile-only Media (above header) -->
      <div
        v-if="hasMedia"
        class="sm:hidden bg-gray-900 flex items-center justify-center min-h-0"
        style="height: 40vh; min-height: 200px; max-height: 400px;"
      >
        <div class="relative w-full h-full flex items-center justify-center p-2">
          <!-- Image Display -->
          <div v-if="currentMediaType === 'image'" class="relative w-full h-full flex items-center justify-center">
            <img
              :src="getMediaUrl(currentMediaUrl)"
              :alt="post.title"
              class="w-full h-full object-contain rounded-lg max-w-full max-h-full"
              loading="lazy"
              @load="onImageLoad"
              @error="onImageError"
            />
          </div>

          <!-- Video Display -->
          <div v-else-if="currentMediaType === 'video'" class="relative w-full h-full flex items-center justify-center">
            <video
              :src="getMediaUrl(currentMediaUrl)"
              controls
              class="w-full h-full object-contain rounded-lg max-w-full max-h-full"
              @error="onVideoError"
            />
          </div>

          <!-- Multiple Media Navigation -->
          <div v-if="mediaFiles.length > 1" class="absolute inset-0 flex items-center justify-between p-2 pointer-events-none">
            <button
              v-if="currentMediaIndex > 0"
              @click="previousMedia"
              class="bg-black bg-opacity-50 text-white p-1.5 rounded-full hover:bg-opacity-75 transition-all pointer-events-auto flex-shrink-0"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            
            <!-- Spacer to push next button to the right -->
            <div class="flex-1 pointer-events-none"></div>
            
            <button
              v-if="currentMediaIndex < mediaFiles.length - 1"
              @click="nextMedia"
              class="bg-black bg-opacity-50 text-white p-1.5 rounded-full hover:bg-opacity-75 transition-all pointer-events-auto flex-shrink-0"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          <!-- Media Counter -->
          <div v-if="mediaFiles.length > 1" class="absolute bottom-2 right-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded-full text-xs">
            {{ currentMediaIndex + 1 }} / {{ mediaFiles.length }}
          </div>
        </div>
      </div>

      <!-- Modal Header -->
      <div class="flex items-center justify-between p-3 sm:p-4 border-b border-gray-200">
        <h3 class="text-base sm:text-lg font-semibold text-gray-900 truncate">
          {{ post.user.full_name }}'s Post
        </h3>
        <button
          @click="closeModal"
          class="p-2 hover:bg-gray-100 rounded-full transition-colors flex-shrink-0"
        >
          <svg class="w-5 h-5 sm:w-6 sm:h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Modal Content -->
      <div class="flex-1 overflow-hidden flex flex-col sm:flex-row">
        <!-- Desktop-only Left side - Media (if exists) -->
        <div
          v-if="hasMedia"
          class="hidden sm:flex flex-1 bg-gray-900 flex items-center justify-center min-h-0 sm:min-h-0"
        >
          <div class="relative w-full h-full flex items-center justify-center p-4">
            <!-- Image Display -->
            <div v-if="currentMediaType === 'image'" class="relative w-full h-full flex items-center justify-center">
              <img
                :src="getMediaUrl(currentMediaUrl)"
                :alt="post.title"
                class="w-full h-full object-contain rounded-lg max-w-full max-h-full"
                style="max-height: calc(100vh - 80px); max-width: calc(100vw - 40px);"
                loading="lazy"
                @load="onImageLoad"
                @error="onImageError"
              />
            </div>

            <!-- Video Display -->
            <div v-else-if="currentMediaType === 'video'" class="relative w-full h-full flex items-center justify-center">
              <video
                :src="getMediaUrl(currentMediaUrl)"
                controls
                class="w-full h-full object-contain rounded-lg max-w-full max-h-full"
                style="max-height: calc(100vh - 80px); max-width: calc(100vw - 40px);"
                @error="onVideoError"
              />
            </div>

            <!-- Multiple Media Navigation -->
            <div v-if="mediaFiles.length > 1" class="absolute inset-0 flex items-center justify-between p-4 pointer-events-none">
              <button
                v-if="currentMediaIndex > 0"
                @click="previousMedia"
                class="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-75 transition-all pointer-events-auto flex-shrink-0"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              
              <!-- Spacer to push next button to the right -->
              <div class="flex-1 pointer-events-none"></div>
              
              <button
                v-if="currentMediaIndex < mediaFiles.length - 1"
                @click="nextMedia"
                class="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-75 transition-all pointer-events-auto flex-shrink-0"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>

            <!-- Media Counter -->
            <div v-if="mediaFiles.length > 1" class="absolute bottom-4 right-4 bg-black bg-opacity-50 text-white px-3 py-1 rounded-full text-sm">
              {{ currentMediaIndex + 1 }} / {{ mediaFiles.length }}
            </div>
          </div>
        </div>

        <!-- Right side - Post Details and Comments -->
        <div :class="hasMedia ? 'w-full sm:w-[550px]' : 'flex-1'" class="flex flex-col bg-white sm:border-l border-gray-200 h-full">
          <!-- Scrollable Content Area with Fixed Height -->
          <div class="overflow-y-auto" style="height: calc(100% - 70px);">
            <!-- Post Header -->
            <div class="p-2 sm:p-3 md:p-6 border-b border-gray-200">
              <PostHeader
                :post="post"
                :categories="categories"
                :user-profile-picture="userProfilePicture"
                :show-menu="false"
              />
            </div>

            <!-- Post Content -->
            <div class="p-2 sm:p-3 md:p-6 pb-2 sm:pb-4 md:pb-8 border-b border-gray-200">
              <h3 v-if="post.title" class="text-sm sm:text-base md:text-lg lg:text-xl font-semibold text-gray-900 mb-1 sm:mb-2 md:mb-3">
                {{ post.title }}
              </h3>
              <p v-if="post.content" class="text-gray-700 whitespace-pre-wrap text-xs sm:text-sm md:text-base lg:text-lg leading-relaxed">
                {{ post.content }}
              </p>
            </div>

            <!-- Engagement Summary -->
            <div v-if="hasEngagement" class="px-3 sm:px-6 py-3 sm:py-4 border-b border-gray-200 hover-isolation" @mouseenter.stop @mouseover.stop>
              <ReactionSummary
                :reactions-summary="post.reactions_summary"
                :likes-count="post.likes_count"
                :comments-count="post.comments_count"
                :shares-count="post.shares_count"
                @click="openReactionsModal"
              />
            </div>

            <!-- Post Actions -->
            <div class="px-3 sm:px-6 py-3 sm:py-5 border-b border-gray-200 bg-gray-50">
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
            <div class="px-3 sm:px-6 py-2 sm:py-3 bg-gray-50 border-b border-gray-200">
              <h4 class="font-semibold text-gray-900 text-sm sm:text-lg">
                Comments ({{ comments.length || 0 }})
              </h4>
            </div>

            <!-- Comments List -->
            <div class="px-3 sm:px-6 py-2 sm:py-3 space-y-2 sm:space-y-4 bg-gray-50">
              <div v-if="comments.length === 0" class="text-center text-gray-500 py-4 sm:py-8">
                <svg class="mx-auto h-6 w-6 sm:h-12 sm:w-12 text-gray-400 mb-2 sm:mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <p class="text-sm sm:text-lg">No comments yet</p>
                <p class="text-xs sm:text-sm">Be the first to comment!</p>
              </div>
              
              <div v-for="comment in comments" :key="comment.id" class="flex space-x-2 sm:space-x-3">
                <img
                  :src="getProfilePictureUrl(comment.user.profile_picture) || '/default-avatar.png'"
                  :alt="comment.user.full_name"
                  class="w-5 h-5 sm:w-10 sm:h-10 rounded-full object-cover flex-shrink-0"
                />
                <div class="flex-1 min-w-0">
                  <div class="bg-white rounded px-1.5 py-0.5 sm:px-3 sm:py-2 shadow-sm">
                    <p class="font-medium text-gray-900 text-xs sm:text-sm leading-none">
                      {{ comment.user.full_name }}
                    </p>
                    <p class="text-gray-700 leading-none text-xs sm:text-sm">
                      {{ comment.content }}
                    </p>
                  </div>
                  <div class="flex items-center space-x-2 text-xs text-gray-500">
                    <span>{{ comment.time_since }}</span>
                    <button class="hover:text-blue-600">Like</button>
                    <button class="hover:text-blue-600">Reply</button>
                  </div>
                </div>
              </div>
              
              <!-- Add some bottom padding only when there are comments to prevent huge empty space -->
              <div v-if="comments.length > 0" class="pb-2"></div>
            </div>
          </div>

          <!-- Fixed Comment Input at Bottom -->
          <div class="h-16 sm:h-20 px-3 sm:px-6 py-2 sm:py-4 border-t border-gray-200 bg-white flex items-center">
            <div class="flex space-x-2 sm:space-x-3 w-full">
              <img
                :src="getProfilePictureUrl(userProfilePicture) || '/default-avatar.png'"
                alt="Your avatar"
                class="w-7 h-7 sm:w-10 sm:h-10 rounded-full object-cover flex-shrink-0"
              />
              <div class="flex-1 relative">
                <!-- Emoji Picker -->
                <EmojiPicker 
                  :isVisible="showEmojiPicker"
                  @emoji-selected="insertEmoji"
                  @close="closeEmojiPicker"
                />
                
                <div class="flex space-x-1 sm:space-x-2">
                  <!-- Emoji Button -->
                  <button
                    @click="toggleEmojiPicker"
                    class="emoji-button p-1.5 sm:p-3 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                    title="Add emoji"
                  >
                    😀
                  </button>
                  
                  <!-- Comment Input -->
                  <input
                    ref="commentInputRef"
                    v-model="newComment"
                    type="text"
                    placeholder="Write a comment..."
                    class="flex-1 px-3 sm:px-4 py-1.5 sm:py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 text-gray-900 placeholder-gray-500 text-sm sm:text-base"
                    @keyup.enter="addComment"
                    @focus="closeEmojiPicker"
                  />
                  
                  <!-- Send Button -->
                  <button
                    @click="addComment"
                    :disabled="!newComment.trim()"
                    class="px-2 sm:px-6 py-1.5 sm:py-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
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
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import PostHeader from './PostHeader.vue'
import PostActions from './PostActions.vue'
import ReactionSummary from './ReactionSummary.vue'
import ReactionsModal from './ReactionsModal.vue'
import EmojiPicker from './EmojiPicker.vue'
import './PostModal.css'

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
  'reaction-updated'
])

// Local state
const newComment = ref('')
const currentMediaIndex = ref(0)
const focusCommentInput = ref(false) // Add missing property to prevent Vue warning
const showReactionsModal = ref(false)
const showEmojiPicker = ref(false)
const commentInputRef = ref(null)

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

const addComment = () => {
  const content = newComment.value?.trim()
  if (!content) return
  
  emit('add-comment', props.post.id, content)
  newComment.value = ''
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

const onVideoError = (event) => {
  console.error('Failed to load video:', currentMediaUrl.value);
  // Handle video error, e.g., show placeholder
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

const getProfilePictureUrl = (profilePicture) => {
  if (!profilePicture) return '/default-avatar.png'
  
  // If already a full URL, return as is
  if (profilePicture.startsWith('http://') || profilePicture.startsWith('https://')) {
    return profilePicture
  }
  
  // If relative path, prepend base URL
  const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
  return profilePicture.startsWith('/') ? `${BASE_URL}${profilePicture}` : `${BASE_URL}/${profilePicture}`
}

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