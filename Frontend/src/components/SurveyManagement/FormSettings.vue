<template>
  <div class="space-y-6">
    <!-- Basic Information -->
    <div class="bg-gray-50 rounded-lg p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Basic Information</h3>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Form Title</label>
          <input
            v-model="localSettings.name"
            type="text"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            placeholder="Enter form title"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
          <textarea
            v-model="localSettings.description"
            rows="3"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            placeholder="Enter form description"
          ></textarea>
        </div>
      </div>
    </div>

    <!-- Response Settings -->
    <div class="bg-gray-50 rounded-lg p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Response Settings</h3>
      <div class="space-y-4">
        <div class="flex items-center">
          <input
            v-model="localSettings.is_default"
            type="checkbox"
            id="is_default"
            class="w-4 h-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
          />
          <label for="is_default" class="ml-2 text-sm font-medium text-gray-700">
            Use this form for registration (default)
          </label>
        </div>

        <div class="flex items-center">
          <input
            v-model="localSettings.accepting_responses"
            type="checkbox"
            id="accepting"
            class="w-4 h-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
          />
          <label for="accepting" class="ml-2 text-sm font-medium text-gray-700">
            Accept responses
          </label>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
          <input
            v-model="localSettings.start_at"
            type="datetime-local"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">End Date</label>
          <input
            v-model="localSettings.end_at"
            type="date"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          />
          <p class="text-xs text-gray-500 mt-1">Form will close at 11:59 PM on this date</p>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Confirmation Message</label>
          <textarea
            v-model="localSettings.confirmation_message"
            rows="3"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            placeholder="Thank you for submitting the form!"
          ></textarea>
        </div>
      </div>
    </div>

    <!-- Advanced Settings -->
    <div class="bg-gray-50 rounded-lg p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Advanced Settings</h3>
      <div class="space-y-4">
        <div class="flex items-center">
          <input
            v-model="formSettings.allow_multiple_responses"
            type="checkbox"
            id="multiple"
            class="w-4 h-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
          />
          <label for="multiple" class="ml-2 text-sm font-medium text-gray-700">
            Allow multiple responses
          </label>
        </div>
        
        <div class="flex items-center">
          <input
            v-model="formSettings.show_progress_bar"
            type="checkbox"
            id="progress"
            class="w-4 h-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
          />
          <label for="progress" class="ml-2 text-sm font-medium text-gray-700">
            Show progress bar
          </label>
        </div>
        
        <div class="flex items-center">
          <input
            v-model="formSettings.shuffle_questions"
            type="checkbox"
            id="shuffle"
            class="w-4 h-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
          />
          <label for="shuffle" class="ml-2 text-sm font-medium text-gray-700">
            Shuffle questions
          </label>
        </div>
        
        <div class="flex items-center">
          <input
            v-model="formSettings.require_login"
            type="checkbox"
            id="login"
            class="w-4 h-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
          />
          <label for="login" class="ml-2 text-sm font-medium text-gray-700">
            Require login to respond
          </label>
        </div>
      </div>
    </div>

    <!-- Save Button -->
    <div class="flex justify-end">
      <button
        @click="handleSave"
        :disabled="saving"
        class="bg-orange-600 text-white px-8 py-3 rounded-lg hover:bg-orange-700 transition disabled:opacity-50"
      >
        {{ saving ? 'Saving...' : 'Save Settings' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'

const props = defineProps({
  form: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['save'])

const saving = ref(false)

// Helper to convert ISO 8601 to datetime-local format (yyyy-MM-ddThh:mm) for start date
const formatDatetimeLocal = (isoString) => {
  if (!isoString) return ''
  // Remove timezone and milliseconds: "2025-11-18T18:46:00Z" -> "2025-11-18T18:46"
  return isoString.replace(/:\d{2}\.\d{3}Z$/, '').replace(/:\d{2}Z$/, '').slice(0, 16)
}

// Helper to convert ISO 8601 to date format (yyyy-MM-dd)
const formatDate = (isoString) => {
  if (!isoString) return ''
  // Extract just the date part: "2025-11-18T18:46:00Z" -> "2025-11-18"
  return isoString.split('T')[0]
}

// Helper to convert datetime-local format back to ISO 8601 for backend (start date)
const formatISO = (datetimeLocal) => {
  if (!datetimeLocal) return null
  // Append seconds and Z timezone: "2025-11-18T18:46" -> "2025-11-18T18:46:00Z"
  return datetimeLocal + ':00Z'
}

// Helper to convert date to ISO 8601 at 11:59 PM for backend
const formatEndDateISO = (dateString) => {
  if (!dateString) return null
  // Set time to 23:59:59 (11:59 PM): "2025-11-18" -> "2025-11-18T23:59:59Z"
  return dateString + 'T23:59:59Z'
}

const localSettings = reactive({
  name: props.form.name,
  description: props.form.description,
  is_default: props.form.is_default || false,
  accepting_responses: props.form.accepting_responses || false,
  start_at: formatDatetimeLocal(props.form.start_at),
  end_at: formatDate(props.form.end_at),
  confirmation_message: props.form.confirmation_message || ''
})

const formSettings = reactive(props.form.form_settings || {
  allow_multiple_responses: false,
  show_progress_bar: true,
  shuffle_questions: false,
  require_login: true
})

watch(() => props.form, (newForm) => {
  Object.assign(localSettings, {
    name: newForm.name,
    description: newForm.description,
    is_default: newForm.is_default || false,
    accepting_responses: newForm.accepting_responses || false,
    start_at: formatDatetimeLocal(newForm.start_at),
    end_at: formatDate(newForm.end_at),
    confirmation_message: newForm.confirmation_message || ''
  })
  Object.assign(formSettings, newForm.form_settings || {})
}, { deep: true })

const handleSave = async () => {
  saving.value = true
  try {
    await emit('save', {
      ...localSettings,
      start_at: formatISO(localSettings.start_at),
      end_at: formatEndDateISO(localSettings.end_at),
      form_settings: formSettings
    })
  } finally {
    saving.value = false
  }
}
</script>
