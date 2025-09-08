<template>
  <div class="space-y-6">
    <div v-if="following.length > 0">
      <h2 class="text-base sm:text-lg font-semibold text-gray-900 mb-4">People You Follow</h2>
      
      <div class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2 sm:gap-3 md:gap-4">
        <UserCard
          v-for="followedUser in following"
          :key="followedUser.id"
          :user="followedUser"
          :single-action="unfollowAction"
          @view-profile="$emit('view-profile', $event)"
          @unfollow="$emit('unfollow', $event)"
        />
      </div>
    </div>
    
    <div v-else class="text-center py-12">
      <svg class="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
      </svg>
      <h3 class="text-lg font-medium text-gray-900 mb-2">Not following anyone yet</h3>
      <p class="text-gray-600">Start following alumni to see their updates in your feed!</p>
    </div>
  </div>
</template>

<script setup>
import UserCard from './UserCard.vue';

defineProps({
  following: {
    type: Array,
    required: true
  }
});

defineEmits([
  'view-profile',
  'unfollow'
]);

const unfollowAction = {
  label: 'Unfollow',
  event: 'unfollow',
  primary: false
};
</script>
