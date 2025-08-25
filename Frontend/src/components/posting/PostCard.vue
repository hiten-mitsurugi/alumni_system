<template>
  <div
    class="bg-white rounded-3xl shadow-xl border-2 border-slate-100 hover:shadow-2xl transition-all duration-300 overflow-hidden">
    <!-- Post Header -->
    <PostHeader :post="post" :categories="categories" />

    <!-- Post Content -->
    <div class="px-6">
      <h2 v-if="post.title" class="text-2xl font-bold text-slate-900 mb-4 leading-relaxed">{{ post.title }}</h2>
      <div class="text-lg text-slate-800 whitespace-pre-wrap mb-6 leading-relaxed">{{ post.content }}</div>

      <!-- Shared Post Display -->
      <div v-if="post.shared_post" class="border-2 border-slate-200 rounded-2xl p-6 mb-6 bg-slate-50">
        <div class="flex items-center space-x-3 mb-4">
          <img :src="post.shared_post.user?.profile_picture || '/default-avatar.png'" alt="Profile"
            class="w-10 h-10 rounded-full object-cover border-2 border-slate-300" />
          <span class="text-lg font-semibold text-slate-700">
            {{ post.shared_post.user?.first_name }} {{ post.shared_post.user?.last_name }}
          </span>
          <span class="text-sm text-slate-500 font-medium">{{ formatTimeAgo(post.shared_post.created_at) }}</span>
        </div>
        <h3 v-if="post.shared_post.title" class="text-xl font-bold text-slate-900 mb-3">{{ post.shared_post.title }}
        </h3>
        <p class="text-lg text-slate-700 leading-relaxed">{{ post.shared_post.content }}</p>
      </div>

      <!-- Media Files (Clickable to open modal) -->
      <div v-if="hasMedia" class="cursor-pointer relative rounded-2xl overflow-hidden" @click="openPostModal">
        <MediaDisplay :media-files="post.media_files" :alt-text="post.title || 'Post image'"
          @media-click="openPostModal" />
      </div>
    </div>

    <!-- Engagement Stats (Clickable to open modal) -->
    <div v-if="post.likes_count > 0 || post.comments_count > 0 || post.shares_count > 0"
      class="px-6 py-4 border-t-2 border-slate-100">
      <div class="flex items-center justify-between text-lg text-slate-600">
        <div class="flex items-center space-x-6">
          <span v-if="post.likes_count > 0" class="flex items-center space-x-2 font-semibold">
            <div class="flex -space-x-1 text-xl">
              <span>👍</span>
              <span>❤️</span>
              <span>😂</span>
            </div>
            <span class="text-blue-600">{{ post.likes_count }} reactions</span>
          </span>
          <button v-if="post.comments_count > 0" @click="openPostModal"
            class="font-semibold text-green-600 hover:text-green-800 transition-colors">
            💬 {{ post.comments_count }} comments
          </button>
          <span v-if="post.shares_count > 0" class="font-semibold text-purple-600">
            🔄 {{ post.shares_count }} shares
          </span>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <PostActions :post-id="post.id" :selected-reaction="selectedReaction" @react-to-post="handleReaction"
      @comment-clicked="openPostModal" @share-post="$emit('share-post', post.id)"
      @copy-link="$emit('copy-link', post.id)" />

    <!-- Quick Comment Preview (if comments exist) -->
    <div v-if="previewComments.length > 0" class="px-6 pb-4">
      <div class="space-y-3">
        <div v-for="comment in previewComments.slice(0, 2)" :key="comment.id"
          class="flex space-x-3 cursor-pointer hover:bg-gray-50 rounded-lg p-2 -m-2 transition-colors"
          @click="openPostModal">
          <img :src="comment.user.profile_picture || '/default-avatar.png'" :alt="comment.user.full_name"
            class="w-8 h-8 rounded-full object-cover flex-shrink-0" />
          <div class="flex-1 min-w-0">
            <div class="bg-gray-100 rounded-lg px-3 py-2">
              <p class="font-semibold text-sm text-gray-900">
                {{ comment.user.full_name }}
              </p>
              <p class="text-gray-700 text-sm mt-1 line-clamp-2">
                {{ comment.content }}
              </p>
            </div>
          </div>
        </div>

        <!-- Show "view comments" indicator if there are any comments -->
        <div v-if="post.comments_count > 0" class="mt-3">
          <button @click="openPostModal"
            class="text-sm text-blue-600 hover:text-blue-800 font-medium transition-colors">
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
    <div class="px-6 pb-6">
      <div class="flex space-x-3 items-center">
        <img :src="userProfilePicture || '/default-avatar.png'" alt="Your avatar"
          class="w-8 h-8 rounded-full object-cover flex-shrink-0" />
        <button @click="openPostModal"
          class="flex-1 bg-gray-100 hover:bg-gray-200 rounded-full px-4 py-3 text-left text-gray-600 transition-colors text-lg">
          Write a comment...
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import PostHeader from './PostHeader.vue'
import MediaDisplay from './MediaDisplay.vue'
import PostActions from './PostActions.vue'

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
  }
})

// Emits
const emit = defineEmits(['react-to-post', 'add-comment', 'share-post', 'copy-link', 'open-modal'])

// Computed properties
const hasMedia = computed(() => {
  return (props.post.media_files && props.post.media_files.length > 0) ||
    props.post.image_url
})

const previewComments = computed(() => {
  return props.comments.slice(0, 2) // Show only first 2 comments as preview
})

// Methods
const openPostModal = () => {
  console.log('🔗 PostCard: Opening modal for post:', props.post.id)
  emit('open-modal', props.post)
}

const handleReaction = (postId, reactionType) => {
  emit('react-to-post', postId, reactionType)
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
</script>

<style scoped>
/* Enhanced card shadows */
.shadow-xl {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.shadow-2xl {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

/* Smooth transitions for all interactive elements */
.transition-all {
  transition: all 0.3s ease;
}

/* Enhanced spacing for better readability */
.leading-relaxed {
  line-height: 1.75;
}

/* Gradient text for enhanced visual appeal */
.bg-gradient-to-r {
  background-image: linear-gradient(to right, var(--tw-gradient-stops));
}
</style>
