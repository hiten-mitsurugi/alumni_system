<template>
  <div :class="[
    'rounded-xl shadow-sm border p-8 mb-8',
    isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-slate-200'
  ]">
    <div class="flex justify-between items-center">
      <div>
        <h1 :class="['text-4xl font-bold mb-2', isDark ? 'text-white' : 'text-slate-800']">Survey Management</h1>
        <p :class="[isDark ? 'text-gray-300' : 'text-slate-600']">Create, manage, and analyze your dynamic survey system</p>
      </div>
      <div class="flex gap-3">
        <button
          @click="$emit('export')"
          :class="[
            'group flex items-center gap-2 px-5 py-3 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg cursor-pointer transform hover:scale-105',
            isDark 
              ? 'bg-gray-700 hover:bg-gray-600 text-white'
              : 'bg-gradient-to-r from-orange-600 to-orange-500 text-white hover:from-orange-500 hover:to-orange-600'
          ]"
        >
          <Download class="w-4 h-4 group-hover:animate-bounce" />
          Export Data
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Download } from 'lucide-vue-next'

defineProps({
  isDark: {
    type: Boolean,
    default: false
  }
})

defineEmits(['export'])
</script>
