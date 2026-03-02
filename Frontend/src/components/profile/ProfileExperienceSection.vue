<template>
  <div :class="[
    'rounded-lg shadow-lg p-6 transition-colors duration-200',
    themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white'
  ]">
    <SectionPrivacyControl 
      title="Work History"
      :is-own-profile="isOwnProfile"
      :section-visibility="sectionVisibility"
      @add="$emit('add')"
      @visibility-changed="handleVisibilityChange"
    />

    <div v-if="workHistories && workHistories.length > 0" class="space-y-6">
      <div 
        v-for="(work, index) in displayedWork" 
        :key="work.id"
        class="relative border-l-2 border-green-100 pl-6 pb-6"
        :class="{ 'border-b border-gray-200': index < displayedWork.length - 1 }"
      >
        <!-- Timeline dot -->
        <div class="absolute -left-2 top-0 w-4 h-4 bg-green-600 rounded-full border-2 border-white"></div>
        
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ work.occupation }}
            </h3>
            <p class="text-gray-700 font-medium">
              {{ work.employing_agency }}
            </p>
            <p class="text-sm text-gray-500 mt-1">
              {{ formatWorkDuration(work) }}
            </p>
            
            <!-- Classification -->
            <p v-if="work.classification" class="text-sm text-gray-600 mt-1">
              {{ formatClassification(work.classification) }}
            </p>
            
            <!-- Length of Service -->
            <p v-if="work.length_of_service" class="text-sm text-gray-600 mt-1">
              Duration: {{ work.length_of_service }}
            </p>
            
            <!-- Description -->
            <div v-if="work.description || work.responsibilities" class="mt-3">
              <div 
                :class="{ 'line-clamp-4': !work.showFullDescription && getDescription(work).length > 200 }"
                class="text-gray-700 text-sm whitespace-pre-wrap"
              >
                {{ getDescription(work) }}
              </div>
              
              <button 
                v-if="getDescription(work).length > 200"
                @click="toggleDescription(work)"
                class="text-green-600 hover:text-green-700 text-sm font-medium mt-1"
              >
                {{ work.showFullDescription ? 'See less' : 'See more' }}
              </button>
            </div>

            <!-- Skills -->
            <div v-if="work.skills && work.skills.length > 0" class="mt-3">
              <h4 class="text-sm font-medium text-gray-900 mb-2">Skills:</h4>
              <div class="flex flex-wrap gap-2">
                <span 
                  v-for="skill in work.skills" 
                  :key="skill"
                  class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full"
                >
                  {{ skill }}
                </span>
              </div>
            </div>
          </div>

          <!-- Actions for own profile -->
          <div v-if="isOwnProfile" class="flex space-x-2 ml-4">
            <!-- Privacy indicator -->
            <div class="relative">
              <button 
                @click="toggleExperienceVisibilityMenu(work.id)"
                :class="getExperienceVisibilityButtonClass(work)"
                class="p-1 rounded transition-colors"
                :title="`Privacy: ${getExperienceVisibilityDisplay(work)}`"
              >
                <EyeIcon v-if="(work?.visibility || 'connections_only') === 'everyone'" class="w-4 h-4" />
                <LockClosedIcon v-else-if="(work?.visibility || 'connections_only') === 'only_me'" class="w-4 h-4" />
                <ShieldCheckIcon v-else class="w-4 h-4" />
              </button>
              
              <!-- Privacy Menu -->
              <div 
                v-if="showExperienceVisibilityMenu === work.id" 
                class="absolute right-0 top-8 z-10 w-48 bg-white border border-gray-200 rounded-lg shadow-lg"
                @click.stop
              >
                <div class="p-2">
                  <div class="text-xs font-medium text-gray-500 mb-2">Who can see this?</div>
                  <button
                    v-for="option in visibilityOptions"
                    :key="option.value"
                    @click="changeExperienceVisibility(work.id, option.value)"
                    :class="[
                      'w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors text-left',
                      work?.visibility === option.value 
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
              @click="$emit('edit', work)"
              class="text-gray-500 hover:text-green-600 transition-colors"
              title="Edit"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
              </svg>
            </button>
            <button 
              @click="$emit('delete', work.id)"
              class="text-gray-500 hover:text-red-600 transition-colors"
              title="Delete"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Show More/Less Button -->
      <div v-if="workHistories.length > 3" class="text-center pt-4 border-t border-gray-200">
        <button 
          @click="showAllWork = !showAllWork"
          class="text-green-600 hover:text-green-700 font-medium"
        >
          {{ showAllWork ? 'Show less' : `Show all ${workHistories.length} experiences` }}
        </button>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="isOwnProfile" class="text-gray-500 text-center py-8">
      <div class="mb-4">
        <svg class="w-12 h-12 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V8a2 2 0 012-2V6"></path>
        </svg>
      </div>
      <p class="mb-3">Add your work experience to showcase your professional journey.</p>
      <button 
        @click="$emit('add')"
        class="text-green-600 hover:text-green-700 font-medium"
      >
        Add Work History
      </button>
    </div>

    <div v-else class="text-gray-500 text-center py-4">
      <p>No work experience information available.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
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
  workHistories: Array,
  isOwnProfile: Boolean,
  sectionVisibility: {
    type: String,
    default: 'connections_only'
  }
})

const emit = defineEmits(['add', 'edit', 'delete', 'section-visibility-changed', 'experience-visibility-changed'])

console.log('🔧 ProfileExperienceSection: Component loaded with props', {
  workHistoriesLength: props.workHistories?.length || 0,
  workHistories: props.workHistories,
  isOwnProfile: props.isOwnProfile
})

// Watch for prop changes
watch(() => props.workHistories, (newValue, oldValue) => {
  console.log('👁️ ProfileExperienceSection: workHistories prop changed', {
    old: oldValue,
    new: newValue,
    newLength: newValue?.length || 0
  })
}, { deep: true })

// Privacy state
const showExperienceVisibilityMenu = ref(null)

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
  emit('section-visibility-changed', 'experience', newVisibility)
}

// Experience privacy methods
function toggleExperienceVisibilityMenu(experienceId) {
  showExperienceVisibilityMenu.value = showExperienceVisibilityMenu.value === experienceId ? null : experienceId
}

function changeExperienceVisibility(experienceId, newVisibility) {
  emit('experience-visibility-changed', experienceId, newVisibility)
  showExperienceVisibilityMenu.value = null
}

function getExperienceVisibilityDisplay(experience) {
  const option = visibilityOptions.find(opt => opt.value === experience?.visibility)
  return option?.label || 'For Connections'
}

function getExperienceVisibilityButtonClass(experience) {
  const visibility = experience?.visibility || 'connections_only'
  const classes = {
    everyone: 'text-green-600 hover:text-green-700 hover:bg-green-50',
    connections_only: 'text-blue-600 hover:text-blue-700 hover:bg-blue-50',
    only_me: 'text-red-600 hover:text-red-700 hover:bg-red-50'
  }
  return classes[visibility] || classes.connections_only
}

const showAllWork = ref(false)

const displayedWork = computed(() => {
  console.log('🎯 ProfileExperienceSection: Computing displayedWork', {
    workHistories: props.workHistories,
    length: props.workHistories?.length || 0,
    showAllWork: showAllWork.value
  })
  
  if (!props.workHistories) {
    console.log('⚠️ ProfileExperienceSection: No workHistories prop')
    return []
  }
  
  // Sort by start date (most recent first)
  const sorted = [...props.workHistories].sort((a, b) => {
    const dateA = new Date(a.start_date || a.from_date)
    const dateB = new Date(b.start_date || b.from_date)
    return dateB - dateA
  })
  
  console.log('📊 ProfileExperienceSection: Sorted work histories', sorted)
  
  // Show first 3 or all if expanded
  const result = showAllWork.value ? sorted : sorted.slice(0, 3)
  console.log('✅ ProfileExperienceSection: Returning displayed work', result)
  return result
})

const formatWorkDuration = (work) => {
  const formatDate = (date) => {
    return new Date(date).toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short' 
    })
  }
  
  const startDate = work.start_date || work.from_date
  const endDate = work.end_date || work.to_date
  const isCurrent = work.is_current_job || work.currently_working
  
  if (!startDate) return 'Date not specified'
  
  const start = formatDate(startDate)
  const end = isCurrent ? 'Present' : (endDate ? formatDate(endDate) : 'Present')
  
  return `${start} - ${end}`
}

const formatClassification = (type) => {
  const typeMap = {
    'government': 'Government',
    'private': 'Private',
    'ngo': 'NGO',
    'freelance': 'Freelance',
    'business_owner': 'Business Owner'
  }
  return typeMap[type] || type
}

const getDescription = (work) => {
  return work.description || work.responsibilities || ''
}

const toggleDescription = (work) => {
  work.showFullDescription = !work.showFullDescription
}
</script>

<style scoped>
.line-clamp-4 {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
