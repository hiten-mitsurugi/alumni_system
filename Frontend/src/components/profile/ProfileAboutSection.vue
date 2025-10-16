<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-900">About</h2>
      <div v-if="isOwnProfile" class="flex items-center gap-2">
        <!-- Section Privacy Icon -->
        <SectionPrivacyIcon
          section-name="about"
          :current-privacy="sectionPrivacy.about || 'connections_only'"
          @privacy-changed="handleSectionPrivacyChange"
          @apply-to-all-fields="applyPrivacyToAllFields"
        />
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
      <span class="ml-3 text-gray-600">Loading profile data...</span>
    </div>

    <!-- About Information List -->
    <div v-else class="space-y-0">
      <!-- Professional Headline -->
      <AboutItem
        v-if="fieldData['headline']"
        icon="briefcase"
        :field-data="fieldData['headline']"
        :field-name="'headline'"
        :field-label="'Professional Headline'"
        :is-own-profile="isOwnProfile"
        @update-field="updateField"
        @toggle-visibility="toggleVisibility"
      />

      <!-- Bio -->
      <AboutItem
        v-if="fieldData['bio']"
        icon="document-text"
        :field-data="fieldData['bio']"
        :field-name="'bio'"
        :field-label="'Bio'"
        :is-own-profile="isOwnProfile"
        :is-text-area="true"
        @update-field="updateField"
        @toggle-visibility="toggleVisibility"
      />

      <!-- Location -->
      <AboutItem
        v-if="fieldData['location']"
        icon="map-pin"
        :field-data="fieldData['location']"
        :field-name="'location'"
        :field-label="'Location'"
        :is-own-profile="isOwnProfile"
        @update-field="updateField"
        @toggle-visibility="toggleVisibility"
      />

      <!-- Addresses -->
      <AboutItem
        v-if="fieldData['present_address']"
        icon="home"
        :field-data="fieldData['present_address']"
        :field-name="'present_address'"
        :field-label="'Present Address'"
        :is-own-profile="isOwnProfile"
        @update-field="updateField"
        @toggle-visibility="toggleVisibility"
      />

      <AboutItem
        v-if="fieldData['permanent_address']"
        icon="building-office"
        :field-data="fieldData['permanent_address']"
        :field-name="'permanent_address'"
        :field-label="'Permanent Address'"
        :is-own-profile="isOwnProfile"
        @update-field="updateField"
        @toggle-visibility="toggleVisibility"
      />

      <!-- Birth Date -->
      <AboutItem
        v-if="fieldData['birth_date']"
        icon="cake"
        :field-data="fieldData['birth_date']"
        :field-name="'birth_date'"
        :field-label="'Birthday'"
        :is-own-profile="isOwnProfile"
        @update-field="updateField"
        @toggle-visibility="toggleVisibility"
      />

      <!-- Gender -->
      <AboutItem
        v-if="fieldData['gender']"
        icon="user"
        :field-data="fieldData['gender']"
        :field-name="'gender'"
        :field-label="'Gender'"
        :is-own-profile="isOwnProfile"
        @update-field="updateField"
        @toggle-visibility="toggleVisibility"
      />

      <!-- Civil Status -->
      <AboutItem
        v-if="fieldData['civil_status']"
        icon="heart"
        :field-data="fieldData['civil_status']"
        :field-name="'civil_status'"
        :field-label="'Civil Status'"
        :is-own-profile="isOwnProfile"
        @update-field="updateField"
        @toggle-visibility="toggleVisibility"
      />

      <!-- Website -->
      <AboutItem
        v-if="fieldData['website_url']"
        icon="globe-alt"
        :field-data="fieldData['website_url']"
        :field-name="'website_url'"
        :field-label="'Website'"
        :is-own-profile="isOwnProfile"
        :is-url="true"
        @update-field="updateField"
        @toggle-visibility="toggleVisibility"
      />

      <!-- Empty state for own profile -->
      <div v-if="isOwnProfile && !hasAboutInfo" class="text-gray-500 text-center py-8">
        <div class="mb-4">
          <svg class="w-12 h-12 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
          </svg>
        </div>
        <p class="mb-3">Tell people about yourself by adding your bio and personal information.</p>
        <p class="text-sm text-gray-400">Click on any field above to add information.</p>
      </div>

      <!-- Empty state for visitors -->
      <div v-else-if="!hasAboutInfo" class="text-gray-500 text-center py-4">
        <p>No about information available.</p>
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
import { PlusIcon } from '@heroicons/vue/24/outline'
import api from '../../services/api'
import AboutItem from './AboutItem.vue'
import SectionPrivacyIcon from '../privacy/SectionPrivacyIcon.vue'

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
const showAddFieldModal = ref(false)
const sectionPrivacy = ref({
  about: 'connections_only'
})

// About fields only (contact fields moved to separate component)
const aboutFields = [
  'headline', 
  'bio', 
  'location', 
  'present_address', 
  'permanent_address', 
  'birth_date', 
  'gender', 
  'civil_status', 
  'website_url'
]

// Computed
const hasAboutInfo = computed(() => {
  return aboutFields.some(field => fieldData.value[field]?.value)
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
    
    // Filter field data to only include visible fields
    const filteredFieldData = {}
    for (const [fieldName, fieldInfo] of Object.entries(response.data.field_data)) {
      // Only include fields that are visible (for own profile, show all; for others, check is_visible)
      if (props.isOwnProfile || fieldInfo.is_visible) {
        filteredFieldData[fieldName] = fieldInfo
      }
    }
    
    fieldData.value = filteredFieldData
    
    // Calculate section privacy from actual field privacy settings
    calculateSectionPrivacy()
    
    console.log('Profile data loaded:', response.data)
    console.log('Filtered field data:', filteredFieldData)
    console.log('Calculated section privacy:', sectionPrivacy.value)
  } catch (err) {
    console.error('Error fetching profile data:', err)
    error.value = 'Failed to load profile data. Please try again.'
  } finally {
    loading.value = false
  }
}

// Calculate section privacy based on individual field settings
function calculateSectionPrivacy() {
  const aboutFieldNames = Object.keys(fieldData.value).filter(field => 
    aboutFields.includes(field)
  )
  
  if (aboutFieldNames.length === 0) {
    sectionPrivacy.value.about = 'connections_only'
    return
  }
  
  // Get all privacy values for fields in this section
  const privacyValues = aboutFieldNames.map(field => 
    fieldData.value[field]?.visibility || 'connections_only'
  )
  
  // Determine section privacy based on field privacy values
  // If all fields have the same privacy, use that
  // Otherwise, use the most common or most restrictive
  const uniqueValues = [...new Set(privacyValues)]
  
  if (uniqueValues.length === 1) {
    // All fields have the same privacy
    sectionPrivacy.value.about = uniqueValues[0]
  } else {
    // Mixed privacy levels - use the most common one
    const counts = {}
    privacyValues.forEach(value => {
      counts[value] = (counts[value] || 0) + 1
    })
    
    const mostCommon = Object.entries(counts).reduce((a, b) => 
      counts[a[0]] > counts[b[0]] ? a : b
    )[0]
    
    sectionPrivacy.value.about = mostCommon
  }
}

async function updateField(fieldName, newValue) {
  try {
    const payload = {
      field_name: fieldName,
      field_value: newValue,
      visibility: fieldData.value[fieldName]?.visibility || 'connections_only'
    }
    
    // Include target user ID if editing another user's profile
    if (props.userId && props.userId !== 'me') {
      payload.target_user_id = props.userId
    }
    
    const response = await api.post('/auth/profile/field-update/', payload)
    
    // Update local data
    if (fieldData.value[fieldName]) {
      fieldData.value[fieldName].value = newValue
    }
    
    console.log('Field updated:', response.data)
    emit('profile-updated')
  } catch (err) {
    console.error('Error updating field:', err)
    alert('Failed to update field. Please try again.')
  }
}

async function toggleVisibility(fieldName, newVisibility) {
  try {
    const payload = {
      field_name: fieldName,
      visibility: newVisibility
    }
    
    // Include target user ID if editing another user's profile
    if (props.userId && props.userId !== 'me') {
      payload.target_user_id = props.userId
    }
    
    const response = await api.post('/auth/profile/field-update/', payload)
    
    // Update local data
    if (fieldData.value[fieldName]) {
      fieldData.value[fieldName].visibility = newVisibility
    }
    
    // Recalculate section privacy after individual field change
    calculateSectionPrivacy()
    
    console.log('Visibility updated:', response.data)
  } catch (err) {
    console.error('Error updating visibility:', err)
    alert('Failed to update privacy setting. Please try again.')
  }
}

// Section Privacy Methods
async function handleSectionPrivacyChange(data) {
  // Just apply to all fields directly since we don't have separate section privacy
  await applyPrivacyToAllFields(data)
}

async function applyPrivacyToAllFields(data) {
  try {
    // Get all field names in this section
    const fieldNames = Object.keys(fieldData.value)
    
    // Update each field's privacy
    for (const fieldName of fieldNames) {
      const payload = {
        field_name: fieldName,
        visibility: data.privacy
      }
      
      // Include target user ID if editing another user's profile
      if (props.userId && props.userId !== 'me') {
        payload.target_user_id = props.userId
      }
      
      await api.post('/auth/profile/field-update/', payload)
      
      if (fieldData.value[fieldName]) {
        fieldData.value[fieldName].visibility = data.privacy
      }
    }
    
    sectionPrivacy.value[data.section] = data.privacy
    console.log('Applied privacy to all fields in section:', data)
    
    // Don't refetch data immediately to avoid overriding the section privacy state
    // emit('profile-updated')
  } catch (err) {
    console.error('Error applying privacy to all fields:', err)
    alert('Failed to apply privacy to all fields. Please try again.')
  }
}

// Lifecycle
onMounted(() => {
  fetchProfileData()
})
</script>

<style scoped>
.line-clamp-4 {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
