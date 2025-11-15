<template>
  <div
    :class="[
      'group rounded-xl border p-6 hover:shadow-lg transition-all duration-300 cursor-pointer transform hover:scale-105',
      isDark 
        ? 'bg-gray-800 border-gray-700 hover:border-gray-600' 
        : 'bg-white border-slate-200 hover:border-indigo-300'
    ]"
  >
    <div class="flex justify-between items-start mb-4">
      <div class="flex-1">
        <h3 :class="[
          'font-bold text-lg transition-colors',
          isDark
            ? 'text-white group-hover:text-gray-400'
            : 'text-slate-800 group-hover:text-orange-600'
        ]">
          {{ category.name }}
        </h3>
        <p :class="['text-sm mt-2 line-clamp-2', isDark ? 'text-gray-300' : 'text-slate-600']">
          {{ category.description }}
        </p>
      </div>
      <div class="flex gap-1 ml-4">
        <button
          @click.stop="$emit('edit', category)"
          :class="[
            'p-2 rounded-lg transition-all duration-200 cursor-pointer',
            isDark
              ? 'text-gray-400 hover:text-gray-200 hover:bg-gray-700'
              : 'text-slate-400 hover:text-orange-600 hover:bg-orange-50'
          ]"
          title="Edit Category"
        >
          <Edit class="w-4 h-4" />
        </button>
        <button
          @click.stop="$emit('delete', category.id)"
          class="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-200 cursor-pointer"
          title="Delete Category"
        >
          <Trash2 class="w-4 h-4" />
        </button>
      </div>
    </div>
    
    <div class="flex justify-between items-center text-sm mb-4">
      <div class="flex flex-wrap gap-2">
        <span class="inline-flex items-center gap-1 px-3 py-1 bg-slate-100 text-slate-700 rounded-full">
          <FileText class="w-3 h-3" />
          {{ category.active_questions_count || 0 }} questions
          <span class="ml-1 text-xs" :class="[
            (category.total_questions_count || 0) >= 50 
              ? 'text-red-600' 
              : (category.total_questions_count || 0) >= 40 
                ? 'text-yellow-600' 
                : 'text-orange-500'
          ]">
            ({{ category.total_questions_count || 0 }}/50)
          </span>
        </span>
        <span 
          v-if="category.include_in_registration"
          class="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium"
          title="This category appears in the registration survey"
        >
          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
            <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd"/>
          </svg>
          Registration
        </span>
      </div>
    </div>

    <div class="flex flex-wrap gap-2 mb-4">
      <span
        :class="[
          'inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-semibold',
          category.is_active
            ? 'bg-emerald-100 text-emerald-700'
            : 'bg-slate-100 text-slate-600'
        ]"
      >
        <span :class="[
          'w-2 h-2 rounded-full',
          category.is_active ? 'bg-emerald-500' : 'bg-slate-400'
        ]"></span>
        {{ category.is_active ? 'Active' : 'Inactive' }}
      </span>
      <span class="inline-flex items-center gap-1 px-3 py-1.5 bg-slate-100 text-slate-600 rounded-full text-xs">
        <Settings class="w-3 h-3" />
        Order: {{ category.order }}
      </span>
    </div>

    <div class="flex gap-2">
      <button
        @click.stop="$emit('view-questions', category)"
        class="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-600 rounded-lg transition-all duration-200 cursor-pointer shadow-sm hover:shadow-md"
      >
        <Eye class="w-4 h-4" />
        View Questions
      </button>
      <button
        @click.stop="$emit('view-analytics', category)"
        class="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-600 rounded-lg transition-all duration-200 cursor-pointer shadow-sm hover:shadow-md"
      >
        <BarChart3 class="w-4 h-4" />
        Analytics
      </button>
    </div>
  </div>
</template>

<script setup>
import { Edit, Trash2, FileText, Settings, Eye, BarChart3 } from 'lucide-vue-next'

defineProps({
  category: {
    type: Object,
    required: true
  },
  isDark: {
    type: Boolean,
    default: false
  }
})

defineEmits(['edit', 'delete', 'view-questions', 'view-analytics'])
</script>
