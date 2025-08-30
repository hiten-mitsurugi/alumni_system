<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-bold text-gray-900">Experience</h2>
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
              {{ work.position || work.job_title }}
            </h3>
            <p class="text-gray-700 font-medium">
              {{ work.company || work.company_name }}
            </p>
            <p class="text-sm text-gray-500 mt-1">
              {{ formatWorkDuration(work) }}
            </p>
            
            <!-- Employment Type -->
            <p v-if="work.employment_type" class="text-sm text-gray-600 mt-1">
              {{ formatEmploymentType(work.employment_type) }}
            </p>
            
            <!-- Location -->
            <p v-if="work.location" class="text-sm text-gray-600 mt-1">
              📍 {{ work.location }}
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
        Add Experience
      </button>
    </div>

    <div v-else class="text-gray-500 text-center py-4">
      <p>No work experience information available.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  workHistories: Array,
  isOwnProfile: Boolean
})

const emit = defineEmits(['add', 'edit', 'delete'])

const showAllWork = ref(false)

const displayedWork = computed(() => {
  if (!props.workHistories) return []
  
  // Sort by start date (most recent first)
  const sorted = [...props.workHistories].sort((a, b) => {
    const dateA = new Date(a.start_date || a.from_date)
    const dateB = new Date(b.start_date || b.from_date)
    return dateB - dateA
  })
  
  // Show first 3 or all if expanded
  return showAllWork.value ? sorted : sorted.slice(0, 3)
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
  const isCurrent = work.is_current || work.currently_working
  
  if (!startDate) return 'Date not specified'
  
  const start = formatDate(startDate)
  const end = isCurrent ? 'Present' : (endDate ? formatDate(endDate) : 'Present')
  
  return `${start} - ${end}`
}

const formatEmploymentType = (type) => {
  const typeMap = {
    'full_time': 'Full-time',
    'part_time': 'Part-time',
    'contract': 'Contract',
    'internship': 'Internship',
    'freelance': 'Freelance',
    'volunteer': 'Volunteer'
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
