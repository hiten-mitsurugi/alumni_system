<template>
  <div :class="[
    'rounded-lg shadow-lg p-6 transition-colors duration-200',
    themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white'
  ]">
    <SectionPrivacyControl 
      title="Achievements"
      :is-own-profile="isOwnProfile"
      :section-visibility="sectionVisibility"
      @add="$emit('add')"
      @visibility-changed="handleVisibilityChange"
    />

    <div v-if="achievements && achievements.length > 0" class="space-y-8">
      <!-- Featured Achievements First -->
      <div v-if="featuredAchievements.length > 0" class="space-y-6">
        <div class="flex items-center space-x-3">
          <div class="flex items-center justify-center w-8 h-8 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full">
            <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900">Featured Achievements</h3>
          <div class="flex-1 h-px bg-gradient-to-r from-yellow-300 to-transparent"></div>
        </div>
        
        <div class="space-y-6">
          <AchievementCard 
            v-for="achievement in featuredAchievements" 
            :key="achievement.id"
            :achievement="achievement" 
            :is-own-profile="isOwnProfile"
            :is-featured="true"
            @edit="$emit('edit', achievement)"
            @delete="$emit('delete', achievement.id)"
            @toggle-visibility="handleAchievementVisibilityChange"
          />
        </div>
      </div>

      <!-- Regular Achievements -->
      <div v-if="regularAchievements.length > 0" class="space-y-6">
        <div v-if="featuredAchievements.length > 0" class="flex items-center space-x-3">
          <div class="flex items-center justify-center w-8 h-8 bg-gradient-to-r from-green-400 to-blue-500 rounded-full">
            <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M5 16L3 21l5.25-1.875L12 21l3.75-1.875L21 21l-2-5 1-11H4l1 11zm7-11a2 2 0 100 4 2 2 0 000-4z"/>
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900">All Achievements</h3>
          <div class="flex-1 h-px bg-gradient-to-r from-green-300 to-transparent"></div>
        </div>
        
        <div class="space-y-6">
          <AchievementCard 
            v-for="achievement in displayedAchievements" 
            :key="achievement.id"
            :achievement="achievement" 
            :is-own-profile="isOwnProfile"
            @edit="$emit('edit', achievement)"
            @delete="$emit('delete', achievement.id)"
            @toggle-visibility="handleAchievementVisibilityChange"
          />
        </div>

        <!-- Show More/Less Button -->
        <div v-if="regularAchievements.length > 5" class="text-center pt-6">
          <button 
            @click="showAllAchievements = !showAllAchievements"
            class="inline-flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-full hover:from-green-600 hover:to-blue-600 transition-all duration-300 transform hover:scale-105 shadow-lg"
          >
            <span>{{ showAllAchievements ? 'Show Less' : `Show All ${regularAchievements.length} Achievements` }}</span>
            <svg 
              class="w-4 h-4 transition-transform duration-300" 
              :class="{ 'rotate-180': showAllAchievements }"
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="isOwnProfile" class="text-gray-500 text-center py-8">
      <div class="mb-4">
        <div class="w-16 h-16 mx-auto bg-gray-100 rounded-full flex items-center justify-center">
          <svg class="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
          </svg>
        </div>
      </div>
      <h3 :class="[
        'text-lg font-medium mb-2',
        themeStore.isDarkMode ? 'text-gray-100' : 'text-gray-900'
      ]">No achievements yet</h3>
      <p :class="[
        'mb-4',
        themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
      ]">Showcase your accomplishments, certifications, awards, and recognition.</p>
      <button 
        @click="$emit('add')"
        class="inline-flex items-center px-4 py-2 text-green-600 hover:text-green-700"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
        </svg>
        Add Your First Achievement
      </button>
    </div>

    <div v-else :class="[
      'text-center py-4',
      themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
    ]">
      <p>No achievements information available.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import AchievementCard from './AchievementCard.vue'
import SectionPrivacyControl from './SectionPrivacyControl.vue'

const themeStore = useThemeStore()

const props = defineProps({
  achievements: Array,
  isOwnProfile: Boolean,
  sectionVisibility: {
    type: String,
    default: 'connections_only'
  }
})

const emit = defineEmits(['add', 'edit', 'delete', 'section-visibility-changed', 'toggle-visibility'])

// Handle section visibility changes
function handleVisibilityChange(newVisibility) {
  emit('section-visibility-changed', 'achievements', newVisibility)
}

// Handle individual achievement visibility changes
function handleAchievementVisibilityChange(achievementId, newVisibility) {
  console.log('🎯 ProfileAchievementsSection: forwarding visibility change', { achievementId, newVisibility })
  emit('toggle-visibility', achievementId, newVisibility)
}

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
