<template>
  <div :class="[
    'rounded-xl shadow-sm border mb-6',
    isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-slate-200'
  ]">
    <nav class="flex space-x-1 p-2">
      <button
        @click="$emit('change-tab', 'categories')"
        :class="[
          'flex items-center gap-2 px-6 py-3 rounded-lg font-medium text-sm transition-all duration-200 cursor-pointer',
          activeTab === 'categories'
            ? isDark 
              ? 'bg-gray-700 text-white shadow-md'
              : 'bg-gradient-to-r from-orange-600 to-orange-500 text-white shadow-md'
            : isDark
              ? 'text-gray-300 hover:text-white hover:bg-gray-700'
              : 'text-slate-600 hover:text-slate-800 hover:bg-slate-100'
        ]"
      >
        <FolderPlus class="w-4 h-4" />
        Categories
      </button>
      <button
        @click="$emit('change-tab', 'questions')"
        :class="[
          'flex items-center gap-2 px-6 py-3 rounded-lg font-medium text-sm transition-all duration-200 cursor-pointer',
          activeTab === 'questions'
            ? isDark 
              ? 'bg-gray-700 text-white shadow-md'
              : 'bg-gradient-to-r from-orange-600 to-orange-500 text-white shadow-md'
            : isDark
              ? 'text-gray-300 hover:text-white hover:bg-gray-700'
              : 'text-slate-600 hover:text-slate-800 hover:bg-slate-100'
        ]"
      >
        <ListChecks class="w-4 h-4" />
        Questions
      </button>
      <button
        @click="$emit('change-tab', 'analytics')"
        :class="[
          'flex items-center gap-2 px-6 py-3 rounded-lg font-medium text-sm transition-all duration-200 cursor-pointer',
          activeTab === 'analytics'
            ? isDark 
              ? 'bg-gray-700 text-white shadow-md'
              : 'bg-gradient-to-r from-orange-600 to-orange-500 text-white shadow-md'
            : isDark
              ? 'text-gray-300 hover:text-white hover:bg-gray-700'
              : 'text-slate-600 hover:text-slate-800 hover:bg-slate-100'
        ]"
      >
        <BarChart3 class="w-4 h-4" />
        Analytics
      </button>
    </nav>
  </div>
</template>

<script setup>
import { FolderPlus, ListChecks, BarChart3 } from 'lucide-vue-next'

defineProps({
  activeTab: {
    type: String,
    required: true
  },
  isDark: {
    type: Boolean,
    default: false
  }
})

defineEmits(['change-tab'])
</script>
