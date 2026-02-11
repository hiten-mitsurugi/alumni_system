<template>
  <div :class="[
    'border-b shadow-sm transition-colors duration-200',
    isDarkMode
      ? 'bg-gray-800 border-gray-700'
      : 'bg-white border-gray-200'
  ]">
    <div class="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
      <nav class="flex space-x-8">
        <button
          @click="$emit('update:activeTab', 'about')"
          :class="[
            'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'about'
              ? 'border-orange-500 ' + (isDarkMode ? 'text-orange-400' : 'text-orange-600')
              : 'border-transparent ' + (isDarkMode
                  ? 'text-gray-400 hover:text-gray-200 hover:border-gray-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300')
          ]"
        >
          About
        </button>
        <button
          @click="$emit('update:activeTab', 'posts')"
          :class="[
            'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'posts'
              ? 'border-orange-500 ' + (isDarkMode ? 'text-orange-400' : 'text-orange-600')
              : 'border-transparent ' + (isDarkMode
                  ? 'text-gray-400 hover:text-gray-200 hover:border-gray-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300')
          ]"
        >
          Posts
        </button>
      </nav>
    </div>
  </div>
</template>

<script setup>
defineProps({
  activeTab: {
    type: String,
    required: true
  },
  isDarkMode: {
    type: Boolean,
    default: false
  }
})

defineEmits(['update:activeTab'])
</script>
