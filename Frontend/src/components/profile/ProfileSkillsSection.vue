<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-bold text-gray-900">Skills</h2>
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

    <div v-if="skills && skills.length > 0">
      <!-- Skills Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div 
          v-for="(skill, index) in displayedSkills" 
          :key="index"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <div class="flex items-center space-x-3">
            <div class="flex-shrink-0 w-2 h-2 bg-green-600 rounded-full"></div>
            <span class="text-gray-900 font-medium">{{ skill }}</span>
          </div>
          
          <!-- Remove button for own profile -->
          <button 
            v-if="isOwnProfile"
            @click="$emit('delete', skill)"
            class="text-gray-400 hover:text-red-600 transition-colors opacity-0 group-hover:opacity-100"
            title="Remove skill"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>

      <!-- Show More/Less Button -->
      <div v-if="skills.length > 10" class="text-center pt-4 border-t border-gray-200">
        <button 
          @click="showAllSkills = !showAllSkills"
          class="text-green-600 hover:text-green-700 font-medium"
        >
          {{ showAllSkills ? 'Show less' : `Show all ${skills.length} skills` }}
        </button>
      </div>
    </div>

    <!-- Skills Categories (if we have categorized skills) -->
    <div v-else-if="categorizedSkills && Object.keys(categorizedSkills).length > 0" class="space-y-6">
      <div v-for="(skillList, category) in categorizedSkills" :key="category" class="space-y-3">
        <h3 class="text-lg font-semibold text-gray-900 capitalize">{{ category }}</h3>
        <div class="flex flex-wrap gap-2">
          <span 
            v-for="skill in skillList" 
            :key="skill"
            class="relative group px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full hover:bg-green-200 transition-colors"
          >
            {{ skill }}
            <button 
              v-if="isOwnProfile"
              @click="$emit('delete', skill)"
              class="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white rounded-full text-xs opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
              title="Remove skill"
            >
              ×
            </button>
          </span>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="isOwnProfile" class="text-gray-500 text-center py-8">
      <div class="mb-4">
        <svg class="w-12 h-12 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
        </svg>
      </div>
      <p class="mb-3">Add skills to highlight your expertise and help others find you.</p>
      <button 
        @click="$emit('add')"
        class="text-green-600 hover:text-green-700 font-medium"
      >
        Add Skills
      </button>
    </div>

    <div v-else class="text-gray-500 text-center py-4">
      <p>No skills information available.</p>
    </div>

    <!-- Top Skills Section (for other users' profiles) -->
    <div v-if="!isOwnProfile && skills && skills.length > 0" class="mt-6 pt-6 border-t border-gray-200">
      <div class="flex items-center space-x-2 mb-3">
        <svg class="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
        <h3 class="text-lg font-semibold text-gray-900">Top Skills</h3>
      </div>
      <div class="flex flex-wrap gap-2">
        <span 
          v-for="skill in skills.slice(0, 6)" 
          :key="skill"
          class="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
        >
          {{ skill }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  skills: Array,
  isOwnProfile: Boolean
})

const emit = defineEmits(['add', 'edit', 'delete'])

const showAllSkills = ref(false)

const displayedSkills = computed(() => {
  if (!props.skills) return []
  
  // Show first 10 or all if expanded
  return showAllSkills.value ? props.skills : props.skills.slice(0, 10)
})

// For future enhancement - categorized skills
const categorizedSkills = computed(() => {
  // This could be enhanced to categorize skills by type
  // For now, returning null to use simple grid layout
  return null
})
</script>

<style scoped>
.group:hover .opacity-0 {
  opacity: 1;
}
</style>
