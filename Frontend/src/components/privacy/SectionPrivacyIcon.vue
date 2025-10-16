<template>
  <div class="relative">
    <!-- Section Privacy Icon Button -->
    <button 
      @click="toggleDropdown"
      class="flex items-center space-x-1 px-2 py-1 text-sm border rounded-md hover:bg-gray-50 focus:outline-none transition-colors"
      :class="getButtonClasses()"
      :title="`Section Privacy: ${getVisibilityLabel()}`"
    >
      <component :is="getVisibilityIcon()" class="w-4 h-4" />
      <ChevronDownIcon class="w-3 h-3" />
    </button>
    
    <!-- Dropdown Menu -->
    <div 
      v-if="showDropdown" 
      class="absolute right-0 mt-2 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-50"
      @click.stop
    >
      <div class="p-2">
        <div class="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
          Section Privacy
        </div>
        <div class="text-xs text-gray-400 mb-3">
          Control who can see this entire section
        </div>
        
        <!-- Visibility Options -->
        <div class="space-y-1">
          <button
            v-for="option in visibilityOptions"
            :key="option.value"
            @click="selectVisibility(option.value)"
            class="w-full flex items-center space-x-3 px-3 py-2 text-sm text-left rounded-md hover:bg-gray-50 transition-colors"
            :class="{ 'bg-blue-50 text-blue-700': sectionPrivacy === option.value }"
          >
            <component :is="option.icon" class="w-4 h-4 flex-shrink-0" />
            <div class="flex-1">
              <div class="font-medium">{{ option.label }}</div>
              <div class="text-xs text-gray-500">{{ option.description }}</div>
            </div>
            <CheckIcon v-if="sectionPrivacy === option.value" class="w-4 h-4 text-blue-600" />
          </button>
        </div>
        
        <hr class="my-3" />
        
        <!-- Apply to All Fields Button -->
        <button
          @click="applyToAllFields"
          class="w-full px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
        >
          Apply to All Fields in Section
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { 
  GlobeAltIcon, 
  UserGroupIcon, 
  UserIcon, 
  LockClosedIcon,
  ChevronDownIcon,
  CheckIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  sectionName: {
    type: String,
    required: true
  },
  currentPrivacy: {
    type: String,
    default: 'connections_only'
  }
})

const emit = defineEmits(['privacy-changed', 'apply-to-all-fields'])

const showDropdown = ref(false)
const sectionPrivacy = ref(props.currentPrivacy)

// Visibility options - matching backend VISIBILITY_CHOICES
const visibilityOptions = [
  {
    value: 'everyone',
    label: 'Everyone',
    description: 'Anyone can see this section',
    icon: GlobeAltIcon
  },
  {
    value: 'connections_only',
    label: 'Connections Only',
    description: 'Only your connections can see this',
    icon: UserIcon
  },
  {
    value: 'only_me',
    label: 'Only Me',
    description: 'Only you can see this section',
    icon: LockClosedIcon
  }
]

// Get current visibility option
const getCurrentOption = () => {
  return visibilityOptions.find(option => option.value === sectionPrivacy.value) || visibilityOptions[0]
}

// Get visibility icon component
const getVisibilityIcon = () => {
  const option = getCurrentOption()
  return option.icon
}

// Get visibility label
const getVisibilityLabel = () => {
  const option = getCurrentOption()
  return option.label
}

// Get button classes based on visibility
const getButtonClasses = () => {
  const visibilityClasses = {
    everyone: 'border-green-300 text-green-700 hover:bg-green-50',
    connections_only: 'border-purple-300 text-purple-700 hover:bg-purple-50',
    only_me: 'border-gray-400 text-gray-700 hover:bg-gray-50'
  }
  
  return visibilityClasses[sectionPrivacy.value] || visibilityClasses.connections_only
}

// Toggle dropdown visibility
const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

// Select visibility option
const selectVisibility = (visibility) => {
  sectionPrivacy.value = visibility
  showDropdown.value = false
  emit('privacy-changed', {
    section: props.sectionName,
    privacy: visibility
  })
}

// Apply to all fields in section
const applyToAllFields = () => {
  showDropdown.value = false
  emit('apply-to-all-fields', {
    section: props.sectionName,
    privacy: sectionPrivacy.value
  })
}

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    showDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Watch for prop changes - but only update if it's a meaningful change
watch(() => props.currentPrivacy, (newValue, oldValue) => {
  // Only update if the new value is different and not empty/undefined
  if (newValue && newValue !== oldValue && newValue !== sectionPrivacy.value) {
    console.log(`Section privacy updated from parent: ${oldValue} -> ${newValue}`)
    sectionPrivacy.value = newValue
  }
})
</script>

<style scoped>
/* Smooth transitions for dropdown */
.absolute {
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Hover states for better UX */
button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Focus states for accessibility */
button:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 1px;
}
</style>