<template>
  <div class="relative" ref="menuContainer">
    <!-- 3-dot menu button -->
    <button
      @click="toggleMenu"
      :class="themeStore.isAdminDark()
        ? 'text-gray-400 hover:text-gray-200 p-2 rounded-full hover:bg-gray-600 transition-colors'
        : 'text-slate-400 hover:text-slate-600 p-2 rounded-full hover:bg-slate-100 transition-colors'"
    >
      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
        <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
      </svg>
    </button>

    <!-- Dropdown menu -->
    <div
      v-if="showMenu"
      :class="themeStore.isAdminDark()
        ? 'absolute right-0 top-full mt-2 w-48 bg-gray-800 border border-gray-600 rounded-lg shadow-lg z-50'
        : 'absolute right-0 top-full mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-50'"
    >
      <!-- Pin/Unpin (Admin only) -->
      <button
        v-if="canPin"
        @click="handlePin"
        :disabled="loading.pin"
        :class="themeStore.isAdminDark()
          ? 'w-full text-left px-4 py-3 text-sm text-gray-200 hover:bg-gray-700 flex items-center space-x-3 disabled:opacity-50'
          : 'w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-3 disabled:opacity-50'"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            :d="post.is_pinned ? 'M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z' : 'M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z'" />
        </svg>
        <span>{{ post.is_pinned ? 'Unpin Post' : 'Pin Post' }}</span>
        <div v-if="loading.pin" class="ml-auto">
          <div class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
        </div>
      </button>

      <!-- Report Post -->
      <button
        v-if="canReport"
        @click="handleReport"
        :disabled="loading.report"
        :class="themeStore.isAdminDark()
          ? 'w-full text-left px-4 py-3 text-sm text-gray-200 hover:bg-gray-700 flex items-center space-x-3 disabled:opacity-50'
          : 'w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-3 disabled:opacity-50'"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
        <span>Report Post</span>
        <div v-if="loading.report" class="ml-auto">
          <div class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
        </div>
      </button>

      <!-- Delete Post (Admin or Owner only) -->
      <button
        v-if="canDelete"
        @click="handleDelete"
        :disabled="loading.delete"
        :class="themeStore.isAdminDark()
          ? 'w-full text-left px-4 py-3 text-sm text-red-400 hover:bg-gray-700 flex items-center space-x-3 disabled:opacity-50'
          : 'w-full text-left px-4 py-3 text-sm text-red-600 hover:bg-red-50 flex items-center space-x-3 disabled:opacity-50'"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
        <span>Delete Post</span>
        <div v-if="loading.delete" class="ml-auto">
          <div class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
        </div>
      </button>
    </div>

    <!-- Report Modal -->
    <ReportModal
      v-if="showReportModal"
      :post="post"
      @close="showReportModal = false"
      @reported="onReported"
    />

    <!-- Delete Confirmation Modal -->
    <ConfirmModal
      v-if="showDeleteModal"
      title="Delete Post"
      message="Are you sure you want to delete this post? This action cannot be undone."
      confirmText="Delete"
      confirmClass="bg-red-600 hover:bg-red-700 text-white"
      @confirm="confirmDelete"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'
import { postsService } from '@/services/postsService'
import { reportsService } from '@/services/reportsService'
import ReportModal from './ReportModal.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'

// Stores
const themeStore = useThemeStore()
const authStore = useAuthStore()

// Props & Emits
const props = defineProps({
  post: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['deleted', 'pinned', 'reported'])

// Refs
const menuContainer = ref(null)
const showMenu = ref(false)
const showReportModal = ref(false)
const showDeleteModal = ref(false)

const loading = ref({
  pin: false,
  report: false,
  delete: false
})

// Computed
const currentUser = computed(() => authStore.user)

const isAdmin = computed(() =>
  currentUser.value && [1, 2].includes(currentUser.value.user_type)
)

const isOwner = computed(() =>
  currentUser.value && currentUser.value.id === props.post.user?.id
)

const canPin = computed(() => isAdmin.value)
const canReport = computed(() => {
  // Show report for all users except the post owner
  // If post.user is missing, allow reporting (defensive)
  if (!currentUser.value) return false;
  if (!props.post.user || typeof props.post.user.id === 'undefined') return true;
  return currentUser.value.id !== props.post.user.id;
})
const canDelete = computed(() => isAdmin.value || isOwner.value)

// Methods
const toggleMenu = () => {
  showMenu.value = !showMenu.value
}

const closeMenu = () => {
  showMenu.value = false
}

const handlePin = async () => {
  if (loading.value.pin) return

  loading.value.pin = true
  try {
    const result = await postsService.pinPost(props.post.id)

    // Update local post object
    props.post.is_pinned = result.is_pinned

    emit('pinned', {
      postId: props.post.id,
      isPinned: result.is_pinned,
      message: result.message
    })

    closeMenu()
  } catch (error) {
    console.error('Error pinning post:', error)
    alert('Failed to pin/unpin post. Please try again.')
  } finally {
    loading.value.pin = false
  }
}

const handleReport = () => {
  showReportModal.value = true
  closeMenu()
}

const handleDelete = () => {
  showDeleteModal.value = true
  closeMenu()
}

const confirmDelete = async () => {
  if (loading.value.delete) return

  loading.value.delete = true
  try {
    await postsService.deletePost(props.post.id)

    emit('deleted', {
      postId: props.post.id,
      // Don't send message here - let the parent handle it to avoid duplicates
    })

    showDeleteModal.value = false
  } catch (error) {
    console.error('Error deleting post:', error)
    alert('Failed to delete post. Please try again.')
  } finally {
    loading.value.delete = false
  }
}

const onReported = (reportData) => {
  emit('reported', {
    postId: props.post.id,
    reportData,
    message: 'Post reported successfully'
  })
  showReportModal.value = false
}

// Click outside handler
const handleClickOutside = (event) => {
  if (menuContainer.value && !menuContainer.value.contains(event.target)) {
    closeMenu()
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.transition-colors {
  transition: all 0.3s ease;
}
</style>
