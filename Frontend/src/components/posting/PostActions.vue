<template>
  <div :class="['px-6 py-6 border-t-2', themeStore.isDarkMode ? 'border-slate-700' : 'border-slate-100']">
    <div class="flex items-center justify-between">
      <!-- Reactions -->
      <div class="flex items-center space-x-2">
        <div class="relative group">
          <button
            @click="handleReaction('like')"
            :class="[
              'flex items-center transition-all duration-300',
              size === 'small'
                ? 'space-x-1.5 px-3 py-1.5 rounded-full font-medium text-sm'
                : 'space-x-2 px-4 py-2 rounded-full font-medium text-base',
              selectedReaction === 'like'
                ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white transform scale-105 shadow-lg'
                : (themeStore.isDarkMode ? 'text-slate-300 hover:bg-slate-600 hover:text-blue-400' : 'text-slate-600 hover:bg-blue-50 hover:text-blue-600')
            ]"
          >
            <span :class="size === 'small' ? 'text-base' : 'text-lg'">👍</span>
            <span>Like</span>
          </button>

          <!-- Reaction Picker -->
          <div class="absolute top-0 left-full ml-4 opacity-0 group-hover:opacity-100 transition-all duration-300 flex space-x-3 z-10">
            <button
              v-for="reaction in reactionTypes"
              :key="reaction.type"
              @click="handleReaction(reaction.type)"
              :class="[
                size === 'small' ? 'w-12 h-12' : 'w-14 h-14',
                'flex items-center justify-center transition-all duration-300 transform hover:scale-125'
              ]"
              :title="reaction.label"
            >
              <span :class="size === 'small' ? 'text-2xl' : 'text-3xl'">{{ reaction.emoji }}</span>
            </button>
          </div>
        </div>
      </div>

      <div class="flex items-center space-x-2">
        <!-- Comment -->
        <button
          @click="handleCommentClick"
          :class="[
            (themeStore.isDarkMode ? 'text-slate-300 hover:bg-slate-600 hover:text-green-400' : 'text-slate-600 hover:bg-green-50 hover:text-green-600'),
            'flex items-center transition-all duration-300',
            size === 'small'
              ? 'space-x-1.5 px-3 py-1.5 rounded-full font-medium text-sm'
              : 'space-x-2 px-4 py-2 rounded-full font-medium text-base'
          ]"
        >
          <svg :class="size === 'small' ? 'w-4 h-4' : 'w-5 h-5'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <span>Comment</span>
        </button>

        <!-- Share -->
        <button
          @click="$emit('share-post')"
          :class="[
            (themeStore.isDarkMode ? 'text-slate-300 hover:bg-slate-600 hover:text-purple-400' : 'text-slate-600 hover:bg-purple-50 hover:text-purple-600'),
            'flex items-center transition-all duration-300',
            size === 'small'
              ? 'space-x-1.5 px-3 py-1.5 rounded-full font-medium text-sm'
              : 'space-x-2 px-4 py-2 rounded-full font-medium text-base'
          ]"
        >
          <svg :class="size === 'small' ? 'w-4 h-4' : 'w-5 h-5'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
          </svg>
          <span>Share</span>
        </button>

        <!-- Copy Link -->
        <button
          @click="$emit('copy-link')"
          :class="[
            (themeStore.isDarkMode ? 'text-slate-300 hover:bg-slate-600 hover:text-orange-400' : 'text-slate-600 hover:bg-orange-50 hover:text-orange-600'),
            'flex items-center transition-all duration-300',
            size === 'small'
              ? 'space-x-1.5 px-3 py-1.5 rounded-full font-medium text-sm'
              : 'space-x-2 px-4 py-2 rounded-full font-medium text-base'
          ]"
        >
          <svg :class="size === 'small' ? 'w-4 h-4' : 'w-5 h-5'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          <span>Copy Link</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useThemeStore } from '@/stores/theme'

// Theme store
const themeStore = useThemeStore()

// Props
const props = defineProps({
  postId: {
    type: [String, Number],
    required: true
  },
  selectedReaction: {
    type: String,
    default: null
  },
  size: {
    type: String,
    default: 'large',
    validator: (value) => ['small', 'large'].includes(value)
  }
})

// Emits
const emit = defineEmits(['react-to-post', 'comment-clicked', 'share-post', 'copy-link'])

// Reaction types
const reactionTypes = [
  { type: 'like', emoji: '👍', label: 'Like' },
  { type: 'love', emoji: '❤️', label: 'Love' },
  { type: 'laugh', emoji: '😂', label: 'Laugh' },
  { type: 'wow', emoji: '😮', label: 'Wow' },
  { type: 'sad', emoji: '😢', label: 'Sad' },
  { type: 'angry', emoji: '😠', label: 'Angry' }
]

// Methods
const handleReaction = (reactionType) => {
  emit('react-to-post', props.postId, reactionType)
}

const handleCommentClick = () => {
  console.log('💬 PostActions: Comment button clicked')
  emit('comment-clicked')
}
</script>

<style scoped>
/* Smooth transitions for all interactive elements */
.transition-all {
  transition: all 0.3s ease;
}

/* Enhanced hover effects */
button:hover:not(:disabled) {
  transform: translateY(-1px);
}

/* Focus states for accessibility */
button:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Reaction picker enhanced styling */
.group:hover .group-hover\:opacity-100 {
  opacity: 1;
  transform: translateY(-5px);
}

/* Enhanced card shadows */
.shadow-md {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.shadow-lg {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.shadow-2xl {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

/* Reaction picker positioning */
.group:hover .group-hover\:opacity-100 {
  opacity: 1;
}
</style>
