<template>
  <router-link
    :to="to"
    class="relative group flex items-center pl-3 pr-2 py-3 mb-2 rounded-lg transition-all duration-150"
    :class="[
      themeStore.isDarkMode 
        ? 'text-gray-300 hover:text-white hover:bg-gray-700/50'
        : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
    ]"
    active-class="bg-orange-600 text-white shadow-lg"
  >
    <!-- Icon Component -->
    <div class="flex-shrink-0 flex items-center justify-left" :class="expanded ? 'w-10' : 'w-12'">
      <component :is="icon" :class="expanded ? 'w-8 h-8' : 'w-8 h-8'" class="transition-all duration-150" />
    </div>

    <!-- Label (expanded) -->
    <span v-if="expanded" class="ml-2 font-medium">{{ label }}</span>

    <!-- Badge -->
    <div 
      v-if="badge" 
      class="ml-auto bg-red-500 text-white text-xs px-2 py-1 rounded-full font-semibold shadow-sm"
    >
      {{ badge }}
    </div>

    <!-- Tooltip (collapsed) -->
    <div
      v-if="!expanded"
      :class="[
        'absolute left-full top-1/2 -translate-y-1/2 ml-3 hidden group-hover:block text-white text-sm px-3 py-2 rounded-lg z-10 whitespace-nowrap shadow-lg',
        themeStore.isDarkMode 
          ? 'bg-orange-500 border border-orange-400'
          : 'bg-orange-600 border border-orange-500'
      ]"
    >
      {{ label }}
      <div v-if="badge" class="inline-block ml-2 bg-red-500 text-xs px-1.5 py-0.5 rounded-full">{{ badge }}</div>
    </div>
  </router-link>
</template>

<script setup>
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

defineProps({
  icon: [Object, Function], 
  label: String,
  to: String,
  expanded: Boolean,
  badge: [String, Number]
})
</script>
