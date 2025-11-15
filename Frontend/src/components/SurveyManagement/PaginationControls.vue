<template>
  <div class="flex items-center justify-center gap-2">
    <button
      @click="$emit('prev')"
      :disabled="currentPage === 1"
      :class="[
        'p-2 rounded-lg transition-colors cursor-pointer',
        isDark
          ? 'hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed text-gray-300'
          : 'hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed text-slate-600'
      ]"
    >
      <ChevronLeft class="w-5 h-5" />
    </button>

    <template v-for="(page, index) in pageNumbers">
      <span
        v-if="page === '...'"
        :key="`ellipsis-${index}`"
        :class="['px-3 py-2', isDark ? 'text-gray-400' : 'text-slate-400']"
      >
        ...
      </span>
      <button
        v-else
        :key="`page-${page}`"
        @click="$emit('goto', page)"
        :class="[
          'min-w-[40px] px-3 py-2 rounded-lg font-medium transition-all cursor-pointer',
          currentPage === page
            ? isDark
              ? 'bg-gray-700 text-white'
              : 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg'
            : isDark
              ? 'text-gray-300 hover:bg-gray-700'
              : 'text-slate-600 hover:bg-slate-100'
        ]"
      >
        {{ page }}
      </button>
    </template>

    <button
      @click="$emit('next')"
      :disabled="currentPage === totalPages"
      :class="[
        'p-2 rounded-lg transition-colors cursor-pointer',
        isDark
          ? 'hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed text-gray-300'
          : 'hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed text-slate-600'
      ]"
    >
      <ChevronRight class="w-5 h-5" />
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

const props = defineProps({
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

defineEmits(['prev', 'next', 'goto'])

const pageNumbers = computed(() => {
  const pages = []
  const total = props.totalPages
  const current = props.currentPage
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) pages.push(i)
      pages.push('...')
      pages.push(total)
    } else if (current >= total - 3) {
      pages.push(1)
      pages.push('...')
      for (let i = total - 4; i <= total; i++) pages.push(i)
    } else {
      pages.push(1)
      pages.push('...')
      for (let i = current - 1; i <= current + 1; i++) pages.push(i)
      pages.push('...')
      pages.push(total)
    }
  }
  
  return pages
})
</script>
