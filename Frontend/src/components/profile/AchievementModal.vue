<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
      <!-- Modal Header -->
      <div class="flex items-center justify-between p-6 border-b">
        <h3 class="text-lg font-semibold text-gray-900">
          {{ isEditing ? 'Edit Achievement' : 'Add Achievement' }}
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
          <!-- Title -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Title *
            </label>
            <input
              v-model="form.title"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Enter achievement title"
            />
          </div>

          <!-- Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Type *
            </label>
            <select
              v-model="form.type"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">Select achievement type</option>
              <option value="academic">Academic</option>
              <option value="professional">Professional</option>
              <option value="certification">Certification</option>
              <option value="award">Award</option>
              <option value="volunteer">Volunteer Work</option>
              <option value="project">Project</option>
              <option value="publication">Publication</option>
              <option value="patent">Patent</option>
              <option value="other">Other</option>
            </select>
          </div>

          <!-- Organization -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Organization/Institution
            </label>
            <input
              v-model="form.organization"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Enter issuing organization"
            />
          </div>

          <!-- Date Achieved -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Date Achieved
            </label>
            <input
              v-model="form.date_achieved"
              type="date"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>

          <!-- URL -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              URL (Optional)
            </label>
            <input
              v-model="form.url"
              type="url"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="https://example.com/certificate"
            />
          </div>

          <!-- Featured -->
          <div class="flex items-center">
            <input
              v-model="form.is_featured"
              type="checkbox"
              id="is_featured"
              class="rounded border-gray-300 text-green-600 focus:ring-green-500"
            />
            <label for="is_featured" class="ml-2 text-sm text-gray-700">
              Feature this achievement prominently on profile
            </label>
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              v-model="form.description"
              rows="4"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Describe your achievement, what you learned, or why it's significant..."
            ></textarea>
          </div>

          <!-- Attachment -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Attachment (Optional)
            </label>
            <input
              ref="fileInput"
              type="file"
              @change="handleFileChange"
              accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
            <p class="text-xs text-gray-500 mt-1">
              Supported formats: PDF, JPG, PNG, DOC, DOCX (Max 5MB)
            </p>
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
import { reactive, ref } from 'vue'

const props = defineProps({
  achievement: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

const loading = ref(false)
const isEditing = ref(false)
const fileInput = ref(null)

const form = reactive({
  title: '',
  type: '',
  organization: '',
  date_achieved: '',
  url: '',
  description: '',
  is_featured: false,
  attachment: null
})

// Initialize form data if editing
if (props.achievement) {
  isEditing.value = true
  Object.keys(form).forEach(key => {
    if (props.achievement[key] !== undefined) {
      form[key] = props.achievement[key]
    }
  })
}

const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    // Check file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      alert('File size must be less than 5MB')
      fileInput.value.value = ''
      return
    }
    form.attachment = file
  }
}

const handleSubmit = async () => {
  loading.value = true
  
  try {
    const achievementData = { ...form }
    
    // Convert empty strings to null for optional fields
    if (!achievementData.organization) achievementData.organization = null
    if (!achievementData.date_achieved) achievementData.date_achieved = null
    if (!achievementData.url) achievementData.url = null
    if (!achievementData.description) achievementData.description = null
    
    emit('save', achievementData)
  } catch (error) {
    console.error('Error saving achievement:', error)
  } finally {
    loading.value = false
  }
}
</script>