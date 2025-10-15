<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-900">Contact Information</h2>
      <div v-if="isOwnProfile" class="flex items-center gap-2">
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
      <span class="ml-3 text-gray-600">Loading contact information...</span>
    </div>

    <!-- Contact Information List -->
    <div v-else class="space-y-0">
      <!-- Contact Numbers -->
      <AboutItem
        v-if="fieldData['contact_number']"
        icon="phone"
        :field-data="fieldData['contact_number']"
        :field-name="'contact_number'"
        :field-label="'Contact Number'"
        :is-own-profile="isOwnProfile"
        @update-field="updateField"
        @toggle-visibility="toggleVisibility"
      />

      <AboutItem
        v-if="fieldData['mobile_number']"
        icon="device-phone-mobile"
        :field-data="fieldData['mobile_number']"
        :field-name="'mobile_number'"
        :field-label="'Mobile Number'"
        :is-own-profile="isOwnProfile"
        @update-field="updateField"
        @toggle-visibility="toggleVisibility"
      />

      <!-- Social Media Links -->
      <AboutItem
        v-if="fieldData['linkedin_url']"
        icon="linkedin"
        :field-data="fieldData['linkedin_url']"
        :field-name="'linkedin_url'"
        :field-label="'LinkedIn'"
        :is-own-profile="isOwnProfile"
        :is-url="true"
        @update-field="updateField"
        @toggle-visibility="toggleVisibility"
      />

      <AboutItem
        v-if="fieldData['facebook_url']"
        icon="facebook"
        :field-data="fieldData['facebook_url']"
        :field-name="'facebook_url'"
        :field-label="'Facebook'"
        :is-own-profile="isOwnProfile"
        :is-url="true"
        @update-field="updateField"
        @toggle-visibility="toggleVisibility"
      />

      <AboutItem
        v-if="fieldData['instagram_url']"
        icon="instagram"
        :field-data="fieldData['instagram_url']"
        :field-name="'instagram_url'"
        :field-label="'Instagram'"
        :is-own-profile="isOwnProfile"
        :is-url="true"
        @update-field="updateField"
        @toggle-visibility="toggleVisibility"
      />

      <AboutItem
        v-if="fieldData['twitter_url']"
        icon="twitter"
        :field-data="fieldData['twitter_url']"
        :field-name="'twitter_url'"
        :field-label="'Twitter'"
        :is-own-profile="isOwnProfile"
        :is-url="true"
        @update-field="updateField"
        @toggle-visibility="toggleVisibility"
      />



      <!-- Empty state for own profile -->
      <div v-if="isOwnProfile && !hasContactInfo" class="text-gray-500 text-center py-8">
        <div class="mb-4">
          <svg class="w-12 h-12 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
          </svg>
        </div>
        <p class="mb-3">Add your contact information to help people connect with you.</p>
        <p class="text-sm text-gray-400">Click on any field above to add information.</p>
      </div>

      <!-- Empty state for visitors -->
      <div v-else-if="!hasContactInfo" class="text-gray-500 text-center py-4">
        <p>No contact information available.</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
      <p class="text-red-600">{{ error }}</p>
      <button @click="fetchProfileData" class="mt-2 text-red-700 hover:text-red-800 font-medium">
        Try Again
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import AboutItem from './AboutItem.vue'

const props = defineProps({
  profile: Object,
  isOwnProfile: Boolean,
  userId: Number
})

const emit = defineEmits(['profile-updated'])

// State
const loading = ref(true)
const error = ref(null)
const fieldData = ref({})

// Contact fields
const contactFields = [
  'contact_number', 
  'mobile_number', 
  'linkedin_url', 
  'facebook_url', 
  'instagram_url', 
  'twitter_url'
]

// Computed
const hasContactInfo = computed(() => {
  return contactFields.some(field => fieldData.value[field]?.value)
})

// Methods
async function fetchProfileData() {
  try {
    loading.value = true
    error.value = null
    
    const url = props.userId 
      ? `/auth/profile/about-data/${props.userId}/`
      : '/auth/profile/about-data/'
    
    const response = await api.get(url)
    
    // Filter fields based on visibility - only show fields that are visible
    const filteredFieldData = {}
    for (const [fieldName, fieldInfo] of Object.entries(response.data.field_data)) {
      if (fieldInfo.is_visible) {
        filteredFieldData[fieldName] = fieldInfo
      }
    }
    fieldData.value = filteredFieldData
    
    console.log('Contact info loaded:', response.data)
  } catch (err) {
    console.error('Error fetching contact data:', err)
    error.value = 'Failed to load contact information. Please try again.'
  } finally {
    loading.value = false
  }
}

async function updateField(fieldName, newValue) {
  try {
    const response = await api.post('/auth/profile/field-update/', {
      field_name: fieldName,
      field_value: newValue,
      visibility: fieldData.value[fieldName]?.visibility || 'alumni_only'
    })
    
    // Update local data
    if (fieldData.value[fieldName]) {
      fieldData.value[fieldName].value = newValue
    }
    
    console.log('Contact field updated:', response.data)
    emit('profile-updated')
  } catch (err) {
    console.error('Error updating contact field:', err)
    alert('Failed to update contact field. Please try again.')
  }
}

async function toggleVisibility(fieldName, newVisibility) {
  try {
    const response = await api.post('/auth/profile/field-update/', {
      field_name: fieldName,
      visibility: newVisibility
    })
    
    // Update local data
    if (fieldData.value[fieldName]) {
      fieldData.value[fieldName].visibility = newVisibility
    }
    
    console.log('Contact visibility updated:', response.data)
  } catch (err) {
    console.error('Error updating contact visibility:', err)
    alert('Failed to update privacy setting. Please try again.')
  }
}

// Lifecycle
onMounted(() => {
  fetchProfileData()
})
</script>

<style scoped>
/* Contact section specific styles if needed */
</style>