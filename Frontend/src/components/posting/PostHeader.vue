<template>
  <div class="flex items-start justify-between p-6 pb-4">
    <div class="flex items-start space-x-4">
      <img
        :src="post.user?.profile_picture || '/default-avatar.png'"
        alt="Profile"
        class="w-16 h-16 rounded-full object-cover border-4 border-blue-200 shadow-lg"
      />
      <div>
        <div class="flex items-center space-x-3">
          <h3 :class="['text-lg font-bold', themeStore.isDarkMode ? 'text-white' : 'text-slate-800']">
            {{ post.user?.first_name }} {{ post.user?.last_name }}
          </h3>
          <span v-if="post.user?.user_type <= 2" :class="['text-sm font-medium', themeStore.isDarkMode ? 'text-blue-400' : 'text-blue-600']">
            {{ post.user?.user_type === 1 ? 'Admin' : 'SuperAdmin' }}
          </span>
        </div>
        <div :class="['flex items-center space-x-3 text-base mt-1', themeStore.isDarkMode ? 'text-slate-300' : 'text-slate-600']">
          <span class="font-medium">{{ formatTimeAgo(post.created_at) }}</span>
          <span :class="themeStore.isDarkMode ? 'text-slate-500' : 'text-slate-400'">•</span>
          <span :class="['capitalize font-medium px-3 py-1 rounded-full', themeStore.isDarkMode ? 'bg-slate-700 text-slate-200' : 'bg-slate-100 text-slate-700']">
            {{ post.content_category }}
          </span>
          <span v-if="post.post_type === 'shared'" :class="['px-3 py-1 rounded-full font-medium', themeStore.isDarkMode ? 'bg-green-800 text-green-200' : 'bg-green-100 text-green-700']">
            🔄 Shared
          </span>
        </div>
      </div>
    </div>

    <!-- Post Menu -->
    <div class="relative">
      <button
        @click="toggleMenu"
        :class="[
          'p-2 rounded-full transition-colors',
          themeStore.isDarkMode
            ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-700'
            : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100'
        ]"
      >
        <svg class="w-7 h-7" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
        </svg>
      </button>

      <!-- Dropdown Menu -->
      <div
        v-show="showMenu"
        :class="[
          'absolute right-0 mt-2 w-48 rounded-xl shadow-xl border z-50 py-2',
          themeStore.isDarkMode
            ? 'bg-slate-800 border-slate-700'
            : 'bg-white border-slate-200'
        ]"
      >
        <!-- Delete Post -->
        <button
          @click="handleAction('delete-post')"
          :class="[
            'w-full px-4 py-3 text-left flex items-center space-x-3 transition-colors',
            themeStore.isDarkMode
              ? 'text-red-400 hover:bg-slate-700'
              : 'text-red-600 hover:bg-red-50'
          ]"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          <span class="font-medium">Delete Post</span>
        </button>

        <!-- Pin Post -->
        <button
          @click="handleAction('pin-post')"
          :class="[
            'w-full px-4 py-3 text-left flex items-center space-x-3 transition-colors',
            themeStore.isDarkMode
              ? 'text-slate-200 hover:bg-slate-700'
              : 'text-slate-700 hover:bg-slate-50'
          ]"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
          </svg>
          <span class="font-medium">{{ post.is_pinned ? 'Unpin Post' : 'Pin Post' }}</span>
        </button>

        <!-- Feature Post -->
        <button
          @click="handleAction('feature-post')"
          :class="[
            'w-full px-4 py-3 text-left flex items-center space-x-3 transition-colors',
            themeStore.isDarkMode
              ? 'text-yellow-400 hover:bg-slate-700'
              : 'text-yellow-600 hover:bg-yellow-50'
          ]"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
          </svg>
          <span class="font-medium">{{ post.is_featured ? 'Unfeature Post' : 'Feature Post' }}</span>
        </button>

        <!-- Report Post -->
        <button
          @click="handleAction('report-post')"
          :class="[
            'w-full px-4 py-3 text-left flex items-center space-x-3 transition-colors border-t',
            themeStore.isDarkMode
              ? 'text-orange-400 hover:bg-slate-700 border-slate-700'
              : 'text-orange-600 hover:bg-orange-50 border-slate-200'
          ]"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <span class="font-medium">Report Post</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useThemeStore } from '@/stores/theme'

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
  }
})

// Emits
const emit = defineEmits([
  'delete-post',
  'pin-post',
  'feature-post',
  'report-post'
])

// State
const showMenu = ref(false)

// Methods
const toggleMenu = () => {
  showMenu.value = !showMenu.value
}

const handleAction = (action) => {
  emit(action, props.post)
  showMenu.value = false
}

const closeMenu = (event) => {
  // Close menu when clicking outside
  if (!event.target.closest('.relative')) {
    showMenu.value = false
  }
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

// Lifecycle
onMounted(() => {
  document.addEventListener('click', closeMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', closeMenu)
})
</script>

<style scoped>
/* Smooth transitions for all interactive elements */
.transition-colors {
  transition: all 0.3s ease;
}
</style>
