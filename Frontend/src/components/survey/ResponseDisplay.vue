<template>
  <div :class="[
    'rounded-lg p-4',
    themeStore.isDarkMode ? 'bg-gray-800 border border-gray-600' : 'bg-white border border-gray-300'
  ]">
    <!-- No Response -->
    <div 
      v-if="!response || response === '' || (Array.isArray(response) && response.length === 0)"
      :class="[
        'italic',
        themeStore.isDarkMode ? 'text-gray-500' : 'text-gray-400'
      ]"
    >
      No response provided
    </div>

    <!-- Text/Textarea/Email/Number Response -->
    <div 
      v-else-if="['text', 'textarea', 'email', 'number', 'date'].includes(question.question_type)"
      :class="themeStore.isDarkMode ? 'text-gray-200' : 'text-gray-900'"
    >
      {{ formatResponse(response) }}
    </div>

    <!-- Radio/Select/Yes-No Response -->
    <div 
      v-else-if="['radio', 'select', 'yes_no'].includes(question.question_type)"
      class="flex items-center gap-2"
    >
      <svg class="w-5 h-5 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
      </svg>
      <span :class="[
        'font-medium',
        themeStore.isDarkMode ? 'text-gray-200' : 'text-gray-900'
      ]">
        {{ response }}
      </span>
    </div>

    <!-- Checkbox Response (Array) -->
    <div 
      v-else-if="question.question_type === 'checkbox' && Array.isArray(response)"
      class="space-y-2"
    >
      <div 
        v-for="(item, index) in response"
        :key="index"
        class="flex items-center gap-2"
      >
        <svg class="w-5 h-5 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
        <span :class="themeStore.isDarkMode ? 'text-gray-200' : 'text-gray-900'">
          {{ item }}
        </span>
      </div>
    </div>

    <!-- Rating Response -->
    <div 
      v-else-if="question.question_type === 'rating'"
      class="flex items-center gap-2"
    >
      <div class="flex gap-1">
        <span
          v-for="star in 5"
          :key="star"
          :class="[
            'text-2xl',
            star <= parseInt(response) ? 'text-yellow-500' : 'text-gray-300'
          ]"
        >
          ★
        </span>
      </div>
      <span :class="[
        'font-semibold ml-2',
        themeStore.isDarkMode ? 'text-gray-200' : 'text-gray-900'
      ]">
        {{ response }} / {{ question.max_value || 5 }}
      </span>
    </div>

    <!-- Fallback for unknown types -->
    <div 
      v-else
      :class="themeStore.isDarkMode ? 'text-gray-200' : 'text-gray-900'"
    >
      {{ response }}
    </div>
  </div>
</template>

<script setup>
import { useThemeStore } from '@/stores/theme'

const props = defineProps({
  question: Object,
  response: [String, Number, Array, Boolean, Object]
})

const themeStore = useThemeStore()

const formatResponse = (value) => {
  if (props.question.question_type === 'date' && value) {
    return new Date(value).toLocaleDateString()
  }
  return value
}
</script>
