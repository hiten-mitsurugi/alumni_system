<template>
  <router-link
    :to="to"
    class="relative group flex items-center pl-3 pr-2 py-3 mb-2 rounded-lg transition-all duration-150 text-gray-600 hover:text-gray-800 hover:bg-gray-100 border border-transparent hover:border-gray-200"
    active-class="bg-orange-600 text-white border-orange-500 shadow-lg"
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
      class="absolute left-full top-1/2 -translate-y-1/2 ml-3 hidden group-hover:block bg-orange-600 text-white text-sm px-3 py-2 rounded-lg z-10 whitespace-nowrap shadow-lg border border-orange-500"
    >
      {{ label }}
      <div v-if="badge" class="inline-block ml-2 bg-red-500 text-xs px-1.5 py-0.5 rounded-full">{{ badge }}</div>
    </div>
  </router-link>
</template>

<script setup>
defineProps({
  icon: [Object, Function], 
  label: String,
  to: String,
  expanded: Boolean,
  badge: [String, Number]
})
</script>
