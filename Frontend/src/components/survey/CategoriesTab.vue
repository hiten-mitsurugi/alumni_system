<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold text-slate-800">Survey Categories</h2>
        <p class="text-slate-600 mt-1">Organize your survey questions into logical categories</p>
      </div>
      <button
        @click="$emit('add-category')"
        class="group flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-600 to-orange-500 text-white rounded-lg hover:from-orange-500 hover:to-orange-600 transition-all duration-200 shadow-md hover:shadow-lg cursor-pointer transform hover:scale-105"
      >
        <Plus class="w-5 h-5 group-hover:rotate-90 transition-transform" />
        Add Category
      </button>
    </div>

    <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="category in paginatedCategories"
        :key="category.id"
        class="group bg-white rounded-xl border border-slate-200 hover:border-indigo-300 p-6 hover:shadow-lg transition-all duration-300 cursor-pointer transform hover:scale-105"
      >
        <div class="flex justify-between items-start mb-4">
          <div class="flex-1">
            <h3 class="font-bold text-lg text-slate-800 group-hover:text-orange-600 transition-colors">
              {{ category.name }}
            </h3>
            <p class="text-slate-600 text-sm mt-2 line-clamp-2">{{ category.description }}</p>
          </div>
          <div class="flex gap-1 ml-4">
            <button
              @click.stop="$emit('edit-category', category)"
              class="p-2 text-slate-400 hover:text-orange-600 hover:bg-orange-50 rounded-lg transition-all duration-200 cursor-pointer"
              title="Edit Category"
            >
              <Edit class="w-4 h-4" />
            </button>
            <button
              @click.stop="$emit('delete-category', category.id)"
              class="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-200 cursor-pointer"
              title="Delete Category"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>

        <div class="flex justify-between items-center text-sm mb-4">
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
          <span :class="[
            'inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium',
            category.is_active
              ? 'bg-emerald-100 text-emerald-700'
              : 'bg-red-100 text-red-700'
          ]">
            <div :class="[
              'w-2 h-2 rounded-full',
              category.is_active ? 'bg-emerald-500' : 'bg-red-500'
            ]"></div>
            {{ category.is_active ? 'Active' : 'Inactive' }}
          </span>
        </div>

        <button
          @click.stop="$emit('view-questions', category)"
          class="w-full px-4 py-2 text-sm bg-gradient-to-r from-orange-600 to-orange-500 text-white rounded-lg hover:from-orange-500 hover:to-orange-600 transition-all duration-200 cursor-pointer shadow-md hover:shadow-lg transform hover:scale-105"
        >
          View Questions →
        </button>
      </div>
    </div>

    <!-- Categories Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-center mt-8">
      <nav class="flex items-center gap-2">
        <button
          @click="$emit('page-change', currentPage - 1)"
          :disabled="currentPage === 1"
          :class="[
            'flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200',
            currentPage === 1
              ? 'text-slate-400 cursor-not-allowed'
              : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 cursor-pointer'
          ]"
        >
          <ChevronLeft class="w-4 h-4" />
          Previous
        </button>

        <div class="flex gap-1 mx-4">
          <button
            v-for="page in Math.min(totalPages, 5)"
            :key="page"
            @click="$emit('page-change', page)"
            :class="[
              'w-10 h-10 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer',
              currentPage === page
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50'
            ]"
          >
            {{ page }}
          </button>
        </div>

        <button
          @click="$emit('page-change', currentPage + 1)"
          :disabled="currentPage === totalPages"
          :class="[
            'flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200',
            currentPage === totalPages
              ? 'text-slate-400 cursor-not-allowed'
              : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 cursor-pointer'
          ]"
        >
          Next
          <ChevronRight class="w-4 h-4" />
        </button>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { Plus, Edit, Trash2, FileText, ChevronLeft, ChevronRight } from 'lucide-vue-next'

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
  }
})

defineEmits(['add-category', 'edit-category', 'delete-category', 'view-questions', 'page-change'])
</script>
