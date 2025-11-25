<template>
  <div :class="themeStore.isDarkMode ? 'bg-gray-800 rounded-lg shadow-sm border border-gray-700 p-4 hover:shadow-md transition-shadow w-full max-w-[396px] sm:max-w-none' : 'bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow w-full max-w-[396px] sm:max-w-none'">
    <div class="text-center">
      <!-- Profile Picture -->
      <img
        :src="getProfilePictureUrl(user.profile_picture)"
        :alt="`${getFirstName()} ${getLastName()}`"
        :class="themeStore.isDarkMode ? 'w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 rounded-full mx-auto mb-2 sm:mb-3 object-cover border-2 border-gray-600 cursor-pointer hover:ring-2 hover:ring-green-500 transition-all' : 'w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 rounded-full mx-auto mb-2 sm:mb-3 object-cover border-2 border-gray-100 cursor-pointer hover:ring-2 hover:ring-green-500 transition-all'"
        @click="$emit('view-profile', user)"
        @error="handleImageError"
      />
      
      <!-- User Info -->
      <h3 
        :class="themeStore.isDarkMode ? 'font-semibold text-white text-sm mb-1 cursor-pointer hover:text-green-400 transition-colors' : 'font-semibold text-gray-900 text-sm mb-1 cursor-pointer hover:text-green-600 transition-colors'"
        @click="$emit('view-profile', user)"
      >
        {{ getFirstName() }} {{ getLastName() }}
      </h3>
      <p :class="themeStore.isDarkMode ? 'text-xs text-gray-400 mb-2 line-clamp-2' : 'text-xs text-gray-600 mb-2 line-clamp-2'">{{ user.headline }}</p>
      
      <!-- Address -->
      <p v-if="getAddress()" :class="themeStore.isDarkMode ? 'text-xs text-gray-500 mb-2' : 'text-xs text-gray-500 mb-2'">
        📍 {{ getAddress() }}
      </p>
      
      <!-- Additional Info -->
      <p v-if="user.mutualConnections > 0" :class="themeStore.isDarkMode ? 'text-xs text-gray-500 mb-3' : 'text-xs text-gray-500 mb-3'">
        {{ user.mutualConnections }} mutual connection{{ user.mutualConnections !== 1 ? 's' : '' }}
      </p>
      
      <!-- Action Buttons -->
      <div v-if="actions.length > 0" class="flex space-x-2">
        <button
          v-for="action in actions"
          :key="action.key"
          @click="$emit(action.event, user)"
          :disabled="user.processing"
          :class="[
            'flex-1 px-2 py-1.5 rounded-lg text-xs font-medium transition-colors disabled:opacity-50',
            action.primary 
              ? 'bg-orange-600 text-white hover:bg-orange-700' 
              : (themeStore.isDarkMode 
                ? 'border border-gray-600 text-gray-300 hover:bg-gray-700' 
                : 'border border-gray-300 text-gray-700 hover:bg-gray-50')
          ]"
        >
          <span v-if="user.processing && action.showLoading" class="animate-spin mr-1">⟳</span>
          {{ action.label }}
        </button>
      </div>
      
      <!-- Single Action Button -->
      <button
        v-else-if="singleAction"
        @click="$emit(singleAction.event, user)"
        :disabled="user.processing"
        :class="[
          'w-full px-2 py-1.5 rounded-lg text-xs font-medium transition-colors disabled:opacity-50',
          singleAction.primary 
            ? 'bg-orange-600 text-white hover:bg-orange-700' 
            : (themeStore.isDarkMode 
              ? 'border border-gray-600 text-gray-300 hover:bg-gray-700' 
              : 'border border-gray-300 text-gray-700 hover:bg-gray-50')
        ]"
      >
        <span v-if="user.processing" class="animate-spin mr-1">⟳</span>
        {{ singleAction.label }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useThemeStore } from '@/stores/theme';

const themeStore = useThemeStore();

const props = defineProps({
  user: {
    type: Object,
    required: true
  },
  actions: {
    type: Array,
    default: () => []
  },
  singleAction: {
    type: Object,
    default: null
  }
});

defineEmits([
  'view-profile',
  'connect',
  'message',
  'remove',
  'accept',
  'ignore',
  'follow',
  'unfollow'
]);

const BASE_URL = 'http://localhost:8000';  // Backend server for media files

const getProfilePictureUrl = (profilePicture) => {
  if (!profilePicture) {
    return '/default-avatar.png';
  }
  
  if (profilePicture.startsWith('http')) {
    return profilePicture;
  }
  
  return `${BASE_URL}${profilePicture}`;
};

const getFirstName = () => {
  return props.user.first_name || props.user.name?.split(' ')[0] || '';
};

const getLastName = () => {
  return props.user.last_name || props.user.name?.split(' ').slice(1).join(' ') || '';
};

const getAddress = () => {
  return props.user.present_address || 
         props.user.profile?.location || 
         props.user.profile?.present_address ||
         '';
};

const handleImageError = (event) => {
  // Silently fallback to default avatar to reduce console flooding
  event.target.src = '/default-avatar.png';
};
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.transition-all {
  transition: all 0.2s ease;
}

.transition-colors {
  transition: color 0.2s ease, background-color 0.2s ease, border-color 0.2s ease;
}

.transition-shadow {
  transition: box-shadow 0.2s ease;
}

/* Force mobile compactness */
@media (max-width: 639px) {
  .max-w-xs {
    max-width: 140px !important;
  }
  
  .text-xs {
    font-size: 0.7rem !important;
    line-height: 1rem !important;
  }
  
  .w-10 {
    width: 2.5rem !important;
    height: 2.5rem !important;
  }
  
  .p-1 {
    padding: 0.25rem !important;
  }
  
  .mb-1 {
    margin-bottom: 0.25rem !important;
  }
  
  .px-1 {
    padding-left: 0.25rem !important;
    padding-right: 0.25rem !important;
  }
  
  .py-1 {
    padding-top: 0.25rem !important;
    padding-bottom: 0.25rem !important;
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
