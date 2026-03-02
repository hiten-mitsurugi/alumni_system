<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
    <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <!-- Modal Header -->
      <div class="flex items-center justify-between p-6 border-b sticky top-0 bg-white z-10">
        <h3 class="text-lg font-semibold text-gray-900">
          {{ isEditing ? 'Edit Work History' : 'Add Work History' }}
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
          <!-- 1. Are you currently employed? -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Are you currently employed? *
            </label>
            <div class="flex items-center space-x-4">
              <label class="flex items-center">
                <input
                  v-model="isEmployed"
                  type="radio"
                  :value="true"
                  class="mr-2 text-green-600 focus:ring-green-500"
                />
                <span class="text-sm text-gray-700">Yes</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="isEmployed"
                  type="radio"
                  :value="false"
                  class="mr-2 text-green-600 focus:ring-green-500"
                />
                <span class="text-sm text-gray-700">No</span>
              </label>
            </div>
          </div>

          <!-- Conditional Forms based on employment status -->
          <div class="pt-4 border-t border-gray-200">
            <!-- Unemployment Reason Form (if NOT employed) -->
            <UnemploymentReasonForm 
              v-if="isEmployed === false"
              :model-value="form"
              @update:model-value="updateForm"
            />

            <!-- Employed Work Form (if employed) -->
            <EmployedWorkForm 
              v-if="isEmployed === true"
              :model-value="form"
              @update:model-value="updateForm"
            />

            <!-- Message when employment status not selected -->
            <div v-if="isEmployed === null" class="text-center py-8 text-gray-500">
              <p>Please select your employment status to continue</p>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              @click="$emit('close')"
              class="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="loading || isEmployed === null"
              class="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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
import UnemploymentReasonForm from './UnemploymentReasonForm.vue'
import EmployedWorkForm from './EmployedWorkForm.vue'

const props = defineProps({
  experience: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

const loading = ref(false)
const isEditing = ref(false)
const isEmployed = ref(null)

const form = reactive({
  // Common fields
  is_employed: null,
  
  // Unemployed fields
  reason_unemployed: '',
  reason_unemployed_other: '',
  
  // Employed fields
  occupation: '',
  employing_agency: '',
  company_address: '',
  employment_status: '',
  classification: '',
  classification_other: '',
  how_got_job: '',
  how_got_job_other: '',
  monthly_income: '',
  is_breadwinner: false,
  length_of_service: '',
  college_education_relevant: '',
  start_date: '',
  end_date: '',
  is_current_job: false,
  description: ''
})

// Initialize form data if editing
if (props.experience) {
  isEditing.value = true
  
  // Determine employment status from the data
  if (props.experience.reason_unemployed) {
    isEmployed.value = false
  } else if (props.experience.occupation || props.experience.employing_agency) {
    isEmployed.value = true
  }
  
  // Copy all fields from experience to form
  Object.keys(form).forEach(key => {
    if (props.experience[key] !== undefined) {
      form[key] = props.experience[key]
    }
  })
}

// Watch isEmployed to clear opposite form data
watch(isEmployed, (newValue) => {
  if (newValue === true) {
    // Clear unemployment fields
    form.reason_unemployed = ''
    form.reason_unemployed_other = ''
  } else if (newValue === false) {
    // Clear employment fields
    form.occupation = ''
    form.employing_agency = ''
    form.company_address = ''
    form.employment_status = ''
    form.classification = ''
    form.classification_other = ''
    form.how_got_job = ''
    form.how_got_job_other = ''
    form.monthly_income = ''
    form.is_breadwinner = false
    form.length_of_service = ''
    form.college_education_relevant = ''
    form.start_date = ''
    form.end_date = ''
    form.is_current_job = false
    form.description = ''
  }
})

// Watch is_current_job to clear end_date when checked
watch(() => form.is_current_job, (isCurrentJob) => {
  if (isCurrentJob) {
    form.end_date = ''
  }
})

// Update form with proper reactivity
const updateForm = (updatedData) => {
  Object.assign(form, updatedData)
}

const handleSubmit = async () => {
  if (isEmployed.value === null) {
    alert('Please select your employment status')
    return
  }

  loading.value = true
  
  try {
    const workHistoryData = {
      is_employed: isEmployed.value,
      ...form
    }
    
    // Convert empty strings to null for optional fields
    Object.keys(workHistoryData).forEach(key => {
      if (workHistoryData[key] === '') {
        workHistoryData[key] = null
      }
    })
    
    console.log('📤 WorkHistoryModal: Emitting save event', {
      workHistoryData,
      isEditing: isEditing.value,
      isEmployed: isEmployed.value
    })
    
    emit('save', workHistoryData)
  } catch (error) {
    console.error('❌ WorkHistoryModal: Error in handleSubmit:', error)
  } finally {
    loading.value = false
  }
}
</script>
