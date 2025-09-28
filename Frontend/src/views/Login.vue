<!-- eslint-disable vue/multi-word-component-names -->
<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import api from '../services/api';
import backgroundImage from "@/assets/Background.png";

const email = ref('');
const password = ref('');
const error = ref('');
const showPassword = ref(false);
const router = useRouter();
const authStore = useAuthStore();

const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
const validatePassword = (password) =>
  /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/.test(password);

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
  try {
    const response = await api.post('/login/', {
      email: email.value,
      password: password.value,
    });
    authStore.setToken(response.data.token);
    authStore.setUser(response.data.user);
    if (response.data.user.user_type === 1) {
      router.push('/super-admin');
    } else if (response.data.user.user_type === 2) {
      router.push('/admin');
    } else if (response.data.user.user_type === 3) {
      router.push('/alumni');
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Login failed. Please try again.';
    console.error('Login error:', error.value);
  }
};

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value;
};
</script>

<template>
  <div
    class="min-h-screen bg-cover bg-center flex flex-col"
    :style="{ backgroundImage: `url(${backgroundImage})` }"
  >
    <!-- Main Content -->
    <div class="flex flex-1 items-center justify-center px-6 md:px-16">
      <!-- Left Section -->
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

      <!-- Right Section (Login Form) -->
      <div class="w-full md:w-1/2 flex justify-center">
        <div class="bg-white bg-opacity-90 backdrop-blur-md shadow-lg rounded-xl p-8 max-w-md w-full">
          <h2 class="text-3xl font-bold text-center text-gray-800 mb-4">
            Alumni Mates
          </h2>

          <!-- Small logos in login form -->
          <div class="flex justify-center space-x-4 mb-4">
            <img src="@/assets/CSU Icon.png" alt="CSU Logo" class="h-12 w-auto" />
            <img src="@/assets/ARO_logo-removebg-preview.png" alt="ARO Logo" class="h-12 w-auto" />
          </div>

          <h3 class="text-xl font-semibold text-center mb-6 text-gray-800">
            Login
          </h3>

          <!-- Form Start -->
          <form @submit.prevent="login" class="space-y-4">
            <input
              v-model="email"
              type="email"
              placeholder="Email"
              class="w-full p-3 bg-white border border-gray-300 text-gray-900 placeholder-gray-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
            <div class="relative">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Password"
                class="w-full p-3 bg-white border border-gray-300 text-gray-900 placeholder-gray-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 pr-12"
                required
              />
              <button
                type="button"
                @click="togglePasswordVisibility"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500 hover:text-gray-700"
              >
                <svg
                  v-if="!showPassword"
                  class="h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  ></path>
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  ></path>
                </svg>
                <svg
                  v-else
                  class="h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"
                  ></path>
                </svg>
              </button>
            </div>
            <button
              type="submit"
              class="w-full bg-green-700 text-white py-3 rounded-lg hover:bg-green-800 font-medium"
            >
              Login
            </button>
            <p v-if="error" class="text-red-500 text-sm text-center">{{ error }}</p>
            <p class="text-center text-sm text-gray-600">
              Don't have an account?
              <router-link to="/register" class="text-blue-600 hover:text-blue-700 hover:underline">
                Register
              </router-link>
            </p>
          </form>
          <!-- Form End -->
        </div>
      </div>
    </div>
  </div>
</template>
