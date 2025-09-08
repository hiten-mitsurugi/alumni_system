<template>
  <div class="space-y-6">
    <div v-if="followers.length > 0">
      <h2 class="text-base sm:text-lg font-semibold text-gray-900 mb-4">Your Followers</h2>
      
      <div class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2 sm:gap-3 md:gap-4">
        <UserCard
          v-for="follower in followers"
          :key="follower.id"
          :user="follower"
          :single-action="getFollowerAction(follower)"
          @view-profile="$emit('view-profile', $event)"
          @follow="$emit('follow-back', $event)"
          @unfollow="$emit('unfollow', $event)"
        />
      </div>
    </div>
    
    <div v-else class="text-center py-12">
      <svg class="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
      </svg>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No followers yet</h3>
      <p class="text-gray-600">Start creating valuable content to attract followers!</p>
    </div>
  </div>
</template>

<script setup>
import UserCard from './UserCard.vue';

defineProps({
  followers: {
    type: Array,
    required: true
  }
});

defineEmits([
  'view-profile',
  'follow-back',
  'unfollow'
]);

const getFollowerAction = (follower) => {
  if (follower.isFollowing) {
    return {
      label: 'Connected',
      event: 'unfollow',
      primary: false
    };
  } else {
    return {
      label: 'Connect Back',
      event: 'follow',
      primary: true
    };
  }
};
</script>
