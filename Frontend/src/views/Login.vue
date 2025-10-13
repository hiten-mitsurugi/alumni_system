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
    const response = await api.post('/auth/login/', {
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
          <h2 class="text-3xl font-bold text-center text-gray-800 mb-4">Alumni Mates</h2>
          <div class="flex justify-center items-center space-x-4 mb-6">
            <img src="@/assets/CSU Icon.png" alt="Logo 1" class="h-12" />
            <img src="@/assets/ARO_logo-removebg-preview.png" alt="Logo 2" class="h-12" />
          </div>
          <h3 class="text-xl font-semibold text-center mb-6">Login</h3>

          <!-- Form Start -->
          <form @submit.prevent="login" class="space-y-4">
            <input
              v-model="email"
              type="email"
              placeholder="Email"
              class="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
            <input
              v-model="password"
              type="password"
              placeholder="Password"
              class="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
            <button
              type="submit"
              class="w-full bg-green-700 text-white py-3 rounded-lg hover:bg-green-800 font-medium"
            >
              Login
            </button>
            <p v-if="error" class="text-red-500 text-sm text-center">{{ error }}</p>
            <p class="text-center text-sm">
              Don't have an account?
              <router-link to="/register" class="text-blue-600 hover:underline">Register</router-link>
            </p>
          </form>
          <!-- Form End -->
        </div>
      </div>
    </div>
  </div>
</template>