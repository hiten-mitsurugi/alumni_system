<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border dark:border-gray-700">
    <!-- Header -->
    <div class="p-6 border-b dark:border-gray-700">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white">
          Recent Posts
        </h3>
        <div class="flex items-center space-x-2">
          <button 
            @click="$emit('refresh')"
            :disabled="loading"
            class="text-sm text-blue-600 dark:text-blue-400 hover:underline disabled:opacity-50"
          >
            <RefreshCw class="w-4 h-4 inline mr-1" :class="{ 'animate-spin': loading }" />
            Refresh
          </button>
          <router-link 
            to="/admin/contents"
            class="text-sm text-blue-600 dark:text-blue-400 hover:underline"
          >
            View All
          </router-link>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="p-6">
      <div class="space-y-4">
        <div v-for="i in 3" :key="i" class="animate-pulse">
          <div class="flex items-center space-x-3">
            <div class="h-10 w-10 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
            <div class="flex-1 space-y-2">
              <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>
              <div class="h-3 bg-gray-300 dark:bg-gray-600 rounded w-1/2"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="p-6 text-center">
      <AlertCircle class="w-8 h-8 text-red-500 mx-auto mb-2" />
      <p class="text-sm text-red-600 dark:text-red-400">{{ error }}</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="posts.length === 0" class="p-6 text-center">
      <FileText class="w-8 h-8 text-gray-400 mx-auto mb-2" />
      <p class="text-sm text-gray-500 dark:text-gray-400">No recent posts found</p>
    </div>

    <!-- Posts List -->
    <div v-else class="divide-y dark:divide-gray-700 max-h-96 overflow-y-auto">
      <div 
        v-for="post in posts" 
        :key="post.id"
        class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        <div class="flex items-start space-x-3">
          <!-- Author Avatar -->
          <div class="flex-shrink-0">
            <img 
              v-if="getAuthor(post)?.profile_picture" 
              :src="getAuthor(post).profile_picture" 
              :alt="getAuthorName(post)"
              class="w-10 h-10 rounded-full object-cover"
            >
            <div 
              v-else
              class="w-10 h-10 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center"
            >
              <User class="w-5 h-5 text-gray-500 dark:text-gray-400" />
            </div>
          </div>

          <!-- Post Content -->
          <div class="flex-1 min-w-0">
            <!-- Post Header -->
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center space-x-2">
                  <span class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ getAuthorName(post) }}
                  </span>
                <span class="text-xs text-gray-500 dark:text-gray-400">
                  {{ formatRelativeTime(post.created_at) }}
                </span>
              </div>
              <div class="flex items-center space-x-2">
                <!-- Status Badge -->
                <span 
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="getStatusClass(post.status)"
                >
                  {{ getStatusLabel(post.status) }}
                </span>
              </div>
            </div>

            <!-- Post Content Preview -->
            <p class="text-sm text-gray-700 dark:text-gray-300 mb-2 line-clamp-1">
              {{ post.content || 'No content available' }}
            </p>

            <!-- Post Image Preview -->
            <div v-if="post.image" class="mb-2">
              <img 
                :src="post.image" 
                :alt="'Post image'"
                class="w-full h-20 object-cover rounded"
              >
            </div>

            <!-- Post Metadata -->
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                <span v-if="post.likes_count">
                  <Heart class="w-3 h-3 inline mr-1" />
                  {{ post.likes_count }} likes
                </span>
                <span v-if="post.comments_count">
                  <MessageCircle class="w-3 h-3 inline mr-1" />
                  {{ post.comments_count }} comments
                </span>
                <span v-if="post.category">
                  <Tag class="w-3 h-3 inline mr-1" />
                  {{ post.category }}
                </span>
              </div>

              <!-- Quick Actions -->
              <div class="flex items-center space-x-2">
                <button
                  v-if="post.status === 'pending'"
                  @click="$emit('approve-post', post.id)"
                  class="text-xs text-green-600 hover:text-green-700 dark:text-green-400"
                  title="Approve Post"
                >
                  <Check class="w-4 h-4" />
                </button>
                <button
                  v-if="post.status === 'pending'"
                  @click="$emit('reject-post', post.id)"
                  class="text-xs text-red-600 hover:text-red-700 dark:text-red-400"
                  title="Reject Post"
                >
                  <X class="w-4 h-4" />
                </button>
                <button
                  @click="$emit('view-post', post)"
                  class="text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400"
                  title="View Details"
                >
                  <Eye class="w-4 h-4" />
                </button>
                <button
                  @click="$emit('delete-post', post.id)"
                  class="text-xs text-red-600 hover:text-red-700 dark:text-red-400"
                  title="Delete Post"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div v-if="posts.length > 0" class="p-4 border-t dark:border-gray-700">
      <div class="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
        <span>Showing {{ posts.length }} recent posts</span>
        <router-link 
          to="/admin/contents"
          class="text-blue-600 dark:text-blue-400 hover:underline"
        >
          Manage all posts →
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { 
  RefreshCw, AlertCircle, FileText, User, Heart, MessageCircle, 
  Tag, Check, X, Eye, Trash2 
} from 'lucide-vue-next'

// Props
const props = defineProps({
  posts: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  }
})

// Emits
const emit = defineEmits([
  'refresh', 'approve-post', 'reject-post', 
  'view-post', 'delete-post'
])

// Utility methods
// Utility to get author object from different possible keys returned by API
const getAuthor = (post) => {
  return post.author || post.user || post.user_info || null
}

const getAuthorName = (post) => {
  const author = getAuthor(post)
  if (!author) return 'Unknown User'
  // Prefer a provided full_name field, then first/last, then username or email
  if (author.full_name) return author.full_name
  const name = `${author.first_name || ''} ${author.last_name || ''}`.trim()
  if (name) return name
  return author.username || author.email || 'Anonymous'
}

const getStatusClass = (status) => {
  switch (status) {
    case 'approved':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
    case 'pending':
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
    case 'declined':
      return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
  }
}

const getStatusLabel = (status) => {
  switch (status) {
    case 'approved': return 'Approved'
    case 'pending': return 'Pending'
    case 'declined': return 'Declined'
    default: return 'Unknown'
  }
}

const formatRelativeTime = (dateString) => {
  if (!dateString) return 'Unknown'
  
  try {
    const date = new Date(dateString)
    const now = new Date()
    const diffInSeconds = Math.floor((now - date) / 1000)
    
    if (diffInSeconds < 60) return 'Just now'
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`
    
    return date.toLocaleDateString()
  } catch {
    return 'Invalid date'
  }
}
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>