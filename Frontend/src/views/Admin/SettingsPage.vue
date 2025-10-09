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
  User as UserIcon,
  Shield as ShieldIcon,
  Palette as PaletteIcon,
  Check as CheckIcon
} from 'lucide-vue-next'

// Composables and stores
const themeStore = useThemeStore()
const {
  // keep compatible API but we will derive activeSection from the route param
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

const { profileForm, initializeProfile, user, getProfilePictureUrl } = useProfile()

// Helper functions for child components
const showSuccessMessage = (title, message) => showSuccess(title, message)
const showErrorMessage = (title, message) => showError(title, message)

// Initialize profile form on mount
onMounted(() => {
  initializeProfile()
})

// Sections configuration
const sections = [
  { id: 'profile', label: 'Profile', icon: UserIcon },
  { id: 'account', label: 'Account & Security', icon: ShieldIcon },
  { id: 'appearance', label: 'Appearance', icon: PaletteIcon }
]

// Event handlers
const handleProfileSaved = (result) => {
  console.log('Profile saved:', result)
}

const handleAccountSaved = (result) => {
  console.log('Account saved:', result)
}
</script>

<template>
  <div class="min-h-screen transition-colors duration-200 relative z-10"
    :class="themeStore.isAdminDark() ? 'bg-gray-900' : 'bg-gray-50'"
       style="margin-left: 0; padding: 24px; padding-left: 24px;">

    <!-- Header -->
    <div class="mb-8">
      <div class="mb-4">
        <h1 class="text-3xl font-bold mb-1"
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

    <div class="flex gap-8">
      <!-- Main Content (settings panels) - controlled by route param -->
      <div class="flex-1 max-w-4xl relative z-10">
        <div class="rounded-xl shadow-sm border transition-colors duration-200"
             :class="themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'">

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

          <AppearanceSection v-if="activeSection === 'appearance'" />
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
