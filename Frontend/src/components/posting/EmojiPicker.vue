<template>
  <div class="relative emoji-picker-container">
    <!-- Emoji Picker Dropdown -->
    <div 
      v-if="isVisible"
      class="absolute bottom-12 left-0 w-80 h-80 bg-white border border-gray-200 rounded-lg shadow-xl z-50 overflow-hidden"
    >
      <!-- Header with search and categories -->
      <div class="p-3 border-b border-gray-200">
        <!-- Search -->
        <div class="relative mb-2">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search emojis..."
            class="w-full px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            @input="handleSearch"
          />
          <svg class="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        
        <!-- Category tabs -->
        <div class="flex gap-1">
          <button
            v-for="category in categories"
            :key="category.name"
            @click="activeCategory = category.name"
            :class="[
              'px-2 py-1 text-xs rounded transition-colors',
              activeCategory === category.name 
                ? 'bg-blue-100 text-blue-600' 
                : 'text-gray-600 hover:bg-gray-100'
            ]"
            :title="category.name"
          >
            {{ category.icon }}
          </button>
        </div>
      </div>

      <!-- Recent emojis section -->
      <div v-if="!searchQuery && recentEmojis.length > 0" class="p-2 border-b border-gray-100">
        <div class="text-xs text-gray-500 mb-1">Recently used</div>
        <div class="grid grid-cols-8 gap-1">
          <button
            v-for="emoji in recentEmojis.slice(0, 16)"
            :key="`recent-${emoji}`"
            @click="selectEmoji(emoji)"
            class="p-1 text-lg hover:bg-gray-100 rounded transition-colors"
            :title="emoji"
          >
            {{ emoji }}
          </button>
        </div>
      </div>

      <!-- Emoji grid -->
      <div class="flex-1 overflow-y-auto p-2">
        <div class="grid grid-cols-8 gap-1">
          <button
            v-for="emoji in displayedEmojis"
            :key="emoji"
            @click="selectEmoji(emoji)"
            class="p-1 text-lg hover:bg-gray-100 rounded transition-colors"
            :title="emoji"
          >
            {{ emoji }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['emoji-selected', 'close'])

const searchQuery = ref('')
const activeCategory = ref('smileys')
const recentEmojis = ref([])

// Emoji categories with popular emojis
const categories = [
  {
    name: 'smileys',
    icon: '😀',
    emojis: [
      '😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣',
      '😊', '😇', '🙂', '🙃', '😉', '😌', '😍', '🥰',
      '😘', '😗', '😙', '😚', '😋', '😛', '😝', '😜',
      '🤪', '🤨', '🧐', '🤓', '😎', '🤩', '🥳', '😏',
      '😒', '😞', '😔', '😟', '😕', '🙁', '☹️', '😣',
      '😖', '😫', '😩', '🥺', '😢', '😭', '😤', '😠',
      '😡', '🤬', '🤯', '😳', '🥵', '🥶', '😱', '😨',
      '😰', '😥', '😓', '🤗', '🤔', '🤭', '🤫', '🤥',
      '😶', '😐', '😑', '😬', '🙄', '😯', '😦', '😧',
      '😮', '😲', '🥱', '😴', '🤤', '😪', '😵', '🤐'
    ]
  },
  {
    name: 'people',
    icon: '👥',
    emojis: [
      '👋', '🤚', '🖐️', '✋', '🖖', '👌', '🤌', '🤏',
      '✌️', '🤞', '🤟', '🤘', '🤙', '👈', '👉', '👆',
      '🖕', '👇', '☝️', '👍', '👎', '👊', '✊', '🤛',
      '🤜', '👏', '🙌', '👐', '🤲', '🤝', '🙏', '✍️',
      '💅', '🤳', '💪', '🦾', '🦿', '🦵', '🦶', '👂',
      '🦻', '👃', '🧠', '🫀', '🫁', '🦷', '🦴', '👀',
      '👁️', '👅', '👄', '💋', '🩸', '👶', '🧒', '👦',
      '👧', '🧑', '👱', '👨', '🧔', '👩', '🧓', '👴',
      '👵', '🙍', '🙎', '🙅', '🙆', '💁', '🙋', '🧏'
    ]
  },
  {
    name: 'animals',
    icon: '🐶',
    emojis: [
      '🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼',
      '🐨', '🐯', '🦁', '🐮', '🐷', '🐽', '🐸', '🐵',
      '🙈', '🙉', '🙊', '🐒', '🐔', '🐧', '🐦', '🐤',
      '🐣', '🐥', '🦆', '🦅', '🦉', '🦇', '🐺', '🐗',
      '🐴', '🦄', '🐝', '🐛', '🦋', '🐌', '🐞', '🐜',
      '🦟', '🦗', '🕷️', '🕸️', '🦂', '🐢', '🐍', '🦎',
      '🦖', '🦕', '🐙', '🦑', '🦐', '🦞', '🦀', '🐡',
      '🐠', '🐟', '🐬', '🐳', '🐋', '🦈', '🐊', '🐅',
      '🐆', '🦓', '🦍', '🦧', '🐘', '🦛', '🦏', '🐪'
    ]
  },
  {
    name: 'food',
    icon: '🍕',
    emojis: [
      '🍎', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓',
      '🫐', '🍈', '🍒', '🍑', '🥭', '🍍', '🥥', '🥝',
      '🍅', '🍆', '🥑', '🥦', '🥬', '🥒', '🌶️', '🫑',
      '🌽', '🥕', '🫒', '🧄', '🧅', '🥔', '🍠', '🥐',
      '🥯', '🍞', '🥖', '🥨', '🧀', '🥚', '🍳', '🧈',
      '🥞', '🧇', '🥓', '🥩', '🍗', '🍖', '🌭', '🍔',
      '🍟', '🍕', '🥪', '🥙', '🌮', '🌯', '🫔', '🥗',
      '🥘', '🫕', '🍝', '🍜', '🍲', '🍛', '🍣', '🍱',
      '🥟', '🦪', '🍤', '🍙', '🍚', '🍘', '🍥', '🥠'
    ]
  },
  {
    name: 'activities',
    icon: '⚽',
    emojis: [
      '⚽', '🏀', '🏈', '⚾', '🥎', '🎾', '🏐', '🏉',
      '🥏', '🎱', '🪀', '🏓', '🏸', '🏒', '🏑', '🥍',
      '🏏', '🪃', '🥅', '⛳', '🪁', '🏹', '🎣', '🤿',
      '🥊', '🥋', '🎽', '🛹', '🛷', '⛸️', '🥌', '🎿',
      '⛷️', '🏂', '🪂', '🏋️', '🤼', '🤸', '⛹️', '🤺',
      '🏊', '🏄', '🚣', '🧗', '🚵', '🚴', '🏆', '🥇',
      '🥈', '🥉', '🏅', '🎖️', '🏵️', '🎗️', '🎫', '🎟️',
      '🎪', '🤹', '🎭', '🩰', '🎨', '🎬', '🎤', '🎧',
      '🎼', '🎵', '🎶', '🥁', '🪘', '🎹', '🎻', '🎺'
    ]
  },
  {
    name: 'travel',
    icon: '✈️',
    emojis: [
      '🚗', '🚕', '🚙', '🚌', '🚎', '🏎️', '🚓', '🚑',
      '🚒', '🚐', '🛻', '🚚', '🚛', '🚜', '🏍️', '🛵',
      '🚲', '🛴', '🛹', '🛼', '🚁', '🛸', '✈️', '🛩️',
      '🛫', '🛬', '🪂', '⛵', '🚤', '🛥️', '🛳️', '⛴️',
      '🚢', '⚓', '⛽', '🚧', '🚦', '🚥', '🚏', '🗺️',
      '🗿', '🗽', '🗼', '🏰', '🏯', '🏟️', '🎡', '🎢',
      '🎠', '⛲', '⛱️', '🏖️', '🏝️', '🏜️', '🌋', '⛰️',
      '🏔️', '🗻', '🏕️', '⛺', '🛖', '🏠', '🏡', '🏘️',
      '🏚️', '🏗️', '🏭', '🏢', '🏬', '🏣', '🏤', '🏥'
    ]
  },
  {
    name: 'objects',
    icon: '💎',
    emojis: [
      '⌚', '📱', '📲', '💻', '⌨️', '🖥️', '🖨️', '🖱️',
      '🖲️', '🕹️', '💽', '💾', '💿', '📀', '📼', '📷',
      '📸', '📹', '🎥', '📽️', '🎞️', '📞', '☎️', '📟',
      '📠', '📺', '📻', '🎙️', '🎚️', '🎛️', '🧭', '⏰',
      '⏲️', '⏱️', '⏳', '⌛', '📡', '🔋', '🔌', '💡',
      '🔦', '🕯️', '🪔', '🧯', '🛢️', '💸', '💵', '💴',
      '💶', '💷', '🪙', '💰', '💳', '💎', '⚖️', '🧰',
      '🔧', '🔨', '⚒️', '🛠️', '⛏️', '🪓', '🪚', '🔩',
      '⚙️', '🪜', '⛓️', '🧲', '🔫', '💣', '🧨', '🪓'
    ]
  },
  {
    name: 'symbols',
    icon: '❤️',
    emojis: [
      '❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍',
      '🤎', '💔', '❣️', '💕', '💞', '💓', '💗', '💖',
      '💘', '💝', '💟', '☮️', '✝️', '☪️', '🕉️', '☸️',
      '✡️', '🔯', '🕎', '☯️', '☦️', '🛐', '⛎', '♈',
      '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐',
      '♑', '♒', '♓', '🆔', '⚛️', '🉑', '☢️', '☣️',
      '📴', '📳', '🈶', '🈚', '🈸', '🈺', '🈷️', '✴️',
      '🆚', '💮', '🉐', '㊙️', '㊗️', '🈴', '🈵', '🈹',
      '🈲', '🅰️', '🅱️', '🆎', '🆑', '🅾️', '🆘', '❌'
    ]
  }
]

// Computed properties
const currentCategoryEmojis = computed(() => {
  const category = categories.find(cat => cat.name === activeCategory.value)
  return category ? category.emojis : []
})

const displayedEmojis = computed(() => {
  if (searchQuery.value) {
    // Simple search - could be enhanced with emoji names/keywords
    return allEmojis.value.filter(emoji => 
      emoji.includes(searchQuery.value) || 
      getEmojiKeywords(emoji).some(keyword => 
        keyword.toLowerCase().includes(searchQuery.value.toLowerCase())
      )
    ).slice(0, 64) // Limit search results
  }
  return currentCategoryEmojis.value
})

const allEmojis = computed(() => {
  return categories.flatMap(category => category.emojis)
})

// Helper function to get keywords for emojis (basic implementation)
function getEmojiKeywords(emoji) {
  const keywords = {
    '😀': ['happy', 'smile', 'grin'],
    '😢': ['sad', 'cry', 'tear'],
    '😂': ['laugh', 'lol', 'funny'],
    '❤️': ['love', 'heart', 'red'],
    '👍': ['thumbs', 'up', 'good', 'ok'],
    '👎': ['thumbs', 'down', 'bad'],
    '🔥': ['fire', 'hot', 'lit'],
    '💯': ['hundred', 'perfect', 'score']
    // Add more as needed
  }
  return keywords[emoji] || []
}

// Methods
function selectEmoji(emoji) {
  // Add to recent emojis
  addToRecent(emoji)
  
  // Emit the selected emoji
  emit('emoji-selected', emoji)
}

function addToRecent(emoji) {
  // Remove if already exists
  const index = recentEmojis.value.indexOf(emoji)
  if (index > -1) {
    recentEmojis.value.splice(index, 1)
  }
  
  // Add to beginning
  recentEmojis.value.unshift(emoji)
  
  // Keep only last 24 emojis
  recentEmojis.value = recentEmojis.value.slice(0, 24)
  
  // Save to localStorage
  saveRecentEmojis()
}

function loadRecentEmojis() {
  try {
    const saved = localStorage.getItem('posting_recent_emojis')
    if (saved) {
      recentEmojis.value = JSON.parse(saved)
    }
  } catch (error) {
    console.error('Failed to load recent emojis:', error)
  }
}

function saveRecentEmojis() {
  try {
    localStorage.setItem('posting_recent_emojis', JSON.stringify(recentEmojis.value))
  } catch (error) {
    console.error('Failed to save recent emojis:', error)
  }
}

function handleSearch(event) {
  searchQuery.value = event.target.value
}

// Load recent emojis on mount
onMounted(() => {
  loadRecentEmojis()
})
</script>

<style scoped>
/* Custom scrollbar for the emoji grid */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}
</style>
