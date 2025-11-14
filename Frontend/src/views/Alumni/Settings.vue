<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <div class="w-full p-6 bg-amber-50 dark:bg-gray-900 min-h-screen transition-colors duration-200">
    <!-- Header -->
    <div class="max-w-5xl mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">Settings</h1>
      <p class="text-gray-600 dark:text-gray-400">Manage your account and preferences</p>
    </div>

    <!-- Settings Layout -->
    <div class="max-w-5xl grid lg:grid-cols-4 gap-8">
      <!-- Sidebar Navigation -->
      <div class="lg:col-span-1">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 sticky top-6">
          <nav class="space-y-1">
            <button
              v-for="section in settingsSections"
              :key="section.id"
              @click="activeSection = section.id"
              :class="[
                'w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200',
                activeSection === section.id
                  ? 'bg-orange-50 dark:bg-orange-900/20 text-orange-700 dark:text-orange-300 border-l-4 border-orange-500'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100'
              ]"
            >
              <component :is="section.icon" class="h-5 w-5 mr-3" />
              {{ section.name }}
            </button>
          </nav>
        </div>
      </div>

      <!-- Content Area -->
      <div class="lg:col-span-3">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <!-- Profile Settings -->
          <div v-if="activeSection === 'profile'" class="p-6">
            <div class="border-b border-gray-200 dark:border-gray-600 pb-6 mb-6">
              <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-1">Profile Information</h2>
              <p class="text-gray-600 dark:text-gray-400">Update your profile details and personal information</p>
            </div>

            <!-- Profile Picture Section -->
            <div class="mb-8">
              <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Profile Picture</h3>
              <div class="flex items-center space-x-6">
                <div class="relative">
                  <img 
                    :src="profilePictureUrl" 
                    @error="handleImageError"
                    alt="Profile" 
                    class="w-24 h-24 rounded-full object-cover border-4 border-gray-200 dark:border-gray-600"
                  />
                  <button class="absolute bottom-0 right-0 bg-orange-600 text-white p-2 rounded-full hover:bg-orange-700 transition-colors">
                    <CameraIcon class="h-4 w-4" />
                  </button>
                </div>
                <div>
                  <button class="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors mr-3">
                    Upload New Photo
                  </button>
                  <button class="border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                    Remove
                  </button>
                </div>
              </div>
            </div>

            <!-- Profile Form -->
            <form @submit.prevent="updateProfile" class="space-y-6">
              <div class="grid md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">First Name</label>
                  <input 
                    v-model="profileForm.firstName" 
                    type="text" 
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 placeholder-gray-500 dark:placeholder-gray-400"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Last Name</label>
                  <input 
                    v-model="profileForm.lastName" 
                    type="text" 
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 placeholder-gray-500 dark:placeholder-gray-400"
                  />
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Email</label>
                <input 
                  v-model="profileForm.email" 
                  type="email" 
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 placeholder-gray-500 dark:placeholder-gray-400"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Bio</label>
                <textarea 
                  v-model="profileForm.bio" 
                  rows="4" 
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 placeholder-gray-500 dark:placeholder-gray-400"
                  placeholder="Tell us about yourself..."
                ></textarea>
              </div>

              <div class="flex justify-end">
                <button type="submit" class="bg-orange-600 text-white px-6 py-2 rounded-lg hover:bg-orange-700 transition-colors">
                  Save Changes
                </button>
              </div>
            </form>
          </div>

          <!-- Privacy Settings -->
          <div v-if="activeSection === 'privacy'" class="p-6">
            <div class="border-b border-gray-200 dark:border-gray-600 pb-6 mb-6">
              <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-1">Privacy Settings</h2>
              <p class="text-gray-600 dark:text-gray-400">Control who can see your information and activities</p>
            </div>

            <div class="space-y-6">
              <!-- Profile Visibility -->
              <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-3">Profile Visibility</h3>
                <div class="space-y-4">
                  <div class="flex items-center justify-between">
                    <div>
                      <p class="font-medium text-gray-900 dark:text-gray-100">Make profile visible to</p>
                      <p class="text-sm text-gray-500 dark:text-gray-400">Choose who can see your profile information</p>
                    </div>
                    <select v-model="privacySettings.profileVisibility" class="border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg px-3 py-2">
                      <option value="everyone" class="text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-700">Everyone</option>
                      <option value="alumni" class="text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-700">Alumni Only</option>
                      <option value="connections" class="text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-700">My Connections</option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- Contact Information -->
              <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-3">Contact Information</h3>
                <div class="space-y-4">
                  <div class="flex items-center justify-between">
                    <span class="text-gray-700 dark:text-gray-300">Show email address</span>
                    <ToggleSwitch v-model="privacySettings.showEmail" />
                  </div>
                  <div class="flex items-center justify-between">
                    <span class="text-gray-700 dark:text-gray-300">Show phone number</span>
                    <ToggleSwitch v-model="privacySettings.showPhone" />
                  </div>
                  <div class="flex items-center justify-between">
                    <span class="text-gray-700 dark:text-gray-300">Show graduation year</span>
                    <ToggleSwitch v-model="privacySettings.showGraduation" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Account Settings -->
          <div v-if="activeSection === 'account'" class="p-6">
            <div class="border-b border-gray-200 dark:border-gray-600 pb-6 mb-6">
              <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-1">Account Settings</h2>
              <p class="text-gray-600 dark:text-gray-400">Manage your account security and preferences</p>
            </div>

            <div class="space-y-6">
              <!-- Password Change -->
              <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-3">Change Password</h3>
                <form @submit.prevent="changePassword" class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Current Password</label>
                    <input 
                      v-model="passwordForm.currentPassword" 
                      type="password" 
                      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 placeholder-gray-500 dark:placeholder-gray-400"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">New Password</label>
                    <input 
                      v-model="passwordForm.newPassword" 
                      type="password" 
                      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 placeholder-gray-500 dark:placeholder-gray-400"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Confirm New Password</label>
                    <input 
                      v-model="passwordForm.confirmPassword" 
                      type="password" 
                      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 placeholder-gray-500 dark:placeholder-gray-400"
                    />
                  </div>
                  <button type="submit" class="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors">
                    Update Password
                  </button>
                </form>
              </div>

              <!-- Two-Factor Authentication -->
              <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-3">Two-Factor Authentication</h3>
                <div class="flex items-center justify-between">
                  <div>
                    <p class="font-medium text-gray-900 dark:text-gray-100">Enable 2FA</p>
                    <p class="text-sm text-gray-500 dark:text-gray-400">Add an extra layer of security to your account</p>
                  </div>
                  <button class="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors">
                    Setup
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Appearance Settings -->
          <div v-if="activeSection === 'appearance'" class="p-6">
            <div class="border-b border-gray-200 dark:border-gray-600 pb-6 mb-6">
              <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-1">Appearance</h2>
              <p class="text-gray-600 dark:text-gray-400">Customize how the interface looks</p>
            </div>

            <div class="space-y-6">
              <!-- Theme Selection -->
              <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-3">Theme</h3>
                <div class="grid grid-cols-3 gap-4">
                  <button 
                    v-for="theme in themes"
                    :key="theme.id"
                    @click="handleThemeChange(theme.id)"
                    :class="[
                      'p-4 border-2 rounded-lg transition-all duration-200',
                      currentTheme === theme.id 
                        ? 'border-orange-500 bg-orange-50 dark:bg-orange-900/20' 
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                    ]"
                  >
                    <div class="flex flex-col items-center">
                      <div :class="['w-12 h-8 rounded mb-2', theme.preview]"></div>
                      <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ theme.name }}</span>
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
              <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-3">Language</h3>
                <select v-model="selectedLanguage" class="border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg px-3 py-2">
                  <option value="en" class="text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-700">English</option>
                  <option value="es" class="text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-700">Español</option>
                  <option value="fr" class="text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-700">Français</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Help & Support -->
          <div v-if="activeSection === 'support'" class="p-6">
            <div class="border-b border-gray-200 dark:border-gray-600 pb-6 mb-6">
              <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-1">Help & Support</h2>
              <p class="text-gray-600 dark:text-gray-400">Get help and contact support</p>
            </div>

            <div class="space-y-6">
              <!-- Help Resources -->
              <div class="grid md:grid-cols-2 gap-6">
                <a href="#" class="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:border-orange-300 dark:hover:border-orange-500 transition-colors">
                  <div class="flex items-center">
                    <QuestionMarkCircleIcon class="h-8 w-8 text-orange-600 mr-3" />
                    <div>
                      <h3 class="font-semibold text-gray-900 dark:text-gray-100">FAQ</h3>
                      <p class="text-sm text-gray-500 dark:text-gray-400">Find answers to common questions</p>
                    </div>
                  </div>
                </a>
                <a href="#" class="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:border-orange-300 dark:hover:border-orange-500 transition-colors">
                  <div class="flex items-center">
                    <ChatBubbleLeftRightIcon class="h-8 w-8 text-orange-600 mr-3" />
                    <div>
                      <h3 class="font-semibold text-gray-900 dark:text-gray-100">Contact Support</h3>
                      <p class="text-sm text-gray-500 dark:text-gray-400">Get help from our support team</p>
                    </div>
                  </div>
                </a>
              </div>

              <!-- Feedback -->
              <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-3">Send Feedback</h3>
                <form @submit.prevent="submitFeedback" class="space-y-4">
                  <textarea 
                    v-model="feedbackText" 
                    rows="4" 
                    placeholder="Tell us what you think..."
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 placeholder-gray-500 dark:placeholder-gray-400"
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

// Components
const ToggleSwitch = {
  props: ['modelValue'],
  emits: ['update:modelValue'],
  template: `
    <button 
      @click="$emit('update:modelValue', !modelValue)"
      :class="[
        'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
        modelValue ? 'bg-orange-600' : 'bg-gray-200 dark:bg-gray-600'
      ]"
    >
      <span 
        :class="[
          'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
          modelValue ? 'translate-x-6' : 'translate-x-1'
        ]"
      ></span>
    </button>
  `
}

const authStore = useAuthStore()
const themeStore = useThemeStore()
const BASE_URL = `${window.location.protocol}//${window.location.hostname}:8000`

// State
const activeSection = ref('profile')
const selectedTheme = ref('light')
const selectedLanguage = ref('en')
const feedbackText = ref('')

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
  { id: 'light', name: 'Light', preview: 'bg-white border border-gray-200' },
  { id: 'dark', name: 'Dark', preview: 'bg-gray-800' },
  { id: 'auto', name: 'Auto', preview: 'bg-gradient-to-r from-white to-gray-800' }
]

// Computed
const currentTheme = computed(() => {
  return themeStore.isDarkMode ? 'dark' : 'light'
})

const isDarkMode = computed(() => themeStore.isDarkMode)

// Forms
const profileForm = ref({
  firstName: '',
  lastName: '',
  email: '',
  bio: ''
})

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const privacySettings = ref({
  profileVisibility: 'alumni',
  showEmail: true,
  showPhone: false,
  showGraduation: true
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

function updateProfile() {
  console.log('Updating profile:', profileForm.value)
  // Add API call to update profile
}

function changePassword() {
  console.log('Changing password')
  // Add API call to change password
}

function submitFeedback() {
  console.log('Submitting feedback:', feedbackText.value)
  // Add API call to submit feedback
}

function handleThemeChange(themeId) {
  console.log('🌙 Theme change requested:', themeId)
  console.log('🌙 Current theme state before:', themeStore.isDarkMode)
  
  if (themeId === 'light') {
    themeStore.setTheme('light')
  } else if (themeId === 'dark') {
    themeStore.setTheme('dark')
  } else if (themeId === 'auto') {
    // For auto, we'll just toggle for now - you can enhance this later
    themeStore.toggleTheme()
  }
  
  console.log('🌙 Theme state after:', themeStore.isDarkMode)
  console.log('🌙 HTML dark class:', document.documentElement.classList.contains('dark'))
}

// Initialize with user data
onMounted(() => {
  const user = authStore.user
  if (user) {
    profileForm.value = {
      firstName: user.first_name || '',
      lastName: user.last_name || '',
      email: user.email || '',
      bio: user.bio || ''
    }
  }
})
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
