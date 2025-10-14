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

    <!-- Skills organized by category -->
    <div v-if="categorizedSkills && Object.keys(categorizedSkills).length > 0" class="space-y-0">
      <div v-for="(skillList, category) in categorizedSkills" :key="category" class="space-y-0">
        <div class="flex items-center py-3 border-b border-gray-100">
          <h3 class="text-lg font-semibold text-gray-900">{{ formatCategoryName(category) }}</h3>
        </div>
        <div class="space-y-0">
          <div 
            v-for="skill in skillList" 
            :key="skill.id"
            class="group flex items-center justify-between py-3 hover:bg-gray-50 rounded-lg px-2 -mx-2"
          >
            <div class="flex items-center mr-4">
              <div class="flex-shrink-0 w-2 h-2 bg-green-600 rounded-full mr-4"></div>
              <div class="flex-grow min-w-0">
                <div class="flex items-center space-x-2">
                  <span class="text-gray-900 font-medium">{{ skill.name }}</span>
                  <span v-if="skill.proficiency" class="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
                    {{ formatProficiency(skill.proficiency) }}
                  </span>
                </div>
                <p v-if="skill.description" class="text-sm text-gray-600 mt-1">
                  {{ skill.description }}
                </p>
              </div>
            </div>
            
            <!-- Edit/Delete buttons for own profile -->
            <div v-if="isOwnProfile" class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <button 
                @click="$emit('edit', skill)"
                class="p-1 text-gray-500 hover:text-green-600 rounded transition-colors"
                title="Edit skill"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                </svg>
              </button>
              <button 
                @click="$emit('delete', skill.id)"
                class="p-1 text-gray-500 hover:text-red-600 rounded transition-colors"
                title="Remove skill"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>
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
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  skills: Array,
  isOwnProfile: Boolean
})

const emit = defineEmits(['add', 'edit', 'delete'])

// Categorize skills by their category
const categorizedSkills = computed(() => {
  if (!props.skills || props.skills.length === 0) return {}
  
  const categories = {}
  props.skills.forEach(skill => {
    const category = skill.category || 'other'
    if (!categories[category]) {
      categories[category] = []
    }
    categories[category].push(skill)
  })
  
  return categories
})

// Format category names for display
const formatCategoryName = (category) => {
  const categoryMap = {
    'technical': 'Technical Skills',
    'soft_skills': 'Soft Skills',
    'languages': 'Languages',
    'tools': 'Tools & Software',
    'other': 'Other Skills'
  }
  return categoryMap[category] || category
}

// Format proficiency levels
const formatProficiency = (proficiency) => {
  const proficiencyMap = {
    'beginner': 'Beginner',
    'intermediate': 'Intermediate',
    'advanced': 'Advanced',
    'expert': 'Expert'
  }
  return proficiencyMap[proficiency] || proficiency
}
</script>

<style scoped>
.group:hover .opacity-0 {
  opacity: 1;
}
</style>
