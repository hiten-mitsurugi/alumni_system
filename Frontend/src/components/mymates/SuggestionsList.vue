<template>
  <div class="space-y-6">
    <div v-if="suggestions.length > 0">
      <h2 :class="themeStore.isDarkMode ? 'text-base sm:text-lg font-semibold text-white mb-4' : 'text-base sm:text-lg font-semibold text-gray-900 mb-4'">People You May Know</h2>
      
      <div class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2 sm:gap-3 md:gap-4">
        <UserCard
          v-for="suggestion in suggestions"
          :key="suggestion.id"
          :user="suggestion"
          :single-action="connectAction"
          @view-profile="$emit('view-profile', $event)"
          @connect="$emit('connect-suggestion', $event)"
        />
      </div>
    </div>
    
    <div v-else class="text-center py-12">
      <svg :class="themeStore.isDarkMode ? 'w-16 h-16 mx-auto text-gray-500 mb-4' : 'w-16 h-16 mx-auto text-gray-400 mb-4'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
      </svg>
      <h3 :class="themeStore.isDarkMode ? 'text-lg font-medium text-white mb-2' : 'text-lg font-medium text-gray-900 mb-2'">No suggestions available</h3>
      <p :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'">Check back later for new connection suggestions.</p>
    </div>
  </div>
</template>

<script setup>
import UserCard from './UserCard.vue';
import { useThemeStore } from '@/stores/theme';

const themeStore = useThemeStore();

defineProps({
  suggestions: {
    type: Array,
    required: true
  }
});

defineEmits([
  'view-profile',
  'connect-suggestion'
]);

const connectAction = {
  label: 'Connect',
  event: 'connect',
  primary: true
};
</script>
