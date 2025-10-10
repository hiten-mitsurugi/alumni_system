<template>
  <div v-if="passwordForm && securitySettings" class="p-8">
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
            <input v-model="passwordForm.currentPassword"
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
              <input v-model="passwordForm.newPassword"
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
              <input v-model="passwordForm.confirmPassword"
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
          <button @click="saveAccountSettingsWrapper"
                  :disabled="props.isLoading"
                  class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
            <LockIcon class="w-4 h-4" />
            {{ props.isLoading ? 'Updating...' : 'Update Password' }}
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
          <input v-model="securitySettings.twoFactorEnabled"
                 @change="toggle2FAWrapper"
                 type="checkbox"
                 id="twoFactor"
                 class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                 :disabled="props.isLoading">
          <label for="twoFactor" class="ml-2 text-sm font-medium"
                 :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            {{ securitySettings.twoFactorEnabled ? 'Enabled' : 'Disabled' }}
          </label>
        </div>
      </div>

      <div v-if="securitySettings.twoFactorEnabled" class="space-y-4">
        <div class="flex items-center gap-2 text-sm"
             :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'">
          <CheckIcon class="w-4 h-4 text-green-500" />
          <span>Two-factor authentication is enabled and active</span>
        </div>
        <div class="flex gap-3">
          <button @click="viewRecoveryCodes"
                  class="text-blue-600 hover:text-blue-700 text-sm font-medium">
            View Recovery Codes
          </button>
          <button @click="regenerateRecoveryCodes"
                  class="text-orange-600 hover:text-orange-700 text-sm font-medium">
            Regenerate Codes
          </button>
        </div>
      </div>
    </div>

    <!-- Session Management -->
    <div class="mb-8 p-6 rounded-lg border"
         :class="themeStore.isDarkMode ? 'border-gray-700 bg-gray-750' : 'border-gray-200 bg-gray-50'">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="text-lg font-semibold"
              :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
            Active Sessions
          </h3>
          <p class="text-sm"
             :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'">
            Manage your active login sessions
          </p>
        </div>
        <button @click="loadActiveSessions"
                :disabled="loadingSessions"
                class="text-blue-600 hover:text-blue-700 text-sm font-medium disabled:opacity-50">
          {{ loadingSessions ? 'Loading...' : 'Refresh' }}
        </button>
      </div>

      <div v-if="activeSessions.length > 0" class="space-y-3">
        <div v-for="session in activeSessions" :key="session.id"
             class="flex items-center justify-between p-3 rounded border"
             :class="themeStore.isDarkMode ? 'border-gray-600 bg-gray-700' : 'border-gray-200 bg-white'">
          <div class="flex items-center gap-3">
            <div class="w-2 h-2 rounded-full"
                 :class="session.is_current ? 'bg-green-500' : 'bg-gray-400'">
            </div>
            <div>
              <div class="text-sm font-medium"
                   :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
                {{ session.device || 'Unknown Device' }}
                <span v-if="session.is_current" class="text-green-600 text-xs ml-2">(Current)</span>
              </div>
              <div class="text-xs"
                   :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'">
                {{ session.location || 'Unknown Location' }} • {{ formatDate(session.last_activity) }}
              </div>
            </div>
          </div>
          <button v-if="!session.is_current"
                  @click="terminateSessionWrapper(session.id)"
                  class="text-red-600 hover:text-red-700 text-sm">
            Terminate
          </button>
        </div>
        <button @click="terminateAllOtherSessionsWrapper"
                class="w-full mt-4 px-4 py-2 text-sm text-red-600 border border-red-300 rounded hover:bg-red-50">
          Terminate All Other Sessions
        </button>
      </div>
      <div v-else-if="!loadingSessions" class="text-center py-4">
        <p class="text-sm"
           :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'">
          No active sessions found
        </p>
      </div>
    </div>

    <!-- Login Notifications -->
    <div class="mb-8 p-6 rounded-lg border"
         :class="themeStore.isDarkMode ? 'border-gray-700 bg-gray-750' : 'border-gray-200 bg-gray-50'">
      <h3 class="text-lg font-semibold mb-4"
          :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
        Security Notifications
      </h3>
      
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <label class="text-sm font-medium"
                   :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
              Email notifications for new logins
            </label>
            <p class="text-xs"
               :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'">
              Get notified when someone logs into your account
            </p>
          </div>
          <input v-model="securitySettings.loginNotifications"
                 @change="updateSecuritySettingsWrapper"
                 type="checkbox"
                 class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500">
        </div>

        <div class="flex items-center justify-between">
          <div>
            <label class="text-sm font-medium"
                   :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
              Security alerts
            </label>
            <p class="text-xs"
               :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'">
              Get notified about suspicious activity
            </p>
          </div>
          <input v-model="securitySettings.securityAlerts"
                 @change="updateSecuritySettingsWrapper"
                 type="checkbox"
                 class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500">
        </div>

        <div class="flex items-center justify-between">
          <div>
            <label class="text-sm font-medium"
                   :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
              Session timeout (minutes)
            </label>
            <p class="text-xs"
               :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'">
              Automatically log out after inactivity
            </p>
          </div>
          <select v-model="securitySettings.sessionTimeout"
                  @change="updateSecuritySettingsWrapper"
                  class="text-sm border rounded px-2 py-1"
                  :class="themeStore.isDarkMode
                    ? 'bg-gray-700 border-gray-600 text-white'
                    : 'bg-white border-gray-300 text-gray-900'">
            <option value="15">15 minutes</option>
            <option value="30">30 minutes</option>
            <option value="60">1 hour</option>
            <option value="120">2 hours</option>
            <option value="240">4 hours</option>
            <option value="480">8 hours</option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAccountSecurity } from '@/composables/useAccountSecurity'
import { useThemeStore } from '@/stores/theme'
import {
  Shield as ShieldIcon,
  Eye as EyeIcon,
  EyeOff as EyeOffIcon,
  Lock as LockIcon,
  Check as CheckIcon
} from 'lucide-vue-next'

const props = defineProps({
  isLoading: Boolean,
  showSuccessMessage: Function,
  showErrorMessage: Function
})

const emit = defineEmits(['account-saved'])

const themeStore = useThemeStore()
const {
  passwordForm,
  securitySettings,
  changePassword,
  toggle2FA,
  updateSecuritySettings,
  loadSecuritySettings,
  getActiveSessions,
  terminateSession,
  terminateAllOtherSessions
} = useAccountSecurity()

// Password visibility states
const showPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

// Session management
const activeSessions = ref([])
const loadingSessions = ref(false)

// Load initial data
onMounted(async () => {
  try {
    await loadSecuritySettings()
    await loadActiveSessions()
  } catch (error) {
    console.error('Failed to load security data:', error)
  }
})

// Wrapper functions
const saveAccountSettingsWrapper = async () => {
  try {
    const result = await changePassword()
    props.showSuccessMessage('Success', 'Password updated successfully')
    emit('account-saved', result)
  } catch (error) {
    props.showErrorMessage('Error', error.message || 'Failed to update password')
  }
}

const toggle2FAWrapper = async () => {
  try {
    const result = await toggle2FA()
    props.showSuccessMessage('Success', result.message)
  } catch (error) {
    props.showErrorMessage('Error', error.message || 'Failed to toggle 2FA')
    // Revert the checkbox state
    securitySettings.value.twoFactorEnabled = !securitySettings.value.twoFactorEnabled
  }
}

const updateSecuritySettingsWrapper = async () => {
  try {
    await updateSecuritySettings()
    props.showSuccessMessage('Success', 'Security settings updated')
  } catch (error) {
    props.showErrorMessage('Error', error.message || 'Failed to update security settings')
  }
}

const loadActiveSessions = async () => {
  try {
    loadingSessions.value = true
    activeSessions.value = await getActiveSessions()
  } catch (error) {
    props.showErrorMessage('Error', 'Failed to load active sessions')
    activeSessions.value = []
  } finally {
    loadingSessions.value = false
  }
}

const terminateSessionWrapper = async (sessionId) => {
  try {
    await terminateSession(sessionId)
    props.showSuccessMessage('Success', 'Session terminated')
    await loadActiveSessions()
  } catch (error) {
    props.showErrorMessage('Error', 'Failed to terminate session')
  }
}

const terminateAllOtherSessionsWrapper = async () => {
  if (confirm('Are you sure you want to terminate all other sessions? This will log out all other devices.')) {
    try {
      await terminateAllOtherSessions()
      props.showSuccessMessage('Success', 'All other sessions terminated')
      await loadActiveSessions()
    } catch (error) {
      props.showErrorMessage('Error', 'Failed to terminate sessions')
    }
  }
}

const viewRecoveryCodes = () => {
  // This would typically open a modal or navigate to a recovery codes page
  props.showSuccessMessage('Info', 'Recovery codes feature coming soon')
}

const regenerateRecoveryCodes = () => {
  if (confirm('Are you sure you want to regenerate recovery codes? Your old codes will no longer work.')) {
    props.showSuccessMessage('Info', 'Recovery code regeneration feature coming soon')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  try {
    const date = new Date(dateString)
    return date.toLocaleString()
  } catch (error) {
    return 'Invalid date'
  }
}
</script>