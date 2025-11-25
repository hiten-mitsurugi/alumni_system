<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <div class="w-full p-6 min-h-screen transition-colors duration-200">
    <!-- Header -->
    <div class="max-w-5xl mb-8">
      <h1 :style="{color: themeStore.isDarkMode ? '#e5e7eb' : '#1f2937'}" class="text-3xl font-bold mb-2">Settings</h1>
      <p :style="{color: themeStore.isDarkMode ? '#9ca3af' : '#4b5563'}" class="">Manage your account and preferences</p>
    </div>

    <!-- Settings Layout -->
    <div class="max-w-5xl grid lg:grid-cols-4 gap-8">
      <!-- Sidebar Navigation -->
      <div class="lg:col-span-1">
        <div :style="{backgroundColor: themeStore.isDarkMode ? '#1f2937' : '#ffffff', borderColor: themeStore.isDarkMode ? '#374151' : '#e5e7eb'}" class="rounded-xl shadow-sm border p-4 sticky top-6">
          <nav class="space-y-1">
            <button
              v-for="section in settingsSections"
              :key="section.id"
              @click="activeSection = section.id"
              :style="{
                backgroundColor: activeSection === section.id 
                  ? (themeStore.isDarkMode ? 'rgba(234, 88, 12, 0.2)' : '#fed7aa') 
                  : (themeStore.isDarkMode ? 'transparent' : 'transparent'),
                color: activeSection === section.id 
                  ? (themeStore.isDarkMode ? '#fb923c' : '#c2410c') 
                  : (themeStore.isDarkMode ? '#d1d5db' : '#374151'),
                borderLeft: activeSection === section.id ? '4px solid #ea580c' : 'none'
              }"
              class="w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200 hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <component :is="section.icon" class="h-5 w-5 mr-3" />
              {{ section.name }}
            </button>
          </nav>
        </div>
      </div>

      <!-- Content Area -->
      <div class="lg:col-span-3">
        <div :style="{backgroundColor: themeStore.isDarkMode ? '#1f2937' : '#ffffff', borderColor: themeStore.isDarkMode ? '#374151' : '#e5e7eb'}" class="rounded-xl shadow-sm border">
          <!-- Profile Settings -->
          <div v-if="activeSection === 'profile'" class="p-6">
            <div :style="{borderBottomColor: themeStore.isDarkMode ? '#4b5563' : '#e5e7eb'}" class="border-b pb-6 mb-6">
              <h2 :style="{color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}" class="text-xl font-semibold mb-1">Profile Information</h2>
              <p :style="{color: themeStore.isDarkMode ? '#9ca3af' : '#4b5563'}">Update your profile details and personal information</p>
            </div>

            <!-- Profile Picture Section -->
            <div class="mb-8">
              <h3 :style="{color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}" class="text-lg font-medium mb-4">Profile Picture</h3>
              <div class="flex items-center space-x-6">
                <div class="relative">
                  <img 
                    :src="profilePictureUrl" 
                    @error="handleImageError"
                    alt="Profile" 
                    class="w-24 h-24 rounded-full object-cover border-4 border-gray-200 dark:border-gray-600"
                  />
                  <button @click="triggerFileInput" class="absolute bottom-0 right-0 bg-orange-600 text-white p-2 rounded-full hover:bg-orange-700 transition-colors">
                    <CameraIcon class="h-4 w-4" />
                  </button>
                  <input 
                    ref="fileInput"
                    type="file" 
                    accept="image/*" 
                    @change="handleFileUpload" 
                    class="hidden"
                  />
                </div>
                <div>
                  <button @click="triggerFileInput" class="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors mr-3">
                    Upload New Photo
                  </button>
                  <button @click="removeProfilePicture" :style="{borderColor: themeStore.isDarkMode ? '#4b5563' : '#d1d5db', color: themeStore.isDarkMode ? '#d1d5db' : '#374151'}" class="border px-4 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                    Remove
                  </button>
                </div>
              </div>
            </div>

            <!-- Profile Form -->
            <form @submit.prevent="updateProfile" class="space-y-6">
              <div class="grid md:grid-cols-2 gap-6">
                <div>
                  <label :style="{color: themeStore.isDarkMode ? '#d1d5db' : '#374151'}" class="block text-sm font-medium mb-2">First Name</label>
                  <input 
                    v-model="profileForm.firstName" 
                    type="text" 
                    :style="{backgroundColor: themeStore.isDarkMode ? '#374151' : '#ffffff', borderColor: themeStore.isDarkMode ? '#4b5563' : '#d1d5db', color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}"
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  />
                </div>
                <div>
                  <label :style="{color: themeStore.isDarkMode ? '#d1d5db' : '#374151'}" class="block text-sm font-medium mb-2">Last Name</label>
                  <input 
                    v-model="profileForm.lastName" 
                    type="text" 
                    :style="{backgroundColor: themeStore.isDarkMode ? '#374151' : '#ffffff', borderColor: themeStore.isDarkMode ? '#4b5563' : '#d1d5db', color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}"
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  />
                </div>
              </div>

              <div>
                <label :style="{color: themeStore.isDarkMode ? '#d1d5db' : '#374151'}" class="block text-sm font-medium mb-2">Email</label>
                <input 
                  v-model="profileForm.email" 
                  type="email" 
                  :style="{backgroundColor: themeStore.isDarkMode ? '#374151' : '#ffffff', borderColor: themeStore.isDarkMode ? '#4b5563' : '#d1d5db', color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}"
                  class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                />
              </div>

              <div class="flex justify-end">
                <button type="submit" :disabled="isUpdatingProfile" class="bg-orange-600 text-white px-6 py-2 rounded-lg hover:bg-orange-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                  {{ isUpdatingProfile ? 'Saving...' : 'Save Changes' }}
                </button>
              </div>
            </form>
          </div>

          <!-- Privacy Settings -->
          <div v-if="activeSection === 'privacy'" class="p-6">
            <div :style="{borderBottomColor: themeStore.isDarkMode ? '#4b5563' : '#e5e7eb'}" class="border-b pb-6 mb-6">
              <h2 :style="{color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}" class="text-xl font-semibold mb-1">Privacy Settings</h2>
              <p :style="{color: themeStore.isDarkMode ? '#9ca3af' : '#4b5563'}">Control who can see your information and activities</p>
            </div>

            <div class="space-y-6">
              <!-- Profile Visibility -->
              <div :style="{borderColor: themeStore.isDarkMode ? '#4b5563' : '#e5e7eb'}" class="border rounded-lg p-4">
                <h3 :style="{color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}" class="text-lg font-medium mb-3">Profile Visibility</h3>
                <div class="space-y-4">
                  <div class="flex items-center justify-between">
                    <div class="flex-1">
                      <p :style="{color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}" class="font-medium">Make profile visible to</p>
                      <p :style="{color: themeStore.isDarkMode ? '#9ca3af' : '#6b7280'}" class="text-sm">Choose who can see your profile information</p>
                    </div>
                    <select v-model="privacySettings.profileVisibility" :style="{backgroundColor: themeStore.isDarkMode ? '#374151' : '#ffffff', borderColor: themeStore.isDarkMode ? '#4b5563' : '#d1d5db', color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}" class="border rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500">
                      <option value="public">Public - Everyone can see</option>
                      <option value="connections_only">Connections Only</option>
                      <option value="private">Private - Only me</option>
                    </select>
                  </div>
                  
                  <!-- Save Button and Feedback -->
                  <div class="flex items-center gap-3">
                    <button 
                      @click="savePrivacySettings" 
                      :disabled="isSavingPrivacy"
                      :class="[
                        'px-4 py-2 rounded-lg transition-colors font-medium',
                        isSavingPrivacy 
                          ? 'bg-gray-400 text-white cursor-not-allowed' 
                          : 'bg-orange-600 text-white hover:bg-orange-700'
                      ]">
                      {{ isSavingPrivacy ? 'Saving...' : 'Save Privacy Settings' }}
                    </button>
                    <div v-if="privacyMessage" :class="[
                      'text-sm font-medium',
                      privacyMessageType === 'success' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                    ]">
                      {{ privacyMessage }}
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>

          <!-- Account Settings -->
          <div v-if="activeSection === 'account'" class="p-6">
            <div :style="{borderBottomColor: themeStore.isDarkMode ? '#4b5563' : '#e5e7eb'}" class="border-b pb-6 mb-6">
              <h2 :style="{color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}" class="text-xl font-semibold mb-1">Account Settings</h2>
              <p :style="{color: themeStore.isDarkMode ? '#9ca3af' : '#4b5563'}">Manage your account security and preferences</p>
            </div>

            <div class="space-y-6">
              <!-- Password Change -->
              <div :style="{borderColor: themeStore.isDarkMode ? '#4b5563' : '#e5e7eb'}" class="border rounded-lg p-4">
                <h3 :style="{color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}" class="text-lg font-medium mb-3">Change Password</h3>
                <form @submit.prevent="changePassword" class="space-y-4">
                  <div>
                    <label :style="{color: themeStore.isDarkMode ? '#d1d5db' : '#374151'}" class="block text-sm font-medium mb-2">Current Password</label>
                    <input 
                      v-model="passwordForm.currentPassword" 
                      type="password" 
                      :style="{backgroundColor: themeStore.isDarkMode ? '#374151' : '#ffffff', borderColor: themeStore.isDarkMode ? '#4b5563' : '#d1d5db', color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}"
                      class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      required
                    />
                  </div>
                  <div>
                    <label :style="{color: themeStore.isDarkMode ? '#d1d5db' : '#374151'}" class="block text-sm font-medium mb-2">New Password</label>
                    <input 
                      v-model="passwordForm.newPassword" 
                      type="password" 
                      :style="{backgroundColor: themeStore.isDarkMode ? '#374151' : '#ffffff', borderColor: themeStore.isDarkMode ? '#4b5563' : '#d1d5db', color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}"
                      class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      required
                      minlength="8"
                    />
                  </div>
                  <div>
                    <label :style="{color: themeStore.isDarkMode ? '#d1d5db' : '#374151'}" class="block text-sm font-medium mb-2">Confirm New Password</label>
                    <input 
                      v-model="passwordForm.confirmPassword" 
                      type="password" 
                      :style="{backgroundColor: themeStore.isDarkMode ? '#374151' : '#ffffff', borderColor: themeStore.isDarkMode ? '#4b5563' : '#d1d5db', color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}"
                      class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      required
                    />
                  </div>
                  
                  <!-- Password Change Feedback -->
                  <div v-if="passwordMessage" :class="[
                    'p-3 rounded-lg text-sm',
                    passwordMessageType === 'success' ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300' :
                    passwordMessageType === 'error' ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300' :
                    'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300'
                  ]">
                    {{ passwordMessage }}
                  </div>
                  
                  <button type="submit" :disabled="isChangingPassword" :class="[
                    'px-4 py-2 rounded-lg transition-colors',
                    isChangingPassword 
                      ? 'bg-gray-400 text-white cursor-not-allowed' 
                      : 'bg-orange-600 text-white hover:bg-orange-700'
                  ]">
                    {{ isChangingPassword ? 'Updating...' : 'Update Password' }}
                  </button>
                </form>
              </div>
            </div>
          </div>

          <!-- Appearance Settings -->
          <div v-if="activeSection === 'appearance'" class="p-6">
            <div :style="{borderBottomColor: themeStore.isDarkMode ? '#4b5563' : '#e5e7eb'}" class="border-b pb-6 mb-6">
              <h2 :style="{color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}" class="text-xl font-semibold mb-1">Appearance</h2>
              <p :style="{color: themeStore.isDarkMode ? '#9ca3af' : '#4b5563'}">Customize how the interface looks</p>
            </div>

            <div class="space-y-6">
              <!-- Theme Selection -->
              <div :style="{borderColor: themeStore.isDarkMode ? '#4b5563' : '#e5e7eb'}" class="border rounded-lg p-4">
                <h3 :style="{color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}" class="text-lg font-medium mb-3">Theme</h3>
                <div class="grid grid-cols-3 gap-4">
                  <button 
                    v-for="theme in themes"
                    :key="theme.id"
                    @click="handleThemeChange(theme.id)"
                    :class="[
                      'p-4 border-2 rounded-lg transition-all duration-200 bg-white dark:bg-gray-700',
                      currentTheme === theme.id 
                        ? 'border-orange-500 ring-2 ring-orange-200 dark:ring-orange-800' 
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                    ]"
                  >
                    <div class="flex flex-col items-center">
                      <div :class="['w-12 h-8 rounded mb-2', theme.preview]"></div>
                      <span :style="{color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}" class="text-sm font-medium">{{ theme.name }}</span>
                    </div>
                  </button>
                </div>
                
                <!-- Theme Status -->
                <div class="mt-4 p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20">
                  <div class="flex items-center">
                    <div class="w-3 h-3 rounded-full mr-3"
                         :class="isDarkMode ? 'bg-blue-400' : 'bg-yellow-500'">
                    </div>
                    <p class="text-sm text-blue-700 dark:text-blue-300">
                      Currently using {{ isDarkMode ? 'Dark' : 'Light' }} mode
                    </p>
                  </div>
                </div>
              </div>

              <!-- Language -->
              <div :style="{borderColor: themeStore.isDarkMode ? '#4b5563' : '#e5e7eb'}" class="border rounded-lg p-4">
                <h3 :style="{color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}" class="text-lg font-medium mb-3">Language</h3>
                <select v-model="selectedLanguage" :style="{backgroundColor: themeStore.isDarkMode ? '#374151' : '#ffffff', borderColor: themeStore.isDarkMode ? '#4b5563' : '#d1d5db', color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}" class="border rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500">
                  <option value="en">English</option>
                  <option value="es">Español</option>
                  <option value="fr">Français</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Help & Support -->
          <div v-if="activeSection === 'support'" class="p-6">
            <div :style="{borderBottomColor: themeStore.isDarkMode ? '#4b5563' : '#e5e7eb'}" class="border-b pb-6 mb-6">
              <h2 :style="{color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}" class="text-xl font-semibold mb-1">Help & Support</h2>
              <p :style="{color: themeStore.isDarkMode ? '#9ca3af' : '#4b5563'}">Get help and contact support</p>
            </div>

            <div class="space-y-6">
              <!-- Help Resources -->
              <div class="grid md:grid-cols-2 gap-6">
                <a href="#" :style="{borderColor: themeStore.isDarkMode ? '#4b5563' : '#e5e7eb'}" class="border rounded-lg p-4 hover:border-orange-300 dark:hover:border-orange-500 transition-colors">
                  <div class="flex items-center">
                    <QuestionMarkCircleIcon class="h-8 w-8 text-orange-600 mr-3" />
                    <div>
                      <h3 :style="{color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}" class="font-semibold">FAQ</h3>
                      <p :style="{color: themeStore.isDarkMode ? '#9ca3af' : '#6b7280'}" class="text-sm">Find answers to common questions</p>
                    </div>
                  </div>
                </a>
                <a href="#" :style="{borderColor: themeStore.isDarkMode ? '#4b5563' : '#e5e7eb'}" class="border rounded-lg p-4 hover:border-orange-300 dark:hover:border-orange-500 transition-colors">
                  <div class="flex items-center">
                    <ChatBubbleLeftRightIcon class="h-8 w-8 text-orange-600 mr-3" />
                    <div>
                      <h3 :style="{color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}" class="font-semibold">Contact Support</h3>
                      <p :style="{color: themeStore.isDarkMode ? '#9ca3af' : '#6b7280'}" class="text-sm">Get help from our support team</p>
                    </div>
                  </div>
                </a>
              </div>

              <!-- Feedback -->
              <div :style="{borderColor: themeStore.isDarkMode ? '#4b5563' : '#e5e7eb'}" class="border rounded-lg p-4">
                <h3 :style="{color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}" class="text-lg font-medium mb-3">Send Feedback</h3>
                <form @submit.prevent="submitFeedback" class="space-y-4">
                  <textarea 
                    v-model="feedbackText" 
                    rows="4" 
                    placeholder="Tell us what you think..."
                    :style="{backgroundColor: themeStore.isDarkMode ? '#374151' : '#ffffff', borderColor: themeStore.isDarkMode ? '#4b5563' : '#d1d5db', color: themeStore.isDarkMode ? '#f3f4f6' : '#111827'}"
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  ></textarea>
                  <button type="submit" class="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors">
                    Send Feedback
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { 
  UserIcon, 
  LockClosedIcon, 
  UserCircleIcon, 
  PaintBrushIcon, 
  QuestionMarkCircleIcon,
  ChatBubbleLeftRightIcon,
  CameraIcon 
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()
const themeStore = useThemeStore()
const BASE_URL = `${window.location.protocol}//${window.location.hostname}:8000`

// State
const activeSection = ref('profile')
const selectedTheme = ref('light')
const selectedLanguage = ref('en')
const feedbackText = ref('')
const fileInput = ref(null)
const isUpdatingProfile = ref(false)
const isUploadingPhoto = ref(false)
const isChangingPassword = ref(false)
const isSavingPrivacy = ref(false)
const passwordMessage = ref('')
const passwordMessageType = ref('')
const privacyMessage = ref('')
const privacyMessageType = ref('success')

// Settings sections
const settingsSections = [
  { id: 'profile', name: 'Profile', icon: UserIcon },
  { id: 'privacy', name: 'Privacy', icon: LockClosedIcon },
  { id: 'account', name: 'Account', icon: UserCircleIcon },
  { id: 'appearance', name: 'Appearance', icon: PaintBrushIcon },
  { id: 'support', name: 'Help & Support', icon: QuestionMarkCircleIcon }
]

// Theme options
const themes = [
  { id: 'light', name: 'Light', preview: 'bg-white border border-gray-300' },
  { id: 'dark', name: 'Dark', preview: 'bg-gray-800 border border-gray-600' },
  { id: 'auto', name: 'Auto', preview: 'bg-gradient-to-r from-white via-gray-400 to-gray-800 border border-gray-300' }
]

// Computed
const currentTheme = computed(() => {
  // Return the selected theme preference, not just the current mode
  return selectedTheme.value
})

const isDarkMode = computed(() => themeStore.isDarkMode)

// Forms
const profileForm = ref({
  firstName: '',
  lastName: '',
  email: ''
})

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const privacySettings = ref({
  profileVisibility: 'public'  // will be loaded from user data
})

// Computed
const profilePictureUrl = computed(() => {
  const user = authStore.user
  const pic = user?.profile_picture
  
  if (!pic || pic === '' || pic === 'null') {
    return '/default-avatar.png'
  }
  
  try {
    if (pic.startsWith('http://') || pic.startsWith('https://')) {
      return pic
    }
    
    const relativePath = pic.startsWith('/') ? pic : `/${pic}`
    return `${BASE_URL}${relativePath}`
  } catch {
    return '/default-avatar.png'
  }
})

// Methods
function handleImageError(event) {
  event.target.src = '/default-avatar.png'
}

async function updateProfile() {
  if (isUpdatingProfile.value) return
  
  try {
    isUpdatingProfile.value = true
    
    const updateData = {
      first_name: profileForm.value.firstName,
      last_name: profileForm.value.lastName,
      email: profileForm.value.email
    }
    
    console.log('Updating profile with:', updateData)
    
    const response = await fetch(`${BASE_URL}/api/auth/profile/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify(updateData)
    })
    
    if (response.ok) {
      const updatedUser = await response.json()
      authStore.setUser(updatedUser)
      
      // Update the form with the new data to prevent reversion on refresh
      profileForm.value = {
        firstName: updatedUser.first_name || '',
        lastName: updatedUser.last_name || '',
        email: updatedUser.email || ''
      }
      
      console.log('Profile updated successfully')
      // You could add a success notification here
    } else {
      console.error('Failed to update profile:', await response.text())
      // You could add an error notification here
    }
  } catch (error) {
    console.error('Error updating profile:', error)
  } finally {
    isUpdatingProfile.value = false
  }
}

function triggerFileInput() {
  fileInput.value?.click()
}

async function handleFileUpload(event) {
  const file = event.target.files?.[0]
  if (!file) return
  
  try {
    isUploadingPhoto.value = true
    
    const formData = new FormData()
    formData.append('profile_picture', file)
    
    console.log('Uploading profile picture...')
    
    const response = await fetch(`${BASE_URL}/api/auth/profile/`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      },
      body: formData
    })
    
    if (response.ok) {
      const updatedUser = await response.json()
      authStore.setUser(updatedUser)
      
      // Update form data to reflect current user state
      profileForm.value = {
        firstName: updatedUser.first_name || '',
        lastName: updatedUser.last_name || '',
        email: updatedUser.email || ''
      }
      
      console.log('Profile picture updated successfully')
      // You could add a success notification here
    } else {
      console.error('Failed to update profile picture:', await response.text())
      // You could add an error notification here
    }
  } catch (error) {
    console.error('Error uploading profile picture:', error)
  } finally {
    isUploadingPhoto.value = false
    // Clear the file input
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

async function removeProfilePicture() {
  try {
    isUploadingPhoto.value = true
    
    const response = await fetch(`${BASE_URL}/api/auth/profile/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({ profile_picture: null })
    })
    
    if (response.ok) {
      const updatedUser = await response.json()
      authStore.setUser(updatedUser)
      
      // Update form data to reflect current user state
      profileForm.value = {
        firstName: updatedUser.first_name || '',
        lastName: updatedUser.last_name || '',
        email: updatedUser.email || ''
      }
      
      console.log('Profile picture removed successfully')
      // You could add a success notification here
    } else {
      console.error('Failed to remove profile picture:', await response.text())
      // You could add an error notification here
    }
  } catch (error) {
    console.error('Error removing profile picture:', error)
  } finally {
    isUploadingPhoto.value = false
  }
}

async function changePassword() {
  if (isChangingPassword.value) return
  
  // Reset previous messages
  passwordMessage.value = ''
  passwordMessageType.value = ''
  
  // Validate passwords match
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    passwordMessage.value = 'New passwords do not match'
    passwordMessageType.value = 'error'
    return
  }
  
  // Validate password length
  if (passwordForm.value.newPassword.length < 8) {
    passwordMessage.value = 'Password must be at least 8 characters long'
    passwordMessageType.value = 'error'
    return
  }
  
  try {
    isChangingPassword.value = true
    
    const response = await fetch(`${BASE_URL}/api/auth/change-password/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        current_password: passwordForm.value.currentPassword,
        new_password: passwordForm.value.newPassword
      })
    })
    
    if (response.ok) {
      passwordMessage.value = 'Password updated successfully! You can now use your new password to login.'
      passwordMessageType.value = 'success'
      
      // Clear the form
      passwordForm.value = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
      
      console.log('Password changed successfully')
    } else {
      const errorData = await response.json()
      passwordMessage.value = errorData.error || errorData.message || 'Failed to update password'
      passwordMessageType.value = 'error'
      console.error('Failed to change password:', errorData)
    }
  } catch (error) {
    passwordMessage.value = 'An error occurred while updating password'
    passwordMessageType.value = 'error'
    console.error('Error changing password:', error)
  } finally {
    isChangingPassword.value = false
  }
}

async function savePrivacySettings() {
  if (isSavingPrivacy.value) return
  
  try {
    isSavingPrivacy.value = true
    privacyMessage.value = ''
    
    const response = await fetch(`${BASE_URL}/api/auth/profile/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        profile_visibility: privacySettings.value.profileVisibility
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      privacyMessage.value = 'Privacy settings saved successfully!'
      privacyMessageType.value = 'success'
      console.log('✅ Privacy settings updated:', result)
      
      // Clear message after 3 seconds
      setTimeout(() => {
        privacyMessage.value = ''
      }, 3000)
    } else {
      const error = await response.json()
      privacyMessage.value = error.error || 'Failed to save privacy settings'
      privacyMessageType.value = 'error'
      console.error('❌ Failed to save privacy settings:', error)
    }
  } catch (error) {
    privacyMessage.value = 'Network error. Please try again.'
    privacyMessageType.value = 'error'
    console.error('❌ Error saving privacy settings:', error)
  } finally {
    isSavingPrivacy.value = false
  }
}

function submitFeedback() {
  console.log('Submitting feedback:', feedbackText.value)
  // Add API call to submit feedback
}

function handleThemeChange(themeId) {
  console.log('🌙 Theme change requested:', themeId)
  
  // AGGRESSIVE theme switching - bypass store initially
  if (themeId === 'light') {
    console.log('🌙 FORCING LIGHT MODE')
    // Force remove dark class multiple ways
    document.documentElement.classList.remove('dark')
    document.body.classList.remove('dark')
    document.querySelector('html').classList.remove('dark')
    
    // Set localStorage directly
    localStorage.setItem('theme', 'light')
    selectedTheme.value = 'light'
    
    // Update store state
    themeStore.setTheme('light')
    
  } else if (themeId === 'dark') {
    console.log('🌙 FORCING DARK MODE')
    // Force add dark class
    document.documentElement.classList.add('dark')
    document.body.classList.add('dark')
    
    localStorage.setItem('theme', 'dark')
    selectedTheme.value = 'dark'
    themeStore.setTheme('dark')
    
  } else if (themeId === 'auto') {
    console.log('🌙 Setting AUTO mode')
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    if (prefersDark) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
    selectedTheme.value = 'auto'
  }
  
  // Log final state
  setTimeout(() => {
    console.log('🔍 FINAL CHECK:')
    console.log('🔍 HTML has dark class:', document.documentElement.classList.contains('dark'))
    console.log('🔍 HTML classList:', [...document.documentElement.classList])
    console.log('🔍 localStorage theme:', localStorage.getItem('theme'))
    console.log('🔍 themeStore.isDarkMode:', themeStore.isDarkMode)
  }, 100)
}

// Initialize with user data
onMounted(async () => {
  const user = authStore.user
  if (user) {
    profileForm.value = {
      firstName: user.first_name || '',
      lastName: user.last_name || '',
      email: user.email || ''
    }
    
    // Load current profile visibility
    try {
      const response = await fetch(`${BASE_URL}/api/auth/enhanced-profile/`, {
        headers: {
          'Authorization': `Bearer ${authStore.token}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        if (data.profile && data.profile.profile_visibility) {
          privacySettings.value.profileVisibility = data.profile.profile_visibility
          console.log('✅ Loaded profile visibility:', data.profile.profile_visibility)
        }
      }
    } catch (error) {
      console.error('Error loading profile visibility:', error)
    }
  }
  
  // Initialize theme selection based on current theme
  const savedTheme = localStorage.getItem('theme')
  console.log('🔍 Settings page mounted - Checking theme:')
  console.log('🔍 localStorage theme:', savedTheme)
  console.log('🔍 themeStore.isDarkMode:', themeStore.isDarkMode)
  console.log('🔍 document.documentElement has dark class:', document.documentElement.classList.contains('dark'))
  
  // Force sync theme from localStorage
  if (savedTheme === 'light') {
    console.log('✅ Forcing light mode')
    document.documentElement.classList.remove('dark')
    document.body.classList.remove('dark')
    selectedTheme.value = 'light'
  } else if (savedTheme === 'dark') {
    console.log('✅ Forcing dark mode')
    document.documentElement.classList.add('dark')
    document.body.classList.add('dark')
    selectedTheme.value = 'dark'
  }
  
  // Verify after forcing
  setTimeout(() => {
    console.log('🔍 After force - document has dark class:', document.documentElement.classList.contains('dark'))
  }, 50)
})

// Watch for auth store changes to keep form in sync
import { watch } from 'vue'
watch(
  () => authStore.user,
  (newUser) => {
    if (newUser) {
      profileForm.value = {
        firstName: newUser.first_name || '',
        lastName: newUser.last_name || '',
        email: newUser.email || ''
      }
      console.log('📱 Settings: Auth store updated, refreshing form data')
    }
  },
  { deep: true }
)
</script>

<style scoped>
/* Additional custom styles if needed */
.animate-fade-in {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
