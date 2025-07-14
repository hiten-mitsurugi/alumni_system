<template>
  <router-link
    :to="to"
    class="relative group flex items-center p-3 hover:bg-green-800 cursor-pointer text-white"
  >
    <!-- Icon Component -->
    <component :is="icon" class="w-5 h-5" />

    <!-- Label (expanded) -->
    <span v-if="expanded" class="ml-3">{{ label }}</span>

    <!-- Badge -->
    <div v-if="badge" class="ml-auto bg-red-500 text-xs px-2 py-0.5 rounded-full">
      {{ badge }}
    </div>

    <!-- Tooltip (collapsed) -->
    <div
      v-if="!expanded"
      class="absolute left-full top-1/2 -translate-y-1/2 ml-2 hidden group-hover:block bg-green-800 text-white text-xs p-1 rounded z-10 whitespace-nowrap"
    >
      {{ label }}
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

