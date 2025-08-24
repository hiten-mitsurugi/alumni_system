<template>
  <div v-if="mediaFiles && mediaFiles.length > 0" class="mb-6">
    <div v-if="mediaFiles.length === 1" class="rounded-2xl overflow-hidden shadow-lg">
      <img
        v-if="mediaFiles[0].media_type === 'image'"
        :src="mediaFiles[0].file_url"
        :alt="altText || 'Post image'"
        class="w-full max-h-[500px] object-cover cursor-pointer hover:opacity-90 transition-opacity"
        @error="handleImageError"
      />
      <video
        v-else-if="mediaFiles[0].media_type === 'video'"
        :src="mediaFiles[0].file_url"
        controls
        class="w-full max-h-[500px] rounded-2xl"
      />
    </div>
    <div v-else class="grid grid-cols-2 gap-3 rounded-2xl overflow-hidden">
      <div
        v-for="(media, index) in mediaFiles.slice(0, 4)"
        :key="media.id"
        class="relative aspect-square"
      >
        <img
          v-if="media.media_type === 'image'"
          :src="media.file_url"
          :alt="`Media ${index + 1}`"
          class="w-full h-full object-cover shadow-md cursor-pointer hover:opacity-90 transition-opacity"
          @error="handleImageError"
        />
        <video
          v-else-if="media.media_type === 'video'"
          :src="media.file_url"
          class="w-full h-full object-cover shadow-md"
          muted
        />
        <div
          v-if="index === 3 && mediaFiles.length > 4"
          class="absolute inset-0 bg-black bg-opacity-60 flex items-center justify-center text-white font-bold text-2xl"
        >
          +{{ mediaFiles.length - 4 }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Props
const props = defineProps({
  mediaFiles: {
    type: Array,
    default: () => []
  },
  altText: {
    type: String,
    default: ''
  }
})

// Methods
const handleImageError = (event) => {
  console.error('Image failed to load:', event.target.src)
  event.target.src = '/default-avatar.png' // Fallback image
  event.target.alt = 'Image not available'
}
</script>

<style scoped>
/* Smooth transitions for hover effects */
.transition-opacity {
  transition: opacity 0.3s ease;
}

/* Enhanced card shadows */
.shadow-lg {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.shadow-md {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
</style>
