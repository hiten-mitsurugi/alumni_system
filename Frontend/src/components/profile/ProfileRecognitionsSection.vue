<template>
  <div :class="[
    'rounded-lg shadow-lg p-6 transition-colors duration-200',
    themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white'
  ]">
    <SectionPrivacyControl 
      title="Non-Academic Recognition"
      :is-own-profile="isOwnProfile"
      :section-visibility="sectionVisibility"
      @add="$emit('add')"
      @visibility-changed="handleVisibilityChange"
    />

    <div v-if="recognitions && recognitions.length > 0" class="space-y-4">
      <div 
        v-for="recognition in recognitions" 
        :key="recognition.id"
        class="group border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all duration-200"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0 w-3 h-3 bg-yellow-600 rounded-full"></div>
              <h3 :class="[
                'text-lg font-semibold',
                themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
              ]">{{ recognition.title }}</h3>
            </div>
            
            <div class="ml-6 mt-2 space-y-2">
              <div v-if="recognition.awarded_by" class="flex items-center text-sm">
                <span :class="[
                  'font-medium mr-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Awarded by:</span>
                <span :class="[
                  themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                ]">{{ recognition.awarded_by }}</span>
              </div>
              
              <div v-if="recognition.category" class="flex items-center text-sm">
                <span :class="[
                  'font-medium mr-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Category:</span>
                <span :class="[
                  'px-2 py-1 rounded-full text-xs',
                  getCategoryClass(recognition.category)
                ]">{{ formatCategory(recognition.category) }}</span>
              </div>
              
              <div v-if="recognition.date_awarded" class="flex items-center text-sm">
                <span :class="[
                  'font-medium mr-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Date Awarded:</span>
                <span :class="[
                  themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                ]">{{ formatDate(recognition.date_awarded) }}</span>
              </div>
              
              <div v-if="recognition.level" class="flex items-center text-sm">
                <span :class="[
                  'font-medium mr-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Level:</span>
                <span :class="[
                  'px-2 py-1 rounded-full text-xs',
                  getLevelClass(recognition.level)
                ]">{{ formatLevel(recognition.level) }}</span>
              </div>
              
              <div v-if="recognition.description" class="text-sm">
                <span :class="[
                  'font-medium',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Description:</span>
                <p :class="[
                  'mt-1',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
                ]">{{ recognition.description }}</p>
              </div>
            </div>
          </div>
          
          <!-- Edit/Delete buttons for own profile -->
          <div v-if="isOwnProfile" class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button 
              @click="$emit('edit', recognition)"
              class="p-2 text-gray-400 hover:text-blue-600 transition-colors"
              title="Edit recognition"
            >
              <PencilIcon class="w-4 h-4" />
            </button>
            <button 
              @click="$emit('delete', recognition.id)"
              class="p-2 text-gray-400 hover:text-red-600 transition-colors"
              title="Delete recognition"
            >
              <TrashIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-8">
      <div class="mx-auto w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mb-4">
        <svg class="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
        </svg>
      </div>
      <p :class="[
        'text-lg font-medium',
        themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-900'
      ]">No non-academic recognitions</p>
      <p :class="[
        'text-sm mt-2',
        themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'
      ]">{{ isOwnProfile ? 'Add your non-academic recognitions to showcase your achievements outside academia' : 'This user hasn\'t added any non-academic recognitions yet' }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'
import SectionPrivacyControl from '@/components/profile/SectionPrivacyControl.vue'

defineProps({
  recognitions: {
    type: Array,
    default: () => []
  },
  isOwnProfile: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['add', 'edit', 'delete', 'visibility-changed'])

const themeStore = useThemeStore()
const sectionVisibility = ref('connections_only')

const handleVisibilityChange = (visibility) => {
  sectionVisibility.value = visibility
  emit('visibility-changed', { section: 'recognitions', visibility })
}

const getCategoryClass = (category) => {
  const classes = {
    'community_service': 'bg-green-100 text-green-800',
    'leadership': 'bg-blue-100 text-blue-800',
    'volunteer': 'bg-purple-100 text-purple-800',
    'sports': 'bg-red-100 text-red-800',
    'arts': 'bg-pink-100 text-pink-800',
    'other': 'bg-gray-100 text-gray-800'
  }
  return classes[category] || 'bg-gray-100 text-gray-800'
}

const formatCategory = (category) => {
  const categories = {
    'community_service': 'Community Service',
    'leadership': 'Leadership',
    'volunteer': 'Volunteer Work',
    'sports': 'Sports',
    'arts': 'Arts & Culture',
    'other': 'Other'
  }
  return categories[category] || category
}

const getLevelClass = (level) => {
  const classes = {
    'local': 'bg-blue-100 text-blue-800',
    'regional': 'bg-green-100 text-green-800',
    'national': 'bg-yellow-100 text-yellow-800',
    'international': 'bg-purple-100 text-purple-800'
  }
  return classes[level] || 'bg-gray-100 text-gray-800'
}

const formatLevel = (level) => {
  const levels = {
    'local': 'Local',
    'regional': 'Regional', 
    'national': 'National',
    'international': 'International'
  }
  return levels[level] || level
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long',
    day: 'numeric'
  })
}
</script>