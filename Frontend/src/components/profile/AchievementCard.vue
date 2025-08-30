<template>
  <div class="flex items-start justify-between">
    <div class="flex-1">
      <!-- Achievement Header -->
      <div class="flex items-start space-x-3">
        <!-- Achievement Type Icon -->
        <div class="flex-shrink-0 mt-1">
          <div 
            class="w-8 h-8 rounded-full flex items-center justify-center"
            :class="getTypeColor(achievement.type)"
          >
            <component :is="getTypeIcon(achievement.type)" class="w-4 h-4" />
          </div>
        </div>
        
        <div class="flex-1">
          <!-- Title and Organization -->
          <h4 class="text-lg font-semibold text-gray-900">
            {{ achievement.title }}
          </h4>
          <p v-if="achievement.organization" class="text-gray-600 font-medium">
            {{ achievement.organization }}
          </p>
          
          <!-- Date and Type -->
          <div class="flex items-center space-x-4 mt-1 text-sm text-gray-500">
            <span>{{ formatDate(achievement.date_achieved) }}</span>
            <span class="capitalize">{{ formatType(achievement.type) }}</span>
          </div>
          
          <!-- Description -->
          <div v-if="achievement.description" class="mt-3">
            <div 
              :class="{ 'line-clamp-3': !achievement.showFullDescription && achievement.description.length > 150 }"
              class="text-gray-700 text-sm whitespace-pre-wrap"
            >
              {{ achievement.description }}
            </div>
            
            <button 
              v-if="achievement.description.length > 150"
              @click="toggleDescription"
              class="text-green-600 hover:text-green-700 text-sm font-medium mt-1"
            >
              {{ achievement.showFullDescription ? 'See less' : 'See more' }}
            </button>
          </div>
          
          <!-- URL Link -->
          <div v-if="achievement.url" class="mt-3">
            <a 
              :href="achievement.url" 
              target="_blank"
              class="inline-flex items-center space-x-1 text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
              </svg>
              <span>View Details</span>
            </a>
          </div>
          
          <!-- Attachment -->
          <div v-if="achievement.attachment" class="mt-3">
            <div class="flex items-center space-x-2 p-2 bg-gray-50 rounded-lg">
              <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path>
              </svg>
              <a 
                :href="achievement.attachment" 
                target="_blank"
                class="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                View Attachment
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions for own profile -->
    <div v-if="isOwnProfile" class="flex space-x-2 ml-4">
      <!-- Featured badge -->
      <div v-if="isFeatured" class="text-yellow-500" title="Featured Achievement">
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
      </div>
      
      <button 
        @click="$emit('edit')"
        class="text-gray-500 hover:text-green-600 transition-colors"
        title="Edit"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
        </svg>
      </button>
      <button 
        @click="$emit('delete')"
        class="text-gray-500 hover:text-red-600 transition-colors"
        title="Delete"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { h, ref } from 'vue'

const props = defineProps({
  achievement: Object,
  isOwnProfile: Boolean,
  isFeatured: Boolean
})

const emit = defineEmits(['edit', 'delete'])

const showFullDescription = ref(false)

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long' 
  })
}

const formatType = (type) => {
  const typeMap = {
    'award': 'Award',
    'certification': 'Certification',
    'publication': 'Publication',
    'patent': 'Patent',
    'recognition': 'Recognition',
    'achievement': 'Achievement',
    'other': 'Other'
  }
  return typeMap[type] || type
}

const getTypeColor = (type) => {
  const colorMap = {
    'award': 'bg-yellow-100 text-yellow-600',
    'certification': 'bg-blue-100 text-blue-600',
    'publication': 'bg-purple-100 text-purple-600',
    'patent': 'bg-green-100 text-green-600',
    'recognition': 'bg-orange-100 text-orange-600',
    'achievement': 'bg-indigo-100 text-indigo-600',
    'other': 'bg-gray-100 text-gray-600'
  }
  return colorMap[type] || 'bg-gray-100 text-gray-600'
}

const getTypeIcon = (type) => {
  const iconMap = {
    'award': () => h('svg', { 
      fill: 'currentColor', 
      viewBox: '0 0 24 24' 
    }, [
      h('path', { d: 'M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z' })
    ]),
    'certification': () => h('svg', { 
      fill: 'none', 
      stroke: 'currentColor', 
      viewBox: '0 0 24 24' 
    }, [
      h('path', { 
        'stroke-linecap': 'round', 
        'stroke-linejoin': 'round', 
        'stroke-width': '2', 
        d: 'M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z' 
      })
    ]),
    'publication': () => h('svg', { 
      fill: 'none', 
      stroke: 'currentColor', 
      viewBox: '0 0 24 24' 
    }, [
      h('path', { 
        'stroke-linecap': 'round', 
        'stroke-linejoin': 'round', 
        'stroke-width': '2', 
        d: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' 
      })
    ]),
    'patent': () => h('svg', { 
      fill: 'none', 
      stroke: 'currentColor', 
      viewBox: '0 0 24 24' 
    }, [
      h('path', { 
        'stroke-linecap': 'round', 
        'stroke-linejoin': 'round', 
        'stroke-width': '2', 
        d: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z' 
      })
    ])
  }
  
  return iconMap[type] || iconMap['achievement'] || (() => h('div'))
}

const toggleDescription = () => {
  showFullDescription.value = !showFullDescription.value
  // Also update the achievement object for consistent state
  props.achievement.showFullDescription = showFullDescription.value
}
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
