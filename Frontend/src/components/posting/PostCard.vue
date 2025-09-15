<template>
  <div
    class="bg-white rounded-xl md:rounded-2xl shadow-lg border border-slate-100 hover:shadow-xl transition-all duration-300 overflow-hidden mb-4 w-full mx-auto">
    <!-- Post Header -->
    <PostHeader :post="post" :categories="categories" />

    <!-- Post Content -->
    <div class="px-4 md:px-6 cursor-pointer" @click="openPostModal">
      <h2 v-if="post.title" class="text-base md:text-lg font-semibold text-slate-900 mb-2 leading-snug">{{ post.title }}</h2>
      <div class="text-sm md:text-base text-slate-800 whitespace-pre-wrap mb-3 md:mb-4 leading-relaxed">{{ post.content }}</div>

      <!-- Shared Post Display -->
      <div v-if="post.shared_post" class="border border-slate-200 rounded-lg p-3 mb-3 md:mb-4 bg-slate-50">
        <div class="flex items-center space-x-2 mb-2">
          <img :src="post.shared_post.user?.profile_picture || '/default-avatar.png'" alt="Profile"
            class="w-6 h-6 md:w-8 md:h-8 rounded-full object-cover border border-slate-300" />
          <span class="text-xs md:text-sm font-medium text-slate-700">
            {{ post.shared_post.user?.first_name }} {{ post.shared_post.user?.last_name }}
          </span>
          <span class="text-xs text-slate-500">{{ formatTimeAgo(post.shared_post.created_at) }}</span>
        </div>
        <h3 v-if="post.shared_post.title" class="text-sm md:text-base font-semibold text-slate-900 mb-2">{{ post.shared_post.title }}
        </h3>
        <p class="text-xs md:text-sm text-slate-700 leading-relaxed">{{ post.shared_post.content }}</p>
      </div>

      <!-- Media Files (Clickable to open modal) -->
      <div v-if="hasMedia" class="cursor-pointer relative rounded-lg overflow-hidden" @click="openPostModal">
        <MediaDisplay 
          :media-files="post.media_files" 
          :alt-text="post.title || 'Post image'"
          display-mode="card"
          @media-click="openPostModal" 
        />
      </div>
    </div>

    <!-- Engagement Stats & Reaction Summary -->
    <div v-if="hasEngagement" class="px-4 md:px-6 py-2 border-t border-slate-100 hover-isolation">
      <div class="flex items-center justify-between text-xs md:text-sm text-slate-600" @mouseenter.stop @mouseover.stop>
        <div class="flex items-center space-x-2 md:space-x-3" @mouseenter.stop @mouseover.stop>
          <!-- Facebook-style Reaction Summary -->
          <ReactionSummary
            :reactions-summary="post.reactions_summary"
            :post-id="post.id"
            @open-reactions-modal="openReactionsModal"
          />
          
          <!-- Legacy reaction display (fallback) -->
          <span v-if="!post.reactions_summary && post.likes_count > 0" class="flex items-center space-x-1 font-medium">
            <div class="flex -space-x-1 text-sm md:text-base">
              <span>👍</span>
              <span>👏</span>
              <span>❤️</span>
              <span>😂</span>
              <span>🤝</span>
            </div>
            <span class="text-blue-600">{{ post.likes_count }} reactions</span>
          </span>
        </div>
        
        <div class="flex items-center space-x-2 md:space-x-3">
          <button v-if="post.comments_count > 0" @click="openPostModal"
            class="font-medium text-green-600 hover:text-green-800 transition-colors text-xs">
            💬 {{ post.comments_count }}
            <span class="hidden sm:inline">comments</span>
          </button>
          <span v-if="post.shares_count > 0" class="font-medium text-purple-600 text-xs">
            🔄 {{ post.shares_count }}
            <span class="hidden sm:inline">reposts</span>
          </span>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <PostActions :post-id="post.id" :selected-reaction="selectedReaction" @react-to-post="handleReaction"
      @comment-clicked="openPostModal" @share-post="$emit('share-post', post.id)"
      @copy-link="$emit('copy-link', post.id)" />

    <!-- Quick Comment Preview (if comments exist) -->
    <div v-if="previewComments.length > 0" class="px-4 md:px-6 pb-2">
      <div class="space-y-2">
        <div v-for="comment in previewComments.slice(0, 2)" :key="comment.id"
          class="flex space-x-2 cursor-pointer hover:bg-gray-50 rounded-lg p-2 -m-2 transition-colors"
          @click="openPostModal">
          <img :src="comment.user.profile_picture || '/default-avatar.png'" :alt="comment.user.full_name"
            class="w-5 h-5 md:w-6 md:h-6 rounded-full object-cover flex-shrink-0" />
          <div class="flex-1 min-w-0">
            <div class="bg-gray-100 rounded-lg px-2 py-1">
              <p class="font-medium text-xs text-gray-900">
                {{ comment.user.full_name }}
              </p>
              <p class="text-gray-700 text-xs mt-1 line-clamp-2">
                {{ comment.content }}
              </p>
            </div>
          </div>
        </div>

        <!-- Show "view comments" indicator if there are any comments -->
        <div v-if="post.comments_count > 0" class="mt-2">
          <button @click="openPostModal"
            class="text-xs text-blue-600 hover:text-blue-800 font-medium transition-colors">
            <span v-if="post.comments_count <= 2">
              View {{ post.comments_count === 1 ? 'comment' : `${post.comments_count} comments` }}
            </span>
            <span v-else>
              View all {{ post.comments_count }} comments
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- Quick Comment Input -->
    <div class="px-4 md:px-6 pb-3 md:pb-4">
      <div class="flex space-x-2 items-center">
        <img :src="getProfilePictureUrl(userProfilePicture) || '/default-avatar.png'" alt="Your avatar"
          class="w-5 h-5 md:w-6 md:h-6 rounded-full object-cover flex-shrink-0" />
        <button @click="openPostModal"
          class="flex-1 bg-gray-100 hover:bg-gray-200 rounded-full px-3 py-2 text-left text-gray-600 transition-colors text-xs md:text-sm">
          Write a comment...
        </button>
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
import { ref, computed } from 'vue'
import PostHeader from './PostHeader.vue'
import MediaDisplay from './MediaDisplay.vue'
import PostActions from './PostActions.vue'
import ReactionSummary from './ReactionSummary.vue'
import ReactionsModal from './ReactionsModal.vue'

// Props
const props = defineProps({
  post: {
    type: Object,
    required: true
  },
  categories: {
    type: Array,
    required: true
  },
  selectedReaction: {
    type: String,
    default: null
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
const emit = defineEmits(['react-to-post', 'add-comment', 'share-post', 'copy-link', 'open-modal', 'reaction-updated'])

// Local state
const showReactionsModal = ref(false)

// Computed properties
const hasMedia = computed(() => {
  return (props.post.media_files && props.post.media_files.length > 0) ||
    props.post.image_url
})

const previewComments = computed(() => {
  return props.comments.slice(0, 2) // Show only first 2 comments as preview
})

const hasEngagement = computed(() => {
  return props.post.likes_count > 0 || 
         props.post.comments_count > 0 || 
         props.post.shares_count > 0 ||
         (props.post.reactions_summary && props.post.reactions_summary.total_count > 0)
})

// Methods
const openPostModal = () => {
  console.log('🔗 PostCard: Opening modal for post:', props.post.id)
  emit('open-modal', props.post)
}

const handleReaction = (postId, reactionType) => {
  emit('react-to-post', postId, reactionType)
}

const openReactionsModal = (postId) => {
  showReactionsModal.value = true
}

const handleReactionUpdated = () => {
  // Emit event to parent to refresh post data
  emit('reaction-updated', props.post.id)
  showReactionsModal.value = false
}

const formatTimeAgo = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInSeconds = Math.floor((now - date) / 1000)

  if (diffInSeconds < 60) return 'Just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`

  return date.toLocaleDateString()
}

const getProfilePictureUrl = (profilePicture) => {
  if (!profilePicture) return null
  
  // If already a full URL, return as is
  if (profilePicture.startsWith('http://') || profilePicture.startsWith('https://')) {
    return profilePicture
  }
  
  // If relative path, prepend base URL
  const BASE_URL = 'http://127.0.0.1:8000'
  return profilePicture.startsWith('/') ? `${BASE_URL}${profilePicture}` : `${BASE_URL}/${profilePicture}`
}
</script>

<style scoped>
/* Hover isolation for engagement section */
.hover-isolation {
  isolation: isolate;
  position: relative;
}

.hover-isolation:hover {
  background-color: transparent !important;
}

.hover-isolation * {
  pointer-events: auto;
}

/* Enhanced card shadows - mobile friendly */
.shadow-lg {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.shadow-xl {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* Smooth transitions for all interactive elements */
.transition-all {
  transition: all 0.2s ease;
}

/* Mobile optimizations */
@media (max-width: 768px) {
  /* Compact spacing on mobile */
  .space-x-2 > :not([hidden]) ~ :not([hidden]) {
    margin-left: 0.5rem;
  }
  
  .space-x-3 > :not([hidden]) ~ :not([hidden]) {
    margin-left: 0.75rem;
  }
  
  .space-y-2 > :not([hidden]) ~ :not([hidden]) {
    margin-top: 0.5rem;
  }
  
  /* Touch-friendly buttons */
  button {
    min-height: 44px;
    min-width: 44px;
  }
  
  /* Compact text sizes */
  .text-lg {
    font-size: 1rem;
    line-height: 1.5rem;
  }
  
  .text-xl {
    font-size: 1.125rem;
    line-height: 1.75rem;
  }
  
  /* Reduce padding on mobile */
  .px-4 {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .py-3 {
    padding-top: 0.75rem;
    padding-bottom: 0.75rem;
  }
  
  /* Better readability on mobile */
  .leading-snug {
    line-height: 1.375;
  }
  
  .leading-relaxed {
    line-height: 1.625;
  }
}

/* Desktop hover effects */
@media (hover: hover) {
  .hover\:shadow-xl:hover {
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  }
  
  .hover\:bg-gray-50:hover {
    background-color: #f9fafb;
  }
  
  .hover\:bg-gray-200:hover {
    background-color: #e5e7eb;
  }
}

/* Line clamping for comment previews */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Prevent horizontal overflow */
* {
  box-sizing: border-box;
}

/* Better focus states for accessibility */
button:focus, 
.cursor-pointer:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Smooth color transitions */
.transition-colors {
  transition: color 0.2s ease;
}

/* Avatar border optimization */
.rounded-full {
  border-radius: 50%;
}

/* Card margin optimization */
.mb-4 {
  margin-bottom: 1rem;
}

/* Gradient backgrounds - if used */
.bg-gradient-to-r {
  background-image: linear-gradient(to right, var(--tw-gradient-stops));
}

/* Flexible layouts */
.flex-shrink-0 {
  flex-shrink: 0;
}

.flex-1 {
  flex: 1 1 0%;
}

.min-w-0 {
  min-width: 0px;
}

/* Enhanced spacing */
.space-x-2 > :not([hidden]) ~ :not([hidden]) {
  --tw-space-x-reverse: 0;
  margin-right: calc(0.5rem * var(--tw-space-x-reverse));
  margin-left: calc(0.5rem * calc(1 - var(--tw-space-x-reverse)));
}

.space-x-3 > :not([hidden]) ~ :not([hidden]) {
  --tw-space-x-reverse: 0;
  margin-right: calc(0.75rem * var(--tw-space-x-reverse));
  margin-left: calc(0.75rem * calc(1 - var(--tw-space-x-reverse)));
}

.space-y-2 > :not([hidden]) ~ :not([hidden]) {
  --tw-space-y-reverse: 0;
  margin-top: calc(0.5rem * calc(1 - var(--tw-space-y-reverse)));
  margin-bottom: calc(0.5rem * var(--tw-space-y-reverse));
}

.space-y-3 > :not([hidden]) ~ :not([hidden]) {
  --tw-space-y-reverse: 0;
  margin-top: calc(0.75rem * calc(1 - var(--tw-space-y-reverse)));
  margin-bottom: calc(0.75rem * var(--tw-space-y-reverse));
}
</style>
