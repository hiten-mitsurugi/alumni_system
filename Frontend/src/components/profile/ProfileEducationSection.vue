<template>
  <div :class="[
    'rounded-lg shadow-lg p-6 transition-colors duration-200',
    themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white'
  ]">
    <SectionPrivacyControl 
      title="Education"
      :is-own-profile="isOwnProfile"
      :section-visibility="sectionVisibility"
      @add="$emit('add')"
      @visibility-changed="handleVisibilityChange"
    />


    <div class="space-y-4">
      <!-- ALWAYS show user profile education (Bachelor's degree from registration) -->
      <div v-if="user && (user.program || user.year_graduated)" :class="[
        'flex items-center justify-between py-3 border-b',
        themeStore.isDarkMode ? 'border-gray-600' : 'border-gray-100'
      ]">
        <div class="flex-1">
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
              </svg>
            </div>
            <div>
              <p :class="[
                'font-medium',
                themeStore.isDarkMode ? 'text-gray-100' : 'text-gray-900'
              ]">{{ user.program || 'Program not specified' }}</p>
              <p :class="[
                'text-sm',
                themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
              ]">Caraga State University • {{ user.year_graduated || 'Year not specified' }}</p>
            </div>
          </div>
        </div>
        <!-- Actions for own profile -->
        <div v-if="isOwnProfile" class="flex space-x-2">
          <button 
            @click="$emit('edit-profile')"
            class="text-gray-400 hover:text-blue-600 transition-colors"
            title="Edit Profile"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
          </button>
        </div>
      </div>

      <!-- Show additional education records (Master's, PhD, etc.) -->
      <div v-if="education && education.length > 0">
        <div 
          v-for="edu in education" 
          :key="edu.id"
          :class="[
            'flex items-center justify-between py-3 border-b last:border-b-0',
            themeStore.isDarkMode ? 'border-gray-600' : 'border-gray-100'
          ]"
        >
          <div class="flex-1">
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                </svg>
              </div>
              <div>
                <p class="font-medium text-gray-900">{{ formatDegreeTitle(edu) }}</p>
                <p class="text-sm text-gray-500">{{ edu.institution || 'Institution not specified' }} • {{ formatDateRange(edu.start_date, edu.end_date, edu.is_current) }}</p>
              </div>
            </div>
          </div>
          <!-- Actions for own profile -->
          <div v-if="isOwnProfile" class="flex space-x-2">
            <!-- Privacy indicator -->
            <div class="relative">
              <button 
                @click="toggleEducationVisibilityMenu(edu.id)"
                :class="getEducationVisibilityButtonClass(edu)"
                class="p-1 rounded transition-colors"
                :title="`Privacy: ${getEducationVisibilityDisplay(edu)}`"
              >
                <EyeIcon v-if="(edu?.visibility || 'connections_only') === 'everyone'" class="w-4 h-4" />
                <LockClosedIcon v-else-if="(edu?.visibility || 'connections_only') === 'only_me'" class="w-4 h-4" />
                <ShieldCheckIcon v-else class="w-4 h-4" />
              </button>
              
              <!-- Privacy Menu -->
              <div 
                v-if="showEducationVisibilityMenu === edu.id" 
                class="absolute right-0 top-8 z-10 w-48 bg-white border border-gray-200 rounded-lg shadow-lg"
                @click.stop
              >
                <div class="p-2">
                  <div class="text-xs font-medium text-gray-500 mb-2">Who can see this?</div>
                  <button
                    v-for="option in visibilityOptions"
                    :key="option.value"
                    @click="changeEducationVisibility(edu.id, option.value)"
                    :class="[
                      'w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors text-left',
                      edu?.visibility === option.value 
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
              @click="$emit('edit', edu)"
              class="text-gray-400 hover:text-green-600 transition-colors"
              title="Edit"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
              </svg>
            </button>
            <button 
              @click="$emit('delete', edu.id)"
              class="text-gray-400 hover:text-red-600 transition-colors"
              title="Delete"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Help text for adding more education -->
    <div v-if="isOwnProfile && (!education || education.length === 0)" :class="[
      'mt-4 p-3 rounded-md',
      themeStore.isDarkMode ? 'bg-gray-700' : 'bg-gray-50'
    ]">
      <p :class="[
        'text-sm',
        themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
      ]">Have additional degrees? Click "Add" to include Master's, PhD, or other qualifications.</p>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
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
  education: Array,
  profile: Object,
  user: Object,  // Add user prop to access program and year_graduated
  isOwnProfile: Boolean,
  sectionVisibility: {
    type: String,
    default: 'connections_only'
  }
})

const emit = defineEmits(['add', 'edit', 'edit-profile', 'delete', 'section-visibility-changed', 'education-visibility-changed'])

// Privacy state
const showEducationVisibilityMenu = ref(null)

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
  emit('section-visibility-changed', 'education', newVisibility)
}

// Education privacy methods
function toggleEducationVisibilityMenu(educationId) {
  showEducationVisibilityMenu.value = showEducationVisibilityMenu.value === educationId ? null : educationId
}

function changeEducationVisibility(educationId, newVisibility) {
  console.log('🚀 ProfileEducationSection: changeEducationVisibility called', { educationId, newVisibility })
  emit('education-visibility-changed', educationId, newVisibility)
  console.log('📡 Emitted education-visibility-changed event')
  showEducationVisibilityMenu.value = null
}

function getEducationVisibilityDisplay(education) {
  const option = visibilityOptions.find(opt => opt.value === education?.visibility)
  return option?.label || 'For Connections'
}

function getEducationVisibilityButtonClass(education) {
  const visibility = education?.visibility || 'connections_only'
  const classes = {
    everyone: 'text-green-600 hover:text-green-700 hover:bg-green-50',
    connections_only: 'text-blue-600 hover:text-blue-700 hover:bg-blue-50',
    only_me: 'text-red-600 hover:text-red-700 hover:bg-red-50'
  }
  return classes[visibility] || classes.connections_only
}

// Debug logging - remove duplicate logs
console.log('ProfileEducationSection - Education prop:', props.education)
console.log('ProfileEducationSection - User prop:', props.user)
if (props.user) {
  console.log('ProfileEducationSection - User program:', props.user.program)
  console.log('ProfileEducationSection - User year_graduated:', props.user.year_graduated)
  console.log('ProfileEducationSection - User keys:', Object.keys(props.user))
} else {
  console.log('ProfileEducationSection - User prop is null/undefined')
}

// Watch for changes in education prop
import { watch } from 'vue'
watch(() => props.education, (newEducation) => {
  console.log('Education prop changed:', newEducation)
}, { deep: true })

// Utility function to format degree title
const formatDegreeTitle = (edu) => {
  const degreeTypeLabels = {
    'high_school': 'High School',
    'vocational': 'Vocational',
    'associate': 'Associate Degree',
    'bachelor': 'Bachelor\'s Degree',
    'master': 'Master\'s Degree',
    'doctoral': 'Doctoral Degree',
    'certificate': 'Certificate',
    'diploma': 'Diploma',
    'other': 'Other'
  }
  
  const degreeLabel = degreeTypeLabels[edu.degree_type] || edu.degree_type || 'Degree'
  const fieldOfStudy = edu.field_of_study || 'Field not specified'
  
  return `${degreeLabel} - ${fieldOfStudy}`
}

// Utility function to format date range
const formatDateRange = (startDate, endDate, isCurrent) => {
  const formatDate = (dateStr) => {
    if (!dateStr) return null
    const date = new Date(dateStr)
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return `${months[date.getMonth()]} ${date.getFullYear()}`
  }
  
  const start = formatDate(startDate)
  const end = isCurrent ? 'Present' : formatDate(endDate)
  
  if (start && end) {
    return `${start} - ${end}`
  } else if (end && end !== 'Present') {
    return end
  } else if (start) {
    return start
  }
  return 'Date not specified'
}
</script>
