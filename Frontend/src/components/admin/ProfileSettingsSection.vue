<template>
  <div class="p-8">
    <div class="flex items-center gap-3 mb-6">
      <UserIcon class="w-6 h-6 text-orange-600" />
      <h2 class="text-2xl font-bold"
          :class="themeStore.isAdminDark() ? 'text-white' : 'text-gray-900'">
        Profile Settings
      </h2>
    </div>

    <!-- Profile Form -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      <div>
        <label class="block text-sm font-medium mb-2"
               :class="themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-700'">
          First Name
        </label>
        <input v-model="profileForm.firstName"
               type="text"
               class="w-full px-4 py-2 rounded-lg border transition-colors duration-200"
               :class="themeStore.isAdminDark()
                 ? 'bg-gray-700 border-gray-600 text-white focus:border-orange-500'
                 : 'bg-white border-gray-300 text-gray-900 focus:border-orange-500'">
      </div>
      <div>
        <label class="block text-sm font-medium mb-2"
               :class="themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-700'">
          Last Name
        </label>
        <input v-model="profileForm.lastName"
               type="text"
               class="w-full px-4 py-2 rounded-lg border transition-colors duration-200"
               :class="themeStore.isAdminDark()
                 ? 'bg-gray-700 border-gray-600 text-white focus:border-blue-500'
                 : 'bg-white border-gray-300 text-gray-900 focus:border-blue-500'">
      </div>
      <div>
        <label class="block text-sm font-medium mb-2"
               :class="themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-700'">
          Email
        </label>
        <input v-model="profileForm.email"
               type="email"
               class="w-full px-4 py-2 rounded-lg border transition-colors duration-200"
               :class="themeStore.isAdminDark()
                 ? 'bg-gray-700 border-gray-600 text-white focus:border-orange-500'
                 : 'bg-white border-gray-300 text-gray-900 focus:border-orange-500'">
      </div>
      <div>
        <label class="block text-sm font-medium mb-2"
               :class="themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-700'">
          Phone
        </label>
        <input v-model="profileForm.phone"
               type="tel"
               class="w-full px-4 py-2 rounded-lg border transition-colors duration-200"
               :class="themeStore.isAdminDark()
                 ? 'bg-gray-700 border-gray-600 text-white focus:border-orange-500'
                 : 'bg-white border-gray-300 text-gray-900 focus:border-orange-500'">
      </div>
    </div>

    <!-- Bio -->
    <div class="mb-8">
      <label class="block text-sm font-medium mb-2"
             :class="themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-700'">
        Bio
      </label>
      <textarea v-model="profileForm.bio"
                rows="4"
                class="w-full px-4 py-2 rounded-lg border transition-colors duration-200"
                :class="themeStore.isAdminDark()
                  ? 'bg-gray-700 border-gray-600 text-white focus:border-orange-500'
                  : 'bg-white border-gray-300 text-gray-900 focus:border-orange-500'"
                placeholder="Tell us about yourself..."></textarea>
    </div>

    <!-- Save Button -->
    <div class="flex justify-end">
      <button @click="saveProfileSettingsWrapper"
              :disabled="isLoading"
              class="flex items-center gap-2 px-6 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
        <SaveIcon class="w-4 h-4" />
        {{ isLoading ? 'Saving...' : 'Save Changes' }}
      </button>
    </div>
  </div>
</template>

<script setup>

import { useProfile } from '@/composables/useProfile'
import { useThemeStore } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'
import { watch } from 'vue'
import {
  User as UserIcon,
  Save as SaveIcon
} from 'lucide-vue-next'

const props = defineProps({
  user: {
    type: Object,
    default: () => ({})
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  getProfilePictureUrl: {
    type: Function,
    required: true
  },
  showSuccessMessage: {
    type: Function,
    required: true
  },
  showErrorMessage: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['profile-saved'])

const themeStore = useThemeStore()
const authStore = useAuthStore()

const { profileForm, saveProfile, profileErrors, initializeProfile } = useProfile()

// Sync profileForm with user prop on mount and when user changes
const fillFormFromUser = () => {
  if (props.user) {
    profileForm.value.firstName = props.user.first_name || ''
    profileForm.value.lastName = props.user.last_name || ''
    profileForm.value.email = props.user.email || ''
    profileForm.value.phone = props.user.contact_number || ''
    
    if (props.user.profile) {
      profileForm.value.bio = props.user.profile.bio || ''
      profileForm.value.location = props.user.profile.location || ''
      profileForm.value.website = props.user.profile.website || ''
      profileForm.value.birthDate = props.user.profile.birth_date || null
      profileForm.value.linkedinUrl = props.user.profile.linkedin_url || ''
      profileForm.value.twitterUrl = props.user.profile.twitter_url || ''
      profileForm.value.facebookUrl = props.user.profile.facebook_url || ''
      profileForm.value.instagramUrl = props.user.profile.instagram_url || ''
      profileForm.value.presentOccupation = props.user.profile.present_occupation || ''
      profileForm.value.employingAgency = props.user.profile.employing_agency || ''
      profileForm.value.isPublic = props.user.profile.is_public !== undefined ? props.user.profile.is_public : true
      profileForm.value.showEmail = props.user.profile.show_email || false
      profileForm.value.showPhone = props.user.profile.show_phone || false
      profileForm.value.allowContact = props.user.profile.allow_contact !== undefined ? props.user.profile.allow_contact : true
      profileForm.value.allowMessaging = props.user.profile.allow_messaging !== undefined ? props.user.profile.allow_messaging : true
    }
    
    // Debug log to see if form is populated
    console.log('Profile form filled:', profileForm.value)
  }
}

fillFormFromUser()
watch(() => props.user, fillFormFromUser, { deep: true })

const saveProfileSettingsWrapper = async () => {
  try {
    // Debug log before validation
    console.log('Form data before save:', profileForm.value)
    console.log('Profile errors before save:', profileErrors.value)
    
    const result = await saveProfile()
    props.showSuccessMessage('Success', 'Profile updated successfully')
    emit('profile-saved', result)
  } catch (error) {
    // Show validation errors if present
    let message = 'Failed to save profile'
    if (error && error.message === 'Please fix the validation errors before saving' && profileErrors.value) {
      // Show all validation errors from profileErrors
      const fieldErrors = Object.entries(profileErrors.value)
        .map(([field, msg]) => `${field}: ${msg}`)
        .join('\n')
      message = fieldErrors || error.message || message
    } else if (error && error.details) {
      // If backend returned field errors, show them all
      const fieldErrors = Object.entries(error.details)
        .map(([field, msg]) => `${field}: ${Array.isArray(msg) ? msg.join(', ') : msg}`)
        .join('\n')
      message = fieldErrors || error.message || message
    } else if (error && error.message) {
      message = error.message
    }
    // Log error for debugging
    // eslint-disable-next-line no-console
    console.error('Profile save error:', error)
    console.log('Current validation errors:', profileErrors.value)
    props.showErrorMessage('Error', message)
  }
}
</script>