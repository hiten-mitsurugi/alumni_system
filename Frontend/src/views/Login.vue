<!-- eslint-disable vue/multi-word-component-names -->
<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useUiStore } from '../stores/ui';
import api from '../services/api';
import backgroundImage from "@/assets/Background.png";
import { Eye as EyeIcon, EyeOff as EyeOffIcon } from 'lucide-vue-next';
import LoginLoading from '../components/common/LoginLoading.vue';

// Refs and stores
const email = ref('');
const password = ref('');
const error = ref('');
const showPassword = ref(false);
const loggingIn = ref(false);
const router = useRouter();
const authStore = useAuthStore();
const ui = useUiStore();

const validateEmail = (email) => /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email);
const validatePassword = (password) =>
  /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/.test(password);

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value;
};

const login = async () => {
  error.value = '';
  if (!validateEmail(email.value)) {
    error.value = 'Invalid email format';
    return;
  }
  if (!validatePassword(password.value)) {
    error.value =
      'Password must be at least 8 characters, with 1 uppercase, 1 lowercase, 1 number, and 1 special character';
    return;
  }
  loggingIn.value = true;
  try {
    const response = await api.post('/auth/login/', {
      email: email.value,
      password: password.value,
    });
    // Set user data immediately
    authStore.setToken(response.data.token, null);
    authStore.setUser(response.data.user);
    
    // Redirect immediately based on user type
    if (response.data.user.user_type === 1) {
      router.push('/super-admin');
    } else if (response.data.user.user_type === 2) {
      router.push('/admin');
    } else if (response.data.user.user_type === 3) {
      router.push('/alumni/home');
    }
  } catch (err) {
    // Show error immediately without loading
    error.value = err.response?.data?.detail || 'Invalid email or password';
    console.error('Login error:', error.value);
    loggingIn.value = false;
  }
};
</script>

<template>
  <div>
    <LoginLoading v-if="loggingIn" />
    <div
      class="min-h-screen bg-cover bg-center flex flex-col login-container"
      :style="{ backgroundImage: `url(${backgroundImage})` }"
    >
    <!-- Main Content -->
    <div class="flex flex-1 items-center justify-center px-6 md:px-16">
      <!-- Left Section -->
      <div class="hidden md:flex w-1/2 justify-center">
        <div class="flex flex-col items-center text-white ml-12 text-center">
          <h1 class="text-6xl font-extrabold">Welcome to ATENDA</h1>
          <p class="text-4xl mt-4">Connecting Alumni, Building Futures</p>
          <div class="flex space-x-8 mt-10">
            <img src="@/assets/CSU Icon.png" alt="Logo 2" class="h-68" />
            <img src="@/assets/CCIS.png" alt="Logo 1" class="h-68" />
          </div>
        </div>
      </div>

      <!-- Right Section (Login Form) -->
      <div class="w-full md:w-1/2 flex justify-center">
        <div class="login-form bg-white bg-opacity-90 backdrop-blur-md shadow-lg rounded-xl p-8 max-w-md w-full">
          <h2 class="text-3xl font-bold text-center text-gray-800 mb-4">ATENDA</h2>
          <h3 class="text-xl font-semibold text-center mb-6 text-black">Login</h3>

          <!-- Form Start -->
          <form @submit.prevent="login" class="space-y-4">
            <input
              v-model="email"
              type="email"
              placeholder="Email"
              class="login-input w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-gray-900 placeholder-gray-500"
              style="background-color: #ffffff; color: #111827;"
              required
              @keydown.enter="login"
            />
            <div class="relative">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Password"
                class="login-input w-full p-3 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-gray-900 placeholder-gray-500"
                style="background-color: #ffffff; color: #111827;"
                required
                @keydown.enter="login"
              />
              <button
                type="button"
                @click="togglePasswordVisibility"
                class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 focus:outline-none"
              >
                <EyeIcon v-if="!showPassword" class="w-5 h-5" />
                <EyeOffIcon v-else class="w-5 h-5" />
              </button>
            </div>
            <button
              type="submit"
              :disabled="ui.isLoading"
              class="w-full bg-orange-500 text-white py-3 rounded-lg hover:bg-orange-600 font-medium disabled:opacity-60"
            >
              Login
            </button>
            <p v-if="error" class="text-red-500 text-sm text-center">{{ error }}</p>
            <div class="flex justify-between items-center text-sm mt-4">
              <router-link to="/forgot-password" class="text-orange-600 hover:underline">
                Forgot Password?
              </router-link>
              <span class="text-gray-600">
                Don't have an account?
                <router-link to="/register" class="text-orange-600 hover:underline">Register</router-link>
              </span>
            </div>
          </form>
          <!-- Form End -->
        </div>
      </div>
    </div>
  </div>
  </div>
</template>

<style scoped>
/* Force login page to always stay in light mode */
.login-container {
  background-color: #f9fafb !important;
  color: #111827 !important;
}

.login-container * {
  color: inherit !important;
}

.login-form {
  background-color: rgba(255, 255, 255, 0.9) !important;
  backdrop-filter: blur(12px) !important;
  color: #111827 !important;
}

.login-form h2,
.login-form h3 {
  color: #111827 !important;
}

.login-form span {
  color: #4b5563 !important;
}

.login-input,
input[type="email"],
input[type="password"] {
  background-color: #ffffff !important;
  color: #111827 !important;
  border-color: #d1d5db !important;
  appearance: none !important;
  -webkit-appearance: none !important;
  box-shadow: inset 0 0 0 50px #ffffff !important;
  -webkit-box-shadow: inset 0 0 0 50px #ffffff !important;
  -webkit-text-fill-color: #111827 !important;
}

.login-input::placeholder,
input[type="email"]::placeholder,
input[type="password"]::placeholder {
  color: #9ca3af !important;
}

.login-input:focus,
input[type="email"]:focus,
input[type="password"]:focus {
  outline: none !important;
  box-shadow: 0 0 0 2px #f97316, inset 0 0 0 50px #ffffff !important;
  -webkit-box-shadow: 0 0 0 2px #f97316, inset 0 0 0 50px #ffffff !important;
  border-color: #f97316 !important;
  -webkit-text-fill-color: #111827 !important;
  background-color: #ffffff !important;
}

input[type="email"]:-webkit-autofill,
input[type="password"]:-webkit-autofill {
  -webkit-box-shadow: 0 0 0 30px white inset !important;
  -webkit-text-fill-color: #111827 !important;
  background-color: #ffffff !important;
}

input[type="email"]:-webkit-autofill:focus,
input[type="password"]:-webkit-autofill:focus {
  -webkit-box-shadow: 0 0 0 2px #f97316, 0 0 0 30px white inset !important;
  -webkit-text-fill-color: #111827 !important;
  background-color: #ffffff !important;
}

/* Override any potential dark mode styles */
html.dark .login-container,
.dark .login-container {
  background-color: #f9fafb !important;
  color: #111827 !important;
}

html.dark .login-form,
.dark .login-form {
  background-color: rgba(255, 255, 255, 0.9) !important;
  color: #111827 !important;
}

html.dark .login-form *,
.dark .login-form * {
  color: #111827 !important;
}

html.dark .login-input,
.dark .login-input,
html.dark input[type="email"],
.dark input[type="email"],
html.dark input[type="password"],
.dark input[type="password"] {
  background-color: #ffffff !important;
  color: #111827 !important;
  border-color: #d1d5db !important;
  -webkit-text-fill-color: #111827 !important;
}

/* Ensure router-links stay correct colors */
.login-form a {
  color: #ea580c !important;
}

.login-form span {
  color: #4b5563 !important;
}

/* Override any global dark theme */
:global(.dark) .login-container {
  background-color: #f9fafb !important;
  color: #111827 !important;
}

:global(.dark) .login-form {
  background-color: rgba(255, 255, 255, 0.9) !important;
  color: #111827 !important;
}
</style>