<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <nav :class="['fixed top-0 left-0 right-0 py-4 px-8 flex justify-between items-center z-50 shadow-md', isDark ? 'bg-gray-800 text-white' : 'bg-orange-600 text-white']">
    <div class="text-2xl font-bold">ATENDA</div>
    <div class="space-x-6">
      <router-link
        to="/login"
        class="inline-block font-semibold transition-transform duration-300 transform hover:scale-125"
      >
        Login
      </router-link>
      <router-link
        to="/register"
        class="inline-block font-semibold transition-transform duration-300 transform hover:scale-125"
      >
        Signup
      </router-link>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isAdminDark?.() || false)
</script>


