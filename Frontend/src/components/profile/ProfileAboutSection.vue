<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-900">About</h2>
      <div v-if="isOwnProfile" class="flex items-center gap-2">
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
      <span class="ml-3 text-gray-600">Loading profile data...</span>
    </div>

    <!-- Facebook-style About List -->
    <div v-else class="space-y-0">
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

      <!-- Headline -->
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

      <!-- Email -->
      <AboutItem
        v-if="fieldData['email']"
        icon="envelope"
        :field-data="fieldData['email']"
        :field-name="'email'"
        :field-label="'Email'"
        :is-own-profile="isOwnProfile"
        @update-field="updateField"
        @toggle-visibility="toggleVisibility"
      />

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

// Field categories (Professional and Academic fields removed - now handled by dedicated sections)
const personalFields = ['first_name', 'last_name', 'middle_name', 'email', 'birth_date', 'gender', 'civil_status']
const contactFields = ['contact_number', 'mobile_number', 'present_address', 'permanent_address']
const socialFields = ['linkedin_url', 'facebook_url', 'twitter_url', 'instagram_url', 'website_url']
const bioFields = ['bio', 'headline', 'location', 'summary']

// Field labels for display (Professional and Academic labels removed)
const fieldLabels = {
  first_name: 'First Name',
  last_name: 'Last Name',
  middle_name: 'Middle Name',
  email: 'Email Address (Login)',
  contact_number: 'Contact Number',
  mobile_number: 'Mobile Number',
  birth_date: 'Birth Date',
  gender: 'Gender',
  civil_status: 'Civil Status',
  present_address: 'Present Address',
  permanent_address: 'Permanent Address',
  linkedin_url: 'LinkedIn Profile',
  facebook_url: 'Facebook Profile',
  twitter_url: 'Twitter Profile',
  instagram_url: 'Instagram Profile',
  website_url: 'Website URL',
  bio: 'Biography',
  headline: 'Professional Headline',
  location: 'Location',
  summary: 'Summary'
}

// Methods
async function fetchProfileData() {
  try {
    loading.value = true
    error.value = null
    
    const url = props.userId 
      ? `/auth/profile/about-data/${props.userId}/`
      : '/auth/profile/about-data/'
    
    const response = await api.get(url)
    fieldData.value = response.data.field_data
    
    console.log('Profile data loaded:', response.data)
  } catch (err) {
    console.error('Error fetching profile data:', err)
    error.value = 'Failed to load profile data. Please try again.'
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
    
    console.log('Field updated:', response.data)
    emit('profile-updated')
  } catch (err) {
    console.error('Error updating field:', err)
    alert('Failed to update field. Please try again.')
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
    
    console.log('Visibility updated:', response.data)
  } catch (err) {
    console.error('Error updating visibility:', err)
    alert('Failed to update privacy setting. Please try again.')
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
