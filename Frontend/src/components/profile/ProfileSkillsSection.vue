<template>
  <div :class="[
    'rounded-lg shadow-lg p-6 transition-colors duration-200',
    themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white'
  ]">
    <SectionPrivacyControl 
      title="Skills"
      :is-own-profile="isOwnProfile"
      :section-visibility="sectionVisibility"
      @add="$emit('add')"
      @visibility-changed="handleVisibilityChange"
    />

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
            
            <!-- Edit/Privacy/Delete buttons for own profile -->
            <div v-if="isOwnProfile" class="flex items-center gap-2">
              <!-- Privacy indicator -->
              <div class="relative">
                <button 
                  @click="toggleSkillVisibilityMenu(skill.id)"
                  :class="getSkillVisibilityButtonClass(skill)"
                  class="p-1 rounded transition-colors"
                  :title="`Privacy: ${getSkillVisibilityDisplay(skill)}`"
                >
                  <EyeIcon v-if="(skill?.visibility || 'connections_only') === 'everyone'" class="w-4 h-4" />
                  <LockClosedIcon v-else-if="(skill?.visibility || 'connections_only') === 'only_me'" class="w-4 h-4" />
                  <ShieldCheckIcon v-else class="w-4 h-4" />
                </button>
                
                <!-- Privacy Menu -->
                <div 
                  v-if="showSkillVisibilityMenu === skill.id" 
                  class="absolute right-0 top-8 z-10 w-48 bg-white border border-gray-200 rounded-lg shadow-lg"
                  @click.stop
                >
                  <div class="p-2">
                    <div class="text-xs font-medium text-gray-500 mb-2">Who can see this?</div>
                    <button
                      v-for="option in visibilityOptions"
                      :key="option.value"
                      @click="changeSkillVisibility(skill.id, option.value)"
                      :class="[
                        'w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors text-left',
                        skill?.visibility === option.value 
                          ? 'bg-blue-50 text-blue-700' 
                          : 'hover:bg-gray-50 text-gray-700'
                      ]"
                    >
                      <component :is="option.icon" class="w-4 h-4 mr-2" />
                      <div>
                        <div class="font-medium">{{ option.label }}</div>
                        <div class="text-xs text-gray-500">{{ option.description }}</div>
                      </div>
                    </button>
                  </div>
                </div>
              </div>
              
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
                class="p-1 text-green-600 hover:text-green-800 rounded transition-colors"
                title="Delete skill"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
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
import { useThemeStore } from '@/stores/theme'
import { 
  EyeIcon,
  UsersIcon, 
  LockClosedIcon,
  ShieldCheckIcon
} from '@heroicons/vue/24/outline'
import SectionPrivacyControl from './SectionPrivacyControl.vue'

const themeStore = useThemeStore()

const props = defineProps({
  skills: Array,
  isOwnProfile: Boolean,
  sectionVisibility: {
    type: String,
    default: 'connections_only'
  }
})

const emit = defineEmits(['add', 'edit', 'delete', 'section-visibility-changed', 'skill-visibility-changed'])

// Privacy state
const showSkillVisibilityMenu = ref(null)

// Privacy options
const visibilityOptions = [
  {
    value: 'everyone',
    label: 'For Everyone',
    description: 'Anyone can see this',
    icon: EyeIcon
  },
  {
    value: 'connections_only',
    label: 'For Connections',
    description: 'Only your connections',
    icon: UsersIcon
  },
  {
    value: 'only_me',
    label: 'Only for Me',
    description: 'Only you can see this',
    icon: LockClosedIcon
  }
]

// Handle section visibility changes
function handleVisibilityChange(newVisibility) {
  emit('section-visibility-changed', 'skills', newVisibility)
}

// Skill privacy methods
function toggleSkillVisibilityMenu(skillId) {
  showSkillVisibilityMenu.value = showSkillVisibilityMenu.value === skillId ? null : skillId
}

function changeSkillVisibility(skillId, newVisibility) {
  console.log('🚀 ProfileSkillsSection: changeSkillVisibility called', { skillId, newVisibility })
  emit('skill-visibility-changed', skillId, newVisibility)
  console.log('📡 Emitted skill-visibility-changed event')
  showSkillVisibilityMenu.value = null
}

function getSkillVisibilityDisplay(skill) {
  const option = visibilityOptions.find(opt => opt.value === skill?.visibility)
  return option?.label || 'For Connections'
}

function getSkillVisibilityButtonClass(skill) {
  const visibility = skill?.visibility || 'connections_only'
  const classes = {
    everyone: 'text-green-600 hover:text-green-700 hover:bg-green-50',
    connections_only: 'text-blue-600 hover:text-blue-700 hover:bg-blue-50',
    only_me: 'text-red-600 hover:text-red-700 hover:bg-red-50'
  }
  return classes[visibility] || classes.connections_only
}

// Debug: Log skills data received by the component
console.log('ProfileSkillsSection - Received skills prop:', props.skills)
console.log('ProfileSkillsSection - Skills array length:', props.skills?.length)
console.log('ProfileSkillsSection - isOwnProfile:', props.isOwnProfile)

// Categorize skills by their category
const categorizedSkills = computed(() => {
  console.log('ProfileSkillsSection - Computing categorized skills with:', props.skills)
  if (!props.skills || props.skills.length === 0) {
    console.log('ProfileSkillsSection - No skills found, returning empty object')
    return {}
  }
  
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
