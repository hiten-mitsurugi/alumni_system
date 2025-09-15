<script setup>
import { computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth'; // ✅ Using alias

import {
  LogOut as LogOutIcon,
  LayoutDashboard as DashboardIcon,
  UserCog as UserManagementIcon,
  ListChecks as SurveyIcon,
  BookOpenText as DirectoryIcon,
  ActivitySquare as MonitoringIcon,
  BarChart3 as AnalyticsIcon,
  UserCheck2 as ApprovalIcon,
  Settings as SettingsIcon
} from 'lucide-vue-next';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const BASE_URL = 'http://127.0.0.1:8000';

onMounted(async () => {
  if (!authStore.user && authStore.token) {
    try {
      await authStore.fetchUser();
    } catch (error) {
      console.error('Failed to fetch user:', error);
      authStore.logout();
      router.push('/login');
    }
  }
});

const logout = async () => {
  await authStore.logoutWithAPI();
  router.push('/login');
};

const user = computed(() => authStore.user || {});

const profilePicture = computed(() => {
  const pic = user.value.profile_picture;
  return pic && typeof pic === 'string'
    ? (pic.startsWith('http') ? pic : `${BASE_URL}${pic}`)
    : '/default-profile.png';
});

const userTypeLabel = computed(() => {
  switch (user.value.user_type) {
    case 1: return 'Super Admin';
    case 2: return 'Admin';
    case 3: return 'Alumni';
    default: return 'Unknown';
  }
});

const isActive = (path) => route.path.startsWith(path);
</script>

<template>
  <aside class="bg-white text-gray-800 w-[350px] min-h-screen p-4 flex flex-col">
    <!-- Profile Section -->
    <div class="flex flex-col items-center mb-6" v-if="user && user.first_name">
      <img :src="profilePicture" alt="Profile Picture"
        class="w-24 h-24 rounded-full border-2 border-white object-cover mb-2" />
      <h2 class="text-xl font-semibold">{{ user.first_name }} {{ user.last_name }}</h2>
      <p class="text-base text-gray-400">{{ userTypeLabel }}</p>
    </div>

    <!-- Navigation -->
    <nav class="flex-grow">
      <ul class="space-y-3">
        <li>
          <router-link to="/super-admin"
            class="flex items-center gap-3 p-3 rounded transition transform text-lg"
            :class="isActive('/super-admin') && route.path === '/super-admin'
              ? 'font-semibold text-green-600 scale-105 bg-green-100'
              : 'hover:text-gray-600 hover:scale-105 hover:bg-gray-100'">
            <DashboardIcon class="w-6 h-6" /> <span>Dashboard</span>
          </router-link>
        </li>

        <li>
          <router-link to="/super-admin/user-management"
            class="flex items-center gap-3 p-3 rounded transition transform text-lg"
            :class="isActive('/super-admin/user-management')
              ? 'font-semibold text-green-600 scale-105 bg-green-100'
              : 'hover:text-gray-600 hover:scale-105 hover:bg-gray-100'">
            <UserManagementIcon class="w-6 h-6" /> <span>User Management</span>
          </router-link>
        </li>

        <li>
          <router-link to="/super-admin/survey-management"
            class="flex items-center gap-3 p-3 rounded transition transform text-lg"
            :class="isActive('/super-admin/survey-management')
              ? 'font-semibold text-green-600 scale-105 bg-green-100'
              : 'hover:text-gray-600 hover:scale-105 hover:bg-gray-100'">
            <SurveyIcon class="w-6 h-6" /> <span>Survey Management</span>
          </router-link>
        </li>

        <li>
          <router-link to="/super-admin/alumni-directory"
            class="flex items-center gap-3 p-3 rounded transition transform text-lg"
            :class="isActive('/super-admin/alumni-directory')
              ? 'font-semibold text-green-600 scale-105 bg-green-100'
              : 'hover:text-gray-600 hover:scale-105 hover:bg-gray-100'">
            <DirectoryIcon class="w-6 h-6" /> <span>Alumni Directory</span>
          </router-link>
        </li>

        <li>
          <router-link to="/super-admin/system-monitoring"
            class="flex items-center gap-3 p-3 rounded transition transform text-lg"
            :class="isActive('/super-admin/system-monitoring')
              ? 'font-semibold text-green-600 scale-105 bg-green-100'
              : 'hover:text-gray-600 hover:scale-105 hover:bg-gray-100'">
            <MonitoringIcon class="w-6 h-6" /> <span>System Monitoring</span>
          </router-link>
        </li>

        <li>
          <router-link to="/super-admin/analytic-dashboard"
            class="flex items-center gap-3 p-3 rounded transition transform text-lg"
            :class="isActive('/super-admin/analytic-dashboard')
              ? 'font-semibold text-green-600 scale-105 bg-green-100'
              : 'hover:text-gray-600 hover:scale-105 hover:bg-gray-100'">
            <AnalyticsIcon class="w-6 h-6" /> <span>Analytic Dashboard</span>
          </router-link>
        </li>

        <li>
          <router-link to="/super-admin/pending-user-approval"
            class="flex items-center gap-3 p-3 rounded transition transform text-lg"
            :class="isActive('/super-admin/pending-user-approval')
              ? 'font-semibold text-green-600 scale-105 bg-green-100'
              : 'hover:text-gray-600 hover:scale-105 hover:bg-gray-100'">
            <ApprovalIcon class="w-6 h-6" /> <span>Pending User Approval</span>
          </router-link>
        </li>

        <li>
          <router-link to="/super-admin/settings"
            class="flex items-center gap-3 p-3 rounded transition transform text-lg"
            :class="isActive('/super-admin/settings')
              ? 'font-semibold text-green-600 scale-105 bg-green-100'
              : 'hover:text-gray-600 hover:scale-105 hover:bg-gray-100'">
            <SettingsIcon class="w-6 h-6" /> <span>Settings</span>
          </router-link>
        </li>
      </ul>
    </nav>

    <!-- Logout at the bottom -->
    <div class="border-t border-gray-200 pt-4 mt-4">
      <button @click="logout"
        class="flex items-center gap-3 w-full text-left p-3 rounded transition transform text-lg hover:text-red-600 hover:scale-105 hover:bg-red-200">
        <LogOutIcon class="w-6 h-6" /> <span>Logout</span>
      </button>
    </div>
  </aside>
</template>
