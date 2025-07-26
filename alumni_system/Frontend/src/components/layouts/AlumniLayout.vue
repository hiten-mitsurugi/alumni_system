<script setup>
import { useAuthStore } from '../../stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const logout = () => {
  authStore.logout();
  router.push('/login');
};
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-green-500 text-white p-4">
      <div class="flex justify-between items-center">
        <h1 class="text-xl font-bold">Alumni Dashboard</h1>
        <button @click="logout" class="bg-red-500 px-4 py-2 rounded hover:bg-red-600">
          Logout
        </button>
      </div>
    </header>
    <main class="p-6">
      <slot />
    </main>
  </div>
</template>