<!-- eslint-disable vue/multi-word-component-names -->
<script setup>
import { onMounted, watch, computed, ref } from 'vue'
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
  // keep compatible API but we will derive activeSection from the route param
  isLoading,
  notification,
  hideNotification,
  showSuccess,
  showError
} = useSettings()

const route = useRoute()
const router = useRouter()

// Settings sections configuration
const sections = [
  { 
    id: 'profile', 
    label: 'Profile Settings', 
    icon: UserIcon,
    description: 'Personal information and profile picture'
  },
  { 
    id: 'account', 
    label: 'Account & Security', 
    icon: ShieldIcon,
    description: 'Password and security settings'
  },
  { 
    id: 'appearance', 
    label: 'Appearance', 
    icon: PaletteIcon,
    description: 'Theme and visual preferences'
  }
]

// derive active section reactively from the route param (:section?)
const activeSection = computed(() => {
  return route.params.section || route.query.section || 'profile'
})

// Navigate to a specific section
const navigateToSection = (sectionId) => {
  router.push({ name: 'SuperAdminSettings', params: { section: sectionId } })
}

const { profileForm, initializeProfile, user, getProfilePictureUrl } = useProfile()

// Watch for route changes to ensure proper reactivity
watch(() => route.params.section, (newSection, oldSection) => {
  // Force a re-render if needed
  if (newSection !== oldSection) {
    // The computed activeSection will automatically update
  }
}, { immediate: true })

// Helper functions for child components
const showSuccessMessage = (title, message) => showSuccess(title, message)
const showErrorMessage = (title, message) => showError(title, message)

// Initialize profile form on mount
onMounted(() => {
  initializeProfile()
})

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
       style="margin-left: 0; padding: 24px; padding-left: 24px;">

    <!-- Header -->
    <div class="mb-8">
      <div class="mb-4">
        <h1 class="text-3xl font-bold mb-1"
            :class="themeStore.isAdminDark() ? 'text-white' : 'text-gray-900'">
          Welcome Back! {{ user?.first_name || 'User' }} {{ user?.last_name || '' }}
        </h1>
        <p class="text-lg font-medium text-green-600 dark:text-green-400">
          Super Admin Settings
        </p>
      </div>
      <p class="text-gray-500 dark:text-gray-400">
        Manage your account, preferences, and system settings
      </p>
    </div>

    <!-- Main Content - Layout with Sidebar and Content -->
    <div class="max-w-7xl relative z-10">
      <div class="flex gap-6">
        <!-- Settings Navigation Sidebar -->
        <div class="w-80 flex-shrink-0">
          <div class="rounded-xl shadow-sm border transition-colors duration-200 p-6"
               :class="themeStore.isAdminDark() ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-200'">
            <h3 class="text-lg font-semibold mb-4"
                :class="themeStore.isAdminDark() ? 'text-white' : 'text-gray-900'">
              Settings
            </h3>
            <nav class="space-y-2">
              <button
                v-for="section in sections"
                :key="section.id"
                @click="navigateToSection(section.id)"
                class="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-all duration-200 hover:scale-[1.02] group"
                :class="activeSection === section.id
                  ? (themeStore.isAdminDark() ? 'bg-green-600 text-white shadow-lg' : 'bg-green-600 text-white shadow-lg')
                  : (themeStore.isAdminDark() ? 'text-gray-300 hover:bg-gray-600' : 'text-gray-700 hover:bg-gray-100')
                ">
                
                <!-- Icon -->
                <component 
                  :is="section.icon" 
                  class="w-5 h-5 flex-shrink-0 transition-transform duration-200 group-hover:scale-110" />
                
                <!-- Label and Description -->
                <div class="flex-1 min-w-0">
                  <div class="font-medium">
                    {{ section.label }}
                  </div>
                  <div class="text-xs opacity-75 mt-1"
                       :class="activeSection === section.id ? 'text-green-100' : (themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500')">
                    {{ section.description }}
                  </div>
                </div>

                <!-- Active indicator -->
                <div 
                  v-if="activeSection === section.id"
                  class="w-2 h-2 bg-white rounded-full opacity-75"></div>
              </button>
            </nav>
          </div>
        </div>

        <!-- Settings Content -->
        <div class="flex-1">
          <div class="rounded-xl shadow-sm border transition-colors duration-200"
               :class="themeStore.isAdminDark() ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-200'">

            <!-- Render the appropriate section based on the route param -->
            <ProfileSettingsSection 
              v-show="activeSection === 'profile'"
              v-if="user"
              :key="`profile-${activeSection}`"
              :user="user"
              :isLoading="isLoading"
              :getProfilePictureUrl="getProfilePictureUrl"
              :showSuccessMessage="showSuccessMessage"
              :showErrorMessage="showErrorMessage"
              @profile-saved="handleProfileSaved"
            />

            <AccountSecuritySection 
              v-show="activeSection === 'account'"
              :key="`account-${activeSection}`"
              :isLoading="isLoading"
              :showSuccessMessage="showSuccessMessage"
              :showErrorMessage="showErrorMessage"
              @account-saved="handleAccountSaved"
            />

            <AppearanceSection 
              v-show="activeSection === 'appearance'"
              :key="`appearance-${activeSection}`"
              :showSuccessMessage="showSuccessMessage"
              :showErrorMessage="showErrorMessage"
            />

            <!-- Fallback content when no section matches -->
            <ProfileSettingsSection 
              v-if="!['profile', 'account', 'appearance'].includes(activeSection) && user"
              :key="`profile-fallback-${activeSection}`"
              :user="user"
              :isLoading="isLoading"
              :getProfilePictureUrl="getProfilePictureUrl"
              :showSuccessMessage="showSuccessMessage"
              :showErrorMessage="showErrorMessage"
              @profile-saved="handleProfileSaved"
            />
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
