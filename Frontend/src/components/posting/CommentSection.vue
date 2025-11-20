<template>
  <div v-if="showComments" class="border-t-2 border-slate-200 bg-gradient-to-b from-slate-50 to-white">
    <!-- Add Comment -->
    <div class="p-3 sm:p-4 md:p-6 border-b-2 border-slate-200">
      <div class="flex space-x-2 sm:space-x-3 md:space-x-4 items-start">
        <img 
          :src="userProfilePicture || '/default-avatar.png'"
          alt="Your Profile"
          class="w-9 h-9 sm:w-10 sm:h-10 md:w-12 md:h-12 rounded-full object-cover border-2 border-blue-200 shadow-md flex-shrink-0"
        />
        <div class="flex-1 min-w-0">
          <div class="flex space-x-2 sm:space-x-3 items-center">
            <input
              v-model="localComment"
              type="text"
              placeholder="Write a thoughtful comment..."
              @keypress.enter="addComment"
              class="flex-1 px-3 py-2 sm:px-4 sm:py-3 md:py-3 text-sm sm:text-base md:text-lg border-2 border-slate-300 rounded-xl sm:rounded-2xl focus:ring-2 sm:focus:ring-4 focus:ring-blue-300 focus:border-blue-500 shadow-md h-10 sm:h-12 md:h-auto"
            />
            <button
              @click="addComment"
              :disabled="!localComment?.trim()"
              class="w-10 h-10 sm:w-12 sm:h-12 md:w-auto md:h-auto md:px-6 md:py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl sm:rounded-2xl hover:from-blue-700 hover:to-blue-800 disabled:from-slate-300 disabled:to-slate-400 disabled:cursor-not-allowed shadow-lg transition-all duration-300 font-semibold flex-shrink-0 flex items-center justify-center touch-manipulation"
            >
              <svg class="w-5 h-5 sm:w-6 sm:h-6 md:w-6 md:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Comments List -->
    <div v-if="comments && comments.length > 0" class="p-3 sm:p-4 md:p-6 space-y-3 sm:space-y-4 md:space-y-6">
      <div
        v-for="comment in comments"
        :key="comment.id"
        class="flex space-x-2 sm:space-x-3 md:space-x-4 items-start"
      >
        <img 
          :src="comment.user?.profile_picture || '/default-avatar.png'"
          alt="Profile"
          class="w-9 h-9 sm:w-10 sm:h-10 md:w-12 md:h-12 rounded-full object-cover border-2 border-slate-200 shadow-md flex-shrink-0"
        />
        <div class="flex-1 min-w-0">
          <div class="bg-white rounded-lg sm:rounded-xl md:rounded-2xl px-3 py-2 sm:px-4 sm:py-3 md:px-6 md:py-4 shadow-md border border-slate-200">
            <div class="font-bold text-sm sm:text-base md:text-lg text-slate-900 mb-1">{{ comment.user?.name || 'Anonymous' }}</div>
            <MentionText 
              :content="comment.content"
              :mentions="comment.mentions || []"
              :available-users="{ [comment.user.username]: { full_name: comment.user.full_name, name: comment.user.name } }"
              className="text-sm sm:text-base md:text-lg text-slate-800 leading-relaxed"
            />
          </div>
          <div class="mt-1 sm:mt-2 text-xs sm:text-sm text-slate-500 px-3 sm:px-4 md:px-6 font-medium">
            {{ formatTimeAgo(comment.created_at) }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- Empty Comments State -->
    <div v-else class="p-4 sm:p-6 text-center text-slate-500">
      <svg class="mx-auto h-8 w-8 sm:h-10 sm:w-10 md:h-12 md:w-12 text-slate-300 mb-2 sm:mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
      <p class="text-base sm:text-lg font-medium">No comments yet</p>
      <p class="text-xs sm:text-sm">Be the first to share your thoughts!</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import MentionText from '@/components/common/MentionText.vue'

// Props
const props = defineProps({
  postId: {
    type: [String, Number],
    required: true
  },
  showComments: {
    type: Boolean,
    default: false
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
const emit = defineEmits(['add-comment'])

// Local state
const localComment = ref('')

// Methods
const addComment = () => {
  const content = localComment.value?.trim()
  if (!content) return
  
  emit('add-comment', props.postId, content)
  localComment.value = ''
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
/* Focus states for accessibility */
input:focus, button:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Enhanced hover effects */
button:hover:not(:disabled) {
  transform: translateY(-1px);
}

/* Smooth transitions for all interactive elements */
.transition-all {
  transition: all 0.3s ease;
}

/* Enhanced spacing for better readability */
.leading-relaxed {
  line-height: 1.75;
}

/* Enhanced card shadows */
.shadow-md {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.shadow-lg {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}
</style>
