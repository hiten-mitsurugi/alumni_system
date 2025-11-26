<template>
  <div class="space-y-8">
    <div
      v-for="(category, catIndex) in categories"
      :key="category.category?.id || catIndex"
      :class="[
        'rounded-lg border p-6',
        themeStore.isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'
      ]"
    >
      <!-- Category Header -->
      <div class="mb-6">
        <h3 :class="[
          'text-lg font-semibold mb-2',
          themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
        ]">
          {{ category.category?.name || `Section ${catIndex + 1}` }}
        </h3>
        <p 
          v-if="category.category?.description"
          :class="[
            'text-sm',
            themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'
          ]"
        >
          {{ category.category.description }}
        </p>
      </div>

      <!-- Questions and Responses -->
      <div class="space-y-6">
        <div
          v-for="(question, qIndex) in category.questions"
          :key="question.id"
          :class="[
            'pb-6 border-b last:border-b-0',
            themeStore.isDarkMode ? 'border-gray-600' : 'border-gray-200'
          ]"
        >
          <!-- Question Text -->
          <div class="mb-3">
            <p :class="[
              'font-medium',
              themeStore.isDarkMode ? 'text-gray-200' : 'text-gray-900'
            ]">
              {{ qIndex + 1 }}. {{ question.question_text }}
            </p>
            <p 
              v-if="question.help_text"
              :class="[
                'text-sm mt-1',
                themeStore.isDarkMode ? 'text-gray-500' : 'text-gray-500'
              ]"
            >
              {{ question.help_text }}
            </p>
          </div>

          <!-- Response Display -->
          <ResponseDisplay
            :question="question"
            :response="responses[question.id]"
          />
        </div>
      </div>
    </div>

    <!-- No Responses Message -->
    <div 
      v-if="!categories || categories.length === 0"
      class="text-center py-12"
    >
      <svg 
        class="w-16 h-16 mx-auto mb-4 text-gray-400" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'">
        No responses found
      </p>
    </div>
  </div>
</template>

<script setup>
import { useThemeStore } from '@/stores/theme'
import ResponseDisplay from './ResponseDisplay.vue'

defineProps({
  categories: Array,
  responses: Object
})

const themeStore = useThemeStore()
</script>
