<template>
  <div class="space-y-6">
    <div v-if="connections.length > 0">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-4 space-y-2 sm:space-y-0">
        <h2 :class="themeStore.isDarkMode ? 'text-base sm:text-lg font-semibold text-white' : 'text-base sm:text-lg font-semibold text-gray-900'">My Connections</h2>
        <div class="flex items-center space-x-4">
          <div class="relative w-full sm:w-56">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search connections..."
              :class="themeStore.isDarkMode 
                ? 'w-full pl-7 pr-3 py-1.5 sm:py-2 border border-gray-600 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 text-sm placeholder-gray-400' 
                : 'w-full pl-7 pr-3 py-1.5 sm:py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 text-sm'"
            />
            <svg :class="themeStore.isDarkMode ? 'absolute left-2 top-2 sm:top-2.5 h-3.5 w-3.5 sm:h-4 sm:w-4 text-gray-500' : 'absolute left-2 top-2 sm:top-2.5 h-3.5 w-3.5 sm:h-4 sm:w-4 text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
      </div>
      
      <div class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4 justify-items-center">
        <UserCard
          v-for="connection in filteredConnections"
          :key="connection.id"
          :user="connection"
          :actions="connectionActions"
          @view-profile="$emit('view-profile', $event)"
          @message="$emit('message', $event)"
          @remove="$emit('remove-connection', $event)"
        />
      </div>
    </div>
    
    <div v-else class="text-center py-12">
      <svg :class="themeStore.isDarkMode ? 'w-16 h-16 mx-auto text-gray-500 mb-4' : 'w-16 h-16 mx-auto text-gray-400 mb-4'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
      </svg>
      <h3 :class="themeStore.isDarkMode ? 'text-lg font-medium text-white mb-2' : 'text-lg font-medium text-gray-900 mb-2'">No connections yet</h3>
      <p :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'">Start connecting with fellow alumni to grow your network!</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import UserCard from './UserCard.vue';
import { useThemeStore } from '@/stores/theme';

const themeStore = useThemeStore();

const props = defineProps({
  connections: {
    type: Array,
    required: true
  }
});

defineEmits([
  'view-profile',
  'message',
  'remove-connection'
]);

const searchQuery = ref('');

const connectionActions = [
  { key: 'message', label: 'Message', event: 'message', primary: true },
  { key: 'remove', label: 'Remove', event: 'remove', primary: false, showLoading: true }
];

const filteredConnections = computed(() => {
  if (!searchQuery.value) return props.connections;
  
  const query = searchQuery.value.toLowerCase();
  return props.connections.filter(connection =>
    connection.name.toLowerCase().includes(query) ||
    connection.headline.toLowerCase().includes(query)
  );
});
</script>

<style scoped>
input[type="text"]:focus {
  outline: none;
}
</style>
