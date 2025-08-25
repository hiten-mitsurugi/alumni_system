<template>
  <div class="flex items-start justify-between p-6 pb-4">
    <div class="flex items-start space-x-4">
      <img :src="post.user?.profile_picture || '/default-avatar.png'" alt="Profile"
        class="w-16 h-16 rounded-full object-cover border-4 border-blue-200 shadow-lg" />
      <div>
        <div class="flex items-center space-x-3">
          <h3 class="text-xl font-bold text-slate-800">
            {{ post.user?.first_name }} {{ post.user?.last_name }}
          </h3>

        </div>
        <div class="flex items-center space-x-3 text-lg text-slate-600 mt-1">
          <span class="font-medium">{{ formatTimeAgo(post.created_at) }}</span>
          <span class="text-slate-400">•</span>
          <span
            class="capitalize font-medium bg-slate-100 px-3 py-1 rounded-full cursor-pointer hover:bg-slate-200 transition-colors">
            {{categories.find(c => c.value === post.content_category)?.icon || '📝'}}
            {{ post.content_category }}
          </span>
          <span v-if="post.post_type === 'shared'"
            class="bg-green-100 text-green-700 px-3 py-1 rounded-full font-medium">
            🔄 Shared
          </span>
        </div>
      </div>
    </div>

    <!-- Post Menu -->
    <div class="relative">
      <button class="text-slate-400 hover:text-slate-600 p-2 rounded-full hover:bg-slate-100 transition-colors">
        <svg class="w-7 h-7" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
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

// Methods
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
/* Smooth transitions for all interactive elements */
.transition-colors {
  transition: all 0.3s ease;
}
</style>
