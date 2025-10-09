<script setup>
import { ref, computed } from 'vue'
import { 
  User as UserIcon, 
  Camera as CameraIcon, 
  Save as SaveIcon,
  Upload as UploadIcon,
  AlertCircle as AlertIcon
} from 'lucide-vue-next'
import { useProfile } from '@/composables/useProfile'
import { imageUtils, formatUtils } from '@/utils/settingsHelpers'

// Props
const props = defineProps({
  themeStore: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['save-success', 'save-error'])

// Composables
const {
  profileForm,
  isUpdatingProfile,
  isUploadingPicture,
  profileErrors,
  profilePicturePreview,
  hasProfileChanges,
  user,
  handleProfilePictureChange,
  saveProfile,
  resetProfileForm,
  getProfilePictureUrl
} = useProfile()

// Local state
const showProfilePictureModal = ref(false)
const profilePictureInput = ref(null)

// Computed
const currentProfilePicture = computed(() => {
  if (profilePicturePreview.value) {
    return profilePicturePreview.value
  }
  return getProfilePictureUrl(user.value.profile_picture)
})

// Methods
const triggerProfilePictureUpload = () => {
  profilePictureInput.value?.click()
}

const onProfilePictureChange = async (event) => {
  try {
    await handleProfilePictureChange(event)
    emit('save-success', 'Profile picture updated successfully!')
  } catch (error) {
    emit('save-error', 'Failed to upload profile picture', error.message)
  }
}

const onSaveProfile = async () => {
  try {
    await saveProfile()
    emit('save-success', 'Profile updated successfully!')
  } catch (error) {
    emit('save-error', 'Failed to update profile', error.message)
  }
}

const onResetForm = () => {
  resetProfileForm()
}

// Format error display
const getFieldError = (fieldName) => {
  return profileErrors.value[fieldName] || null
}
</script>

<template>
  <div class="p-6 rounded-xl border transition-colors duration-200"
       :class="themeStore.isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'">
    
    <!-- Header -->
    <div class="flex items-center gap-3 mb-6">
      <UserIcon class="w-6 h-6 text-blue-600" />
      <h3 class="text-xl font-semibold"
          :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
        Profile Settings
      </h3>
    </div>

    <!-- Profile Picture Section -->
    <div class="mb-8">
      <label class="block text-sm font-medium mb-3"
             :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
        Profile Picture
      </label>
      
      <div class="flex items-center gap-6">
        <!-- Profile Picture Display -->
        <div class="relative group">
          <img :src="currentProfilePicture"
               alt="Profile"
               class="w-24 h-24 rounded-full object-cover border-4 border-blue-100 dark:border-blue-900 transition-transform duration-200 group-hover:scale-105">
          
          <!-- Upload Overlay -->
          <div class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-200 cursor-pointer"
               @click="triggerProfilePictureUpload">
            <CameraIcon class="w-6 h-6 text-white" />
          </div>

          <!-- Loading Indicator -->
          <div v-if="isUploadingPicture"
               class="absolute inset-0 flex items-center justify-center bg-blue-600 bg-opacity-75 rounded-full">
            <div class="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          </div>
        </div>

        <!-- Upload Controls -->
        <div class="flex-1">
          <div class="flex gap-3 mb-2">
            <button @click="triggerProfilePictureUpload"
                    :disabled="isUploadingPicture"
                    class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
              <UploadIcon class="w-4 h-4" />
              {{ isUploadingPicture ? 'Uploading...' : 'Upload New Photo' }}
            </button>
            
            <button v-if="profilePicturePreview"
                    @click="profilePicturePreview = null"
                    class="px-4 py-2 border rounded-lg transition-colors"
                    :class="themeStore.isDarkMode 
                      ? 'border-gray-600 text-gray-300 hover:bg-gray-700' 
                      : 'border-gray-300 text-gray-700 hover:bg-gray-50'">
              Cancel
            </button>
          </div>
          
          <p class="text-sm"
             :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'">
            JPG, PNG, GIF or WebP. Max file size 5MB.
          </p>
        </div>

        <!-- Hidden file input -->
        <input ref="profilePictureInput"
               type="file"
               accept="image/*"
               @change="onProfilePictureChange"
               class="hidden">
      </div>
    </div>

    <!-- Profile Form -->
    <div class="space-y-6">
      <!-- Basic Information -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- First Name -->
        <div>
          <label class="block text-sm font-medium mb-2"
                 :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            First Name *
          </label>
          <input v-model="profileForm.firstName"
                 type="text"
                 :class="[
                   'w-full px-4 py-2 rounded-lg border transition-colors duration-200',
                   getFieldError('firstName') 
                     ? 'border-red-500 focus:border-red-500' 
                     : 'focus:border-blue-500',
                   themeStore.isDarkMode
                     ? 'bg-gray-700 border-gray-600 text-white'
                     : 'bg-white border-gray-300 text-gray-900'
                 ]"
                 placeholder="Enter your first name">
          <p v-if="getFieldError('firstName')" class="text-red-500 text-sm mt-1">
            {{ getFieldError('firstName') }}
          </p>
        </div>

        <!-- Last Name -->
        <div>
          <label class="block text-sm font-medium mb-2"
                 :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            Last Name *
          </label>
          <input v-model="profileForm.lastName"
                 type="text"
                 :class="[
                   'w-full px-4 py-2 rounded-lg border transition-colors duration-200',
                   getFieldError('lastName') 
                     ? 'border-red-500 focus:border-red-500' 
                     : 'focus:border-blue-500',
                   themeStore.isDarkMode
                     ? 'bg-gray-700 border-gray-600 text-white'
                     : 'bg-white border-gray-300 text-gray-900'
                 ]"
                 placeholder="Enter your last name">
          <p v-if="getFieldError('lastName')" class="text-red-500 text-sm mt-1">
            {{ getFieldError('lastName') }}
          </p>
        </div>

        <!-- Email -->
        <div>
          <label class="block text-sm font-medium mb-2"
                 :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            Email Address *
          </label>
          <input v-model="profileForm.email"
                 type="email"
                 :class="[
                   'w-full px-4 py-2 rounded-lg border transition-colors duration-200',
                   getFieldError('email') 
                     ? 'border-red-500 focus:border-red-500' 
                     : 'focus:border-blue-500',
                   themeStore.isDarkMode
                     ? 'bg-gray-700 border-gray-600 text-white'
                     : 'bg-white border-gray-300 text-gray-900'
                 ]"
                 placeholder="Enter your email address">
          <p v-if="getFieldError('email')" class="text-red-500 text-sm mt-1">
            {{ getFieldError('email') }}
          </p>
        </div>

        <!-- Phone -->
        <div>
          <label class="block text-sm font-medium mb-2"
                 :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            Phone Number
          </label>
          <input v-model="profileForm.phone"
                 type="tel"
                 :class="[
                   'w-full px-4 py-2 rounded-lg border transition-colors duration-200',
                   getFieldError('phone') 
                     ? 'border-red-500 focus:border-red-500' 
                     : 'focus:border-blue-500',
                   themeStore.isDarkMode
                     ? 'bg-gray-700 border-gray-600 text-white'
                     : 'bg-white border-gray-300 text-gray-900'
                 ]"
                 placeholder="Enter your phone number">
          <p v-if="getFieldError('phone')" class="text-red-500 text-sm mt-1">
            {{ getFieldError('phone') }}
          </p>
        </div>
      </div>

      <!-- Additional Information -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Location -->
        <div>
          <label class="block text-sm font-medium mb-2"
                 :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            Location
          </label>
          <input v-model="profileForm.location"
                 type="text"
                 :class="[
                   'w-full px-4 py-2 rounded-lg border transition-colors duration-200 focus:border-blue-500',
                   themeStore.isDarkMode
                     ? 'bg-gray-700 border-gray-600 text-white'
                     : 'bg-white border-gray-300 text-gray-900'
                 ]"
                 placeholder="City, State/Province, Country">
        </div>

        <!-- Website -->
        <div>
          <label class="block text-sm font-medium mb-2"
                 :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            Website
          </label>
          <input v-model="profileForm.website"
                 type="url"
                 :class="[
                   'w-full px-4 py-2 rounded-lg border transition-colors duration-200',
                   getFieldError('website') 
                     ? 'border-red-500 focus:border-red-500' 
                     : 'focus:border-blue-500',
                   themeStore.isDarkMode
                     ? 'bg-gray-700 border-gray-600 text-white'
                     : 'bg-white border-gray-300 text-gray-900'
                 ]"
                 placeholder="https://yourwebsite.com">
          <p v-if="getFieldError('website')" class="text-red-500 text-sm mt-1">
            {{ getFieldError('website') }}
          </p>
        </div>
      </div>

      <!-- Bio -->
      <div>
        <label class="block text-sm font-medium mb-2"
               :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
          Bio
        </label>
        <textarea v-model="profileForm.bio"
                  rows="4"
                  :class="[
                    'w-full px-4 py-2 rounded-lg border transition-colors duration-200 resize-none',
                    getFieldError('bio') 
                      ? 'border-red-500 focus:border-red-500' 
                      : 'focus:border-blue-500',
                    themeStore.isDarkMode
                      ? 'bg-gray-700 border-gray-600 text-white'
                      : 'bg-white border-gray-300 text-gray-900'
                  ]"
                  placeholder="Tell us about yourself..."></textarea>
        <div class="flex justify-between items-center mt-1">
          <p v-if="getFieldError('bio')" class="text-red-500 text-sm">
            {{ getFieldError('bio') }}
          </p>
          <p class="text-sm ml-auto"
             :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'">
            {{ profileForm.bio.length }}/500 characters
          </p>
        </div>
      </div>

      <!-- Privacy Settings -->
      <div class="border-t pt-6"
           :class="themeStore.isDarkMode ? 'border-gray-700' : 'border-gray-200'">
        <h4 class="font-medium mb-4"
            :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
          Privacy Settings
        </h4>
        
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium"
                 :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                Public Profile
              </p>
              <p class="text-sm"
                 :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'">
                Allow others to find and view your profile
              </p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input v-model="profileForm.isPublic"
                     type="checkbox"
                     class="sr-only peer">
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium"
                 :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                Show Email
              </p>
              <p class="text-sm"
                 :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'">
                Display your email address on your public profile
              </p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input v-model="profileForm.showEmail"
                     type="checkbox"
                     class="sr-only peer">
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex justify-between pt-6 border-t"
           :class="themeStore.isDarkMode ? 'border-gray-700' : 'border-gray-200'">
        <button @click="onResetForm"
                type="button"
                class="px-6 py-2 border rounded-lg transition-colors"
                :class="themeStore.isDarkMode 
                  ? 'border-gray-600 text-gray-300 hover:bg-gray-700' 
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'">
          Reset Changes
        </button>

        <button @click="onSaveProfile"
                :disabled="isUpdatingProfile"
                class="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
          <SaveIcon class="w-4 h-4" />
          {{ isUpdatingProfile ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>

      <!-- Unsaved Changes Warning -->
      <div v-if="hasProfileChanges"
           class="flex items-center gap-3 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
        <AlertIcon class="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
        <p class="text-sm text-yellow-800 dark:text-yellow-200">
          You have unsaved changes. Don't forget to save your profile updates.
        </p>
      </div>
    </div>
  </div>
</template>