<template>
  <div :class="[
    'rounded-lg shadow-lg p-6 transition-colors duration-200',
    themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white'
  ]">
    <SectionPrivacyControl 
      title="Trainings"
      :is-own-profile="isOwnProfile"
      :section-visibility="sectionVisibility"
      @add="$emit('add')"
      @visibility-changed="handleVisibilityChange"
    />

    <div v-if="trainings && trainings.length > 0" class="space-y-4">
      <div 
        v-for="training in trainings" 
        :key="training.id"
        class="group border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all duration-200"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0 w-3 h-3 bg-indigo-600 rounded-full"></div>
              <h3 :class="[
                'text-lg font-semibold',
                themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
              ]">{{ training.training_title }}</h3>
            </div>
            
            <div class="ml-6 mt-2 space-y-2">
              <div v-if="training.conducted_by" class="flex items-center text-sm">
                <span :class="[
                  'font-medium mr-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Conducted by:</span>
                <span :class="[
                  themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                ]">{{ training.conducted_by }}</span>
              </div>
              
              <div v-if="training.training_type" class="flex items-center text-sm">
                <span :class="[
                  'font-medium mr-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Type:</span>
                <span :class="[
                  'px-2 py-1 rounded-full text-xs',
                  getTrainingTypeClass(training.training_type)
                ]">{{ formatTrainingType(training.training_type) }}</span>
              </div>
              
              <div v-if="training.duration" class="flex items-center text-sm">
                <span :class="[
                  'font-medium mr-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Duration:</span>
                <span :class="[
                  themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                ]">{{ training.duration }}</span>
              </div>
              
              <div v-if="training.date_completed" class="flex items-center text-sm">
                <span :class="[
                  'font-medium mr-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Date Completed:</span>
                <span :class="[
                  themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                ]">{{ formatDate(training.date_completed) }}</span>
              </div>
              
              <div v-if="training.certificate_number" class="flex items-center text-sm">
                <span :class="[
                  'font-medium mr-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Certificate #:</span>
                <span :class="[
                  'px-2 py-1 rounded bg-gray-100 text-gray-800 text-xs font-mono',
                  themeStore.isDarkMode ? 'bg-gray-700 text-gray-300' : ''
                ]">{{ training.certificate_number }}</span>
              </div>
              
              <div v-if="training.skills_gained && training.skills_gained.length > 0" class="text-sm">
                <span :class="[
                  'font-medium',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Skills Gained:</span>
                <div class="mt-1 flex flex-wrap gap-2">
                  <span 
                    v-for="skill in training.skills_gained" 
                    :key="skill"
                    :class="[
                      'px-2 py-1 rounded-full text-xs',
                      'bg-indigo-100 text-indigo-800'
                    ]"
                  >{{ skill }}</span>
                </div>
              </div>
              
              <div v-if="training.description" class="text-sm">
                <span :class="[
                  'font-medium',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Description:</span>
                <p :class="[
                  'mt-1',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
                ]">{{ training.description }}</p>
              </div>
            </div>
          </div>
          
          <!-- Edit/Delete buttons for own profile -->
          <div v-if="isOwnProfile" class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button 
              @click="$emit('edit', training)"
              class="p-2 text-gray-400 hover:text-blue-600 transition-colors"
              title="Edit training"
            >
              <PencilIcon class="w-4 h-4" />
            </button>
            <button 
              @click="$emit('delete', training.id)"
              class="p-2 text-gray-400 hover:text-red-600 transition-colors"
              title="Delete training"
            >
              <TrashIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-8">
      <div class="mx-auto w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mb-4">
        <svg class="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      </div>
      <p :class="[
        'text-lg font-medium',
        themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-900'
      ]">No trainings</p>
      <p :class="[
        'text-sm mt-2',
        themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'
      ]">{{ isOwnProfile ? 'Add your trainings to showcase your continuous learning and professional development' : 'This user hasn\'t added any trainings yet' }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'
import SectionPrivacyControl from '@/components/profile/SectionPrivacyControl.vue'

defineProps({
  trainings: {
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
  emit('visibility-changed', { section: 'trainings', visibility })
}

const getTrainingTypeClass = (type) => {
  const classes = {
    'workshop': 'bg-blue-100 text-blue-800',
    'seminar': 'bg-green-100 text-green-800',
    'certification': 'bg-purple-100 text-purple-800',
    'bootcamp': 'bg-red-100 text-red-800',
    'online_course': 'bg-yellow-100 text-yellow-800',
    'conference': 'bg-pink-100 text-pink-800'
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

const formatTrainingType = (type) => {
  const types = {
    'workshop': 'Workshop',
    'seminar': 'Seminar',
    'certification': 'Certification',
    'bootcamp': 'Bootcamp',
    'online_course': 'Online Course',
    'conference': 'Conference'
  }
  return types[type] || type
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