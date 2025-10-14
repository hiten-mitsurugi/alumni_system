<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
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
              accept=".pdf,.jpg,.jpeg,.png,.doc,.docx,.txt"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
            <p class="text-xs text-gray-500 mt-1">
              Supported formats: PDF, JPG, PNG, DOC, DOCX, TXT (Max 5MB)
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
import { reactive, ref, watch } from 'vue'

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

// Use individual ref objects instead of reactive object to avoid issues
const formTitle = ref('')
const formType = ref('')
const formOrganization = ref('')
const formDateAchieved = ref('')
const formUrl = ref('')
const formDescription = ref('')
const formIsFeatured = ref(false)
const formAttachment = ref(null)

// Create computed form object for easy access
const form = reactive({
  get title() { return formTitle.value },
  set title(val) { formTitle.value = val },
  get type() { return formType.value },
  set type(val) { formType.value = val },
  get organization() { return formOrganization.value },
  set organization(val) { formOrganization.value = val },
  get date_achieved() { return formDateAchieved.value },
  set date_achieved(val) { formDateAchieved.value = val },
  get url() { return formUrl.value },
  set url(val) { formUrl.value = val },
  get description() { return formDescription.value },
  set description(val) { formDescription.value = val },
  get is_featured() { return formIsFeatured.value },
  set is_featured(val) { formIsFeatured.value = val },
  get attachment() { return formAttachment.value },
  set attachment(val) { formAttachment.value = val }
})

console.log('🔍 AchievementModal: Initial form state')

// Initialize form data if editing
if (props.achievement) {
  isEditing.value = true
  console.log('🔍 AchievementModal: Editing existing achievement:', props.achievement)
  
  formTitle.value = props.achievement.title || ''
  formType.value = props.achievement.type || ''
  formOrganization.value = props.achievement.organization || ''
  formDateAchieved.value = props.achievement.date_achieved || ''
  formUrl.value = props.achievement.url || ''
  formDescription.value = props.achievement.description || ''
  formIsFeatured.value = props.achievement.is_featured || false
  formAttachment.value = props.achievement.attachment || null
} else {
  console.log('🔍 AchievementModal: Creating new achievement')
}

// Watch the individual ref values
watch(formType, (newType) => {
  console.log('🔍 AchievementModal: Type watcher triggered:', newType)
})

watch(formUrl, (newUrl) => {
  console.log('🔍 AchievementModal: URL watcher triggered:', newUrl)
})

watch(formAttachment, (newAttachment) => {
  console.log('🔍 AchievementModal: Attachment watcher triggered:', newAttachment)
})

const handleFileChange = (event) => {
  console.log('🔍 AchievementModal: File change event:', event)
  const file = event.target.files[0]
  console.log('🔍 AchievementModal: Selected file:', file)
  
  if (file) {
    console.log('🔍 File details:', {
      name: file.name,
      size: file.size,
      type: file.type
    })
    
    // Check file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      alert('File size must be less than 5MB')
      fileInput.value.value = ''
      return
    }
    
    // Set attachment using the new structure
    formAttachment.value = file
    console.log('🔍 AchievementModal: Set formAttachment.value to:', formAttachment.value)
    console.log('🔍 AchievementModal: form.attachment now shows:', form.attachment)
  } else {
    formAttachment.value = null
    console.log('🔍 AchievementModal: No file selected, set attachment to null')
  }
}

const handleSubmit = async () => {
  loading.value = true
  
  try {
    // Create the data object from individual ref values
    const achievementData = {
      title: formTitle.value,
      type: formType.value,
      organization: formOrganization.value,
      date_achieved: formDateAchieved.value,
      url: formUrl.value,
      description: formDescription.value,
      is_featured: formIsFeatured.value,
      attachment: formAttachment.value
    }
    
    console.log('🔍 AchievementModal individual ref values:')
    console.log('  title:', formTitle.value)
    console.log('  type:', formType.value)
    console.log('  organization:', formOrganization.value)
    console.log('  url:', formUrl.value)
    console.log('  attachment:', formAttachment.value)
    
    console.log('🔍 AchievementModal sending data:', achievementData)
    
    // Ensure required fields are present
    if (!achievementData.title || !achievementData.type) {
      alert('Please fill in all required fields (Title and Type)')
      loading.value = false
      return
    }
    
    // Validate URL format if provided
    if (achievementData.url && achievementData.url.trim()) {
      try {
        new URL(achievementData.url)
      } catch {
        alert('Please enter a valid URL (e.g., https://example.com)')
        loading.value = false
        return
      }
    }
    
    // DON'T clean up to empty strings - leave the actual values
    // The backend should handle empty fields properly
    
    console.log('🔍 Final achievementData being emitted:', achievementData)
    emit('save', achievementData)
  } catch (error) {
    console.error('Error saving achievement:', error)
  } finally {
    loading.value = false
  }
}
</script>