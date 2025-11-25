<template>
  <div class="border-l-4 border-green-500 pl-6 py-4 relative">
    <!-- Featured Achievement Indicator -->
    <div v-if="isFeatured" class="absolute -left-2 top-2">
      <div class="bg-yellow-500 text-white rounded-full p-1">
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
      </div>
    </div>

    <div class="flex items-start justify-between">
      <div class="flex-1">
        <!-- Achievement Header -->
        <div class="flex items-start space-x-3">
          <!-- Achievement Type Icon -->
          <div class="flex-shrink-0 mt-1">
            <div 
              class="w-10 h-10 rounded-full flex items-center justify-center shadow-sm"
              :class="getTypeColor(achievement.type)"
            >
              <component :is="getTypeIcon(achievement.type)" class="w-5 h-5" />
            </div>
          </div>
          
          <div class="flex-1">
            <!-- Title and Organization -->
            <h4 class="text-xl font-bold text-gray-900 mb-1">
              {{ achievement.title }}
            </h4>
            <p v-if="achievement.organization" class="text-gray-700 font-semibold text-lg">
              {{ achievement.organization }}
            </p>
            
            <!-- Date and Type -->
            <div class="flex items-center space-x-4 mt-2 text-sm text-gray-600">
              <span class="flex items-center space-x-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                <span>{{ formatDate(achievement.date_achieved) }}</span>
              </span>
              <span class="flex items-center space-x-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                </svg>
                <span class="capitalize">{{ formatType(achievement.type) }}</span>
              </span>
            </div>
          
            <!-- Description -->
            <div v-if="achievement.description" class="mt-4">
              <div 
                :class="{ 'line-clamp-3': !achievement.showFullDescription && achievement.description.length > 150 }"
                class="text-gray-700 leading-relaxed whitespace-pre-wrap"
              >
                {{ achievement.description }}
              </div>
              
              <button 
                v-if="achievement.description.length > 150"
                @click="toggleDescription"
                class="text-green-600 hover:text-green-700 text-sm font-medium mt-2 hover:underline"
              >
                {{ achievement.showFullDescription ? 'Show less' : 'Show more' }}
              </button>
            </div>
            
            <!-- URL Link -->
            <div v-if="achievement.url && achievement.url.trim()" class="mt-4">
              <div class="flex items-start space-x-2">
                <svg class="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
                </svg>
                <div class="flex-1">
                  <p class="text-sm text-gray-600 mb-1">Related Link:</p>
                  <a 
                    :href="achievement.url" 
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-blue-600 hover:text-blue-800 hover:underline break-all text-sm font-medium inline-flex items-center"
                  >
                    {{ achievement.url }}
                    <svg class="w-3 h-3 ml-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                    </svg>
                  </a>
                </div>
              </div>
            </div>
          
            <!-- Attachment -->
            <div v-if="achievement.attachment" class="mt-6">
              <div class="flex items-center space-x-2 mb-3">
                <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path>
                </svg>
                <span class="text-sm font-medium text-gray-700">Attachment:</span>
              </div>
              
              <!-- All attachments shown as clickable links -->
              <div 
                class="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all duration-300 cursor-pointer group"
                @click="openAttachment"
              >
                <div class="flex items-center justify-center w-10 h-10 rounded-lg" :class="getFileIconColor(achievement.attachment)">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                </div>
                <div class="flex-1">
                  <p class="font-medium text-gray-900 group-hover:text-blue-700">{{ getFileName(achievement.attachment) }}</p>
                  <p class="text-sm text-gray-500">{{ getFileType(achievement.attachment).toUpperCase() }} • Click to open</p>
                </div>
                <svg class="w-5 h-5 text-gray-400 group-hover:text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions for own profile -->
      <div v-if="isOwnProfile" class="flex space-x-2 ml-4 flex-shrink-0">
        <!-- Privacy indicator -->
        <div class="relative">
          <button 
            @click="toggleVisibilityMenu"
            :class="visibilityButtonClass"
            class="p-1 rounded transition-colors"
            :title="`Privacy: ${visibilityDisplay}`"
          >
            <EyeIcon v-if="(achievement?.visibility || 'connections_only') === 'everyone'" class="w-4 h-4" />
            <LockClosedIcon v-else-if="(achievement?.visibility || 'connections_only') === 'only_me'" class="w-4 h-4" />
            <ShieldCheckIcon v-else class="w-4 h-4" />
          </button>
          
          <!-- Privacy Menu -->
          <div 
            v-if="showVisibilityMenu" 
            class="absolute right-0 top-8 z-10 w-48 bg-white border border-gray-200 rounded-lg shadow-lg"
            @click.stop
          >
            <div class="p-2">
              <div class="text-xs font-medium text-gray-500 mb-2">Who can see this?</div>
              <button
                v-for="option in visibilityOptions"
                :key="option.value"
                @click="changeVisibility(option.value)"
                :class="[
                  'w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors text-left',
                  achievement?.visibility === option.value 
                    ? 'bg-blue-50 text-blue-700' 
                    : 'hover:bg-gray-50 text-gray-700'
                ]"
              >
                <component :is="option.icon" class="w-4 h-4 mr-2" />
                <div>
                  <div class="font-medium">{{ option.label }}</div>
                  <div class="text-xs text-gray-500">{{ option.description }}</div>
                </div>
              </button>
            </div>
          </div>
        </div>
        
        <button 
          @click="$emit('edit')"
          class="text-gray-400 hover:text-green-600 transition-colors p-1"
          title="Edit Achievement"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
          </svg>
        </button>
        <button 
          @click="$emit('delete')"
          class="text-gray-400 hover:text-red-600 transition-colors p-1"
          title="Delete Achievement"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { h, ref, computed } from 'vue'
import { 
  EyeIcon,
  UsersIcon, 
  LockClosedIcon,
  ShieldCheckIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  achievement: Object,
  isOwnProfile: Boolean,
  isFeatured: Boolean
})

const emit = defineEmits(['edit', 'delete', 'toggle-visibility'])

// Privacy state
const showVisibilityMenu = ref(false)

// Privacy options
const visibilityOptions = [
  {
    value: 'everyone',
    label: 'For Everyone',
    description: 'Anyone can see this',
    icon: EyeIcon
  },
  {
    value: 'connections_only',
    label: 'For Connections',
    description: 'Only your connections',
    icon: UsersIcon
  },
  {
    value: 'only_me',
    label: 'Only for Me',
    description: 'Only you can see this',
    icon: LockClosedIcon
  }
]

// Privacy computed properties
const visibilityDisplay = computed(() => {
  const option = visibilityOptions.find(opt => opt.value === props.achievement?.visibility)
  return option?.label || 'For Connections'
})

const visibilityButtonClass = computed(() => {
  const visibility = props.achievement?.visibility || 'connections_only'
  const classes = {
    everyone: 'text-green-600 hover:text-green-700 hover:bg-green-50',
    connections_only: 'text-blue-600 hover:text-blue-700 hover:bg-blue-50',
    only_me: 'text-red-600 hover:text-red-700 hover:bg-red-50'
  }
  return classes[visibility] || classes.connections_only
})

// Privacy methods
function toggleVisibilityMenu() {
  showVisibilityMenu.value = !showVisibilityMenu.value
}

function changeVisibility(newVisibility) {
  console.log('🚀 AchievementCard: changeVisibility called', { achievementId: props.achievement.id, newVisibility })
  emit('toggle-visibility', props.achievement.id, newVisibility)
  console.log('📡 Emitted toggle-visibility event')
  showVisibilityMenu.value = false
}

const showFullDescription = ref(false)

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long' 
  })
}

const formatType = (type) => {
  const typeMap = {
    'academic': 'Academic',
    'professional': 'Professional',
    'certification': 'Certification',
    'award': 'Award',
    'volunteer': 'Volunteer Work',
    'project': 'Project',
    'publication': 'Publication',
    'patent': 'Patent',
    'recognition': 'Recognition',
    'achievement': 'Achievement',
    'other': 'Other'
  }
  return typeMap[type] || type.charAt(0).toUpperCase() + type.slice(1)
}

const getTypeColor = (type) => {
  const colorMap = {
    'academic': 'bg-indigo-100 text-indigo-600',
    'professional': 'bg-slate-100 text-slate-600',
    'certification': 'bg-blue-100 text-blue-600',
    'award': 'bg-yellow-100 text-yellow-600',
    'volunteer': 'bg-green-100 text-green-600',
    'project': 'bg-cyan-100 text-cyan-600',
    'publication': 'bg-purple-100 text-purple-600',
    'patent': 'bg-emerald-100 text-emerald-600',
    'recognition': 'bg-orange-100 text-orange-600',
    'achievement': 'bg-rose-100 text-rose-600',
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
      h('path', { d: 'M5 16L3 21l5.25-1.875L12 21l3.75-1.875L21 21l-2-5 1-11H4l1 11zm7-11a2 2 0 100 4 2 2 0 000-4z' })
    ]),
    'certification': () => h('svg', { 
      fill: 'currentColor', 
      viewBox: '0 0 24 24' 
    }, [
      h('path', { d: 'M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z' }),
      h('path', { d: 'M14 2v6h6M16 13a3 3 0 11-6 0 3 3 0 016 0z' }),
      h('path', { d: 'M15 17h-6' })
    ]),
    'academic': () => h('svg', { 
      fill: 'currentColor', 
      viewBox: '0 0 24 24' 
    }, [
      h('path', { d: 'M12 3L1 9l4 2.18v6L12 21l7-3.82v-6L23 9l-11-6zM5 13.18l7 3.82 7-3.82V11L12 15 5 11v2.18z' })
    ]),
    'professional': () => h('svg', { 
      fill: 'currentColor', 
      viewBox: '0 0 24 24' 
    }, [
      h('path', { d: 'M20 6h-2.5l-1.5-1.5h-8L6.5 6H4c-1.1 0-1.99.9-1.99 2L2 19c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h4.5l1.5-1.5h4l1.5 1.5H20v10z' })
    ]),
    'publication': () => h('svg', { 
      fill: 'currentColor', 
      viewBox: '0 0 24 24' 
    }, [
      h('path', { d: 'M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z' })
    ]),
    'patent': () => h('svg', { 
      fill: 'currentColor', 
      viewBox: '0 0 24 24' 
    }, [
      h('path', { d: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' })
    ]),
    'recognition': () => h('svg', { 
      fill: 'currentColor', 
      viewBox: '0 0 24 24' 
    }, [
      h('path', { d: 'M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z' })
    ]),
    'volunteer': () => h('svg', { 
      fill: 'currentColor', 
      viewBox: '0 0 24 24' 
    }, [
      h('path', { d: 'M16.5 3c-1.74 0-3.41.81-4.5 2.09C10.91 3.81 9.24 3 7.5 3 4.42 3 2 5.42 2 8.5c0 3.78 3.4 6.86 8.55 11.54L12 21.35l1.45-1.32C18.6 15.36 22 12.28 22 8.5 22 5.42 19.58 3 16.5 3z' })
    ]),
    'project': () => h('svg', { 
      fill: 'currentColor', 
      viewBox: '0 0 24 24' 
    }, [
      h('path', { d: 'M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z' })
    ]),
    'other': () => h('svg', { 
      fill: 'currentColor', 
      viewBox: '0 0 24 24' 
    }, [
      h('path', { d: 'M5 16L3 21l5.25-1.875L12 21l3.75-1.875L21 21l-2-5 1-11H4l1 11zm7-11a2 2 0 100 4 2 2 0 000-4z' })
    ])
  }
  
  return iconMap[type] || iconMap['other'] || (() => h('div'))
}

const toggleDescription = () => {
  showFullDescription.value = !showFullDescription.value
  // Also update the achievement object for consistent state
  props.achievement.showFullDescription = showFullDescription.value
}

const isImageAttachment = (attachmentUrl) => {
  if (!attachmentUrl) return false
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
  const url = attachmentUrl.toLowerCase()
  return imageExtensions.some(ext => url.includes(ext))
}

const openAttachment = () => {
  // Open attachment in a new window/tab for viewing
  window.open(props.achievement.attachment, '_blank')
}

const getFileType = (attachmentUrl) => {
  if (!attachmentUrl) return ''
  const extension = attachmentUrl.split('.').pop().toLowerCase()
  return extension
}

const getFileName = (attachmentUrl) => {
  if (!attachmentUrl) return 'Unknown File'
  const parts = attachmentUrl.split('/')
  return parts[parts.length - 1]
}



const getFileIconColor = (attachmentUrl) => {
  const extension = getFileType(attachmentUrl)
  switch(extension) {
    case 'pdf':
      return 'bg-red-500'
    case 'doc':
    case 'docx':
      return 'bg-blue-600'
    default:
      return 'bg-gray-500'
  }
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
