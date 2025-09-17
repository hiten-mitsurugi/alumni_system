<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h2 class="text-xl font-semibold text-gray-900">Edit Profile</h2>
        <button 
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="saveProfile" class="p-6 space-y-6">
        <!-- Basic Information -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">Basic Information</h3>
          
          <!-- Headline -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Headline
            </label>
            <input 
              v-model="formData.headline"
              type="text"
              placeholder="e.g., Software Engineer at Tech Corp"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
            <p class="text-xs text-gray-500 mt-1">
              A brief professional title or description
            </p>
          </div>

          <!-- Location -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Location
            </label>
            <input 
              v-model="formData.location"
              type="text"
              placeholder="e.g., San Francisco, CA"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>

          <!-- Summary/About -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              About / Summary
            </label>
            <textarea 
              v-model="formData.summary"
              rows="4"
              placeholder="Write a brief summary about yourself, your experience, and your interests..."
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
            ></textarea>
            <p class="text-xs text-gray-500 mt-1">
              {{ formData.summary?.length || 0 }}/2000 characters
            </p>
          </div>
        </div>

        <!-- Address Information -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">Address Information</h3>
          
          <!-- Present Address -->
          <div>
            <h4 class="text-md font-medium text-gray-700 mb-3">Present Address</h4>
            <AddressSelector 
              v-model="formData.present_address_data"
              label="Present Address"
            />
          </div>

          <!-- Permanent Address -->
          <div>
            <h4 class="text-md font-medium text-gray-700 mb-3">Permanent Address</h4>
            <div class="mb-3">
              <label class="flex items-center">
                <input 
                  v-model="formData.same_as_present"
                  type="checkbox"
                  class="text-green-600 focus:ring-green-500 rounded"
                />
                <span class="ml-2 text-sm text-gray-700">Same as present address</span>
              </label>
            </div>
            <div v-if="!formData.same_as_present">
              <AddressSelector 
                v-model="formData.permanent_address_data"
                label="Permanent Address"
              />
            </div>
          </div>
        </div>

        <!-- Social Links -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">Social Links</h3>
          
          <!-- LinkedIn -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              LinkedIn URL
            </label>
            <input 
              v-model="formData.linkedin_url"
              type="url"
              placeholder="https://linkedin.com/in/yourprofile"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>

          <!-- Website -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Website URL
            </label>
            <input 
              v-model="formData.website_url"
              type="url"
              placeholder="https://yourwebsite.com"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>

          <!-- Facebook -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Facebook URL
            </label>
            <input 
              v-model="formData.facebook_url"
              type="url"
              placeholder="https://facebook.com/yourprofile"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>

          <!-- Twitter -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Twitter URL
            </label>
            <input 
              v-model="formData.twitter_url"
              type="url"
              placeholder="https://twitter.com/yourhandle"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>

          <!-- Instagram -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Instagram URL
            </label>
            <input 
              v-model="formData.instagram_url"
              type="url"
              placeholder="https://instagram.com/yourhandle"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>
        </div>

        <!-- Privacy Settings -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">Privacy Settings</h3>
          
          <!-- Profile Visibility -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Profile Visibility
            </label>
            <div class="space-y-2">
              <label class="flex items-center">
                <input 
                  v-model="formData.profile_visibility"
                  type="radio"
                  value="public"
                  class="text-green-600 focus:ring-green-500"
                />
                <span class="ml-2 text-sm text-gray-700">
                  Public - Anyone can view your profile
                </span>
              </label>
              <label class="flex items-center">
                <input 
                  v-model="formData.profile_visibility"
                  type="radio"
                  value="alumni_only"
                  class="text-green-600 focus:ring-green-500"
                />
                <span class="ml-2 text-sm text-gray-700">
                  Alumni Only - Only fellow alumni can view your profile
                </span>
              </label>
              <label class="flex items-center">
                <input 
                  v-model="formData.profile_visibility"
                  type="radio"
                  value="connections_only"
                  class="text-green-600 focus:ring-green-500"
                />
                <span class="ml-2 text-sm text-gray-700">
                  Connections Only - Only your connections can view your profile
                </span>
              </label>
            </div>
          </div>

          <!-- Contact Permissions -->
          <div class="space-y-3">
            <label class="flex items-center">
              <input 
                v-model="formData.allow_contact"
                type="checkbox"
                class="text-green-600 focus:ring-green-500 rounded"
              />
              <span class="ml-2 text-sm text-gray-700">
                Allow others to contact me
              </span>
            </label>

            <label class="flex items-center">
              <input 
                v-model="formData.allow_messaging"
                type="checkbox"
                class="text-green-600 focus:ring-green-500 rounded"
              />
              <span class="ml-2 text-sm text-gray-700">
                Allow direct messaging
              </span>
            </label>
          </div>
        </div>

        <!-- Form Actions -->
        <div class="flex justify-end space-x-3 pt-6 border-t border-gray-200">
          <button 
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Cancel
          </button>
          <button 
            type="submit"
            :disabled="saving"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
          >
            <span v-if="saving" class="animate-spin mr-2">⟳</span>
            Save Changes
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import AddressSelector from '@/components/common/AddressSelector.vue'

const props = defineProps({
  profile: Object
})

const emit = defineEmits(['close', 'save'])

const saving = ref(false)

const formData = reactive({
  headline: '',
  location: '',
  summary: '',
  linkedin_url: '',
  website_url: '',
  facebook_url: '',
  twitter_url: '',
  instagram_url: '',
  profile_visibility: 'public',
  allow_contact: true,
  allow_messaging: true,
  // Address fields
  present_address_data: {
    address_type: 'philippines',
    region_code: '',
    region_name: '',
    province_code: '',
    province_name: '',
    city_code: '',
    city_name: '',
    barangay: '',
    street_address: '',
    postal_code: '',
    country: '',
    full_address: ''
  },
  permanent_address_data: {
    address_type: 'philippines',
    region_code: '',
    region_name: '',
    province_code: '',
    province_name: '',
    city_code: '',
    city_name: '',
    barangay: '',
    street_address: '',
    postal_code: '',
    country: '',
    full_address: ''
  },
  same_as_present: false
})

// Watch for "same as present address" checkbox
watch(() => formData.same_as_present, (newValue) => {
  if (newValue) {
    Object.assign(formData.permanent_address_data, formData.present_address_data);
  }
});

// Watch for changes in present address when "same as present" is checked
watch(() => formData.present_address_data, (newAddressData) => {
  if (formData.same_as_present) {
    Object.assign(formData.permanent_address_data, newAddressData);
  }
}, { deep: true });

const initializeForm = () => {
  if (props.profile) {
    Object.keys(formData).forEach(key => {
      if (props.profile[key] !== undefined) {
        if (key === 'present_address_data' || key === 'permanent_address_data') {
          // Handle address data objects
          if (props.profile[key] && typeof props.profile[key] === 'object') {
            Object.assign(formData[key], props.profile[key]);
          }
        } else {
          formData[key] = props.profile[key]
        }
      }
    })
  }
}

const saveProfile = async () => {
  try {
    saving.value = true
    
    // Validate URLs if provided
    const urlFields = ['linkedin_url', 'website_url', 'facebook_url', 'twitter_url', 'instagram_url']
    for (const field of urlFields) {
      if (formData[field] && !isValidUrl(formData[field])) {
        alert(`Please enter a valid URL for ${field.replace('_url', '').replace('_', ' ')}`)
        return
      }
    }
    
    // Validate summary length
    if (formData.summary && formData.summary.length > 2000) {
      alert('Summary must be 2000 characters or less')
      return
    }
    
    emit('save', { ...formData })
  } catch (error) {
    console.error('Error saving profile:', error)
    alert('Failed to save profile. Please try again.')
  } finally {
    saving.value = false
  }
}

const isValidUrl = (url) => {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

onMounted(() => {
  initializeForm()
})
</script>
