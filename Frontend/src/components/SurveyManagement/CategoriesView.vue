<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h2 :class="['text-2xl font-bold', isDark ? 'text-white' : 'text-slate-800']">Survey Categories</h2>
        <p :class="['mt-1', isDark ? 'text-gray-300' : 'text-slate-600']">Organize your survey questions into logical categories</p>
      </div>
      <button
        @click="$emit('add-category')"
        :class="[
          'group flex items-center gap-2 px-6 py-3 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg cursor-pointer transform hover:scale-105',
          isDark 
            ? 'bg-gray-700 hover:bg-gray-600 text-white'
            : 'bg-gradient-to-r from-orange-600 to-orange-500 text-white hover:from-orange-500 hover:to-orange-600'
        ]"
      >
        <Plus class="w-5 h-5 group-hover:rotate-90 transition-transform" />
        Add Category
      </button>
    </div>

    <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <CategoryCard
        v-for="category in paginatedCategories"
        :key="category.id"
        :category="category"
        :is-dark="isDark"
        @edit="$emit('edit', $event)"
        @delete="$emit('delete', $event)"
        @view-questions="$emit('view-questions', $event)"
        @view-analytics="$emit('view-analytics', $event)"
      />
    </div>

    <PaginationControls
      v-if="totalPages > 1"
      :current-page="currentPage"
      :total-pages="totalPages"
      :is-dark="isDark"
      @prev="$emit('prev-page')"
      @next="$emit('next-page')"
      @goto="$emit('goto-page', $event)"
    />
  </div>
</template>

<script setup>
import { Plus } from 'lucide-vue-next'
import CategoryCard from './CategoryCard.vue'
import PaginationControls from './PaginationControls.vue'

defineProps({
  paginatedCategories: {
    type: Array,
    required: true
  },
  currentPage: {
    type: Number,
    required: true
  },
  totalPages: {
    type: Number,
    required: true
  },
  isDark: {
    type: Boolean,
    default: false
  }
})

defineEmits(['add-category', 'edit', 'delete', 'view-questions', 'view-analytics', 'prev-page', 'next-page', 'goto-page'])
</script>
