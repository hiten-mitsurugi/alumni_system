<template>
  <div
    :class="[
      'transition-all duration-300 hover:shadow-md overflow-hidden mb-3 md:mb-4 lg:mb-6 w-full',
      'border border-l-0 border-r-0 md:border-l md:border-r md:rounded-lg md:shadow-sm lg:rounded-xl lg:shadow-lg',
      'md:mx-auto md:hover:shadow-lg lg:hover:shadow-xl',
      themeStore.isDarkMode
        ? 'bg-gray-700 border-gray-600 text-gray-100'
        : 'bg-white border-slate-100 text-slate-900'
    ]"
  >
    <!-- Post Header -->
    <PostHeader
      :post="post"
      :categories="categories"
      @deleted="handlePostDeleted"
      @pinned="handlePostPinned"
      @reported="handlePostReported"
    />

    <!-- Post Content -->
    <div :class="[
      'px-3 md:px-4 lg:px-6 cursor-pointer',
      themeStore.isDarkMode ? '' : ''
    ]" @click="openPostModal">
      <h2 v-if="post.title" :class="[
        'font-semibold mb-2 leading-snug text-clamp-base md:text-base lg:text-lg',
        themeStore.isDarkMode ? 'text-gray-100' : 'text-slate-900'
      ]">{{ post.title }}</h2>
      <MentionText 
        :content="post.content"
        :mentions="post.mentions || []"
        :available-users="post.mentioned_users || {}"
        :className="[
          'mb-3 md:mb-4 text-clamp-sm md:text-sm lg:text-base',
          themeStore.isDarkMode ? 'text-gray-300' : 'text-slate-800'
        ].join(' ')"
      />

      <!-- Shared Post Display -->
      <div v-if="post.shared_post" :class="[
        'border rounded-lg p-2 md:p-3 mb-3 md:mb-4',
        themeStore.isDarkMode ? 'border-gray-600 bg-gray-600' : 'border-slate-200 bg-slate-50'
      ]">
        <div class="flex items-center space-x-2 mb-2">
          <img :src="post.shared_post.user?.profile_picture || '/default-avatar.png'" alt="Profile"
            :class="[
              'w-5 h-5 md:w-6 md:h-6 lg:w-8 lg:h-8 rounded-full object-cover border',
              themeStore.isDarkMode ? 'border-gray-700' : 'border-slate-300'
            ]" />
          <span :class="[
            'font-medium text-clamp-xs md:text-xs lg:text-sm',
            themeStore.isDarkMode ? 'text-gray-200' : 'text-slate-700'
          ]">
            {{ post.shared_post.user?.first_name }} {{ post.shared_post.user?.last_name }}
          </span>
          <span :class="[
            'text-clamp-xs md:text-xs',
            themeStore.isDarkMode ? 'text-gray-300' : 'text-slate-500'
          ]">{{ formatTimeAgo(post.shared_post.created_at) }}</span>
        </div>
        <h3 v-if="post.shared_post.title" :class="[
          'font-semibold mb-2 text-clamp-sm md:text-sm lg:text-base',
          themeStore.isDarkMode ? 'text-gray-100' : 'text-slate-900'
        ]">{{ post.shared_post.title }}
        </h3>
        <MentionText 
          :content="post.shared_post.content"
          :mentions="post.shared_post.mentions || []"
          :available-users="post.shared_post.mentioned_users || {}"
          :className="[
            'text-clamp-sm md:text-sm lg:text-base',
            themeStore.isDarkMode ? 'text-gray-200' : 'text-slate-700'
          ].join(' ')"
        />
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
    <PostActions :post-id="post.id" :selected-reaction="selectedReaction" @react-to-post="handleReaction"
      @comment-clicked="openPostModal" @share-post="handleShare" />

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
              <MentionText 
                :content="comment.content"
                :mentions="comment.mentions || []"
                :available-users="comment.mentioned_users || {}"
                :className="[
                  'text-xs mt-1 line-clamp-2',
                  themeStore.isDarkMode ? 'text-gray-200' : 'text-gray-700'
                ].join(' ')"
              />
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
    
    <!-- Repost Modal -->
    <RepostModal
      :is-visible="showRepostModal"
      :original-post="post"
      @close="showRepostModal = false"
      @reposted="handleRepostSuccess"
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
import RepostModal from './RepostModal.vue'
import MentionText from '@/components/common/MentionText.vue'

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
const emit = defineEmits(['react-to-post', 'add-comment', 'share-post', 'repost', 'open-modal', 'reaction-updated', 'deleted', 'pinned', 'reported'])

// Local state
// State
const showReactionsModal = ref(false)
const showRepostModal = ref(false)

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

const handleShare = (postId) => {
  console.log('🔄 PostCard: Opening repost modal for post:', postId)
  showRepostModal.value = true
}

const handleRepostSuccess = (repostData) => {
  console.log('✅ PostCard: Repost successful:', repostData)
  
  // Show success message
  // You can replace this with a toast notification
  alert(`Post reposted successfully with ${repostData.visibility} visibility!`)
  
  // Emit repost event to parent (for feed refresh)
  emit('repost', {
    originalPostId: props.post.id,
    repostId: repostData.repost.id,
    visibility: repostData.visibility
  })
}

const openReactionsModal = () => {
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

