<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-opacity-50 backdrop-blur-sm p-4"
    @click.self="closeModal"
  >
    <div
      class="bg-white rounded-2xl shadow-2xl max-w-[70vw] w-full max-h-[95vh] overflow-hidden flex flex-col"
      @click.stop
    >
      <!-- Modal Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900">
          {{ post.user.full_name }}'s Post
        </h3>
        <button
          @click="closeModal"
          class="p-2 hover:bg-gray-100 rounded-full transition-colors"
        >
          <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Modal Content -->
      <div class="flex-1 overflow-hidden flex">
        <!-- Left side - Media (if exists) -->
        <div
          v-if="hasMedia"
          class="flex-1 bg-gray-900 flex items-center justify-center min-h-0"
        >
          <div class="relative w-full h-full flex items-center justify-center p-4">
            <!-- Image Display -->
            <div v-if="currentMediaType === 'image'" class="relative w-full h-full flex items-center justify-center">
              <img
                :src="currentMediaUrl"
                :alt="post.title"
                class="w-full h-full object-contain rounded-lg"
                style="max-height: calc(95vh - 200px);"
                @load="onImageLoad"
                @error="onImageError"
              />
            </div>

            <!-- Video Display -->
            <div v-else-if="currentMediaType === 'video'" class="relative w-full h-full flex items-center justify-center">
              <video
                :src="currentMediaUrl"
                controls
                class="w-full h-full object-contain rounded-lg"
                style="max-height: calc(95vh - 200px);"
              />
            </div>

            <!-- Multiple Media Navigation -->
            <div v-if="mediaFiles.length > 1" class="absolute inset-0 flex items-center justify-between p-4 pointer-events-none">
              <button
                v-if="currentMediaIndex > 0"
                @click="previousMedia"
                class="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-75 transition-all pointer-events-auto"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              
              <button
                v-if="currentMediaIndex < mediaFiles.length - 1"
                @click="nextMedia"
                class="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-75 transition-all pointer-events-auto"
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
        <div :class="hasMedia ? 'w-[550px]' : 'flex-1'" class="flex flex-col bg-white border-l border-gray-200">
          <!-- Post Header -->
          <div class="p-6 border-b border-gray-200">
            <PostHeader
              :post="post"
              :categories="categories"
              :user-profile-picture="userProfilePicture"
              :show-menu="false"
            />
          </div>

          <!-- Post Content -->
          <div class="p-6 pb-8 border-b border-gray-200">
            <h3 v-if="post.title" class="text-xl font-semibold text-gray-900 mb-3">
              {{ post.title }}
            </h3>
            <p v-if="post.content" class="text-gray-700 whitespace-pre-wrap text-lg leading-relaxed">
              {{ post.content }}
            </p>
          </div>

          <!-- Post Actions -->
          <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
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

          <!-- Comments Section -->
          <div class="flex-1 flex flex-col min-h-0">
            <!-- Comments Header -->
            <div class="px-6 py-4 bg-gray-50 border-b border-gray-200">
              <h4 class="font-semibold text-gray-900 text-lg">
                Comments ({{ comments.length || 0 }})
              </h4>
            </div>

            <!-- Comments List -->
            <div class="flex-1 overflow-y-auto px-6 py-4 space-y-4 bg-gray-50">
              <div v-if="comments.length === 0" class="text-center text-gray-500 py-12">
                <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <p class="text-lg">No comments yet</p>
                <p class="text-sm">Be the first to comment!</p>
              </div>
              
              <div v-for="comment in comments" :key="comment.id" class="flex space-x-3">
                <img
                  :src="comment.user.profile_picture || '/default-avatar.png'"
                  :alt="comment.user.full_name"
                  class="w-10 h-10 rounded-full object-cover flex-shrink-0"
                />
                <div class="flex-1 min-w-0">
                  <div class="bg-white rounded-xl px-4 py-3 shadow-sm">
                    <p class="font-semibold text-gray-900">
                      {{ comment.user.full_name }}
                    </p>
                    <p class="text-gray-700 mt-1 leading-relaxed">
                      {{ comment.content }}
                    </p>
                  </div>
                  <div class="flex items-center space-x-4 mt-1 text-xs text-gray-500">
                    <span>{{ comment.time_since }}</span>
                    <button class="hover:text-blue-600 transition-colors">Like</button>
                    <button class="hover:text-blue-600 transition-colors">Reply</button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Add Comment -->
            <div class="px-6 py-4 border-t border-gray-200 bg-white">
              <div class="flex space-x-3">
                <img
                  :src="userProfilePicture || '/default-avatar.png'"
                  alt="Your avatar"
                  class="w-10 h-10 rounded-full object-cover flex-shrink-0"
                />
                <div class="flex-1">
                  <div class="flex space-x-3">
                    <input
                      v-model="newComment"
                      type="text"
                      placeholder="Write a comment..."
                      class="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 text-gray-900 placeholder-gray-500"
                      @keyup.enter="addComment"
                    />
                    <button
                      @click="addComment"
                      :disabled="!newComment.trim()"
                      class="px-6 py-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import PostHeader from './PostHeader.vue'
import PostActions from './PostActions.vue'

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
  'navigate'
])

// Local state
const newComment = ref('')
const currentMediaIndex = ref(0)
const focusCommentInput = ref(false) // Add missing property to prevent Vue warning

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

const onImageError = () => {
  console.error('Failed to load image:', currentMediaUrl.value)
}

// Handle escape key
const handleEscape = (event) => {
  if (event.key === 'Escape' && props.isOpen) {
    closeModal()
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
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
  // Ensure body scroll is restored
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* Custom scrollbar for comments */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Smooth transitions */
.transition-all {
  transition: all 0.2s ease-in-out;
}

/* Modal animation */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { 
    opacity: 0; 
    transform: scale(0.9) translateY(20px); 
  }
  to { 
    opacity: 1; 
    transform: scale(1) translateY(0); 
  }
}

.fixed {
  animation: fadeIn 0.2s ease-out;
}

.bg-white {
  animation: slideIn 0.3s ease-out;
}
</style>
