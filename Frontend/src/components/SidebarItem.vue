<template>
  <router-link
    :to="to"
    class="relative group flex items-center p-3 mb-2 rounded-lg transition-all duration-150 text-slate-300 hover:text-white hover:bg-slate-800 border border-transparent hover:border-slate-700"
    active-class="bg-blue-600 text-white border-blue-500 shadow-lg"
  >
    <!-- Icon Component -->
    <component :is="icon" class="w-5 h-5 transition-colors duration-150" />

    <!-- Label (expanded) -->
    <span v-if="expanded" class="ml-3 font-medium">{{ label }}</span>

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
      class="absolute left-full top-1/2 -translate-y-1/2 ml-2 hidden group-hover:block bg-slate-800 text-white text-sm px-3 py-2 rounded-lg z-10 whitespace-nowrap shadow-lg border border-slate-600"
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

