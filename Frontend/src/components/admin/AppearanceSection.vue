<template>
  <div class="p-8">
    <div class="flex items-center gap-3 mb-6">
      <PaletteIcon class="w-6 h-6 text-blue-600" />
      <h2 class="text-2xl font-bold"
          :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
        Appearance
      </h2>
    </div>

    <!-- Theme Selection -->
    <div class="mb-8">
      <h3 class="text-lg font-semibold mb-4"
          :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
        Theme Preference
      </h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Light Theme -->
      <div class="relative cursor-pointer group"
         @click="themeStore.setAdminTheme('light')">
          <div class="p-6 rounded-xl border-2 transition-all duration-300 hover:shadow-lg"
               :class="!themeStore.isDarkMode
                 ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-md'
                 : 'border-gray-300 hover:border-blue-300 dark:border-gray-600'">

            <!-- Light Theme Preview -->
            <div class="bg-white rounded-lg p-6 shadow-inner mb-4 border border-gray-100">
              <div class="flex items-center gap-3 mb-4">
                <div class="w-4 h-4 bg-blue-500 rounded-full"></div>
                <div class="flex-1">
                  <div class="w-24 h-3 bg-gray-200 rounded mb-1"></div>
                  <div class="w-16 h-2 bg-gray-100 rounded"></div>
                </div>
              </div>
              <div class="space-y-3">
                <div class="w-full h-3 bg-gray-100 rounded"></div>
                <div class="w-5/6 h-3 bg-gray-100 rounded"></div>
                <div class="w-4/6 h-3 bg-gray-100 rounded"></div>
              </div>
              <div class="mt-4 flex gap-2">
                <div class="w-16 h-6 bg-blue-500 rounded text-xs"></div>
                <div class="w-16 h-6 bg-gray-200 rounded text-xs"></div>
              </div>
            </div>

            <div class="text-center">
              <span class="font-semibold text-lg"
                    :class="themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-900'">
                 Admin Light
              </span>
              <div class="text-sm text-gray-500">Applies only to admin pages</div>
            </div>
          </div>
        </div>

        <!-- Dark Theme -->
     <div class="relative cursor-pointer group"
       @click="themeStore.setAdminTheme('dark')">
          <div class="p-6 rounded-xl border-2 transition-all duration-300 hover:shadow-lg"
               :class="themeStore.isDarkMode
                 ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-md'
                 : 'border-gray-300 hover:border-blue-300'">

            <!-- Dark Theme Preview -->
            <div class="bg-gray-800 rounded-lg p-6 shadow-inner mb-4 border border-gray-700">
              <div class="flex items-center gap-3 mb-4">
                <div class="w-4 h-4 bg-blue-400 rounded-full"></div>
                <div class="flex-1">
                  <div class="w-24 h-3 bg-gray-600 rounded mb-1"></div>
                  <div class="w-16 h-2 bg-gray-700 rounded"></div>
                </div>
              </div>
              <div class="space-y-3">
                <div class="w-full h-3 bg-gray-700 rounded"></div>
                <div class="w-5/6 h-3 bg-gray-700 rounded"></div>
                <div class="w-4/6 h-3 bg-gray-700 rounded"></div>
              </div>
              <div class="mt-4 flex gap-2">
                <div class="w-16 h-6 bg-blue-500 rounded text-xs"></div>
                <div class="w-16 h-6 bg-gray-600 rounded text-xs"></div>
              </div>
            </div>

            <div class="text-center">
              <span class="font-semibold text-lg"
                    :class="themeStore.isAdminDark() ? 'text-white' : 'text-gray-900'">
                 Admin Dark
              </span>
              <div class="text-sm text-gray-500">Applies only to admin pages</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="mt-6">
      <button class="px-4 py-2 bg-gray-200 rounded" @click="themeStore.setAdminTheme('auto')">Follow System</button>
    </div>
  </div>
</template>

<script setup>
import { useThemeStore } from '@/stores/theme'
import { Palette as PaletteIcon } from 'lucide-vue-next'

const themeStore = useThemeStore()
</script>