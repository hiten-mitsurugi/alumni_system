<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
      <!-- Modal Header -->
      <div class="flex items-center justify-between p-6 border-b">
        <h3 class="text-lg font-semibold text-gray-900">
          {{ isEditing ? 'Edit Education' : 'Add Education' }}
        </h3>
        <button 
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Modal Body -->
      <div class="p-6">
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Institution -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Institution *
            </label>
            <input
              v-model="form.institution"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Enter institution name"
            />
          </div>

          <!-- Degree Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Degree Type *
            </label>
            <select
              v-model="form.degree_type"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">Select degree type</option>
              <option value="master">Master's Degree</option>
              <option value="doctoral">Doctoral Degree</option>
              <option value="vocational">Vocational Degree</option>
              <option value="other">Other</option>
            </select>
          </div>

          <!-- Field of Study -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Field of Study
            </label>
            <input
              v-model="form.field_of_study"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Enter field of study"
            />
          </div>

          <!-- Date Range (Month and Year) -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Start Month & Year
              </label>
              <div class="flex space-x-2">
                <select
                  v-model="form.start_month"
                  required
                  class="w-1/2 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="">Month</option>
                  <option v-for="(month, idx) in months" :key="idx" :value="idx+1">{{ month }}</option>
                </select>
                <input
                  v-model="form.start_year"
                  type="number"
                  min="1950"
                  :max="currentYear + 30"
                  required
                  placeholder="Year"
                  class="w-1/2 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                End Month & Year
              </label>
              <div class="flex space-x-2">
                <select
                  v-model="form.end_month"
                  :disabled="form.is_current"
                  class="w-1/2 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100"
                >
                  <option value="">Month</option>
                  <option v-for="(month, idx) in months" :key="idx" :value="idx+1">{{ month }}</option>
                </select>
                <input
                  v-model="form.end_year"
                  type="number"
                  min="1950"
                  :max="currentYear + 30"
                  :disabled="form.is_current"
                  placeholder="Year"
                  class="w-1/2 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100"
                />
              </div>
            </div>
          </div>

          <!-- Currently Studying -->
          <div class="flex items-center">
            <input
              v-model="form.is_current"
              type="checkbox"
              id="is_current"
              class="rounded border-gray-300 text-green-600 focus:ring-green-500"
            />
            <label for="is_current" class="ml-2 text-sm text-gray-700">
              I am currently studying here
            </label>
          </div>







          <!-- Form Actions -->
          <div class="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              @click="$emit('close')"
              class="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              <span v-if="loading" class="animate-spin mr-2">⟳</span>
              {{ isEditing ? 'Update' : 'Save' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'

const props = defineProps({
  education: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

const loading = ref(false)
const isEditing = ref(false)



const months = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]
const currentYear = new Date().getFullYear();
const form = reactive({
  institution: '',
  degree_type: '',
  field_of_study: '',
  start_month: '',
  start_year: '',
  end_month: '',
  end_year: '',
  is_current: false
})

// Initialize form data if editing
if (props.education) {
  isEditing.value = true
  // Handle existing date fields by parsing them into month/year
  if (props.education.start_date) {
    const startDate = new Date(props.education.start_date)
    form.start_month = startDate.getMonth() + 1
    form.start_year = startDate.getFullYear()
  }
  if (props.education.end_date) {
    const endDate = new Date(props.education.end_date)
    form.end_month = endDate.getMonth() + 1
    form.end_year = endDate.getFullYear()
  }
  
  // Set other fields
  form.institution = props.education.institution || ''
  form.degree_type = props.education.degree_type || ''
  form.field_of_study = props.education.field_of_study || ''
  form.is_current = props.education.is_current || false
}

// Clear end month/year when is_current is checked
watch(() => form.is_current, (newValue) => {
  if (newValue) {
    form.end_month = ''
    form.end_year = ''
  }
})

const handleSubmit = async () => {
  loading.value = true
  try {
    console.log('📝 EducationModal - Form data before processing:', form)
    
    let degreeType = form.degree_type;
    
    const educationData = {
      institution: form.institution,
      degree_type: degreeType,
      field_of_study: form.field_of_study || null,
      is_current: form.is_current
    }
    
    // Convert month/year to proper date format for backend
    if (form.start_month && form.start_year) {
      // Use first day of the month for start date
      educationData.start_date = `${form.start_year}-${String(form.start_month).padStart(2, '0')}-01`
    } else {
      educationData.start_date = null
    }
    
    if (form.end_month && form.end_year && !form.is_current) {
      // Use last day of the month for end date
      const lastDay = new Date(form.end_year, form.end_month, 0).getDate()
      educationData.end_date = `${form.end_year}-${String(form.end_month).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`
    } else {
      educationData.end_date = null
    }
    
    console.log('📤 EducationModal - Final data being sent:', educationData)
    
    emit('save', educationData)
  } catch (error) {
    console.error('❌ EducationModal - Error processing form:', error)
  } finally {
    loading.value = false
  }
}
</script>