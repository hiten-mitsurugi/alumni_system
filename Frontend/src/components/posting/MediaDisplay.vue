<template>
  <div v-if="mediaFiles && mediaFiles.length > 0" class="mb-6">
    <!-- Single image -->
    <div v-if="mediaFiles.length === 1" class="rounded-2xl overflow-hidden shadow-lg bg-white">
      <img
        v-if="mediaFiles[0].media_type === 'image' && mediaFiles[0].file_url"
        :src="mediaFiles[0].file_url"
        :alt="altText || 'Post image'"
        :class="[
          'w-full cursor-pointer hover:opacity-90 transition-opacity duration-300',
          displayMode === 'card' ? 'aspect-square object-cover' : 'max-h-[500px] object-cover'
        ]"
        @error="handleImageError"
        @click="handleMediaClick"
        @load="handleImageLoad"
        style="background: white; display: block;"
      />
      <div
        v-else-if="mediaFiles[0].media_type === 'image' && !mediaFiles[0].file_url"
        :class="[
          'w-full bg-gray-200 flex items-center justify-center',
          displayMode === 'card' ? 'aspect-square' : 'h-[300px] rounded-2xl'
        ]"
      >
        <span class="text-gray-500">Image URL not available</span>
      </div>
      <video
        v-else-if="mediaFiles[0].media_type === 'video' && mediaFiles[0].file_url"
        :src="mediaFiles[0].file_url"
        controls
        :class="[
          'w-full rounded-2xl',
          displayMode === 'card' ? 'aspect-square object-cover' : 'max-h-[500px]'
        ]"
      />
    </div>
    <!-- Multiple images layout - Facebook style -->
    <div v-else class="rounded-2xl overflow-hidden bg-white">
      <!-- Always 2x2 grid, show maximum 4 images -->
      <div class="grid grid-cols-2 gap-1">
        <div
          v-for="(media, index) in mediaFiles.slice(0, 4)"
          :key="media.id"
          :class="[
            'relative bg-white',
            displayMode === 'card' ? 'aspect-square' : 'aspect-square'
          ]"
        >
          <img
            v-if="media.media_type === 'image' && media.file_url"
            :src="media.file_url"
            :alt="`Media ${index + 1}`"
            class="w-full h-full object-cover cursor-pointer hover:opacity-90 transition-opacity duration-300"
            @error="handleImageError"
            @click="handleMediaClick"
            @load="handleImageLoad"
            style="background: white; display: block;"
          />
          <div
            v-else-if="media.media_type === 'image' && !media.file_url"
            class="w-full h-full bg-gray-200 flex items-center justify-center"
          >
            <span class="text-gray-500 text-sm">No image</span>
          </div>
          <video
            v-else-if="media.media_type === 'video' && media.file_url"
            :src="media.file_url"
            class="w-full h-full object-cover"
            muted
          />
          
          <!-- "+X more" overlay ONLY on 4th image when there are more than 4 images -->
          <div
            v-if="index === 3 && mediaFiles.length > 4"
            class="absolute inset-0 bg-white/30 backdrop-blur-md bg-opacity-70 flex items-center justify-center text-white font-bold cursor-pointer transition-all duration-300 hover:bg-opacity-80"
            @click="handleMediaClick"
          >
            <div class="text-center">
              <div class="text-2xl md:text-3xl font-bold">+{{ mediaFiles.length - 4 }}</div>
            </div>
          </div>
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
  },
  displayMode: {
    type: String,
    default: 'card', // 'card' for PostCard (square/cropped), 'modal' for PostModal (original size)
    validator: (value) => ['card', 'modal'].includes(value)
  }
})

// Emits
const emit = defineEmits(['media-click'])

// Methods
const handleImageError = (event) => {
  console.error('🖼️ Image failed to load:', event.target.src)
  console.log('📄 Full media file object:', props.mediaFiles)
  console.log('🌐 Attempting to load from:', event.target.src)
  console.log('🎨 Image computed styles:', window.getComputedStyle(event.target))
  console.log('📐 Image dimensions:', {
    naturalWidth: event.target.naturalWidth,
    naturalHeight: event.target.naturalHeight,
    clientWidth: event.target.clientWidth,
    clientHeight: event.target.clientHeight
  })
  
  // Try to diagnose the issue
  if (event.target.src.includes('blob:')) {
    console.error('❌ Blob URL detected - this usually means the URL was revoked or invalid')
  } else if (!event.target.src.startsWith('http')) {
    console.error('❌ Relative URL detected - might need absolute URL')
  }
  
  event.target.src = '/default-avatar.png' // Fallback image
  event.target.alt = 'Image not available'
}

const handleImageLoad = (event) => {
  console.log('✅ Image loaded successfully:', event.target.src)
  console.log('📐 Loaded image dimensions:', {
    naturalWidth: event.target.naturalWidth,
    naturalHeight: event.target.naturalHeight,
    clientWidth: event.target.clientWidth,
    clientHeight: event.target.clientHeight
  })
  
  const computedStyles = window.getComputedStyle(event.target)
  console.log('🎨 Critical CSS properties:', {
    display: computedStyles.display,
    visibility: computedStyles.visibility,
    opacity: computedStyles.opacity,
    filter: computedStyles.filter,
    transform: computedStyles.transform,
    backgroundColor: computedStyles.backgroundColor,
    backgroundImage: computedStyles.backgroundImage,
    mixBlendMode: computedStyles.mixBlendMode,
    zIndex: computedStyles.zIndex
  })
  
  // Check if image is actually visible
  const rect = event.target.getBoundingClientRect()
  console.log('📍 Image position:', rect)
  
  // Store reference to avoid null errors
  const imageElement = event.target
  
  // Force visibility and remove any potential issues
  if (imageElement && imageElement.style) {
    imageElement.style.filter = 'none'
    imageElement.style.mixBlendMode = 'normal'
    imageElement.style.opacity = '1'
    imageElement.style.backgroundColor = 'transparent'
    imageElement.style.visibility = 'visible'
    console.log('🔧 Applied visibility fixes to image')
  }
}

const handleMediaClick = () => {
  emit('media-click')
}

// Debug: Log media files when component mounts
import { onMounted } from 'vue'
onMounted(() => {
  console.log('🎬 MediaDisplay mounted with mediaFiles:', props.mediaFiles)
  if (props.mediaFiles && props.mediaFiles.length > 0) {
    props.mediaFiles.forEach((media, index) => {
      console.log(`📸 Media ${index}:`, {
        id: media.id,
        type: media.media_type,
        file_url: media.file_url,
        thumbnail_url: media.thumbnail_url,
        full_object: media
      })
      
      // Test if the URL is accessible
      if (media.file_url) {
        fetch(media.file_url, { method: 'HEAD' })
          .then(response => {
            if (response.ok) {
              console.log(`✅ Media ${index} URL is accessible`)
            } else {
              console.error(`❌ Media ${index} URL returned status:`, response.status)
            }
          })
          .catch(error => {
            console.error(`❌ Media ${index} URL fetch failed:`, error)
          })
      }
    })
  }
})
</script>

<style scoped>
/* Force image visibility - override any global styles */
img {
  max-width: 100% !important;
  height: auto !important;
  display: block !important;
  background: transparent !important;
  border: none !important;
  filter: none !important;
  opacity: 1 !important;
  visibility: visible !important;
  mix-blend-mode: normal !important;
  transform: none !important;
  clip-path: none !important;
  mask: none !important;
  box-shadow: none !important;
}

/* Ensure parent containers don't interfere */
.mb-6, .rounded-2xl, .overflow-hidden, .shadow-lg, .grid, .grid-cols-2, .gap-1, .relative {
  background: transparent !important;
  filter: none !important;
  mix-blend-mode: normal !important;
}

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

/* Responsive grid improvements */
.aspect-square {
  aspect-ratio: 1 / 1;
  width: 100%;
  height: auto;
}

/* Ensure perfect squares in card mode */
.aspect-square img,
.aspect-square video {
  width: 100% !important;
  height: 100% !important;
  object-fit: cover !important;
  object-position: center !important;
}

/* Mobile responsive adjustments */
@media (max-width: 640px) {
  /* Reduce max height for mobile */
  .max-h-\[400px\] {
    max-height: 300px !important;
  }
  
  /* Adjust fixed heights for mobile */
  img[style*="height: 400px"] {
    height: 250px !important;
  }
  
  img[style*="height: 199px"] {
    height: 124px !important;
  }
  
  /* Better gap spacing on mobile */
  .gap-1 {
    gap: 2px;
  }
  
  /* Ensure proper aspect ratio on mobile */
  .aspect-square {
    aspect-ratio: 1 / 1;
    min-height: 150px;
  }
  
  /* More overlay text size for mobile */
  .text-xl {
    font-size: 1.25rem !important;
    line-height: 1.75rem !important;
  }
  
  .text-2xl {
    font-size: 1.5rem !important;
    line-height: 2rem !important;
  }
}

/* Grid layout utilities */
.grid-rows-2 {
  grid-template-rows: repeat(2, minmax(0, 1fr));
}

/* Object fit for proper image scaling */
.object-cover {
  object-fit: cover;
  object-position: center;
}

/* Hover effects for desktop */
@media (hover: hover) and (pointer: fine) {
  .hover\:opacity-90:hover {
    opacity: 0.9;
  }
}

/* Touch-friendly overlays for mobile */
@media (hover: none) and (pointer: coarse) {
  .cursor-pointer {
    touch-action: manipulation;
  }
  
  /* Better touch targets */
  .absolute.inset-0 {
    min-height: 44px;
    min-width: 44px;
  }
}

/* Prevent layout shift during image loading */
img[src] {
  transition: opacity 0.2s ease;
}

/* Loading state */
img:not([src]),
img[src=""] {
  background-color: #f3f4f6;
}

/* Error state */
img[alt*="not available"] {
  background-color: #fee2e2;
  color: #dc2626;
}
</style>
