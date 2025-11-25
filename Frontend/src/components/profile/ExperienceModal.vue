<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
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
                :disabled="currentlyWorking"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
              />
            </div>
          </div>

          <!-- Currently Working Checkbox -->
          <div class="flex items-center">
            <input
              id="currently-working"
              v-model="currentlyWorking"
              type="checkbox"
              class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
            />
            <label for="currently-working" class="ml-2 block text-sm text-gray-700">
              I am currently working here
            </label>
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

          <!-- Job Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Job Description
            </label>
            <textarea
              v-model="form.description"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Describe your responsibilities and key achievements"
            ></textarea>
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
              class="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors disabled:opacity-50"
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
const currentlyWorking = ref(false)

const form = reactive({
  occupation: '',
  employing_agency: '',
  classification: '',
  start_date: '',
  end_date: '',
  length_of_service: '',
  description: ''
})

// Initialize form data if editing
if (props.experience) {
  isEditing.value = true
  Object.keys(form).forEach(key => {
    if (props.experience[key] !== undefined) {
      form[key] = props.experience[key]
    }
  })
  // Set currently working if no end date
  currentlyWorking.value = !props.experience.end_date
}

// Watch currentlyWorking to clear end_date when checked
watch(currentlyWorking, (isCurrentlyWorking) => {
  if (isCurrentlyWorking) {
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