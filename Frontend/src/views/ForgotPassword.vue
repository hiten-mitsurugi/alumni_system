<!-- eslint-disable vue/multi-word-component-names -->
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUiStore } from '../stores/ui'
import api from '../services/api'
import backgroundImage from '@/assets/Background.png'
import { ArrowLeft, CheckCircle, AlertCircle } from 'lucide-vue-next'

const router = useRouter()
const ui = useUiStore()
const email = ref('')
const error = ref('')
const success = ref('')
const step = ref('email') // 'email', 'code', 'password'
const resetCode = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)

const requestReset = async () => {
  error.value = ''
  success.value = ''

  if (!validateEmail(email.value)) {
    error.value = 'Please enter a valid email address'
    return
  }

  try {
    ui.start('Sending reset link...')
    await api.post('/auth/forgot-password/', { email: email.value })
    success.value = 'Reset link has been sent to your email. Please check your inbox.'
    step.value = 'code'
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to send reset link. Please try again.'
  } finally {
    ui.stop()
  }
}

const verifyAndReset = async () => {
  error.value = ''
  success.value = ''

  if (!resetCode.value) {
    error.value = 'Please enter the verification code'
    return
  }

  if (!newPassword.value || !confirmPassword.value) {
    error.value = 'Please enter both password fields'
    return
  }

  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/
  if (!passwordRegex.test(newPassword.value)) {
    error.value = 'Password must be at least 8 characters with uppercase, lowercase, number, and special character'
    return
  }

  try {
    ui.start('Resetting password...')
    await api.post('/auth/reset-password/', {
      email: email.value,
      code: resetCode.value,
      new_password: newPassword.value
    })
    success.value = 'Password reset successfully! Redirecting to login...'
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to reset password. Please try again.'
  } finally {
    ui.stop()
  }
}

const goBack = () => {
  if (step.value === 'code' || step.value === 'password') {
    step.value = 'email'
    resetCode.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
    error.value = ''
    success.value = ''
  } else {
    router.push('/login')
  }
}
</script>

<template>
  <div
    class="min-h-screen bg-cover bg-center flex flex-col"
    :style="{ backgroundImage: `url(${backgroundImage})` }"
  >
    <!-- Main Content -->
    <div class="flex flex-1 items-center justify-center px-6 md:px-16">
      <!-- Left Section (Hidden on mobile) -->
      <div class="hidden md:flex w-1/2 justify-center">
        <div class="flex flex-col items-center text-white ml-12 text-center">
          <h1 class="text-6xl font-extrabold">Welcome to Alumni Mates</h1>
          <p class="text-4xl mt-4">Connecting Alumni, Building Futures</p>
          <div class="flex space-x-8 mt-10">
            <img src="@/assets/CSU Icon.png" alt="Logo 2" class="h-68" />
            <img src="@/assets/ARO_logo-removebg-preview.png" alt="Logo 1" class="h-68" />
          </div>
        </div>
      </div>

      <!-- Right Section (Reset Form) -->
      <div class="w-full md:w-1/2 flex justify-center">
        <div class="bg-white bg-opacity-90 backdrop-blur-md shadow-lg rounded-xl p-8 max-w-md w-full">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-3xl font-bold text-gray-800">Reset Password</h2>
            <button
              @click="goBack"
              class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              title="Go back"
            >
              <ArrowLeft class="w-5 h-5" />
            </button>
          </div>

          <!-- Step 1: Email -->
          <div v-if="step === 'email'" class="space-y-4">
            <p class="text-gray-600 text-sm mb-6">
              Enter your email address and we'll send you a link to reset your password.
            </p>
            <input
              v-model="email"
              type="email"
              placeholder="Enter your email"
              class="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              @keydown.enter="requestReset"
            />
            <button
              @click="requestReset"
              :disabled="ui.isLoading"
              class="w-full bg-orange-500 text-white py-3 rounded-lg hover:bg-orange-600 font-medium disabled:opacity-60 transition-colors"
            >
              {{ ui.isLoading ? 'Sending...' : 'Send Reset Link' }}
            </button>
            <p v-if="error" class="text-red-500 text-sm flex items-center gap-2">
              <AlertCircle class="w-4 h-4" />
              {{ error }}
            </p>
          </div>

          <!-- Step 2: Code & New Password -->
          <div v-if="step === 'code'" class="space-y-4">
            <div v-if="success" class="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
              <CheckCircle class="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <p class="text-green-700 text-sm">{{ success }}</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Verification Code</label>
              <input
                v-model="resetCode"
                type="text"
                placeholder="Enter the code from your email"
                class="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
              <p class="text-xs text-gray-500 mt-1">Check your email for the reset code</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">New Password</label>
              <div class="relative">
                <input
                  v-model="newPassword"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="Enter new password"
                  class="w-full p-3 pr-12 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {{ showPassword ? '👁️' : '👁️‍🗨️' }}
                </button>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Confirm Password</label>
              <div class="relative">
                <input
                  v-model="confirmPassword"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  placeholder="Confirm new password"
                  class="w-full p-3 pr-12 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  @keydown.enter="verifyAndReset"
                />
                <button
                  type="button"
                  @click="showConfirmPassword = !showConfirmPassword"
                  class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {{ showConfirmPassword ? '👁️' : '👁️‍🗨️' }}
                </button>
              </div>
            </div>

            <p class="text-xs text-gray-500 bg-gray-50 p-3 rounded">
              Password must be at least 8 characters with uppercase, lowercase, number, and special character.
            </p>

            <button
              @click="verifyAndReset"
              :disabled="ui.isLoading"
              class="w-full bg-orange-500 text-white py-3 rounded-lg hover:bg-orange-600 font-medium disabled:opacity-60 transition-colors"
            >
              {{ ui.isLoading ? 'Resetting...' : 'Reset Password' }}
            </button>

            <p v-if="error" class="text-red-500 text-sm flex items-center gap-2">
              <AlertCircle class="w-4 h-4" />
              {{ error }}
            </p>
          </div>

          <!-- Back to Login Link -->
          <div class="mt-6 text-center">
            <router-link to="/login" class="text-blue-600 hover:underline text-sm">
              Back to Login
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
