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


    <div class="space-y-4">
      <!-- ALWAYS show user profile education (Bachelor's degree from registration) -->
      <div v-if="user && (user.program || user.year_graduated)" class="flex items-center justify-between py-3 border-b border-gray-100">
        <div class="flex-1">
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
              </svg>
            </div>
            <div>
              <p class="font-medium text-gray-900">{{ user.program || 'Program not specified' }}</p>
              <p class="text-sm text-gray-500">Caraga State University • {{ user.year_graduated || 'Year not specified' }}</p>
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
          class="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0"
        >
          <div class="flex-1">
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                </svg>
              </div>
              <div>
                <p class="font-medium text-gray-900">{{ edu.field_of_study || 'Field not specified' }}</p>
                <p class="text-sm text-gray-500">{{ edu.institution || 'Institution not specified' }} • {{ formatDateRange(edu.start_date, edu.end_date, edu.is_current) }}</p>
              </div>
            </div>
          </div>
          <!-- Actions for own profile -->
          <div v-if="isOwnProfile" class="flex space-x-2">
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
    <div v-if="isOwnProfile && (!education || education.length === 0)" class="mt-4 p-3 bg-gray-50 rounded-md">
      <p class="text-sm text-gray-600">Have additional degrees? Click "Add" to include Master's, PhD, or other qualifications.</p>
    </div>

  </div>
</template>

<script setup>
const props = defineProps({
  education: Array,
  profile: Object,
  user: Object,  // Add user prop to access program and year_graduated
  isOwnProfile: Boolean
})

const emit = defineEmits(['add', 'edit', 'edit-profile', 'delete'])

// Debug logging
console.log('ProfileEducationSection - Education prop:', props.education)
console.log('ProfileEducationSection - User prop:', props.user)
console.log('ProfileEducationSection - User program:', props.user?.program)
console.log('ProfileEducationSection - User year_graduated:', props.user?.year_graduated)
console.log('ProfileEducationSection - User prop:', props.user)
console.log('ProfileEducationSection - User program:', props.user?.program)
console.log('ProfileEducationSection - User year_graduated:', props.user?.year_graduated)

// Watch for changes in education prop
import { watch } from 'vue'
watch(() => props.education, (newEducation) => {
  console.log('Education prop changed:', newEducation)
}, { deep: true })

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
