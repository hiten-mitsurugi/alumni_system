<script setup>
import { onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSettings } from '@/composables/useSettings'
import { useProfile } from '@/composables/useProfile'
import { useThemeStore } from '@/stores/theme'
import ProfileSettingsSection from '@/components/admin/ProfileSettingsSection.vue'
import AccountSecuritySection from '@/components/admin/AccountSecuritySection.vue'
import AppearanceSection from '@/components/admin/AppearanceSection.vue'
import {
  Check as CheckIcon,
  User as UserIcon,
  Shield as ShieldIcon,
  Palette as PaletteIcon
} from 'lucide-vue-next'

// Composables and stores
const themeStore = useThemeStore()
const {
  isLoading,
  notification,
  hideNotification,
  showSuccess,
  showError
} = useSettings()

const route = useRoute()
const router = useRouter()

// derive active section reactively from the route param (:section?)
const activeSection = computed(() => {
  return route.params.section || route.query.section || 'profile'
})

const { initializeProfile, user, getProfilePictureUrl } = useProfile()

// Watch for route changes to ensure proper reactivity
watch(() => route.params.section, () => {
  // Route section changed - Vue will automatically update activeSection computed property
}, { immediate: true })

// Helper functions for child components
const showSuccessMessage = (title, message) => showSuccess(title, message)
const showErrorMessage = (title, message) => showError(title, message)

// Initialize profile form on mount
onMounted(async () => {
  try {
    await initializeProfile()
  } catch (error) {
    console.error('Profile initialization failed:', error)
  }
})

// Event handlers
const handleProfileSaved = () => {
  // Profile saved successfully
}

const handleAccountSaved = () => {
  // Account saved successfully
}

const handleSectionChange = (sectionId) => {
  router.push(`/admin/settings/${sectionId}`)
}
</script>

<template>
  <div class="min-h-screen transition-colors duration-200"
       :class="themeStore.isAdminDark() ? 'bg-gray-800' : 'bg-gray-50'">
    
    <!-- Main Content Area -->
    <div class="p-6">
      <!-- Header -->
      <div class="mb-8">
        <div class="mb-4">
          <h1 class="mb-1 text-3xl font-bold"
              :class="themeStore.isAdminDark() ? 'text-white' : 'text-gray-900'">
            Welcome Back! {{ user?.first_name || 'User' }} {{ user?.last_name || '' }}
          </h1>
          <p class="text-lg font-medium text-blue-600 dark:text-blue-400">
            Admin Settings
          </p>
        </div>
        <p class="text-gray-500 dark:text-gray-400">
          Manage your account, preferences, and system settings
        </p>
      </div>

      <!-- Settings Navigation Tabs -->
      <div class="mb-6">
        <div class="border-b"
             :class="themeStore.isAdminDark() ? 'border-gray-600' : 'border-gray-200'">
          <nav class="flex space-x-8">
            <button @click="handleSectionChange('profile')"
                    :class="[
                      'py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200',
                      activeSection === 'profile'
                        ? 'border-orange-500 text-orange-600 dark:text-orange-400'
                        : 'border-transparent hover:border-gray-300 dark:hover:border-gray-500 ' + (themeStore.isAdminDark() ? 'text-gray-300 hover:text-gray-200' : 'text-gray-500 hover:text-gray-700')
                    ]">
              <UserIcon class="inline w-5 h-5 mr-2" />
              Profile Settings
            </button>
            <button @click="handleSectionChange('account')"
                    :class="[
                      'py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200',
                      activeSection === 'account'
                        ? 'border-orange-500 text-orange-600 dark:text-orange-400'
                        : 'border-transparent hover:border-gray-300 dark:hover:border-gray-500 ' + (themeStore.isAdminDark() ? 'text-gray-300 hover:text-gray-200' : 'text-gray-500 hover:text-gray-700')
                    ]">
              <ShieldIcon class="inline w-5 h-5 mr-2" />
              Account & Security
            </button>
            <button @click="handleSectionChange('appearance')"
                    :class="[
                      'py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200',
                      activeSection === 'appearance'
                        ? 'border-orange-500 text-orange-600 dark:text-orange-400'
                        : 'border-transparent hover:border-gray-300 dark:hover:border-gray-500 ' + (themeStore.isAdminDark() ? 'text-gray-300 hover:text-gray-200' : 'text-gray-500 hover:text-gray-700')
                    ]">
              <PaletteIcon class="inline w-5 h-5 mr-2" />
              Appearance
            </button>
          </nav>
        </div>
      </div>

      <!-- Main Content - Show content based on route -->
      <div class="relative z-10 max-w-4xl">
        <div class="transition-colors duration-200 border shadow-sm rounded-xl"
             :class="themeStore.isAdminDark() ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-200'">

          <!-- Loading State -->
          <div v-if="isLoading" class="p-8 text-center">
            <div class="w-8 h-8 mx-auto border-b-2 border-blue-600 rounded-full animate-spin"></div>
            <p class="mt-2 text-gray-500">Loading...</p>
          </div>

          <!-- Content Sections -->
          <div v-else>
            <!-- Render the appropriate section based on the route param -->
            <ProfileSettingsSection 
              v-if="activeSection === 'profile' && user"
              :user="user"
              :isLoading="isLoading"
              :getProfilePictureUrl="getProfilePictureUrl"
              :showSuccessMessage="showSuccessMessage"
              :showErrorMessage="showErrorMessage"
              @profile-saved="handleProfileSaved"
            />

            <AccountSecuritySection 
              v-if="activeSection === 'account'"
              :isLoading="isLoading"
              :showSuccessMessage="showSuccessMessage"
              :showErrorMessage="showErrorMessage"
              @account-saved="handleAccountSaved"
            />

            <AppearanceSection 
              v-if="activeSection === 'appearance'"
              :showSuccessMessage="showSuccessMessage"
              :showErrorMessage="showErrorMessage"
            />

            <!-- Fallback content when no section matches -->
            <div v-if="!['profile', 'account', 'appearance'].includes(activeSection)" 
                 class="p-8 text-center"
                 :class="themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-600'">
              <p>Section not found. Please select a valid settings section.</p>
            </div>

            <!-- No User Loaded State -->
            <div v-if="!user && !isLoading" class="p-8 text-center">
              <h3 class="mb-2 text-lg font-semibold text-red-600">User Not Loaded</h3>
              <p class="text-gray-500">Unable to load user information. Please try refreshing the page.</p>
              <button @click="initializeProfile" 
                      class="px-4 py-2 mt-4 text-white bg-blue-600 rounded-lg hover:bg-blue-700">
                Retry
              </button>
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
      <div class="flex items-center gap-3 px-6 py-4 border rounded-lg shadow-lg backdrop-blur-sm"
           :class="notification.type === 'success'
             ? 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-700 text-green-800 dark:text-green-200'
             : 'bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-700 text-red-800 dark:text-red-200'">

        <!-- Success Icon -->
        <div v-if="notification.type === 'success'"
             class="flex items-center justify-center flex-shrink-0 w-8 h-8 bg-green-500 rounded-full">
          <CheckIcon class="w-5 h-5 text-white" />
        </div>

        <!-- Error Icon -->
        <div v-else
             class="flex items-center justify-center flex-shrink-0 w-8 h-8 bg-red-500 rounded-full">
          <span class="text-sm font-bold text-white">!</span>
        </div>

        <!-- Message Content -->
        <div class="flex-1">
          <h4 class="text-sm font-semibold">{{ notification.title }}</h4>
          <p class="text-sm opacity-90">{{ notification.message }}</p>
        </div>

        <!-- Close Button -->
        <button @click="hideNotification"
                class="flex-shrink-0 text-gray-400 transition-colors hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300">
          <span class="sr-only">Close</span>
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>
