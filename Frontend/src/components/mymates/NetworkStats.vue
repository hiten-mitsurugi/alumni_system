<template>
  <div :class="themeStore.isDarkMode ? 'flex items-center space-x-6 text-sm text-gray-300' : 'flex items-center space-x-6 text-sm text-gray-600'">
    <div class="text-center">
      <div class="text-lg font-semibold text-orange-600">{{ stats.connectionsCount }}</div>
      <div>Connections</div>
    </div>
    <div class="text-center">
      <div class="text-lg font-semibold text-orange-600">{{ stats.followersCount }}</div>
      <div>Followers</div>
    </div>
    <div class="text-center">
      <div class="text-lg font-semibold text-orange-600">{{ stats.followingCount }}</div>
      <div>Following</div>
    </div>
  </div>
</template>

<script setup>
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

defineProps({
  stats: {
    type: Object,
    required: true,
    default: () => ({
      connectionsCount: 0,
      followersCount: 0,
      followingCount: 0
    })
  }
});
</script>

<style scoped>
.text-green-600 {
  color: #16a34a;
}
</style>
