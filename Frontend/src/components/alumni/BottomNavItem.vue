<template>
  <router-link
    :to="to"
    :class="[
      'relative flex flex-col items-center justify-center px-3 py-2 rounded-xl transition-all duration-200',
      'min-w-[60px] max-w-[80px] flex-1 group touch-manipulation',
      isActive
        ? themeStore.isDarkMode
          ? 'bg-orange-500/20 text-orange-400'
          : 'bg-orange-100 text-orange-600'
        : themeStore.isDarkMode
          ? 'text-gray-400 hover:text-orange-400 hover:bg-orange-500/10'
          : 'text-gray-500 hover:text-orange-600 hover:bg-orange-50',
      'active:scale-95 transform'
    ]"
    @click="handleClick"
  >
    <!-- Icon with badge -->
    <div class="relative mb-1">
      <component
        :is="icon"
        :class="[
          'transition-all duration-200',
          isActive
            ? 'w-6 h-6 scale-110'
            : 'w-5 h-5 group-hover:scale-105'
        ]"
        :stroke-width="isActive ? 2.5 : 2"
      />

      <!-- Badge -->
      <div
        v-if="badge"
        :class="[
          'absolute -top-2 -right-2 min-w-[18px] h-[18px] rounded-full flex items-center justify-center text-xs font-bold text-white',
          'transform transition-all duration-200',
          isActive ? 'scale-110' : 'scale-100',
          getBadgeColor(),
          // Hide survey badge on mobile screens
          to.includes('survey') ? 'hidden md:flex' : ''
        ]"
      >
        {{ badge.length > 2 ? '99+' : badge }}
      </div>
    </div>

    <!-- Label -->
    <span :class="[
      'text-xs font-medium transition-all duration-200 leading-none text-center',
      isActive
        ? 'transform scale-105 font-semibold'
        : 'group-hover:scale-102'
    ]">
      {{ label }}
    </span>

    <!-- Active indicator -->
    <div
      v-if="isActive"
      :class="[
        'absolute -top-0.5 left-1/2 transform -translate-x-1/2 w-6 h-1 rounded-full transition-all duration-300',
        themeStore.isDarkMode ? 'bg-orange-400' : 'bg-orange-500'
      ]"
    ></div>
  </router-link>
</template>

<script setup>
import { useThemeStore } from '@/stores/theme'

const props = defineProps({
  icon: {
    type: [Object, Function],
    required: true
  },
  label: {
    type: String,
    required: true
  },
  to: {
    type: String,
    required: true
  },
  badge: {
    type: String,
    default: null
  },
  isActive: {
    type: Boolean,
    default: false
  }
})

const themeStore = useThemeStore()

// Handle click with haptic feedback (if available)
const handleClick = () => {
  // Haptic feedback for iOS devices
  if (window.navigator && window.navigator.vibrate) {
    window.navigator.vibrate(10)
  }

  // Alternative haptic feedback for iOS
  if (window.AudioContext || window.webkitAudioContext) {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext
      const audioContext = new AudioContext()
      const oscillator = audioContext.createOscillator()
      const gainNode = audioContext.createGain()

      oscillator.connect(gainNode)
      gainNode.connect(audioContext.destination)

      oscillator.frequency.setValueAtTime(800, audioContext.currentTime)
      gainNode.gain.setValueAtTime(0, audioContext.currentTime)
      gainNode.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 0.01)
      gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.1)

      oscillator.start(audioContext.currentTime)
      oscillator.stop(audioContext.currentTime + 0.1)
    } catch {
      // Silent fail for haptic feedback
    }
  }
}

// Get badge color based on route
const getBadgeColor = () => {
  if (props.to.includes('messaging')) {
    return 'bg-green-500'
  } else if (props.to.includes('survey')) {
    return 'bg-blue-500'
  }
  return 'bg-red-500'
}
</script>

<style scoped>
/* Enhanced touch targets for mobile */
@media (max-width: 768px) {
  .touch-manipulation {
    touch-action: manipulation;
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    user-select: none;
  }
}

/* Smooth transitions for better UX */
.router-link-active {
  transform: translateY(-1px);
}

/* Focus states for accessibility */
.router-link:focus {
  outline: none;
}

.router-link:focus-visible {
  outline: 2px solid currentColor;
  outline-offset: 2px;
}
</style>
