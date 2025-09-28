<template>
  <div :class="cardClasses">

    <!-- Pinned/Featured Indicators -->
    <div v-if="post.is_pinned || post.is_featured" class="px-6 pt-4">
      <div class="flex gap-2">
        <div v-if="post.is_pinned" :class="['inline-flex items-center px-3 py-1 text-sm font-semibold rounded-full', themeStore.isDarkMode ? 'bg-amber-800 text-amber-200' : 'bg-amber-100 text-amber-800']">
          <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
          </svg>
          Pinned
        </div>
        <div v-if="post.is_featured" :class="['inline-flex items-center px-3 py-1 text-sm font-semibold rounded-full', themeStore.isDarkMode ? 'bg-purple-800 text-purple-200' : 'bg-purple-100 text-purple-800']">
          <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
          </svg>
          Featured
        </div>
      </div>
    </div>

    <!-- Post Header -->
    <PostHeader
      :post="post"
      :categories="categories"
      @delete-post="handleDeletePost"
      @pin-post="handlePinPost"
      @feature-post="handleFeaturePost"
      @report-post="handleReportPost"
    />

    <!-- Post Content -->
    <div class="px-6">
      <h2 v-if="post.title" :class="titleClasses">{{ post.title }}</h2>
      <div :class="contentClasses">{{ post.content }}</div>

      <!-- Shared Post Display -->
      <div v-if="post.shared_post" :class="sharedPostClasses">
        <div class="flex items-center space-x-3 mb-4">
          <img :src="post.shared_post.user?.profile_picture || '/default-avatar.png'" alt="Profile"
            class="w-10 h-10 rounded-full object-cover border-2 border-slate-300" />
          <span :class="['text-lg font-semibold', themeStore.isDarkMode ? 'text-slate-200' : 'text-slate-700']">
            {{ post.shared_post.user?.first_name }} {{ post.shared_post.user?.last_name }}
          </span>
          <span :class="['text-sm font-medium', themeStore.isDarkMode ? 'text-slate-400' : 'text-slate-500']">{{ formatTimeAgo(post.shared_post.created_at) }}</span>
        </div>
        <h3 v-if="post.shared_post.title" :class="['text-xl font-bold mb-3', themeStore.isDarkMode ? 'text-white' : 'text-slate-900']">{{ post.shared_post.title }}</h3>
        <p :class="['text-lg leading-relaxed', themeStore.isDarkMode ? 'text-slate-300' : 'text-slate-700']">{{ post.shared_post.content }}</p>
      </div>

      <!-- Media Files (Clickable to open modal) -->
      <div v-if="hasMedia" class="cursor-pointer relative rounded-2xl overflow-hidden" @click="openPostModal">
        <MediaDisplay :media-files="post.media_files" :alt-text="post.title || 'Post image'"
          @media-click="openPostModal" />
      </div>
    </div>

    <!-- Engagement Stats (Clickable to open modal) -->
    <div v-if="post.likes_count > 0 || post.comments_count > 0 || post.shares_count > 0"
      :class="['px-6 py-4 border-t-2', themeStore.isDarkMode ? 'border-slate-700' : 'border-slate-100']">
      <div :class="engagementStatsClasses">
        <div class="flex items-center space-x-6">
          <span v-if="post.likes_count > 0" class="flex items-center space-x-2 font-semibold">
            <div class="flex -space-x-1 text-xl">
              <span>👍</span>
              <span>❤️</span>
              <span>😂</span>
            </div>
            <span :class="['font-semibold', themeStore.isDarkMode ? 'text-blue-400' : 'text-blue-600']">{{ post.likes_count }} reactions</span>
          </span>
          <button v-if="post.comments_count > 0" @click="openPostModal"
            :class="['font-semibold transition-colors', themeStore.isDarkMode ? 'text-green-400 hover:text-green-300' : 'text-green-600 hover:text-green-800']">
            💬 {{ post.comments_count }} comments
          </button>
          <span v-if="post.shares_count > 0" :class="['font-semibold', themeStore.isDarkMode ? 'text-purple-400' : 'text-purple-600']">
            🔄 {{ post.shares_count }} shares
          </span>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <PostActions :post-id="post.id" :selected-reaction="selectedReaction" @react-to-post="handleReaction"
      @comment-clicked="openPostModal" @share-post="$emit('share-post', post.id)"
      @copy-link="$emit('copy-link', post.id)" @report-post="handleReportPost" />

    <!-- Quick Comment Preview (if comments exist) -->
    <div v-if="previewComments.length > 0" class="px-6 pb-4">
      <div class="space-y-3">
        <div v-for="comment in previewComments.slice(0, 2)" :key="comment.id"
          :class="commentPreviewClasses"
          @click="openPostModal">
          <img :src="comment.user.profile_picture || '/default-avatar.png'" :alt="comment.user.full_name"
            class="w-8 h-8 rounded-full object-cover flex-shrink-0" />
          <div class="flex-1 min-w-0">
            <div :class="commentBubbleClasses">
              <p :class="commentUserNameClasses">
                {{ comment.user.full_name }}
              </p>
              <p :class="commentContentClasses">
                {{ comment.content }}
              </p>
            </div>
          </div>
        </div>

        <!-- Show "view comments" indicator if there are any comments -->
        <div v-if="post.comments_count > 0" class="mt-3">
          <button @click="openPostModal"
            :class="viewCommentsClasses">
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
          :class="commentInputClasses">
          Write a comment...
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import PostHeader from './PostHeader.vue'
import MediaDisplay from './MediaDisplay.vue'
import PostActions from './PostActions.vue'

// Theme store
const themeStore = useThemeStore()

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
const emit = defineEmits([
  'react-to-post',
  'add-comment',
  'share-post',
  'copy-link',
  'open-modal',
  'delete-post',
  'pin-post',
  'feature-post',
  'report-post'
])

// Dynamic theme classes
const cardClasses = computed(() => [
  'rounded-3xl shadow-xl border-2 hover:shadow-2xl transition-all duration-300 overflow-hidden',
  themeStore.isDarkMode
    ? 'bg-slate-800 border-slate-700'
    : 'bg-white border-slate-100'
])

const titleClasses = computed(() => [
  'text-xl font-bold mb-4 leading-relaxed',
  themeStore.isDarkMode ? 'text-white' : 'text-slate-900'
])

const contentClasses = computed(() => [
  'text-base whitespace-pre-wrap mb-6 leading-relaxed',
  themeStore.isDarkMode ? 'text-slate-200' : 'text-slate-800'
])

const sharedPostClasses = computed(() => [
  'border-2 rounded-2xl p-6 mb-6',
  themeStore.isDarkMode
    ? 'border-slate-600 bg-slate-700'
    : 'border-slate-200 bg-slate-50'
])

const engagementStatsClasses = computed(() => [
  'flex items-center justify-between text-base',
  themeStore.isDarkMode ? 'text-slate-300' : 'text-slate-600'
])

const commentInputClasses = computed(() => [
  'flex-1 rounded-full px-4 py-3 text-left transition-colors text-base',
  themeStore.isDarkMode
    ? 'bg-slate-700 hover:bg-slate-600 text-slate-300'
    : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
])

const commentPreviewClasses = computed(() => [
  'flex space-x-3 cursor-pointer rounded-lg p-2 -m-2 transition-colors',
  themeStore.isDarkMode
    ? 'hover:bg-slate-700'
    : 'hover:bg-gray-50'
])

const commentBubbleClasses = computed(() => [
  'rounded-lg px-3 py-2',
  themeStore.isDarkMode ? 'bg-slate-600' : 'bg-gray-100'
])

const commentUserNameClasses = computed(() => [
  'font-semibold text-sm',
  themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
])

const commentContentClasses = computed(() => [
  'text-sm mt-1 line-clamp-2',
  themeStore.isDarkMode ? 'text-slate-200' : 'text-gray-700'
])

const viewCommentsClasses = computed(() => [
  'text-sm font-medium transition-colors',
  themeStore.isDarkMode
    ? 'text-blue-400 hover:text-blue-300'
    : 'text-blue-600 hover:text-blue-800'
])

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

// Admin control handlers
const handleDeletePost = (post) => {
  console.log('🗑️ Delete post:', post)
  emit('delete-post', post.id)
}

const handlePinPost = (post) => {
  console.log('📌 Pin/Unpin post:', post)
  emit('pin-post', post.id)
}

const handleFeaturePost = (post) => {
  console.log('⭐ Feature/Unfeature post:', post)
  emit('feature-post', post.id)
}

const handleReportPost = (post) => {
  console.log('🚨 Report post:', post)
  emit('report-post', post.id)
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
