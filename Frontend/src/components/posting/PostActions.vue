<template>
  <div :class="size === 'small' ? 'px-2 sm:px-4 py-2 sm:py-4 border-t border-slate-200 bg-slate-50' : 'px-4 sm:px-6 py-3 sm:py-6 border-t-2 border-slate-100 bg-slate-50'">
    <div :class="size === 'small' ? 'flex items-center justify-around' : 'flex items-center justify-between space-x-1 sm:space-x-2'">
      <!-- Reactions -->
      <div class="flex items-center">
        <div class="relative group">
          <button
            @click="handleMainButtonClick"
            :class="[
              'flex items-center transition-all duration-300 cursor-pointer relative z-10 group',
              size === 'small' 
                ? 'space-x-1 sm:space-x-2 px-2 sm:px-3 py-1.5 sm:py-2 rounded-md sm:rounded-lg font-medium text-xs sm:text-sm shadow-sm'
                : 'space-x-2 sm:space-x-3 px-2 sm:px-4 py-1.5 sm:py-2 rounded-lg sm:rounded-2xl font-semibold text-sm sm:text-lg shadow-md',
              selectedReaction
                ? 'bg-gradient-to-r from-green-600 to-green-700 text-white transform scale-105 hover:from-green-700 hover:to-green-800 hover:scale-110' + (size === 'small' ? ' shadow-md' : ' shadow-lg')
                : 'text-green-700 border border-green-700 hover:bg-green-100 hover:text-green-700 bg-white hover:scale-105'
            ]"
            :title="getMainButtonTooltip()"
          >
            <!-- Reaction Icon (consistent with other buttons) -->
            <svg v-if="!selectedReaction" :class="size === 'small' ? 'w-4 h-4 sm:w-5 sm:h-5' : 'w-5 h-5 sm:w-6 sm:h-6'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.20-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
            </svg>
            <!-- Show emoji when reaction is selected -->
            <span v-if="selectedReaction" :class="size === 'small' ? 'text-base sm:text-xl' : 'text-xl sm:text-2xl'">{{ currentReactionEmoji }}</span>
            <span class="hidden sm:inline">{{ selectedReaction ? currentReactionLabel : 'Like' }}</span>
            <span class="sm:hidden text-xs">{{ selectedReaction ? currentReactionEmoji : 'Like' }}</span>
          </button>
          
          <!-- Reaction Picker -->
          <div :class="size === 'small' ? 'absolute bottom-full left-0 mb-2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 delay-300 bg-white border border-slate-200 rounded-2xl shadow-xl p-3 flex space-x-2 z-30' : 'absolute bottom-full left-0 mb-3 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 delay-300 bg-white border-2 border-slate-200 rounded-3xl shadow-2xl p-4 flex space-x-3 z-30'">
            <button
              v-for="reaction in reactionTypes"
              :key="reaction.type"
              @click="handleReaction(reaction.type)"
              :class="[
                size === 'small' ? 'w-10 h-10' : 'w-12 h-12',
                'flex flex-col items-center justify-center rounded-xl transition-all duration-200 transform hover:scale-110 hover:shadow-lg group/reaction',
                selectedReaction === reaction.type 
                  ? 'bg-green-100 border-2 border-green-500 scale-105' 
                  : 'hover:bg-slate-100'
              ]"
              :title="selectedReaction === reaction.type ? `Click to remove ${reaction.label}` : reaction.label"
            >
              <span :class="size === 'small' ? 'text-lg' : 'text-2xl'" class="filter drop-shadow-sm">{{ reaction.emoji }}</span>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Comment -->
      <button
        @click="handleCommentClick"
        :class="[
          'flex items-center text-green-700 hover:bg-green-100 hover:text-green-700 transition-all duration-300 bg-white border border-green-700 rounded-md',
          size === 'small' 
            ? 'space-x-1 sm:space-x-2 px-2 sm:px-3 py-1.5 sm:py-2 rounded-md sm:rounded-lg font-medium text-xs sm:text-sm shadow-sm'
            : 'space-x-2 sm:space-x-3 px-2 sm:px-4 py-1.5 sm:py-2 rounded-lg sm:rounded-2xl font-semibold text-sm sm:text-lg shadow-md'
        ]"
      >
        <svg :class="size === 'small' ? 'w-4 h-4 sm:w-5 sm:h-5' : 'w-5 h-5 sm:w-6 sm:h-6'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        <span class="hidden sm:inline">Comment</span>
        <span class="sm:hidden text-xs">Comment</span>
      </button>
      
      <!-- Repost -->
      <button
        @click="$emit('share-post')"
        :class="[
          'flex items-center text-green-700 hover:bg-green-100 hover:text-green-700 transition-all duration-300 bg-white border border-green-700 rounded-md',
          size === 'small' 
            ? 'space-x-1 sm:space-x-2 px-2 sm:px-3 py-1.5 sm:py-2 rounded-md sm:rounded-lg font-medium text-xs sm:text-sm shadow-sm'
            : 'space-x-2 sm:space-x-3 px-2 sm:px-4 py-1.5 sm:py-2 rounded-lg sm:rounded-2xl font-semibold text-sm sm:text-lg shadow-md'
        ]"
      >
        <svg :class="size === 'small' ? 'w-4 h-4 sm:w-5 sm:h-5' : 'w-5 h-5 sm:w-6 sm:h-6'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        <span class="hidden sm:inline">Repost</span>
        <span class="sm:hidden text-xs">Repost</span>
      </button>
      
      <!-- Copy Link -->
      <button
        @click="$emit('copy-link')"
        :class="[
          'flex items-center text-green-700 hover:bg-green-100 hover:text-green-700 transition-all duration-300 bg-white border border-green-700 rounded-md',
          size === 'small' 
            ? 'space-x-1 sm:space-x-2 px-2 sm:px-3 py-1.5 sm:py-2 rounded-md sm:rounded-lg font-medium text-xs sm:text-sm shadow-sm'
            : 'space-x-2 sm:space-x-3 px-2 sm:px-4 py-1.5 sm:py-2 rounded-lg sm:rounded-2xl font-semibold text-sm sm:text-lg shadow-md'
        ]"
      >
        <svg :class="size === 'small' ? 'w-4 h-4 sm:w-5 sm:h-5' : 'w-5 h-5 sm:w-6 sm:h-6'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
        </svg>
        <span class="hidden sm:inline">Copy Link</span>
        <span class="sm:hidden text-xs">Copy</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

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

// Reaction types - LinkedIn style
const reactionTypes = [
  { type: 'like', emoji: '👍', label: 'Like' },
  { type: 'applaud', emoji: '👏', label: 'Applaud' },
  { type: 'heart', emoji: '❤️', label: 'Heart' },
  { type: 'support', emoji: '🤝', label: 'Support' },
  { type: 'laugh', emoji: '😂', label: 'Laugh' },
  { type: 'sad', emoji: '😢', label: 'Sad' }
]

// Methods
const handleReaction = (reactionType) => {
  console.log('🎯 PostActions: handleReaction called', {
    reactionType,
    currentSelectedReaction: props.selectedReaction,
    postId: props.postId,
    isUndo: props.selectedReaction === reactionType
  });
  
  // Just emit the reaction - let the parent handle the undo logic
  emit('react-to-post', props.postId, reactionType)
}

// Smart main button handler for Facebook-style behavior
const handleMainButtonClick = () => {
  console.log('🎯 PostActions: Main button clicked', {
    currentSelectedReaction: props.selectedReaction,
    postId: props.postId
  });
  
  if (props.selectedReaction) {
    // If user has a reaction, clicking main button should remove it
    emit('react-to-post', props.postId, props.selectedReaction)
  } else {
    // If no reaction, add 'like' as default
    emit('react-to-post', props.postId, 'like')
  }
}

// Enhanced tooltip for better UX
const getMainButtonTooltip = () => {
  if (props.selectedReaction) {
    return `Click to remove your ${currentReactionLabel.value} reaction`
  }
  return 'Click to like this post'
}

const handleCommentClick = () => {
  console.log('💬 PostActions: Comment button clicked')
  emit('comment-clicked')
}

// Computed properties for current reaction
const currentReactionEmoji = computed(() => {
  if (!props.selectedReaction) return '👍'
  const reaction = reactionTypes.find(r => r.type === props.selectedReaction)
  return reaction ? reaction.emoji : '👍'
})

const currentReactionLabel = computed(() => {
  if (!props.selectedReaction) return 'React'
  const reaction = reactionTypes.find(r => r.type === props.selectedReaction)
  return reaction ? reaction.label : 'React'
})
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

/* Smooth scale animations for buttons */
.group:hover {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Reaction button specific animations */
button[title]:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 8px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
}

/* Active state feedback */
button:active {
  transform: translateY(0) scale(0.98);
  transition: all 0.1s ease;
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

/* Mobile optimizations */
@media (max-width: 640px) {
  /* Ensure buttons are evenly spaced on mobile */
  .justify-between {
    justify-content: space-around;
  }
  
  /* Compact button sizing on mobile */
  .space-x-1 > :not([hidden]) ~ :not([hidden]) {
    margin-left: 0.25rem;
  }
  
  /* Make sure all buttons fit within mobile viewport */
  button {
    min-width: 0;
    flex-shrink: 1;
  }
  
  /* Reduce padding on very small screens */
  .px-2 {
    padding-left: 0.375rem;
    padding-right: 0.375rem;
  }
  
  .py-1\.5 {
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
  }
  
  /* Ensure text doesn't wrap */
  span {
    white-space: nowrap;
  }
  
  /* Mobile-specific button adjustments */
  .text-xs {
    font-size: 0.7rem;
    line-height: 1rem;
  }
}
</style>
