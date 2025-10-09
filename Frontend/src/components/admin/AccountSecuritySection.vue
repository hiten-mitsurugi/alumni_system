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
       type="checkbox"
       id="twoFactor"
       class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500">
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
        <button class="text-blue-600 hover:text-blue-700 text-sm font-medium">
          View Recovery Codes
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
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
const { passwordForm, securitySettings, changePassword } = useAccountSecurity()

// Password visibility states
const showPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

// Wrapper for save function to emit events
const saveAccountSettingsWrapper = async () => {
  try {
    const result = await changePassword()
    props.showSuccessMessage('Success', 'Password updated successfully')
    emit('account-saved', result)
  } catch (error) {
    props.showErrorMessage('Error', error.message || 'Failed to update password')
  }
}
</script>