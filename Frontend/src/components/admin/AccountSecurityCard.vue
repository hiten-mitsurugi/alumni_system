<script setup>
import { ref, computed } from 'vue'
import { 
  Shield as ShieldIcon, 
  Lock as LockIcon,
  Key as KeyIcon,
  Eye as EyeIcon,
  EyeOff as EyeOffIcon,
  Save as SaveIcon,
  AlertCircle as AlertIcon,
  CheckCircle as CheckIcon,
  RefreshCw as RefreshIcon,
  Smartphone as SmartphoneIcon
} from 'lucide-vue-next'
import { useAccountSecurity } from '@/composables/useAccountSecurity'

// Props
const props = defineProps({
  themeStore: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['save-success', 'save-error', 'security-change'])

// Composables
const {
  passwordForm,
  securitySettings,
  passwordVisibility,
  isChangingPassword,
  isEnabling2FA,
  passwordErrors,
  passwordStrength,
  changePassword,
  resetPasswordForm,
  toggle2FA,
  togglePasswordVisibility,
  generateStrongPassword
} = useAccountSecurity()

// Local state
const show2FAModal = ref(false)
const twoFactorSetupData = ref(null)
const verificationCode = ref('')

// Computed
const passwordStrengthColor = computed(() => {
  const colors = {
    'Very Weak': 'bg-red-500',
    'Weak': 'bg-orange-500',
    'Fair': 'bg-yellow-500',
    'Good': 'bg-blue-500',
    'Strong': 'bg-green-500',
    'Very Strong': 'bg-green-600'
  }
  return colors[passwordStrength.value.strength] || 'bg-gray-300'
})

const passwordStrengthWidth = computed(() => {
  return `${(passwordStrength.value.score / 5) * 100}%`
})

// Methods
const onChangePassword = async () => {
  try {
    await changePassword()
    emit('save-success', 'Password changed successfully!')
    emit('security-change', 'password_changed')
  } catch (error) {
    emit('save-error', 'Failed to change password', error.message)
  }
}

const onToggle2FA = async () => {
  try {
    const result = await toggle2FA()
    
    if (result.qrCode) {
      // Show setup modal for enabling 2FA
      twoFactorSetupData.value = result
      show2FAModal.value = true
    } else {
      emit('save-success', result.message)
      emit('security-change', securitySettings.value.twoFactorEnabled ? '2fa_enabled' : '2fa_disabled')
    }
  } catch (error) {
    emit('save-error', 'Failed to update two-factor authentication', error.message)
  }
}

const onGeneratePassword = () => {
  passwordForm.value.newPassword = generateStrongPassword()
}

const getFieldError = (fieldName) => {
  return passwordErrors.value[fieldName] || null
}
</script>

<template>
  <div class="p-6 rounded-xl border transition-colors duration-200"
  :class="themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'">
    
    <!-- Header -->
    <div class="flex items-center gap-3 mb-6">
      <ShieldIcon class="w-6 h-6 text-blue-600" />
      <h3 class="text-xl font-semibold"
          :class="themeStore.isAdminDark() ? 'text-white' : 'text-gray-900'">
        Account & Security
      </h3>
    </div>

    <!-- Password Change Section -->
    <div class="mb-8 p-6 rounded-lg border"
         :class="themeStore.isAdminDark() ? 'border-gray-700 bg-gray-750' : 'border-gray-200 bg-gray-50'">
      <div class="flex items-center gap-3 mb-4">
        <LockIcon class="w-5 h-5 text-blue-600" />
        <h4 class="text-lg font-semibold"
            :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
          Change Password
        </h4>
      </div>

      <div class="space-y-4">
        <!-- Current Password -->
        <div>
          <label class="block text-sm font-medium mb-2"
                :class="themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-700'">
            Current Password *
          </label>
          <div class="relative">
            <input v-model="passwordForm.currentPassword"
                   :type="passwordVisibility.current ? 'text' : 'password'"
                   :class="[
                     'w-full px-4 py-2 pr-12 rounded-lg border transition-colors duration-200',
                     getFieldError('currentPassword') 
                       ? 'border-red-500 focus:border-red-500' 
                       : 'focus:border-blue-500',
                     themeStore.isDarkMode
                       ? 'bg-gray-700 border-gray-600 text-white'
                       : 'bg-white border-gray-300 text-gray-900'
                   ]"
                   placeholder="Enter your current password">
            <button @click="togglePasswordVisibility('current')"
                    type="button"
                    class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
              <EyeIcon v-if="!passwordVisibility.current" class="w-5 h-5" />
              <EyeOffIcon v-else class="w-5 h-5" />
            </button>
          </div>
          <p v-if="getFieldError('currentPassword')" class="text-red-500 text-sm mt-1">
            {{ getFieldError('currentPassword') }}
          </p>
        </div>

        <!-- New Password -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="block text-sm font-medium"
                   :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
              New Password *
            </label>
            <button @click="onGeneratePassword"
                    type="button"
                    class="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700 transition-colors">
              <KeyIcon class="w-4 h-4" />
              Generate
            </button>
          </div>
          <div class="relative">
            <input v-model="passwordForm.newPassword"
                   :type="passwordVisibility.new ? 'text' : 'password'"
                   :class="[
                     'w-full px-4 py-2 pr-12 rounded-lg border transition-colors duration-200',
                     getFieldError('newPassword') 
                       ? 'border-red-500 focus:border-red-500' 
                       : 'focus:border-blue-500',
                     themeStore.isDarkMode
                       ? 'bg-gray-700 border-gray-600 text-white'
                       : 'bg-white border-gray-300 text-gray-900'
                   ]"
                   placeholder="Enter your new password">
            <button @click="togglePasswordVisibility('new')"
                    type="button"
                    class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
              <EyeIcon v-if="!passwordVisibility.new" class="w-5 h-5" />
              <EyeOffIcon v-else class="w-5 h-5" />
            </button>
          </div>

          <!-- Password Strength Indicator -->
          <div v-if="passwordForm.newPassword" class="mt-2">
            <div class="flex items-center justify-between text-sm mb-1">
              <span :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                Password Strength:
              </span>
              <span :class="`font-medium ${passwordStrength.color === 'red' ? 'text-red-500' : 
                             passwordStrength.color === 'orange' ? 'text-orange-500' : 
                             passwordStrength.color === 'yellow' ? 'text-yellow-500' : 
                             passwordStrength.color === 'blue' ? 'text-blue-500' : 'text-green-500'}`">
                {{ passwordStrength.strength }}
              </span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div :class="passwordStrengthColor" 
                   :style="{ width: passwordStrengthWidth }"
                   class="h-2 rounded-full transition-all duration-300"></div>
            </div>
          </div>

          <p v-if="getFieldError('newPassword')" class="text-red-500 text-sm mt-1">
            {{ getFieldError('newPassword') }}
          </p>
        </div>

        <!-- Confirm Password -->
        <div>
          <label class="block text-sm font-medium mb-2"
                 :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            Confirm Password *
          </label>
          <div class="relative">
            <input v-model="passwordForm.confirmPassword"
                   :type="passwordVisibility.confirm ? 'text' : 'password'"
                   :class="[
                     'w-full px-4 py-2 pr-12 rounded-lg border transition-colors duration-200',
                     getFieldError('confirmPassword') 
                       ? 'border-red-500 focus:border-red-500' 
                       : 'focus:border-blue-500',
                     themeStore.isDarkMode
                       ? 'bg-gray-700 border-gray-600 text-white'
                       : 'bg-white border-gray-300 text-gray-900'
                   ]"
                   placeholder="Confirm your new password">
            <button @click="togglePasswordVisibility('confirm')"
                    type="button"
                    class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
              <EyeIcon v-if="!passwordVisibility.confirm" class="w-5 h-5" />
              <EyeOffIcon v-else class="w-5 h-5" />
            </button>
          </div>
          <p v-if="getFieldError('confirmPassword')" class="text-red-500 text-sm mt-1">
            {{ getFieldError('confirmPassword') }}
          </p>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end pt-4">
          <button @click="resetPasswordForm"
                  type="button"
                  class="mr-3 px-4 py-2 border rounded-lg transition-colors"
                   :class="themeStore.isAdminDark()
                    ? 'border-gray-600 text-gray-300 hover:bg-gray-700' 
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50'">
            Reset
          </button>

          <button @click="onChangePassword"
                  :disabled="isChangingPassword"
                  class="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
            <LockIcon class="w-4 h-4" />
            {{ isChangingPassword ? 'Updating...' : 'Update Password' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Two-Factor Authentication Section -->
    <div class="mb-8 p-6 rounded-lg border"
         :class="themeStore.isDarkMode ? 'border-gray-700 bg-gray-750' : 'border-gray-200 bg-gray-50'">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-3">
          <SmartphoneIcon class="w-5 h-5 text-blue-600" />
          <div>
            <h4 class="text-lg font-semibold"
                :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
              Two-Factor Authentication
            </h4>
            <p class="text-sm"
               :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'">
              Add an extra layer of security to your account
            </p>
          </div>
        </div>

        <!-- 2FA Toggle -->
        <div class="flex items-center">
          <label class="relative inline-flex items-center cursor-pointer">
            <input :checked="securitySettings.twoFactorEnabled"
                   @change="onToggle2FA"
                   :disabled="isEnabling2FA"
                   type="checkbox"
                   class="sr-only peer">
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600 peer-disabled:opacity-50"></div>
          </label>
          <span class="ml-3 text-sm font-medium"
                :class="themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-700'">
            {{ securitySettings.twoFactorEnabled ? 'Enabled' : 'Disabled' }}
          </span>
        </div>
      </div>

      <!-- 2FA Status -->
      <div v-if="securitySettings.twoFactorEnabled" 
           class="flex items-center gap-3 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
        <CheckIcon class="w-5 h-5 text-green-600 dark:text-green-400" />
        <div>
          <p class="text-sm font-medium text-green-800 dark:text-green-200">
            Two-factor authentication is active
          </p>
          <p class="text-sm text-green-700 dark:text-green-300">
            Your account is protected with an additional security layer
          </p>
        </div>
      </div>

      <div v-else 
           class="flex items-center gap-3 p-4 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg">
        <AlertIcon class="w-5 h-5 text-orange-600 dark:text-orange-400" />
        <div>
          <p class="text-sm font-medium text-orange-800 dark:text-orange-200">
            Two-factor authentication is disabled
          </p>
          <p class="text-sm text-orange-700 dark:text-orange-300">
            Enable 2FA to better protect your account from unauthorized access
          </p>
        </div>
      </div>
    </div>

    <!-- Session Management -->
    <div class="p-6 rounded-lg border"
         :class="themeStore.isDarkMode ? 'border-gray-700 bg-gray-750' : 'border-gray-200 bg-gray-50'">
      <h4 class="text-lg font-semibold mb-4"
          :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
        Active Sessions
      </h4>
      
      <div class="space-y-3">
        <!-- Current Session -->
        <div class="flex items-center justify-between p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <div class="flex items-center gap-3">
            <div class="w-2 h-2 bg-green-500 rounded-full"></div>
            <div>
              <p class="font-medium text-blue-800 dark:text-blue-200">Current Session</p>
              <p class="text-sm text-blue-700 dark:text-blue-300">Chrome on Windows • Active now</p>
            </div>
          </div>
          <span class="text-sm font-medium text-blue-600 dark:text-blue-400">This device</span>
        </div>

        <!-- Other Sessions Placeholder -->
        <div class="text-center py-4">
          <p class="text-sm"
             :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'">
            No other active sessions found
          </p>
        </div>
      </div>
    </div>

    <!-- 2FA Setup Modal -->
    <div v-if="show2FAModal" 
         class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-semibold mb-4"
            :class="themeStore.isDarkMode ? 'text-white' : 'text-gray-900'">
          Set Up Two-Factor Authentication
        </h3>
        
        <div v-if="twoFactorSetupData" class="text-center">
          <!-- QR Code would go here -->
          <div class="bg-gray-100 dark:bg-gray-700 rounded-lg p-8 mb-4">
            <p class="text-sm"
               :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'">
              QR Code placeholder
            </p>
          </div>
          
          <p class="text-sm mb-4"
             :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'">
            Scan this QR code with your authenticator app, then enter the verification code below.
          </p>
          
          <input v-model="verificationCode"
                 type="text"
                 placeholder="Enter verification code"
                 class="w-full px-4 py-2 border rounded-lg mb-4 text-center"
                 :class="themeStore.isDarkMode
                   ? 'bg-gray-700 border-gray-600 text-white'
                   : 'bg-white border-gray-300 text-gray-900'">
          
          <div class="flex gap-3">
            <button @click="show2FAModal = false"
                    class="flex-1 px-4 py-2 border rounded-lg"
                    :class="themeStore.isDarkMode 
                      ? 'border-gray-600 text-gray-300 hover:bg-gray-700' 
                      : 'border-gray-300 text-gray-700 hover:bg-gray-50'">
              Cancel
            </button>
            <button class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              Verify & Enable
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>