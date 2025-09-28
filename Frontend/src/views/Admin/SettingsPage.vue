<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import {
  User as UserIcon,
  Shield as ShieldIcon,
  Palette as PaletteIcon,
  Save as SaveIcon,
  Camera as CameraIcon,
  Eye as EyeIcon,
  EyeOff as EyeOffIcon,
  Lock as LockIcon,
  Check as CheckIcon
} from 'lucide-vue-next'

// Stores
const authStore = useAuthStore()
const themeStore = useThemeStore()

// Active section
const activeSection = ref('profile')

// Sidebar state
const sidebarExpanded = ref(false)
const hoverDisabled = ref(false)

// Form states
const isLoading = ref(false)
const showPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

// Notification state
const notification = ref({
  show: false,
  type: 'success', // 'success', 'error', 'warning'
  title: '',
  message: ''
})

// Profile form data
const profileForm = ref({
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  bio: '',
  profilePicture: null
})

// Account form data
const accountForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
  twoFactorEnabled: false
})

// Computed
const user = computed(() => authStore.user || {})

// Initialize form data
onMounted(() => {
  if (user.value) {
    profileForm.value = {
      firstName: user.value.first_name || '',
      lastName: user.value.last_name || '',
      email: user.value.email || '',
      phone: user.value.contact_number || '',
      bio: user.value.profile?.bio || '',
      profilePicture: null
    }
  }
})

// Methods
const setActiveSection = (section) => {
  activeSection.value = section
}

const toggleSidebar = () => {
  sidebarExpanded.value = false
  hoverDisabled.value = true
  // Re-enable hover after a short delay
  setTimeout(() => {
    hoverDisabled.value = false
  }, 500)
}

const handleProfilePictureChange = async (event) => {
  const file = event.target.files[0]
  if (file) {
    console.log('Selected file:', file.name, 'Size:', file.size, 'Type:', file.type)

    // Validate file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      alert('File size must be less than 5MB')
      return
    }

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file')
      return
    }

    try {
      isLoading.value = true
      console.log('Uploading profile picture...')

      // Upload the profile picture
      const result = await authStore.uploadProfilePicture(file)

      console.log('Profile picture upload successful:', result)

      // Update the form to trigger reactivity
      profileForm.value.profilePicture = file

      showSuccessMessage('Success!', 'Profile picture updated successfully!')
    } catch (error) {
      console.error('Error uploading profile picture:', error)
      console.error('Error response:', error.response?.data)
      console.error('Error status:', error.response?.status)

      const errorMessage = error.response?.data?.detail ||
                          error.response?.data?.error ||
                          error.message ||
                          'Unknown error occurred'
      showErrorMessage('Upload Failed', `Failed to upload profile picture: ${errorMessage}`)
    } finally {
      isLoading.value = false
    }
  }
}

const saveProfileSettings = async () => {
  isLoading.value = true
  try {
    // Prepare the profile data for API call
    const profileUpdateData = {
      first_name: profileForm.value.firstName,
      last_name: profileForm.value.lastName,
      email: profileForm.value.email,
      contact_number: profileForm.value.phone,
      profile: {
        bio: profileForm.value.bio
      }
    }

    console.log('Sending profile update data:', profileUpdateData)
    console.log('API endpoint: /api/profile/')
    console.log('Current user:', user.value)

    // Call the API to update profile
    const result = await authStore.updateProfile(profileUpdateData)

    console.log('Profile update successful:', result)
    // Show success message
    showSuccessMessage('Profile Updated!', 'Your profile information has been updated successfully!')
  } catch (error) {
    console.error('Error saving profile:', error)
    console.error('Error response:', error.response?.data)
    console.error('Error status:', error.response?.status)

    // Show error message with more details
    const errorMessage = error.response?.data?.detail ||
                        error.response?.data?.error ||
                        error.message ||
                        'Unknown error occurred'
    showErrorMessage('Update Failed', `Failed to update profile: ${errorMessage}`)
  } finally {
    isLoading.value = false
  }
}

const saveAccountSettings = async () => {
  isLoading.value = true
  try {
    // Implement save logic here
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API call
    console.log('Account settings saved:', accountForm.value)
  } catch (error) {
    console.error('Error saving account:', error)
  } finally {
    isLoading.value = false
  }
}

// Helper function to get correct profile picture URL
const getProfilePictureUrl = (profilePicturePath) => {
  if (!profilePicturePath) {
    return '/default-profile.png'
  }

  // If it's already a full URL, return as is
  if (profilePicturePath.startsWith('http')) {
    return profilePicturePath
  }

  // If it starts with /, it's a relative path from backend
  if (profilePicturePath.startsWith('/')) {
    return `http://localhost:8000${profilePicturePath}`
  }

  // Otherwise, assume it's a media file
  return `http://localhost:8000/media/${profilePicturePath}`
}

// Notification helper functions
const showNotification = (type, title, message) => {
  notification.value = {
    show: true,
    type,
    title,
    message
  }

  // Auto-hide after 5 seconds
  setTimeout(() => {
    hideNotification()
  }, 5000)
}

const hideNotification = () => {
  notification.value.show = false
}

const showSuccessMessage = (title, message) => {
  showNotification('success', title, message)
}

const showErrorMessage = (title, message) => {
  showNotification('error', title, message)
}

// Sections configuration
const sections = [
  { id: 'profile', label: 'Profile', icon: UserIcon },
  { id: 'account', label: 'Account & Security', icon: ShieldIcon },
  { id: 'appearance', label: 'Appearance', icon: PaletteIcon }
]
</script>

<template>
  <div class="min-h-screen transition-colors duration-200 relative z-10"
       :class="themeStore.isDarkMode ? 'bg-gray-900' : 'bg-gray-50'"
       style="margin-left: 0; padding: 24px; padding-left: 24px;">

    <!-- Header -->
    <div class="mb-8">
      <div class="mb-4">
        <h1 class="text-3xl font-bold mb-1"
            :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
          Welcome Back! {{ user.first_name }} {{ user.last_name }}
        </h1>
        <p class="text-lg font-medium text-blue-600 dark:text-blue-400">
          Admin Settings
        </p>
      </div>
      <p class="text-gray-500 dark:text-gray-400">
        Manage your account, preferences, and system settings
      </p>
    </div>

    <div class="flex gap-8">
      <!-- Sidebar Navigation -->
      <div
        :class="sidebarExpanded ? 'w-64' : 'w-16'"
        class="flex-shrink-0 transition-all duration-500 ease-out group"
        @mouseenter="!sidebarExpanded && !hoverDisabled && (sidebarExpanded = true)">
        <div class="sticky top-6 py-2">
          <nav class="space-y-2">
            <button
              v-for="section in sections"
              :key="section.id"
              @click="setActiveSection(section.id)"
              class="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-all duration-300 ease-out hover:scale-[1.02] active:scale-98 relative overflow-hidden hover:shadow-md"
            :class="activeSection === section.id
              ? (themeStore.isDarkMode ? 'bg-blue-600 text-white shadow-lg' : 'bg-blue-600 text-white shadow-lg')
              : (themeStore.isDarkMode ? 'text-gray-300 hover:bg-gray-800/50' : 'text-gray-700 hover:bg-gray-100/80')
            ">
              <!-- Icon - always visible -->
              <component :is="section.icon" class="w-5 h-5 flex-shrink-0 transition-transform duration-300 ease-out"
                         :class="sidebarExpanded ? 'group-hover:scale-110' : ''" />
              <!-- Label - visible when expanded -->
              <span v-if="sidebarExpanded"
                    class="font-medium whitespace-nowrap transition-all duration-400 ease-out">
                {{ section.label }}
              </span>
            </button>
          </nav>

          <!-- Collapse Button - Only visible when expanded -->
          <div v-if="sidebarExpanded" class="flex justify-start mt-6">
            <button
              @click.stop="toggleSidebar"
              class="flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200 hover:scale-105 relative z-10 cursor-pointer select-none"
              :class="themeStore.isDarkMode ? 'text-gray-400 hover:text-white hover:bg-gray-700' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'"
              type="button"
              style="pointer-events: auto;">
              <svg class="w-4 h-4 transform transition-transform duration-200 pointer-events-none" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              <span class="text-sm font-medium pointer-events-none">Back</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div class="flex-1 max-w-4xl relative z-10">
        <div class="rounded-xl shadow-sm border transition-colors duration-200"
             :class="themeStore.isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'">

          <!-- Profile Settings -->
          <div v-if="activeSection === 'profile'" class="p-8">
            <div class="flex items-center gap-3 mb-6">
              <UserIcon class="w-6 h-6 text-blue-600" />
              <h2 class="text-2xl font-bold"
                  :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
                Profile Settings
              </h2>
            </div>

            <!-- Profile Picture -->
            <div class="mb-8">
              <label class="block text-sm font-medium mb-3"
                     :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                Profile Picture
              </label>
              <div class="flex items-center gap-4">
                <div class="relative">
                  <img :src="getProfilePictureUrl(user.profile_picture)"
                       alt="Profile"
                       class="w-20 h-20 rounded-full object-cover border-4 border-blue-100 dark:border-blue-900">
                  <button @click="() => document.getElementById('profilePicture').click()"
                          :disabled="isLoading"
                          class="absolute bottom-0 right-0 bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                    <CameraIcon class="w-4 h-4" />
                  </button>
                </div>
                <div>
                  <input type="file"
                         id="profilePicture"
                         accept="image/*"
                         @change="handleProfilePictureChange"
                         class="hidden">
                  <label for="profilePicture"
                         :class="[
                           'inline-flex items-center px-4 py-2 rounded-lg cursor-pointer transition-colors',
                           isLoading
                             ? 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                             : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                         ]">
                    {{ isLoading ? 'Uploading...' : 'Upload New Photo' }}
                  </label>
                  <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    JPG, PNG up to 5MB
                  </p>
                </div>
              </div>
            </div>

            <!-- Profile Form -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div>
                <label class="block text-sm font-medium mb-2"
                       :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                  First Name
                </label>
                <input v-model="profileForm.firstName"
                       type="text"
                       class="w-full px-4 py-2 rounded-lg border transition-colors duration-200"
                       :class="themeStore.isDarkMode
                         ? 'bg-gray-700 border-gray-600 text-white focus:border-blue-500'
                         : 'bg-white border-gray-300 text-gray-900 focus:border-blue-500'">
              </div>
              <div>
                <label class="block text-sm font-medium mb-2"
                       :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                  Last Name
                </label>
                <input v-model="profileForm.lastName"
                       type="text"
                       class="w-full px-4 py-2 rounded-lg border transition-colors duration-200"
                       :class="themeStore.isDarkMode
                         ? 'bg-gray-700 border-gray-600 text-white focus:border-blue-500'
                         : 'bg-white border-gray-300 text-gray-900 focus:border-blue-500'">
              </div>
              <div>
                <label class="block text-sm font-medium mb-2"
                       :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                  Email
                </label>
                <input v-model="profileForm.email"
                       type="email"
                       class="w-full px-4 py-2 rounded-lg border transition-colors duration-200"
                       :class="themeStore.isDarkMode
                         ? 'bg-gray-700 border-gray-600 text-white focus:border-blue-500'
                         : 'bg-white border-gray-300 text-gray-900 focus:border-blue-500'">
              </div>
              <div>
                <label class="block text-sm font-medium mb-2"
                       :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                  Phone
                </label>
                <input v-model="profileForm.phone"
                       type="tel"
                       class="w-full px-4 py-2 rounded-lg border transition-colors duration-200"
                       :class="themeStore.isDarkMode
                         ? 'bg-gray-700 border-gray-600 text-white focus:border-blue-500'
                         : 'bg-white border-gray-300 text-gray-900 focus:border-blue-500'">
              </div>
            </div>

            <!-- Bio -->
            <div class="mb-8">
              <label class="block text-sm font-medium mb-2"
                     :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                Bio
              </label>
              <textarea v-model="profileForm.bio"
                        rows="4"
                        class="w-full px-4 py-2 rounded-lg border transition-colors duration-200"
                        :class="themeStore.isDarkMode
                          ? 'bg-gray-700 border-gray-600 text-white focus:border-blue-500'
                          : 'bg-white border-gray-300 text-gray-900 focus:border-blue-500'"
                        placeholder="Tell us about yourself..."></textarea>
            </div>

            <!-- Save Button -->
            <div class="flex justify-end">
              <button @click="saveProfileSettings"
                      :disabled="isLoading"
                      class="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                <SaveIcon class="w-4 h-4" />
                {{ isLoading ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </div>

          <!-- Account & Security Settings -->
          <div v-if="activeSection === 'account'" class="p-8">
            <div class="flex items-center gap-3 mb-6">
              <ShieldIcon class="w-6 h-6 text-blue-600" />
              <h2 class="text-2xl font-bold"
                  :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
                Account & Security
              </h2>
            </div>

            <!-- Password Change Section -->
            <div class="mb-8 p-6 rounded-lg border"
                 :class="themeStore.isDarkMode ? 'border-gray-700 bg-gray-750' : 'border-gray-200 bg-gray-50'">
              <h3 class="text-lg font-semibold mb-4"
                  :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
                Change Password
              </h3>

              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium mb-2"
                         :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                    Current Password
                  </label>
                  <div class="relative">
                    <input v-model="accountForm.currentPassword"
                           :type="showPassword ? 'text' : 'password'"
                           class="w-full px-4 py-2 pr-12 rounded-lg border transition-colors duration-200"
                           :class="themeStore.isDarkMode
                             ? 'bg-gray-700 border-gray-600 text-white focus:border-blue-500'
                             : 'bg-white border-gray-300 text-gray-900 focus:border-blue-500'">
                    <button @click="showPassword = !showPassword"
                            type="button"
                            class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600">
                      <EyeIcon v-if="!showPassword" class="w-5 h-5" />
                      <EyeOffIcon v-else class="w-5 h-5" />
                    </button>
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium mb-2"
                           :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                      New Password
                    </label>
                    <div class="relative">
                      <input v-model="accountForm.newPassword"
                             :type="showNewPassword ? 'text' : 'password'"
                             class="w-full px-4 py-2 pr-12 rounded-lg border transition-colors duration-200"
                             :class="themeStore.isDarkMode
                               ? 'bg-gray-700 border-gray-600 text-white focus:border-blue-500'
                               : 'bg-white border-gray-300 text-gray-900 focus:border-blue-500'">
                      <button @click="showNewPassword = !showNewPassword"
                              type="button"
                              class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600">
                        <EyeIcon v-if="!showNewPassword" class="w-5 h-5" />
                        <EyeOffIcon v-else class="w-5 h-5" />
                      </button>
                    </div>
                  </div>

                  <div>
                    <label class="block text-sm font-medium mb-2"
                           :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                      Confirm Password
                    </label>
                    <div class="relative">
                      <input v-model="accountForm.confirmPassword"
                             :type="showConfirmPassword ? 'text' : 'password'"
                             class="w-full px-4 py-2 pr-12 rounded-lg border transition-colors duration-200"
                             :class="themeStore.isDarkMode
                               ? 'bg-gray-700 border-gray-600 text-white focus:border-blue-500'
                               : 'bg-white border-gray-300 text-gray-900 focus:border-blue-500'">
                      <button @click="showConfirmPassword = !showConfirmPassword"
                              type="button"
                              class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600">
                        <EyeIcon v-if="!showConfirmPassword" class="w-5 h-5" />
                        <EyeOffIcon v-else class="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>

                <div class="flex justify-end">
                  <button @click="saveAccountSettings"
                          :disabled="isLoading"
                          class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                    <LockIcon class="w-4 h-4" />
                    {{ isLoading ? 'Updating...' : 'Update Password' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Two-Factor Authentication -->
            <div class="mb-8 p-6 rounded-lg border"
                 :class="themeStore.isDarkMode ? 'border-gray-700 bg-gray-750' : 'border-gray-200 bg-gray-50'">
              <div class="flex items-center justify-between mb-4">
                <div>
                  <h3 class="text-lg font-semibold"
                      :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
                    Two-Factor Authentication
                  </h3>
                  <p class="text-sm"
                     :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'">
                    Add an extra layer of security to your account
                  </p>
                </div>
                <div class="flex items-center">
                  <input v-model="accountForm.twoFactorEnabled"
                         type="checkbox"
                         id="twoFactor"
                         class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500">
                  <label for="twoFactor" class="ml-2 text-sm font-medium"
                         :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                    {{ accountForm.twoFactorEnabled ? 'Enabled' : 'Disabled' }}
                  </label>
                </div>
              </div>

              <div v-if="accountForm.twoFactorEnabled" class="space-y-4">
                <div class="flex items-center gap-2 text-sm"
                     :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'">
                  <CheckIcon class="w-4 h-4 text-green-500" />
                  <span>Two-factor authentication is enabled and active</span>
                </div>
                <button class="text-blue-600 hover:text-blue-700 text-sm font-medium">
                  View Recovery Codes
                </button>
              </div>
            </div>
          </div>

          <!-- Appearance Settings -->
          <div v-if="activeSection === 'appearance'" class="p-8">
            <div class="flex items-center gap-3 mb-6">
              <PaletteIcon class="w-6 h-6 text-blue-600" />
              <h2 class="text-2xl font-bold"
                  :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
                Appearance
              </h2>
            </div>

            <!-- Theme Selection -->
            <div class="mb-8">
              <h3 class="text-lg font-semibold mb-4"
                  :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
                Theme Preference
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Light Theme -->
                <div class="relative cursor-pointer group"
                     @click="themeStore.toggleTheme">
                  <div class="p-6 rounded-xl border-2 transition-all duration-300 hover:shadow-lg"
                       :class="!themeStore.isDarkMode
                         ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-md'
                         : 'border-gray-300 hover:border-blue-300 dark:border-gray-600'">

                    <!-- Light Theme Preview -->
                    <div class="bg-white rounded-lg p-6 shadow-inner mb-4 border border-gray-100">
                      <div class="flex items-center gap-3 mb-4">
                        <div class="w-4 h-4 bg-blue-500 rounded-full"></div>
                        <div class="flex-1">
                          <div class="w-24 h-3 bg-gray-200 rounded mb-1"></div>
                          <div class="w-16 h-2 bg-gray-100 rounded"></div>
                        </div>
                      </div>
                      <div class="space-y-3">
                        <div class="w-full h-3 bg-gray-100 rounded"></div>
                        <div class="w-5/6 h-3 bg-gray-100 rounded"></div>
                        <div class="w-4/6 h-3 bg-gray-100 rounded"></div>
                      </div>
                      <div class="mt-4 flex gap-2">
                        <div class="w-16 h-6 bg-blue-500 rounded text-xs"></div>
                        <div class="w-16 h-6 bg-gray-200 rounded text-xs"></div>
                      </div>
                    </div>

                    <div class="text-center">
                      <span class="font-semibold text-lg"
                            :class="themeStore.isDarkMode ? 'text-gray-700' : 'text-gray-900'">
                         Light Mode
                      </span>
                    </div>
                  </div>
                </div>

                <!-- Dark Theme -->
                <div class="relative cursor-pointer group"
                     @click="themeStore.toggleTheme">
                  <div class="p-6 rounded-xl border-2 transition-all duration-300 hover:shadow-lg"
                       :class="themeStore.isDarkMode
                         ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-md'
                         : 'border-gray-300 hover:border-blue-300'">

                    <!-- Dark Theme Preview -->
                    <div class="bg-gray-800 rounded-lg p-6 shadow-inner mb-4 border border-gray-700">
                      <div class="flex items-center gap-3 mb-4">
                        <div class="w-4 h-4 bg-blue-400 rounded-full"></div>
                        <div class="flex-1">
                          <div class="w-24 h-3 bg-gray-600 rounded mb-1"></div>
                          <div class="w-16 h-2 bg-gray-700 rounded"></div>
                        </div>
                      </div>
                      <div class="space-y-3">
                        <div class="w-full h-3 bg-gray-700 rounded"></div>
                        <div class="w-5/6 h-3 bg-gray-700 rounded"></div>
                        <div class="w-4/6 h-3 bg-gray-700 rounded"></div>
                      </div>
                      <div class="mt-4 flex gap-2">
                        <div class="w-16 h-6 bg-blue-500 rounded text-xs"></div>
                        <div class="w-16 h-6 bg-gray-600 rounded text-xs"></div>
                      </div>
                    </div>

                    <div class="text-center">
                      <span class="font-semibold text-lg"
                            :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
                         Dark Mode
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>


          </div>

        </div>
      </div>
    </div>

    <!-- Modern Notification Component -->
    <div v-if="notification.show"
         class="fixed top-4 right-4 z-[9999] transform transition-all duration-300 ease-in-out"
         :class="notification.show ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'"
         style="position: fixed !important;">
      <div class="flex items-center gap-3 px-6 py-4 rounded-lg shadow-lg backdrop-blur-sm border"
           :class="notification.type === 'success'
             ? 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-700 text-green-800 dark:text-green-200'
             : 'bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-700 text-red-800 dark:text-red-200'">

        <!-- Success Icon -->
        <div v-if="notification.type === 'success'"
             class="flex-shrink-0 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
          <CheckIcon class="w-5 h-5 text-white" />
        </div>

        <!-- Error Icon -->
        <div v-else
             class="flex-shrink-0 w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
          <span class="text-white font-bold text-sm">!</span>
        </div>

        <!-- Message Content -->
        <div class="flex-1">
          <h4 class="font-semibold text-sm">{{ notification.title }}</h4>
          <p class="text-sm opacity-90">{{ notification.message }}</p>
        </div>

        <!-- Close Button -->
        <button @click="hideNotification"
                class="flex-shrink-0 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 transition-colors">
          <span class="sr-only">Close</span>
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>
