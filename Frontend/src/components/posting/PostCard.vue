<template>
  <div
    :class="themeStore.isDarkMode ? 'bg-gray-700 border border-gray-600 text-gray-100 rounded-lg md:rounded-xl lg:rounded-2xl shadow-md md:shadow-lg hover:shadow-lg md:hover:shadow-xl transition-all duration-300 overflow-visible mb-3 md:mb-4 lg:mb-6 w-full mx-auto' : 'bg-white border border-slate-100 text-slate-900 rounded-lg md:rounded-xl lg:rounded-2xl shadow-md md:shadow-lg hover:shadow-lg md:hover:shadow-xl transition-all duration-300 overflow-visible mb-3 md:mb-4 lg:mb-6 w-full mx-auto'">
    <!-- Post Header -->
    <PostHeader 
      :post="post" 
      :categories="categories" 
      @deleted="handlePostDeleted"
      @pinned="handlePostPinned"
      @reported="handlePostReported"
    />

    <!-- Post Content -->
    <div :class="themeStore.isDarkMode ? 'px-3 md:px-4 lg:px-6 cursor-pointer' : 'px-3 md:px-4 lg:px-6 cursor-pointer'" @click="openPostModal">
      <h2 v-if="post.title" :class="themeStore.isDarkMode ? 'text-sm md:text-base lg:text-lg font-semibold text-gray-100 mb-2 leading-snug' : 'text-sm md:text-base lg:text-lg font-semibold text-slate-900 mb-2 leading-snug'">{{ post.title }}</h2>
      <div :class="themeStore.isDarkMode ? 'text-sm md:text-base text-gray-300 whitespace-pre-wrap mb-3 md:mb-4 leading-relaxed' : 'text-sm md:text-base text-slate-800 whitespace-pre-wrap mb-3 md:mb-4 leading-relaxed'">{{ post.content }}</div>

      <!-- Shared Post Display -->
      <div v-if="post.shared_post" :class="themeStore.isDarkMode ? 'border border-gray-600 rounded-lg p-2 md:p-3 mb-3 md:mb-4 bg-gray-600' : 'border border-slate-200 rounded-lg p-2 md:p-3 mb-3 md:mb-4 bg-slate-50'">
        <div class="flex items-center space-x-2 mb-2">
          <img :src="post.shared_post.user?.profile_picture || '/default-avatar.png'" alt="Profile"
            :class="themeStore.isDarkMode ? 'w-5 h-5 md:w-6 md:h-6 lg:w-8 lg:h-8 rounded-full object-cover border border-gray-700' : 'w-5 h-5 md:w-6 md:h-6 lg:w-8 lg:h-8 rounded-full object-cover border border-slate-300'" />
          <span :class="themeStore.isDarkMode ? 'text-xs md:text-sm font-medium text-gray-200' : 'text-xs md:text-sm font-medium text-slate-700'">
            {{ post.shared_post.user?.first_name }} {{ post.shared_post.user?.last_name }}
          </span>
          <span :class="themeStore.isDarkMode ? 'text-xs text-gray-300' : 'text-xs text-slate-500'">{{ formatTimeAgo(post.shared_post.created_at) }}</span>
        </div>
        <h3 v-if="post.shared_post.title" :class="themeStore.isDarkMode ? 'text-sm md:text-base font-semibold text-gray-100 mb-2' : 'text-sm md:text-base font-semibold text-slate-900 mb-2'">{{ post.shared_post.title }}
        </h3>
        <p :class="themeStore.isDarkMode ? 'text-xs md:text-sm text-gray-200 leading-relaxed' : 'text-xs md:text-sm text-slate-700 leading-relaxed'">{{ post.shared_post.content }}</p>
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
    <div v-if="hasEngagement" :class="themeStore.isDarkMode ? 'px-3 md:px-4 lg:px-6 py-2 border-t border-gray-600 hover-isolation' : 'px-3 md:px-4 lg:px-6 py-2 border-t border-slate-100 hover-isolation'">
      <div :class="themeStore.isDarkMode ? 'flex items-center justify-between text-xs md:text-sm text-gray-200' : 'flex items-center justify-between text-xs md:text-sm text-slate-600'" @mouseenter.stop @mouseover.stop>
        <div class="flex items-center space-x-1 md:space-x-2 lg:space-x-3" @mouseenter.stop @mouseover.stop>
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
        
        <div class="flex items-center space-x-1 md:space-x-2 lg:space-x-3">
          <button v-if="post.comments_count > 0" @click="openPostModal"
            class="font-medium text-green-600 hover:text-green-800 transition-colors text-xs">
            💬 {{ post.comments_count }}
            <span class="hidden sm:inline">comments</span>
          </button>
          <span v-if="post.shares_count > 0" :class="[
            'font-medium text-xs',
            themeStore.isDarkMode ? 'text-orange-400' : 'text-orange-600'
          ]">
            🔄 {{ post.shares_count }}
            <span class="hidden sm:inline">reposts</span>
          </span>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div style="overflow: visible; position: relative; z-index: 10;">
      <PostActions :post-id="post.id" :selected-reaction="selectedReaction" @react-to-post="handleReaction"
        @comment-clicked="openPostModal" @copy-link="$emit('copy-link', post.id)" />
    </div>

    <!-- Quick Comment Preview (if comments exist) -->
    <div v-if="previewComments.length > 0" :class="themeStore.isDarkMode ? 'px-3 md:px-4 lg:px-6 pb-2 bg-gray-700' : 'px-3 md:px-4 lg:px-6 pb-2 bg-white'">
      <div class="space-y-2">
        <div v-for="comment in previewComments.slice(0, 2)" :key="comment.id"
          :class="themeStore.isDarkMode ? 'flex space-x-2 cursor-pointer hover:bg-gray-600 rounded-lg p-2 -m-2 transition-colors' : 'flex space-x-2 cursor-pointer hover:bg-gray-50 rounded-lg p-2 -m-2 transition-colors'"
          @click="openPostModal">
          <img :src="comment.user.profile_picture || '/default-avatar.png'" :alt="comment.user.full_name"
            class="w-4 h-4 md:w-5 md:h-5 lg:w-6 lg:h-6 rounded-full object-cover flex-shrink-0" />
          <div class="flex-1 min-w-0">
            <div :class="themeStore.isDarkMode ? 'bg-gray-600 rounded-lg px-2 py-1' : 'bg-gray-100 rounded-lg px-2 py-1'">
              <p :class="themeStore.isDarkMode ? 'font-medium text-xs text-gray-100' : 'font-medium text-xs text-gray-900'">
                {{ comment.user.full_name }}
              </p>
              <p :class="themeStore.isDarkMode ? 'text-gray-200 text-xs mt-1 line-clamp-2' : 'text-gray-700 text-xs mt-1 line-clamp-2'">
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
    <div :class="themeStore.isDarkMode ? 'px-3 md:px-4 lg:px-6 pb-3 md:pb-4 bg-gray-700' : 'px-3 md:px-4 lg:px-6 pb-3 md:pb-4 bg-white'">
      <div class="flex space-x-2 items-center">
        <img :src="getProfilePictureUrl(userProfilePicture) || '/default-avatar.png'" alt="Your avatar"
          class="w-4 h-4 md:w-5 md:h-5 lg:w-6 lg:h-6 rounded-full object-cover flex-shrink-0" />
        <button @click="openPostModal"
          :class="themeStore.isDarkMode ? 'flex-1 bg-gray-600 hover:bg-gray-500 rounded-full px-3 py-2 text-left text-gray-200 transition-colors text-xs md:text-sm' : 'flex-1 bg-gray-100 hover:bg-gray-200 rounded-full px-3 py-2 text-left text-gray-600 transition-colors text-xs md:text-sm'">
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
import { useThemeStore } from '@/stores/theme'
const themeStore = useThemeStore()
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
const emit = defineEmits(['react-to-post', 'add-comment', 'copy-link', 'open-modal', 'reaction-updated', 'deleted', 'pinned', 'reported'])

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

const getBackendBaseUrl = () => {
  const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
  const hostname = window.location.hostname;
  return `${protocol}//${hostname}:8000`;
};

const getProfilePictureUrl = (profilePicture) => {
  if (!profilePicture) return null;
  // If already a full URL, return as is
  if (profilePicture.startsWith('http://') || profilePicture.startsWith('https://')) {
    return profilePicture;
  }
  // If relative path, prepend dynamic base URL
  const BASE_URL = getBackendBaseUrl();
  return profilePicture.startsWith('/') ? `${BASE_URL}${profilePicture}` : `${BASE_URL}/${profilePicture}`;
};

// Event handlers for PostMenu actions
const handlePostDeleted = (data) => {
  emit('deleted', data)
}

const handlePostPinned = (data) => {
  emit('pinned', data)
}

const handlePostReported = (data) => {
  emit('reported', data)
}
</script>

