<template>
  <div class="flex items-center justify-between mb-4">
    <h2 class="text-xl font-bold text-gray-900">{{ title }}</h2>
    <div class="flex items-center gap-2">
      <!-- Privacy Control -->
      <div v-if="isOwnProfile" class="relative">
        <button 
          @click="toggleVisibilityMenu"
          :class="visibilityButtonClass"
          class="p-2 rounded-lg transition-colors"
          :title="`Privacy: ${visibilityDisplay}`"
        >
          <component :is="visibilityIcon" class="w-5 h-5" />
        </button>
        
        <!-- Privacy Menu -->
        <div 
          v-if="showVisibilityMenu" 
          class="absolute right-0 z-10 mt-2 w-56 bg-white border border-gray-200 rounded-lg shadow-lg"
          @click.stop
        >
          <div class="p-3">
            <div class="text-xs font-medium text-gray-500 mb-3">Who can see this section?</div>
            <button
              v-for="option in visibilityOptions"
              :key="option.value"
              @click="changeVisibility(option.value)"
              :class="[
                'w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors text-left mb-1',
                currentVisibility === option.value 
                  ? 'bg-blue-50 text-blue-700' 
                  : 'hover:bg-gray-50 text-gray-700'
              ]"
            >
              <component :is="option.icon" class="w-4 h-4 mr-3" />
              <div>
                <div class="font-medium">{{ option.label }}</div>
                <div class="text-xs text-gray-500">{{ option.description }}</div>
              </div>
            </button>
          </div>
        </div>
      </div>

      <!-- Add Button -->
      <button 
        v-if="isOwnProfile && showAddButton" 
        @click="$emit('add')"
        class="flex items-center space-x-1 text-green-600 hover:text-green-700 transition-colors px-3 py-2 rounded-lg hover:bg-green-50"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
        </svg>
        <span>Add</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { 
  EyeIcon,
  UsersIcon, 
  LockClosedIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  isOwnProfile: {
    type: Boolean,
    default: false
  },
  showAddButton: {
    type: Boolean,
    default: true
  },
  sectionVisibility: {
    type: String,
    default: 'connections_only'
  }
})

const emit = defineEmits(['add', 'visibility-changed'])

// State
const showVisibilityMenu = ref(false)
const currentVisibility = ref(props.sectionVisibility)

// Privacy options
const visibilityOptions = [
  {
    value: 'everyone',
    label: 'For Everyone',
    description: 'Anyone can see this section',
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

// Computed properties
const visibilityDisplay = computed(() => {
  const option = visibilityOptions.find(opt => opt.value === currentVisibility.value)
  return option?.label || 'For Connections'
})

const visibilityIcon = computed(() => {
  const option = visibilityOptions.find(opt => opt.value === currentVisibility.value)
  return option?.icon || UsersIcon
})

const visibilityButtonClass = computed(() => {
  const visibility = currentVisibility.value
  const classes = {
    everyone: 'text-green-600 hover:text-green-700 hover:bg-green-50',
    connections_only: 'text-blue-600 hover:text-blue-700 hover:bg-blue-50',
    only_me: 'text-gray-600 hover:text-gray-700 hover:bg-gray-50'
  }
  return classes[visibility] || classes.connections_only
})

// Methods
function toggleVisibilityMenu() {
  showVisibilityMenu.value = !showVisibilityMenu.value
}

function changeVisibility(newVisibility) {
  currentVisibility.value = newVisibility
  emit('visibility-changed', newVisibility)
  showVisibilityMenu.value = false
}

// Close menu when clicking outside
document.addEventListener('click', () => {
  showVisibilityMenu.value = false
})
</script>