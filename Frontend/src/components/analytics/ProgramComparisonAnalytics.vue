<script setup>
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { BarChart3, TrendingUp, Users, Award } from 'lucide-vue-next'

const props = defineProps({
  data: {
    type: Object,
    required: true
  },
  appliedFilters: {
    type: Object,
    default: () => ({})
  }
})

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isAdminDark?.() || false)
</script>

<template>
  <div class="space-y-8">
    <!-- Page Header -->
    <div>
      <h1 :class="['text-3xl font-bold mb-2', isDark ? 'text-white' : 'text-gray-900']">
        Program Comparison Analytics
      </h1>
      <p :class="['text-lg', isDark ? 'text-gray-400' : 'text-gray-600']">
        Comprehensive cross-program performance evaluation for strategic planning
      </p>
    </div>

    <!-- Coming Soon Placeholder -->
    <div :class="['rounded-xl border p-12 text-center', isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
      <BarChart3 :class="['w-16 h-16 mx-auto mb-4', isDark ? 'text-gray-600' : 'text-gray-400']" />
      <h3 :class="['text-xl font-semibold mb-2', isDark ? 'text-white' : 'text-gray-900']">
        Program Comparison Analytics Coming Soon
      </h3>
      <p :class="['text-base', isDark ? 'text-gray-400' : 'text-gray-600']">
        This component will provide comprehensive cross-program performance evaluation and rankings.
      </p>
      <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
        <div :class="['p-4 rounded-lg', isDark ? 'bg-gray-700' : 'bg-gray-50']">
          <Award :class="['w-6 h-6 mx-auto mb-2', isDark ? 'text-gold-400' : 'text-yellow-500']" />
          <p :class="['text-sm font-medium', isDark ? 'text-gray-300' : 'text-gray-700']">
            Performance Matrix
          </p>
        </div>
        <div :class="['p-4 rounded-lg', isDark ? 'bg-gray-700' : 'bg-gray-50']">
          <TrendingUp :class="['w-6 h-6 mx-auto mb-2', isDark ? 'text-green-400' : 'text-green-500']" />
          <p :class="['text-sm font-medium', isDark ? 'text-gray-300' : 'text-gray-700']">
            Trend Analysis
          </p>
        </div>
        <div :class="['p-4 rounded-lg', isDark ? 'bg-gray-700' : 'bg-gray-50']">
          <Users :class="['w-6 h-6 mx-auto mb-2', isDark ? 'text-blue-400' : 'text-blue-500']" />
          <p :class="['text-sm font-medium', isDark ? 'text-gray-300' : 'text-gray-700']">
            Best Practices
          </p>
        </div>
      </div>
    </div>
  </div>
</template>