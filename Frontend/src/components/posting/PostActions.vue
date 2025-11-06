<template>
  <div :class="themeStore.isAdminDark() ? 
    (size === 'small' ? 'px-2 sm:px-3 py-3' : 'px-4 py-4') : 
    (size === 'small' ? 'px-2 sm:px-3 py-3' : 'px-4 py-4')">
    <div class="flex items-center gap-0 w-full justify-between">
      <!-- Reactions -->
      <div class="flex justify-center flex-1">
        <div class="relative group flex justify-center w-full">
          <button
            @click="handleReaction('like')"
            :class="[
              'action-btn transition-all duration-300 cursor-pointer relative z-10 flex items-center justify-center flex-1',
              size === 'small' ? 'action-small' : 'action-regular',
              selectedReaction ? 'active-reaction' : 'action-neutral',
              'action-compact'
            ]"
          >
            <!-- Reaction Icon (consistent with other buttons) -->
            <svg v-if="!selectedReaction" class="action-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.20-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
            </svg>
            <!-- Show emoji when reaction is selected -->
            <span v-if="selectedReaction" class="text-xl">{{ currentReactionEmoji }}</span>

            <!-- Tooltip for desktop -->
            <span class="action-tooltip">React</span>
          </button>

          <!-- Reaction picker buttons -->
          <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto transition-opacity duration-200 flex gap-1 bg-white rounded-lg shadow-lg p-2">
            <button
              v-for="reaction in reactionTypes"
              :key="reaction.type"
              @click="handleReaction(reaction.type)"
              :class="['flex items-center justify-center rounded-md transition-all duration-150 hover:bg-orange-100', size === 'small' ? 'w-8 h-8 text-base' : 'w-9 h-9 text-lg']"
              :title="reaction.label"
            >
              <span :class="size === 'small' ? 'text-base filter drop-shadow-sm' : 'text-lg filter drop-shadow-sm'">{{ reaction.emoji }}</span>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Comment -->
      <div class="flex justify-center flex-1">
        <button
          @click="handleCommentClick"
          class="action-btn action-neutral action-compact flex-1"
          aria-label="Comment"
        >
          <svg class="action-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <span class="action-tooltip">Comment</span>
          <span class="action-label sm:hidden">Comment</span>
        </button>
      </div>

      <!-- Share/Repost -->
      <div class="flex justify-center flex-1">
        <button
          @click="handleShare"
          class="action-btn action-neutral action-compact flex-1"
          aria-label="Repost"
        >
          <svg class="action-icon" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
          </svg>
          <span class="action-tooltip">Repost</span>
          <span class="action-label sm:hidden">Repost</span>
        </button>
      </div>

      <!-- Copy Link -->
      <div class="flex justify-center flex-1">
        <button
          @click="$emit('copy-link')"
          class="action-btn action-neutral action-compact flex-1"
          aria-label="Copy link"
        >
          <svg class="action-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          <span class="action-tooltip">Copy Link</span>
          <span class="action-label sm:hidden">Copy Link</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
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
const emit = defineEmits(['react-to-post', 'comment-clicked', 'copy-link', 'share-post'])

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
  emit('react-to-post', props.postId, reactionType)
}

const handleCommentClick = () => {
  console.log('💬 PostActions: Comment button clicked')
  emit('comment-clicked')
}

const handleShare = () => {
  console.log('🔄 PostActions: Share button clicked')
  emit('share-post', props.postId)
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
/* Modern action button styles with circular design */
.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border-radius: 9999px; /* Full rounded for modern pill shape */
  border: none;
  background: transparent;
  transition: all 0.2s ease;
  position: relative;
  width: 100%;
  flex: 1;
}
.action-regular {
  padding: 0.5rem 1rem;
  font-weight: 500;
  font-size: 0.875rem;
}
.action-small {
  padding: 0.375rem 0.75rem;
  font-weight: 500;
  font-size: 0.8rem;
}
.action-neutral {
  color: #f97316; /* orange-500 */
  background: transparent;
}
.action-compact {
  padding: 0.5rem 1rem;
  min-height: 2.5rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border: none;
  background: transparent;
  flex: 1;
  width: 100%;
}
.action-icon {
  width: 1.25rem; /* 20px */
  height: 1.25rem; /* 20px */
  color: #f97316; /* orange-500 for modern neutral icons */
  display: inline-block;
  transition: all 0.2s ease;
}

/* Thicken SVG strokes inside action icons when possible */
.action-icon path,
.action-icon line,
.action-icon circle,
.action-icon rect {
  stroke-width: 2.2 !important;
}
.action-label {
  color: #f97316; /* orange-500 for modern neutral text */
  font-size: 0.875rem;
  font-weight: 600;
}

/* Tooltip (desktop): modern tooltip design */
.action-tooltip {
  position: absolute;
  top: -2.5rem;
  left: 50%;
  transform: translateX(-50%) translateY(0.5rem);
  background: rgba(17, 24, 39, 0.9); /* More modern dark background */
  color: white;
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease, transform 0.2s ease;
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* Show tooltip when its parent button is hovered (desktop) */
button:hover .action-tooltip {
  opacity: 1;
  transform: translateX(-50%) translateY(-0.25rem);
}

/* Hide tooltip on small screens (use inline labels instead) */
@media (max-width: 640px) {
  .action-tooltip { display: none; }
}

/* Ensure each action column receives equal width */
.flex-1 {
  flex: 1 1 0%;
}

/* Compact action button baseline */
.action-compact {
  padding: 0.5rem 0.25rem;
  min-width: 3.25rem;
  border-radius: 0.5rem;
}

/* Remove border visuals and keep only color and hover */
.action-neutral {
  color: #f97316; /* orange-500 */
  background: transparent;
  border: none;
}

.action-btn:hover {
  background-color: rgba(249, 115, 22, 0.1); /* orange-500 with transparency */
  color: #ea580c; /* orange-600 */
  border-radius: 9999px; /* Keep full rounded on hover */
  transform: scale(1.05); /* Subtle scale instead of translate */
}

.action-btn:hover .action-icon {
  color: #ea580c; /* orange-600 */
  transform: scale(1.1);
}

.action-btn:hover .action-label {
  color: #ea580c; /* orange-600 */
}

.active-reaction {
  background: rgba(249, 115, 22, 0.1); /* orange-500 transparent */
  color: #f97316 !important; /* orange-500 */
  border-radius: 9999px;
}

.active-reaction .action-icon {
  color: #f97316 !important; /* orange-500 */
}

/* Smooth transitions for all interactive elements */
.transition-all {
  transition: all 0.3s ease;
}

/* Enhanced hover effects - modern subtle hover without jumping */

/* Focus states for accessibility */
button:focus {
  outline: 2px solid #f97316; /* orange-500 */
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
