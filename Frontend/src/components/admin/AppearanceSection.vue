<template>
  <div class="p-8">
    <div class="flex items-center gap-3 mb-6">
      <PaletteIcon class="w-6 h-6 text-blue-600" />
      <h2 class="text-2xl font-bold"
          :class="themeStore.isAdminDark() ? 'text-white' : 'text-gray-900'">
        Appearance
      </h2>
    </div>

    <!-- Theme Selection -->
    <div class="mb-8">
      <h3 class="text-lg font-semibold mb-4"
          :class="themeStore.isAdminDark() ? 'text-white' : 'text-gray-900'">
        Admin Theme Preference
      </h3>
      <p class="text-sm mb-6"
         :class="themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600'">
        Choose how the admin interface appears. This setting only affects admin pages.
      </p>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Light Theme -->
      <div class="relative cursor-pointer group"
         @click="themeStore.setAdminTheme('light')">
          <div class="p-4 rounded-xl border-2 transition-all duration-300 hover:shadow-lg"
               :class="themeStore.adminThemeMode === 'light'
                 ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-md'
                 : 'border-gray-300 hover:border-blue-300 dark:border-gray-600'">

            <!-- Light Theme Preview -->
            <div class="bg-white rounded-lg p-4 shadow-inner mb-3 border border-gray-100">
              <div class="flex items-center gap-2 mb-3">
                <div class="w-3 h-3 bg-blue-500 rounded-full"></div>
                <div class="flex-1">
                  <div class="w-16 h-2 bg-gray-200 rounded mb-1"></div>
                  <div class="w-12 h-1.5 bg-gray-100 rounded"></div>
                </div>
              </div>
              <div class="space-y-2">
                <div class="w-full h-2 bg-gray-100 rounded"></div>
                <div class="w-3/4 h-2 bg-gray-100 rounded"></div>
              </div>
              <div class="mt-3 flex gap-1">
                <div class="w-8 h-4 bg-blue-500 rounded text-xs"></div>
                <div class="w-8 h-4 bg-gray-200 rounded text-xs"></div>
              </div>
            </div>

            <div class="text-center">
              <div class="flex items-center justify-center gap-2 mb-1">
                <SunIcon class="w-4 h-4 text-yellow-500" />
                <span class="font-semibold text-sm"
                      :class="themeStore.isAdminDark() ? 'text-white' : 'text-gray-900'">
                   Light Mode
                </span>
              </div>
              <div class="text-xs text-gray-500">Always light theme</div>
            </div>
          </div>
        </div>

        <!-- Dark Theme -->
        <div class="relative cursor-pointer group"
           @click="themeStore.setAdminTheme('dark')">
            <div class="p-4 rounded-xl border-2 transition-all duration-300 hover:shadow-lg"
                 :class="themeStore.adminThemeMode === 'dark'
                   ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-md'
                   : 'border-gray-300 hover:border-blue-300 dark:border-gray-600'">

              <!-- Dark Theme Preview -->
              <div class="bg-gray-800 rounded-lg p-4 shadow-inner mb-3 border border-gray-700">
                <div class="flex items-center gap-2 mb-3">
                  <div class="w-3 h-3 bg-blue-400 rounded-full"></div>
                  <div class="flex-1">
                    <div class="w-16 h-2 bg-gray-600 rounded mb-1"></div>
                    <div class="w-12 h-1.5 bg-gray-700 rounded"></div>
                  </div>
                </div>
                <div class="space-y-2">
                  <div class="w-full h-2 bg-gray-700 rounded"></div>
                  <div class="w-3/4 h-2 bg-gray-700 rounded"></div>
                </div>
                <div class="mt-3 flex gap-1">
                  <div class="w-8 h-4 bg-blue-500 rounded text-xs"></div>
                  <div class="w-8 h-4 bg-gray-600 rounded text-xs"></div>
                </div>
              </div>

              <div class="text-center">
                <div class="flex items-center justify-center gap-2 mb-1">
                  <MoonIcon class="w-4 h-4 text-blue-400" />
                  <span class="font-semibold text-sm"
                        :class="themeStore.isAdminDark() ? 'text-white' : 'text-gray-900'">
                     Dark Mode
                  </span>
                </div>
                <div class="text-xs text-gray-500">Always dark theme</div>
              </div>
            </div>
          </div>

        <!-- Auto Theme (Time-based) -->
        <div class="relative cursor-pointer group"
           @click="themeStore.setAdminTheme('auto')">
            <div class="p-4 rounded-xl border-2 transition-all duration-300 hover:shadow-lg"
                 :class="themeStore.adminThemeMode === 'auto'
                   ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-md'
                   : 'border-gray-300 hover:border-blue-300 dark:border-gray-600'">

              <!-- Auto Theme Preview -->
              <div class="relative rounded-lg mb-3 border overflow-hidden" style="height: 80px;">
                <!-- Light side -->
                <div class="absolute left-0 top-0 bottom-0 w-1/2 bg-white border-r border-gray-200 p-2">
                  <div class="flex items-center gap-1 mb-2">
                    <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <div class="w-8 h-1 bg-gray-200 rounded"></div>
                  </div>
                  <div class="space-y-1">
                    <div class="w-full h-1 bg-gray-100 rounded"></div>
                    <div class="w-2/3 h-1 bg-gray-100 rounded"></div>
                  </div>
                </div>
                <!-- Dark side -->
                <div class="absolute right-0 top-0 bottom-0 w-1/2 bg-gray-800 p-2">
                  <div class="flex items-center gap-1 mb-2">
                    <div class="w-2 h-2 bg-blue-400 rounded-full"></div>
                    <div class="w-8 h-1 bg-gray-600 rounded"></div>
                  </div>
                  <div class="space-y-1">
                    <div class="w-full h-1 bg-gray-700 rounded"></div>
                    <div class="w-2/3 h-1 bg-gray-700 rounded"></div>
                  </div>
                </div>
              </div>

              <div class="text-center">
                <div class="flex items-center justify-center gap-2 mb-1">
                  <ClockIcon class="w-4 h-4 text-purple-500" />
                  <span class="font-semibold text-sm"
                        :class="themeStore.isAdminDark() ? 'text-white' : 'text-gray-900'">
                     Auto Mode
                  </span>
                </div>
                <div class="text-xs text-gray-500">6PM-6AM: Dark, 6AM-6PM: Light</div>
              </div>
            </div>
          </div>

        <!-- System Theme -->
        <div class="relative cursor-pointer group"
           @click="themeStore.setAdminTheme('system')">
            <div class="p-4 rounded-xl border-2 transition-all duration-300 hover:shadow-lg"
                 :class="themeStore.adminThemeMode === 'system'
                   ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-md'
                   : 'border-gray-300 hover:border-blue-300 dark:border-gray-600'">

              <!-- System Theme Preview -->
              <div class="relative rounded-lg mb-3 border overflow-hidden bg-gradient-to-r from-white via-gray-100 to-gray-800" style="height: 80px;">
                <div class="absolute inset-0 p-2">
                  <div class="flex items-center gap-1 mb-2">
                    <div class="w-2 h-2 bg-gradient-to-r from-yellow-400 to-blue-400 rounded-full"></div>
                    <div class="w-8 h-1 bg-gradient-to-r from-gray-200 to-gray-600 rounded"></div>
                  </div>
                  <div class="space-y-1">
                    <div class="w-full h-1 bg-gradient-to-r from-gray-100 to-gray-700 rounded"></div>
                    <div class="w-2/3 h-1 bg-gradient-to-r from-gray-100 to-gray-700 rounded"></div>
                  </div>
                </div>
              </div>

              <div class="text-center">
                <div class="flex items-center justify-center gap-2 mb-1">
                  <MonitorIcon class="w-4 h-4 text-indigo-500" />
                  <span class="font-semibold text-sm"
                        :class="themeStore.isAdminDark() ? 'text-white' : 'text-gray-900'">
                     System Mode
                  </span>
                </div>
                <div class="text-xs text-gray-500">Follows OS preference</div>
              </div>
            </div>
          </div>
      </div>

      <!-- Current Status -->
      <div class="mt-6 p-4 rounded-lg"
           :class="themeStore.isAdminDark() ? 'bg-gray-700/50' : 'bg-gray-100'">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-sm font-medium"
                 :class="themeStore.isAdminDark() ? 'text-white' : 'text-gray-900'">
              Current Theme Status
            </div>
            <div class="text-xs mt-1"
                 :class="themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-600'">
              {{ getThemeStatusText() }}
            </div>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full"
                 :class="themeStore.isAdminDark() ? 'bg-blue-400' : 'bg-yellow-500'">
            </div>
            <span class="text-sm font-medium"
                  :class="themeStore.isAdminDark() ? 'text-blue-400' : 'text-yellow-600'">
              {{ themeStore.isAdminDark() ? 'Dark' : 'Light' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Additional Settings -->
    <div class="border-t pt-8"
         :class="themeStore.isAdminDark() ? 'border-gray-700' : 'border-gray-200'">
      <h3 class="text-lg font-semibold mb-4"
          :class="themeStore.isAdminDark() ? 'text-white' : 'text-gray-900'">
        Display Settings
      </h3>
      
      <div class="space-y-4">
        <!-- Reduced Motion -->
        <div class="flex items-center justify-between">
          <div>
            <label class="text-sm font-medium"
                   :class="themeStore.isAdminDark() ? 'text-white' : 'text-gray-900'">
              Reduce animations
            </label>
            <p class="text-xs"
               :class="themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600'">
              Minimize motion effects for better accessibility
            </p>
          </div>
          <input v-model="reducedMotion"
                 type="checkbox"
                 class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500">
        </div>

        <!-- High Contrast -->
        <div class="flex items-center justify-between">
          <div>
            <label class="text-sm font-medium"
                   :class="themeStore.isAdminDark() ? 'text-white' : 'text-gray-900'">
              High contrast mode
            </label>
            <p class="text-xs"
               :class="themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600'">
              Enhance text and interface contrast
            </p>
          </div>
          <input v-model="highContrast"
                 type="checkbox"
                 class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500">
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useThemeStore } from '@/stores/theme'
import {
  Palette as PaletteIcon,
  Sun as SunIcon,
  Moon as MoonIcon,
  Clock as ClockIcon,
  Monitor as MonitorIcon
} from 'lucide-vue-next'

const themeStore = useThemeStore()

// Additional display settings
const reducedMotion = ref(false)
const highContrast = ref(false)

// Initialize settings from localStorage
onMounted(() => {
  reducedMotion.value = localStorage.getItem('reducedMotion') === 'true'
  highContrast.value = localStorage.getItem('highContrast') === 'true'
  
  // Apply settings to document
  applyDisplaySettings()
  
  // Start time-based updates if needed
  themeStore.startTimeBasedUpdates()
})

onUnmounted(() => {
  themeStore.stopTimeBasedUpdates()
})

// Watch for changes in display settings
const applyDisplaySettings = () => {
  if (reducedMotion.value) {
    document.documentElement.classList.add('reduce-motion')
  } else {
    document.documentElement.classList.remove('reduce-motion')
  }
  
  if (highContrast.value) {
    document.documentElement.classList.add('high-contrast')
  } else {
    document.documentElement.classList.remove('high-contrast')
  }
  
  // Save to localStorage
  localStorage.setItem('reducedMotion', reducedMotion.value.toString())
  localStorage.setItem('highContrast', highContrast.value.toString())
}

// Watch for changes and apply them
watch([reducedMotion, highContrast], () => {
  applyDisplaySettings()
})

// Get current theme status text
const getThemeStatusText = () => {
  const mode = themeStore.adminThemeMode
  const isCurrentlyDark = themeStore.isAdminDark()
  
  if (mode === 'light') {
    return 'Admin interface is set to always use light theme'
  } else if (mode === 'dark') {
    return 'Admin interface is set to always use dark theme'
  } else if (mode === 'system') {
    return `Following system preference (currently ${isCurrentlyDark ? 'dark' : 'light'})`
  } else if (mode === 'auto') {
    const currentHour = new Date().getHours()
    const isNight = themeStore.isNightTime()
    return `Time-based switching (${currentHour}:00 - currently ${isNight ? 'night' : 'day'} mode)`
  }
  return 'Theme status unknown'
}

// Initialize admin theme on mount
onMounted(() => {
  themeStore.initializeAdminTheme()
})
</script>

<style scoped>
/* Custom styles for theme previews */
.reduce-motion * {
  animation-duration: 0.01ms !important;
  animation-iteration-count: 1 !important;
  transition-duration: 0.01ms !important;
}

.high-contrast {
  --tw-ring-color: #000000;
}

.high-contrast .border-gray-300 {
  border-color: #000000 !important;
}

.high-contrast .text-gray-600 {
  color: #000000 !important;
}

/* Theme preview hover effects */
.group:hover .shadow-inner {
  box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.15);
}

/* Custom animation for theme switching */
@keyframes theme-switch {
  0% { opacity: 0.8; }
  50% { opacity: 1; }
  100% { opacity: 0.8; }
}

.theme-preview {
  animation: theme-switch 2s ease-in-out infinite;
}
</style>