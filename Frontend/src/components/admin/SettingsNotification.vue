<script setup>
import { computed, onMounted, onUnmounted, watch } from 'vue'
import { 
  CheckCircle as CheckIcon,
  XCircle as XIcon,
  AlertCircle as AlertIcon,
  Info as InfoIcon,
  X as CloseIcon
} from 'lucide-vue-next'

// Props
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  type: {
    type: String,
    default: 'success',
    validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
  },
  title: {
    type: String,
    required: true
  },
  message: {
    type: String,
    required: true
  },
  autoHide: {
    type: Boolean,
    default: true
  },
  duration: {
    type: Number,
    default: 5000
  },
  position: {
    type: String,
    default: 'top-right',
    validator: (value) => ['top-right', 'top-left', 'bottom-right', 'bottom-left', 'top-center', 'bottom-center'].includes(value)
  },
  themeStore: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['hide', 'action'])

// Computed properties
const notificationIcon = computed(() => {
  const icons = {
    success: CheckIcon,
    error: XIcon,
    warning: AlertIcon,
    info: InfoIcon
  }
  return icons[props.type] || InfoIcon
})

const notificationClasses = computed(() => {
  const baseClasses = 'flex items-start gap-4 p-4 rounded-lg shadow-lg backdrop-blur-sm border max-w-md w-full'
  
  const typeClasses = {
    success: props.themeStore.isDarkMode 
      ? 'bg-green-900/90 border-green-700 text-green-100'
      : 'bg-green-50 border-green-200 text-green-800',
    error: props.themeStore.isDarkMode
      ? 'bg-red-900/90 border-red-700 text-red-100'
      : 'bg-red-50 border-red-200 text-red-800',
    warning: props.themeStore.isDarkMode
      ? 'bg-yellow-900/90 border-yellow-700 text-yellow-100'
      : 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: props.themeStore.isDarkMode
      ? 'bg-blue-900/90 border-blue-700 text-blue-100'
      : 'bg-blue-50 border-blue-200 text-blue-800'
  }

  return `${baseClasses} ${typeClasses[props.type] || typeClasses.info}`
})

const iconClasses = computed(() => {
  const iconColors = {
    success: 'text-green-500',
    error: 'text-red-500',
    warning: 'text-yellow-500',
    info: 'text-blue-500'
  }
  
  return `w-6 h-6 flex-shrink-0 ${iconColors[props.type] || iconColors.info}`
})

const containerClasses = computed(() => {
  const positions = {
    'top-right': 'fixed top-4 right-4 z-[9999]',
    'top-left': 'fixed top-4 left-4 z-[9999]',
    'top-center': 'fixed top-4 left-1/2 transform -translate-x-1/2 z-[9999]',
    'bottom-right': 'fixed bottom-4 right-4 z-[9999]',
    'bottom-left': 'fixed bottom-4 left-4 z-[9999]',
    'bottom-center': 'fixed bottom-4 left-1/2 transform -translate-x-1/2 z-[9999]'
  }
  
  const baseAnimation = 'transform transition-all duration-300 ease-in-out'
  const showAnimation = props.show ? 'translate-x-0 opacity-100 scale-100' : 'translate-x-full opacity-0 scale-95'
  
  return `${positions[props.position] || positions['top-right']} ${baseAnimation} ${showAnimation}`
})

// Auto-hide functionality
let hideTimeout = null

const startAutoHide = () => {
  if (props.autoHide && props.duration > 0) {
    hideTimeout = setTimeout(() => {
      onHide()
    }, props.duration)
  }
}

const clearAutoHide = () => {
  if (hideTimeout) {
    clearTimeout(hideTimeout)
    hideTimeout = null
  }
}

// Methods
const onHide = () => {
  clearAutoHide()
  emit('hide')
}

const onAction = (actionType) => {
  emit('action', actionType)
  onHide()
}

// Lifecycle
onMounted(() => {
  if (props.show) {
    startAutoHide()
  }
})

onUnmounted(() => {
  clearAutoHide()
})

// Watch for show prop changes
watch(() => props.show, (newShow) => {
  if (newShow) {
    startAutoHide()
  } else {
    clearAutoHide()
  }
})
</script>

<template>
  <Teleport to="body">
    <transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="transform translate-x-full opacity-0 scale-95"
      enter-to-class="transform translate-x-0 opacity-100 scale-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="transform translate-x-0 opacity-100 scale-100"
      leave-to-class="transform translate-x-full opacity-0 scale-95">
      
      <div v-if="show" :class="containerClasses">
        <div :class="notificationClasses" 
             @mouseenter="clearAutoHide"
             @mouseleave="startAutoHide">
          
          <!-- Icon -->
          <div class="flex-shrink-0">
            <div class="p-1 rounded-full"
                 :class="type === 'success' ? 'bg-green-500' : 
                         type === 'error' ? 'bg-red-500' : 
                         type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'">
              <component :is="notificationIcon" class="w-4 h-4 text-white" />
            </div>
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0">
            <!-- Title -->
            <h4 class="font-semibold text-sm mb-1 leading-tight">
              {{ title }}
            </h4>
            
            <!-- Message -->
            <p class="text-sm opacity-90 leading-relaxed">
              {{ message }}
            </p>

            <!-- Action Buttons (if provided via slots) -->
            <div v-if="$slots.actions" class="flex gap-2 mt-3">
              <slot name="actions" :onAction="onAction" />
            </div>
          </div>

          <!-- Close Button -->
          <button 
            @click="onHide"
            class="flex-shrink-0 ml-2 p-1 rounded-full transition-colors hover:bg-black/10 dark:hover:bg-white/10"
            :class="themeStore.isDarkMode ? 'text-gray-300 hover:text-white' : 'text-gray-400 hover:text-gray-600'"
            aria-label="Close notification">
            <CloseIcon class="w-4 h-4" />
          </button>

          <!-- Progress Bar for Auto-hide -->
          <div v-if="autoHide && show" 
               class="absolute bottom-0 left-0 h-1 rounded-b-lg transition-all ease-linear"
               :class="type === 'success' ? 'bg-green-400' : 
                       type === 'error' ? 'bg-red-400' : 
                       type === 'warning' ? 'bg-yellow-400' : 'bg-blue-400'"
               :style="{ 
                 width: '100%', 
                 animation: `shrink ${duration}ms linear` 
               }">
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<style scoped>
@keyframes shrink {
  from {
    width: 100%;
  }
  to {
    width: 0%;
  }
}

/* Ensure the notification appears above everything else */
.z-\[9999\] {
  z-index: 9999;
}

/* Custom backdrop blur for better visibility */
.backdrop-blur-sm {
  backdrop-filter: blur(4px);
}

/* Smooth scaling animation */
.scale-95 {
  transform: scale(0.95);
}

.scale-100 {
  transform: scale(1);
}

/* Enhanced shadow for better visibility */
.shadow-lg {
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -2px rgb(0 0 0 / 0.1);
}

/* Prevent text selection */
.select-none {
  user-select: none;
}

/* Ensure proper pointer events */
button {
  pointer-events: auto;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .max-w-md {
    max-width: calc(100vw - 2rem);
  }
}
</style>