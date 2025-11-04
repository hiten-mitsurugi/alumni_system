<template>
  <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-8 mb-8">
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-4xl font-bold text-slate-800 mb-2">Survey Management</h1>
        <p class="text-slate-600">Create, manage, and analyze your dynamic survey system</p>
      </div>
      <div class="flex gap-3">
        <button
          @click="$emit('export-click')"
          class="group flex items-center gap-2 px-5 py-3 bg-gradient-to-r from-orange-600 to-orange-500 text-white rounded-lg hover:from-orange-500 hover:to-orange-600 transition-all duration-200 shadow-md hover:shadow-lg cursor-pointer transform hover:scale-105"
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

defineEmits(['export-click'])
</script>
