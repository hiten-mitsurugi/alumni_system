<template>
  <div class="flex justify-between items-center px-4 py-4 bg-white shadow"> <!-- changed from py-2 to py-4 -->
    <div class="text-xl font-semibold">Search Alumni Mates</div> <!-- text-lg → text-xl -->
    <div class="flex gap-4 items-center">
      <div class="relative cursor-pointer" @click="$emit('toggleNotification')">
        <svg class="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5" />
        </svg>
        <span v-if="notificationCount"
          class="absolute -top-1 -right-1 bg-red-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
          {{ notificationCount }}
        </span>
      </div>

      <div class="relative" @click="dropdownOpen = !dropdownOpen">
        <img class="w-10 h-10 rounded-full cursor-pointer" src="https://via.placeholder.com/40" alt="Profile" />
        <!-- w-10 h-10 for bigger profile -->
        <div v-if="dropdownOpen" class="absolute right-0 mt-2 w-48 bg-white shadow-md rounded z-50">
          <a href="#" class="block px-4 py-2 hover:bg-gray-100">Settings & Privacy</a>
          <a href="#" class="block px-4 py-2 hover:bg-gray-100">Update Profile</a>
          <a href="#" class="block px-4 py-2 hover:bg-gray-100">Send Feedback</a>
          <button @click.stop="handleLogout" class="w-full text-left px-4 py-2 hover:bg-gray-100 text-red-500">
            Logout
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth' // adjust path if needed

const router = useRouter()
const authStore = useAuthStore()

const notificationCount = ref(0)
const dropdownOpen = ref(false)

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
