<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-bold text-gray-900">Education</h2>
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

    <div v-if="education && education.length > 0" class="space-y-6">
      <div 
        v-for="(edu, index) in displayedEducation" 
        :key="edu.id"
        class="relative border-l-2 border-green-100 pl-6 pb-6"
        :class="{ 'border-b border-gray-200': index < displayedEducation.length - 1 }"
      >
        <!-- Timeline dot -->
        <div class="absolute -left-2 top-0 w-4 h-4 bg-green-600 rounded-full border-2 border-white"></div>
        
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ edu.institution }}
            </h3>
            <p class="text-gray-700 font-medium">
              {{ edu.degree_type }} in {{ edu.field_of_study }}
            </p>
            <p class="text-sm text-gray-500 mt-1">
              {{ formatDateRange(edu.start_date, edu.end_date, edu.is_current) }}
            </p>
            
            <!-- GPA if available -->
            <p v-if="edu.gpa" class="text-sm text-gray-600 mt-1">
              GPA: {{ edu.gpa }}
            </p>
            
            <!-- Description if available -->
            <div v-if="edu.description" class="mt-3">
              <div 
                :class="{ 'line-clamp-3': !edu.showFullDescription && edu.description.length > 150 }"
                class="text-gray-700 text-sm whitespace-pre-wrap"
              >
                {{ edu.description }}
              </div>
              
              <button 
                v-if="edu.description.length > 150"
                @click="toggleDescription(edu)"
                class="text-green-600 hover:text-green-700 text-sm font-medium mt-1"
              >
                {{ edu.showFullDescription ? 'See less' : 'See more' }}
              </button>
            </div>
          </div>

          <!-- Actions for own profile -->
          <div v-if="isOwnProfile" class="flex space-x-2 ml-4">
            <button 
              @click="$emit('edit', edu)"
              class="text-gray-500 hover:text-green-600 transition-colors"
              title="Edit"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
              </svg>
            </button>
            <button 
              @click="$emit('delete', edu.id)"
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
      <div v-if="education.length > 3" class="text-center pt-4 border-t border-gray-200">
        <button 
          @click="showAllEducation = !showAllEducation"
          class="text-green-600 hover:text-green-700 font-medium"
        >
          {{ showAllEducation ? 'Show less' : `Show all ${education.length} education entries` }}
        </button>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="isOwnProfile" class="text-gray-500 text-center py-8">
      <div class="mb-4">
        <svg class="w-12 h-12 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
        </svg>
      </div>
      <p class="mb-3">Add your educational background to showcase your academic achievements.</p>
      <button 
        @click="$emit('add')"
        class="text-green-600 hover:text-green-700 font-medium"
      >
        Add Education
      </button>
    </div>

    <div v-else class="text-gray-500 text-center py-4">
      <p>No education information available.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  education: Array,
  isOwnProfile: Boolean
})

const emit = defineEmits(['add', 'edit', 'delete'])

const showAllEducation = ref(false)

const displayedEducation = computed(() => {
  if (!props.education) return []
  
  // Sort by start date (most recent first)
  const sorted = [...props.education].sort((a, b) => {
    const dateA = new Date(a.start_date)
    const dateB = new Date(b.start_date)
    return dateB - dateA
  })
  
  // Show first 3 or all if expanded
  return showAllEducation.value ? sorted : sorted.slice(0, 3)
})

const formatDateRange = (startDate, endDate, isCurrent) => {
  const formatDate = (date) => {
    return new Date(date).toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short' 
    })
  }
  
  const start = formatDate(startDate)
  const end = isCurrent ? 'Present' : formatDate(endDate)
  
  return `${start} - ${end}`
}

const toggleDescription = (edu) => {
  edu.showFullDescription = !edu.showFullDescription
}
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
