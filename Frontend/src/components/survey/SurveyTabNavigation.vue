<template>
  <div class="bg-white rounded-xl shadow-sm border border-slate-200 mb-6">
    <nav class="flex space-x-1 p-2">
      <button
        v-for="(label, tabValue) in tabs"
        :key="tabValue"
        @click="$emit('update:activeTab', tabValue)"
        :class="[
          'flex items-center gap-2 px-6 py-3 rounded-lg font-medium text-sm transition-all duration-200 cursor-pointer',
          activeTab === tabValue
            ? 'bg-gradient-to-r from-orange-600 to-orange-500 text-white shadow-md'
            : 'text-slate-600 hover:text-slate-800 hover:bg-slate-100'
        ]"
      >
        <component :is="icons[tabValue]" class="w-4 h-4" />
        {{ label }}
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
  }
})

defineEmits(['update:activeTab'])

const tabs = {
  categories: 'Categories',
  questions: 'Questions',
  analytics: 'Analytics'
}

const icons = {
  categories: FolderPlus,
  questions: ListChecks,
  analytics: BarChart3
}
</script>
