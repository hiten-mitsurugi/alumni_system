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
  <aside class="bg-green-700 text-white w-70 min-h-screen p-4">
    <!-- Profile Section -->
    <div class="flex flex-col items-center mb-6" v-if="user && user.first_name">
      <img :src="profilePicture" alt="Profile Picture" class="w-20 h-20 rounded-full border-2 border-white object-cover mb-2" />
      <h2 class="text-lg font-semibold">{{ user.first_name }} {{ user.last_name }}</h2>
      <p class="text-sm text-gray-300">{{ userTypeLabel }}</p>
    </div>

    <!-- Navigation -->
    <nav>
      <ul class="space-y-2">
        <li>
          <router-link to="/super-admin" class="flex items-center gap-2 p-2 rounded"
            :class="isActive('/super-admin') && route.path === '/super-admin' ? 'bg-gray-900 font-semibold' : 'hover:bg-green-800'">
            <DashboardIcon class="w-5 h-5" /> Dashboard
          </router-link>
        </li>
        <li>
          <router-link to="/super-admin/user-management" class="flex items-center gap-2 p-2 rounded"
            :class="isActive('/super-admin/user-management') ? 'bg-gray-900 font-semibold' : 'hover:bg-green-800'">
            <UserManagementIcon class="w-5 h-5" /> User Management
          </router-link>
        </li>
        <li>
          <router-link to="/super-admin/survey-management" class="flex items-center gap-2 p-2 rounded"
            :class="isActive('/super-admin/survey-management') ? 'bg-gray-900 font-semibold' : 'hover:bg-green-800'">
            <SurveyIcon class="w-5 h-5" /> Survey Management
          </router-link>
        </li>
        <li>
          <router-link to="/super-admin/alumni-directory" class="flex items-center gap-2 p-2 rounded"
            :class="isActive('/super-admin/alumni-directory') ? 'bg-gray-900 font-semibold' : 'hover:bg-green-800'">
            <DirectoryIcon class="w-5 h-5" /> Alumni Directory
          </router-link>
        </li>
        <li>
          <router-link to="/super-admin/system-monitoring" class="flex items-center gap-2 p-2 rounded"
            :class="isActive('/super-admin/system-monitoring') ? 'bg-gray-900 font-semibold' : 'hover:bg-green-800'">
            <MonitoringIcon class="w-5 h-5" /> System Monitoring
          </router-link>
        </li>
        <li>
          <router-link to="/super-admin/analytic-dashboard" class="flex items-center gap-2 p-2 rounded"
            :class="isActive('/super-admin/analytic-dashboard') ? 'bg-gray-900 font-semibold' : 'hover:bg-green-800'">
            <AnalyticsIcon class="w-5 h-5" /> Analytic Dashboard
          </router-link>
        </li>
        <li>
          <router-link to="/super-admin/pending-user-approval" class="flex items-center gap-2 p-2 rounded"
            :class="isActive('/super-admin/pending-user-approval') ? 'bg-gray-900 font-semibold' : 'hover:bg-green-800'">
            <ApprovalIcon class="w-5 h-5" /> Pending User Approval
          </router-link>
        </li>
        <li>
          <router-link to="/super-admin/settings" class="flex items-center gap-2 p-2 rounded"
            :class="isActive('/super-admin/settings') ? 'bg-gray-900 font-semibold' : 'hover:bg-green-800'">
            <SettingsIcon class="w-5 h-5" /> Settings
          </router-link>
        </li>
        <li>
          <button @click="logout" class="flex items-center gap-2 w-full text-left p-2 hover:bg-green-800 rounded">
            <LogOutIcon class="w-5 h-5" /> Logout
          </button>
        </li>
      </ul>
    </nav>
  </aside>
</template>
