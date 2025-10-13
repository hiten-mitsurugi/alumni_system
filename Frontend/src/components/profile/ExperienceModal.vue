<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
      <!-- Modal Header -->
      <div class="flex items-center justify-between p-6 border-b">
        <h3 class="text-lg font-semibold text-gray-900">
          {{ isEditing ? 'Edit Experience' : 'Add Experience' }}
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
          <!-- Job Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Job Type *
            </label>
            <select
              v-model="form.job_type"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">Select job type</option>
              <option value="first_job">First Job</option>
              <option value="current_job">Current Job</option>
            </select>
          </div>

          <!-- Occupation -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Occupation *
            </label>
            <input
              v-model="form.occupation"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Enter job title/occupation"
            />
          </div>

          <!-- Employing Agency -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Company/Agency *
            </label>
            <input
              v-model="form.employing_agency"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Enter company or agency name"
            />
          </div>

          <!-- Employment Status -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Employment Status *
            </label>
            <select
              v-model="form.employment_status"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">Select employment status</option>
              <option value="employed_locally">Employed Locally</option>
              <option value="employed_internationally">Employed Internationally</option>
              <option value="self_employed">Self-Employed</option>
              <option value="unemployed">Unemployed</option>
              <option value="retired">Retired</option>
            </select>
          </div>

          <!-- Classification -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Classification *
            </label>
            <select
              v-model="form.classification"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">Select classification</option>
              <option value="government">Government</option>
              <option value="private">Private</option>
              <option value="ngo">NGO</option>
              <option value="freelance">Freelance</option>
              <option value="business_owner">Business Owner</option>
            </select>
          </div>

          <!-- Date Range -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                v-model="form.start_date"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                End Date
              </label>
              <input
                v-model="form.end_date"
                type="date"
                :disabled="form.job_type === 'current_job'"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100"
              />
            </div>
          </div>

          <!-- How Got Job -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              How did you get this job?
            </label>
            <input
              v-model="form.how_got_job"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="e.g., Job fair, referral, online application"
            />
          </div>

          <!-- Monthly Income -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Monthly Income
            </label>
            <select
              v-model="form.monthly_income"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">Select income range</option>
              <option value="less_than_15000">Less than P15,000</option>
              <option value="15000_to_29999">P15,000 - P29,999</option>
              <option value="30000_to_49999">P30,000 - P49,999</option>
              <option value="50000_and_above">P50,000 and above</option>
              <option value="prefer_not_to_say">Prefer not to say</option>
            </select>
          </div>

          <!-- Length of Service -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Length of Service
            </label>
            <input
              v-model="form.length_of_service"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="e.g., 2 years, 6 months"
            />
          </div>

          <!-- College Education Relevant -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Is your college education relevant to this job?
            </label>
            <select
              v-model="form.college_education_relevant"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">Select relevance</option>
              <option value="yes">Yes</option>
              <option value="no">No</option>
              <option value="somewhat">Somewhat</option>
            </select>
          </div>

          <!-- Breadwinner -->
          <div class="flex items-center">
            <input
              v-model="form.is_breadwinner"
              type="checkbox"
              id="is_breadwinner"
              class="rounded border-gray-300 text-green-600 focus:ring-green-500"
            />
            <label for="is_breadwinner" class="ml-2 text-sm text-gray-700">
              I am the breadwinner of the family
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
  experience: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

const loading = ref(false)
const isEditing = ref(false)

const form = reactive({
  job_type: '',
  occupation: '',
  employing_agency: '',
  employment_status: '',
  classification: '',
  start_date: '',
  end_date: '',
  how_got_job: '',
  monthly_income: '',
  length_of_service: '',
  college_education_relevant: '',
  is_breadwinner: false
})

// Initialize form data if editing
if (props.experience) {
  isEditing.value = true
  Object.keys(form).forEach(key => {
    if (props.experience[key] !== undefined) {
      form[key] = props.experience[key]
    }
  })
}

// Clear end date for current job
watch(() => form.job_type, (newValue) => {
  if (newValue === 'current_job') {
    form.end_date = ''
  }
})

const handleSubmit = async () => {
  loading.value = true
  
  try {
    const experienceData = { ...form }
    
    // Convert empty strings to null for optional fields
    Object.keys(experienceData).forEach(key => {
      if (experienceData[key] === '') {
        experienceData[key] = null
      }
    })
    
    emit('save', experienceData)
  } catch (error) {
    console.error('Error saving experience:', error)
  } finally {
    loading.value = false
  }
}
</script>