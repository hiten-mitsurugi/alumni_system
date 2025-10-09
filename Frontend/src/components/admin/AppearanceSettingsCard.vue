<script setup>
import { computed } from 'vue'
import { Palette as PaletteIcon } from 'lucide-vue-next'
import { useThemeSettings } from '@/composables/useThemeSettings'

// Props
const props = defineProps({
  themeStore: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['theme-change'])

// Composables
const {
  appearanceSettings,
  themeOptions,
  colorSchemeOptions,
  fontSizeOptions,
  borderRadiusOptions,
  currentThemeOption,
  currentColorScheme,
  currentFontSize,
  isDarkMode,
  setTheme,
  setColorScheme,
  setFontSize,
  setBorderRadius,
  toggleCompactMode,
  toggleHighContrast,
  toggleReducedMotion,
  toggleAnimations,
  resetToDefaults,
  getAccessibilityRecommendations
} = useThemeSettings()

// Computed
const accessibilityRecommendations = computed(() => getAccessibilityRecommendations())

// Methods
const onThemeChange = (themeId) => {
  setTheme(themeId)
  emit('theme-change', 'theme', themeId)
}

const onColorSchemeChange = (schemeId) => {
  setColorScheme(schemeId)
  emit('theme-change', 'colorScheme', schemeId)
}

const onFontSizeChange = (sizeId) => {
  setFontSize(sizeId)
  emit('theme-change', 'fontSize', sizeId)
}

const onBorderRadiusChange = (radiusId) => {
  setBorderRadius(radiusId)
  emit('theme-change', 'borderRadius', radiusId)
}

const onToggleCompactMode = () => {
  toggleCompactMode()
  emit('theme-change', 'compactMode', appearanceSettings.value.compactMode)
}

const onToggleHighContrast = () => {
  toggleHighContrast()
  emit('theme-change', 'highContrast', appearanceSettings.value.highContrast)
}

const onToggleReducedMotion = () => {
  toggleReducedMotion()
  emit('theme-change', 'reducedMotion', appearanceSettings.value.reducedMotion)
}

const onToggleAnimations = () => {
  toggleAnimations()
  emit('theme-change', 'showAnimations', appearanceSettings.value.showAnimations)
}

const onResetToDefaults = () => {
  resetToDefaults()
  emit('theme-change', 'reset', null)
}
</script>

<template>
  <div class="p-6 rounded-xl border transition-colors duration-200"
       :class="themeStore.isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'">
    
    <!-- Header -->
    <div class="flex items-center gap-3 mb-6">
      <PaletteIcon class="w-6 h-6 text-blue-600" />
      <h3 class="text-xl font-semibold"
          :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
        Appearance Settings
      </h3>
    </div>

    <!-- Theme Selection -->
    <div class="mb-8">
      <h4 class="text-lg font-semibold mb-4"
          :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
        Theme Preference
      </h4>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div v-for="theme in themeOptions"
             :key="theme.id"
             class="relative cursor-pointer group"
             @click="onThemeChange(theme.id)">
          <div class="p-4 rounded-xl border-2 transition-all duration-300 hover:shadow-lg"
               :class="appearanceSettings.theme === theme.id
                 ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-md'
                 : 'border-gray-300 hover:border-blue-300 dark:border-gray-600 dark:hover:border-blue-500'">

            <!-- Theme Preview -->
            <div :class="theme.preview.background" class="rounded-lg p-4 shadow-inner mb-3 border border-gray-100 dark:border-gray-700 min-h-[120px]">
              <div class="flex items-center gap-2 mb-3">
                <div :class="theme.preview.accent" class="w-3 h-3 rounded-full"></div>
                <div class="flex-1">
                  <div :class="theme.preview.text" class="w-16 h-2 rounded mb-1 opacity-80"></div>
                  <div :class="theme.preview.text" class="w-12 h-2 rounded opacity-60"></div>
                </div>
              </div>
              <div class="space-y-2">
                <div :class="theme.preview.surface" class="w-full h-2 rounded"></div>
                <div :class="theme.preview.surface" class="w-4/5 h-2 rounded"></div>
                <div :class="theme.preview.surface" class="w-3/5 h-2 rounded"></div>
              </div>
            </div>

            <div class="text-center">
              <h5 class="font-semibold text-sm"
                  :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
                {{ theme.name }}
              </h5>
              <p class="text-xs mt-1"
                 :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'">
                {{ theme.description }}
              </p>
            </div>

            <!-- Selection Indicator -->
            <div v-if="appearanceSettings.theme === theme.id"
                 class="absolute top-2 right-2 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Color Scheme -->
    <div class="mb-8">
      <h4 class="text-lg font-semibold mb-4"
          :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
        Color Scheme
      </h4>
      
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div v-for="scheme in colorSchemeOptions"
             :key="scheme.id"
             class="cursor-pointer group"
             @click="onColorSchemeChange(scheme.id)">
          <div class="p-4 rounded-lg border-2 transition-all duration-200"
               :class="appearanceSettings.colorScheme === scheme.id
                 ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                 : 'border-gray-300 hover:border-gray-400 dark:border-gray-600'">
            
            <div class="flex items-center gap-3">
              <div :class="scheme.color" class="w-8 h-8 rounded-full shadow-sm"></div>
              <div class="flex-1">
                <h6 class="font-medium text-sm"
                    :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
                  {{ scheme.name }}
                </h6>
                <p class="text-xs"
                   :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'">
                  {{ scheme.description }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Font Size -->
    <div class="mb-8">
      <h4 class="text-lg font-semibold mb-4"
          :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
        Font Size
      </h4>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div v-for="size in fontSizeOptions"
             :key="size.id"
             class="cursor-pointer"
             @click="onFontSizeChange(size.id)">
          <div class="p-4 rounded-lg border-2 transition-all duration-200"
               :class="appearanceSettings.fontSize === size.id
                 ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                 : 'border-gray-300 hover:border-gray-400 dark:border-gray-600'">
            
            <div class="text-center">
              <div :class="[
                     size.class,
                     'font-medium mb-2',
                     themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                   ]">
                Aa
              </div>
              <h6 class="font-medium text-sm"
                  :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
                {{ size.name }}
              </h6>
              <p class="text-xs"
                 :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'">
                {{ size.description }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Border Radius -->
    <div class="mb-8">
      <h4 class="text-lg font-semibold mb-4"
          :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
        Border Radius
      </h4>
      
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div v-for="radius in borderRadiusOptions"
             :key="radius.id"
             class="cursor-pointer"
             @click="onBorderRadiusChange(radius.id)">
          <div class="p-4 border-2 transition-all duration-200"
               :class="[
                 radius.class,
                 appearanceSettings.borderRadius === radius.id
                   ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                   : 'border-gray-300 hover:border-gray-400 dark:border-gray-600'
               ]">
            
            <div class="text-center">
              <div class="w-8 h-8 mx-auto mb-2"
                   :class="[
                     radius.class,
                     themeStore.isDarkMode ? 'bg-gray-600' : 'bg-gray-300'
                   ]"></div>
              <h6 class="font-medium text-sm"
                  :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
                {{ radius.name }}
              </h6>
              <p class="text-xs"
                 :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'">
                {{ radius.description }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Advanced Settings -->
    <div class="border-t pt-6"
         :class="themeStore.isDarkMode ? 'border-gray-700' : 'border-gray-200'">
      <h4 class="text-lg font-semibold mb-4"
          :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
        Advanced Options
      </h4>
      
      <div class="space-y-4">
        <!-- Compact Mode -->
        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium"
               :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
              Compact Mode
            </p>
            <p class="text-sm"
               :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'">
              Reduce spacing and padding for a more condensed layout
            </p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input :checked="appearanceSettings.compactMode"
                   @change="onToggleCompactMode"
                   type="checkbox"
                   class="sr-only peer">
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
          </label>
        </div>

        <!-- High Contrast -->
        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium"
               :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
              High Contrast
            </p>
            <p class="text-sm"
               :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'">
              Increase contrast between text and background colors
            </p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input :checked="appearanceSettings.highContrast"
                   @change="onToggleHighContrast"
                   type="checkbox"
                   class="sr-only peer">
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
          </label>
        </div>

        <!-- Reduced Motion -->
        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium"
               :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
              Reduce Motion
            </p>
            <p class="text-sm"
               :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'">
              Minimize animations and transitions
            </p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input :checked="appearanceSettings.reducedMotion"
                   @change="onToggleReducedMotion"
                   type="checkbox"
                   class="sr-only peer">
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
          </label>
        </div>

        <!-- Show Animations -->
        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium"
               :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
              Show Animations
            </p>
            <p class="text-sm"
               :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'">
              Enable smooth transitions and hover effects
            </p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input :checked="appearanceSettings.showAnimations"
                   @change="onToggleAnimations"
                   type="checkbox"
                   class="sr-only peer">
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
          </label>
        </div>
      </div>
    </div>

    <!-- Accessibility Recommendations -->
    <div v-if="accessibilityRecommendations.length > 0"
         class="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
      <h5 class="font-medium text-blue-800 dark:text-blue-200 mb-2">
        Accessibility Recommendations
      </h5>
      <ul class="space-y-2">
        <li v-for="(rec, index) in accessibilityRecommendations"
            :key="index"
            class="flex items-start gap-3">
          <div class="w-2 h-2 bg-blue-500 rounded-full mt-1.5"></div>
          <div class="flex-1">
            <p class="text-sm text-blue-700 dark:text-blue-300">
              {{ rec.message }}
            </p>
            <button v-if="rec.action"
                    @click="rec.action"
                    class="text-xs text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 underline mt-1">
              Apply this setting
            </button>
          </div>
        </li>
      </ul>
    </div>

    <!-- Reset Button -->
    <div class="mt-8 pt-6 border-t flex justify-end"
         :class="themeStore.isDarkMode ? 'border-gray-700' : 'border-gray-200'">
      <button @click="onResetToDefaults"
              class="px-6 py-2 border rounded-lg transition-colors"
              :class="themeStore.isDarkMode 
                ? 'border-gray-600 text-gray-300 hover:bg-gray-700' 
                : 'border-gray-300 text-gray-700 hover:bg-gray-50'">
        Reset to Defaults
      </button>
    </div>
  </div>
</template>