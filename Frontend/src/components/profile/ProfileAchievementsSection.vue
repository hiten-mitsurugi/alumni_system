<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-bold text-gray-900">Achievements</h2>
      <button 
        v-if="isOwnProfile" 
        @click="$emit('add')"
        class="flex items-center space-x-1 text-green-600 hover:text-green-700 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
        </svg>
        <span>Add</span>
      </button>
    </div>

    <div v-if="achievements && achievements.length > 0" class="space-y-6">
      <!-- Featured Achievements First -->
      <div v-if="featuredAchievements.length > 0" class="space-y-4">
        <h3 class="text-lg font-semibold text-gray-900 flex items-center space-x-2">
          <svg class="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
          </svg>
          <span>Featured</span>
        </h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div 
            v-for="achievement in featuredAchievements" 
            :key="achievement.id"
            class="border border-yellow-200 bg-yellow-50 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <AchievementCard 
              :achievement="achievement" 
              :is-own-profile="isOwnProfile"
              :is-featured="true"
              @edit="$emit('edit', achievement)"
              @delete="$emit('delete', achievement.id)"
            />
          </div>
        </div>
      </div>

      <!-- Regular Achievements -->
      <div v-if="regularAchievements.length > 0" class="space-y-4">
        <h3 v-if="featuredAchievements.length > 0" class="text-lg font-semibold text-gray-900">
          All Achievements
        </h3>
        
        <div class="space-y-4">
          <div 
            v-for="achievement in displayedAchievements" 
            :key="achievement.id"
            class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <AchievementCard 
              :achievement="achievement" 
              :is-own-profile="isOwnProfile"
              @edit="$emit('edit', achievement)"
              @delete="$emit('delete', achievement.id)"
            />
          </div>
        </div>

        <!-- Show More/Less Button -->
        <div v-if="regularAchievements.length > 5" class="text-center pt-4 border-t border-gray-200">
          <button 
            @click="showAllAchievements = !showAllAchievements"
            class="text-green-600 hover:text-green-700 font-medium"
          >
            {{ showAllAchievements ? 'Show less' : `Show all ${regularAchievements.length} achievements` }}
          </button>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="isOwnProfile" class="text-gray-500 text-center py-8">
      <div class="mb-4">
        <svg class="w-12 h-12 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"></path>
        </svg>
      </div>
      <p class="mb-3">Add your achievements to showcase your accomplishments and recognition.</p>
      <button 
        @click="$emit('add')"
        class="text-green-600 hover:text-green-700 font-medium"
      >
        Add Achievement
      </button>
    </div>

    <div v-else class="text-gray-500 text-center py-4">
      <p>No achievements information available.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import AchievementCard from './AchievementCard.vue'

const props = defineProps({
  achievements: Array,
  isOwnProfile: Boolean
})

const emit = defineEmits(['add', 'edit', 'delete'])

const showAllAchievements = ref(false)

const featuredAchievements = computed(() => {
  if (!props.achievements) return []
  return props.achievements.filter(achievement => achievement.is_featured)
})

const regularAchievements = computed(() => {
  if (!props.achievements) return []
  return props.achievements
    .filter(achievement => !achievement.is_featured)
    .sort((a, b) => new Date(b.date_achieved) - new Date(a.date_achieved))
})

const displayedAchievements = computed(() => {
  return showAllAchievements.value ? regularAchievements.value : regularAchievements.value.slice(0, 5)
})
</script>

<style scoped>
/* Additional styles if needed */
</style>
