<template>
  <div class="privacy-selector">
    <!-- Field Privacy Selector -->
    <div class="relative" v-if="mode === 'field'">
      <button 
        @click="toggleDropdown"
        class="flex items-center space-x-2 px-3 py-2 text-sm border rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
        :class="getButtonClasses()"
      >
        <component :is="getVisibilityIcon()" class="w-4 h-4" />
        <span class="hidden sm:inline">{{ getVisibilityLabel() }}</span>
        <ChevronDownIcon class="w-4 h-4" />
      </button>
      
      <!-- Dropdown Menu -->
      <div 
        v-if="showDropdown" 
        class="absolute right-0 mt-2 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-50"
        @click.stop
      >
        <div class="p-2">
          <div class="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
            Who can see this?
          </div>
          
          <!-- Visibility Options -->
          <div class="space-y-1">
            <button
              v-for="option in visibilityOptions"
              :key="option.value"
              @click="selectVisibility(option.value)"
              class="w-full flex items-center space-x-3 px-3 py-2 text-sm text-left rounded-md hover:bg-gray-50 transition-colors"
              :class="{ 'bg-blue-50 text-blue-700': value === option.value }"
            >
              <component :is="option.icon" class="w-4 h-4 flex-shrink-0" />
              <div class="flex-1">
                <div class="font-medium">{{ option.label }}</div>
                <div class="text-xs text-gray-500">{{ option.description }}</div>
              </div>
              <CheckIcon v-if="value === option.value" class="w-4 h-4 text-blue-600" />
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Section Privacy Selector -->
    <div class="section-privacy-controls" v-else-if="mode === 'section'">
      <div class="flex items-center space-x-2">
        <span class="text-sm font-medium text-gray-700">Section Privacy:</span>
        <select 
          :value="value"
          @change="$emit('update:modelValue', $event.target.value)"
          class="px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="" disabled>Select privacy level</option>
          <option 
            v-for="option in visibilityOptions" 
            :key="option.value" 
            :value="option.value"
          >
            {{ option.label }}
          </option>
        </select>
        <button
          @click="$emit('apply-to-section')"
          class="px-3 py-1 text-xs bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          :disabled="!value"
        >
          Apply to All
        </button>
      </div>
    </div>
    
    <!-- Privacy Indicator (read-only) -->
    <div class="privacy-indicator" v-else-if="mode === 'indicator'">
      <div class="flex items-center space-x-1 text-xs text-gray-500">
        <component :is="getVisibilityIcon()" class="w-3 h-3" />
        <span class="hidden sm:inline">{{ getVisibilityLabel() }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { 
  GlobeAltIcon, 
  UserGroupIcon, 
  UserIcon, 
  LockClosedIcon,
  ChevronDownIcon,
  CheckIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  modelValue: {
    type: String,
    default: 'public'
  },
  mode: {
    type: String,
    default: 'field', // 'field', 'section', 'indicator'
    validator: (value) => ['field', 'section', 'indicator'].includes(value)
  },
  fieldName: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'sm', // 'xs', 'sm', 'md'
    validator: (value) => ['xs', 'sm', 'md'].includes(value)
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'apply-to-section'])

const showDropdown = ref(false)
const value = computed(() => props.modelValue)

// Visibility options with icons and descriptions
const visibilityOptions = [
  {
    value: 'public',
    label: 'Everyone',
    description: 'Anyone can see this information',
    icon: GlobeAltIcon
  },
  {
    value: 'alumni_only',
    label: 'Alumni Only',
    description: 'Only verified alumni can see this',
    icon: UserGroupIcon
  },
  {
    value: 'connections_only',
    label: 'Connections Only',
    description: 'Only your connections can see this',
    icon: UserIcon
  },
  {
    value: 'private',
    label: 'Only Me',
    description: 'Only you can see this information',
    icon: LockClosedIcon
  }
]

// Get current visibility option
const getCurrentOption = () => {
  return visibilityOptions.find(option => option.value === value.value) || visibilityOptions[0]
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

// Get button classes based on size and visibility
const getButtonClasses = () => {
  const baseClasses = 'transition-colors duration-200'
  const sizeClasses = {
    xs: 'px-2 py-1 text-xs',
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2.5 text-base'
  }
  
  const visibilityClasses = {
    public: 'border-green-300 text-green-700 hover:bg-green-50',
    alumni_only: 'border-blue-300 text-blue-700 hover:bg-blue-50',
    connections_only: 'border-purple-300 text-purple-700 hover:bg-purple-50',
    private: 'border-gray-400 text-gray-700 hover:bg-gray-50'
  }
  
  return [
    baseClasses,
    sizeClasses[props.size],
    visibilityClasses[value.value] || visibilityClasses.public,
    props.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
  ].join(' ')
}

// Toggle dropdown visibility
const toggleDropdown = () => {
  if (!props.disabled) {
    showDropdown.value = !showDropdown.value
  }
}

// Select visibility option
const selectVisibility = (visibility) => {
  emit('update:modelValue', visibility)
  showDropdown.value = false
}

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.privacy-selector')) {
    showDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* Custom styles for the privacy selector */
.privacy-selector {
  @apply relative;
}

/* Smooth transitions for dropdown */
.privacy-selector .absolute {
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
.privacy-selector button:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Focus states for accessibility */
.privacy-selector button:focus,
.privacy-selector select:focus {
  @apply ring-2 ring-blue-500 ring-offset-1;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .privacy-selector .w-64 {
    @apply w-56;
  }
}
</style>