<script setup>
import { computed, onMounted, ref } from 'vue';
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
  Settings as SettingsIcon,
  Camera as CameraIcon
} from 'lucide-vue-next';

import { settingsService } from '@/services/settingsService';
const handleProfilePictureUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  // Validate file
  if (file.size > 5 * 1024 * 1024) {
    alert('File size must be less than 5MB');
    return;
  }

  if (!file.type.startsWith('image/')) {
    alert('Please select an image file');
    return;
  }

  try {
    const result = await settingsService.uploadProfilePicture(file);
    // Update the user's profile picture in auth store immediately
    if (result.profile_picture && authStore.user) {
      authStore.user.profile_picture = result.profile_picture;
      authStore.setUser(authStore.user);
    }
    event.target.value = '';
    console.log('Profile picture updated successfully');
  } catch (error) {
    console.error('Failed to upload profile picture:', error);
    alert('Failed to upload profile picture: ' + (error.message || 'Unknown error'));
  }
};

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

// Logout confirmation state
const showLogoutConfirmation = ref(false)

const confirmLogout = () => {
  showLogoutConfirmation.value = true
}

const cancelLogout = () => {
  showLogoutConfirmation.value = false
}

const logout = async () => {
  showLogoutConfirmation.value = false
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
  <aside class="bg-white text-green-600 w-full sm:w-[220px] md:w-[240px] lg:w-[260px] min-h-screen max-h-screen overflow-y-auto p-2 sm:p-3 flex flex-col font-['Poppins']">
    <!-- Profile Section -->
    <div class="flex flex-col items-center mb-3 sm:mb-4" v-if="user && user.first_name">
      <div class="relative">
        <img :src="profilePicture" alt="Profile Picture"
          class="w-12 sm:w-16 md:w-18 h-12 sm:h-16 md:h-18 rounded-full border-2 border-green-600 object-cover mb-1" />
        <label for="profilePictureUploadSuperAdmin"
               class="absolute bottom-0 right-0 bg-green-600 text-white p-1 rounded-full hover:bg-green-700 transition-colors cursor-pointer">
          <CameraIcon class="w-3 h-3" />
        </label>
        <input type="file"
               id="profilePictureUploadSuperAdmin"
               accept="image/*"
               @change="handleProfilePictureUpload"
               class="hidden">
      </div>
      <h2 class="text-sm sm:text-base font-semibold text-center leading-tight text-green-600 font-['Poppins']">{{ user.first_name }} {{ user.last_name }}</h2>
      <p class="text-xs sm:text-sm text-green-400 font-['Poppins']">{{ userTypeLabel }}</p>
    </div>

    <!-- Navigation -->
  <nav class="flex-grow overflow-y-auto font-['Poppins']">
      <ul class="space-y-1 sm:space-y-2">
        <li>
          <router-link to="/super-admin"
            class="flex items-center gap-2 p-2 rounded transition text-sm font-['Poppins']"
            :class="isActive('/super-admin') && route.path === '/super-admin'
              ? 'font-semibold text-green-600 bg-green-100'
              : 'hover:text-gray-600 hover:bg-gray-100'">
            <DashboardIcon class="w-4 h-4 text-green-600" /> <span class="text-green-600">Dashboard</span>
          </router-link>
        </li>

        <li>
          <router-link to="/super-admin/user-management"
            class="flex items-center gap-2 p-2 rounded transition text-sm font-['Poppins']"
            :class="isActive('/super-admin/user-management')
              ? 'font-semibold text-green-600 bg-green-100'
              : 'hover:text-gray-600 hover:bg-gray-100'">
            <UserManagementIcon class="w-4 h-4 text-green-600" /> <span class="text-green-600">User Management</span>
          </router-link>
        </li>

        <li>
          <router-link to="/super-admin/survey-management"
            class="flex items-center gap-2 p-2 rounded transition text-sm font-['Poppins']"
            :class="isActive('/super-admin/survey-management')
              ? 'font-semibold text-green-600 bg-green-100'
              : 'hover:text-gray-600 hover:bg-gray-100'">
            <SurveyIcon class="w-4 h-4 text-green-600" /> <span class="text-green-600">Survey Management</span>
          </router-link>
        </li>

        <li>
          <router-link to="/super-admin/alumni-directory"
            class="flex items-center gap-2 p-2 rounded transition text-sm font-['Poppins']"
            :class="isActive('/super-admin/alumni-directory')
              ? 'font-semibold text-green-600 bg-green-100'
              : 'hover:text-gray-600 hover:bg-gray-100'">
            <DirectoryIcon class="w-4 h-4 text-green-600" /> <span class="text-green-600">Alumni Directory</span>
          </router-link>
        </li>

        <li>
          <router-link to="/super-admin/system-monitoring"
            class="flex items-center gap-2 p-2 rounded transition text-sm font-['Poppins']"
            :class="isActive('/super-admin/system-monitoring')
              ? 'font-semibold text-green-600 bg-green-100'
              : 'hover:text-gray-600 hover:bg-gray-100'">
            <MonitoringIcon class="w-4 h-4 text-green-600" /> <span class="text-green-600">System Monitoring</span>
          </router-link>
        </li>

        <li>
          <router-link to="/super-admin/analytic-dashboard"
            class="flex items-center gap-2 p-2 rounded transition text-sm font-['Poppins']"
            :class="isActive('/super-admin/analytic-dashboard')
              ? 'font-semibold text-green-600 bg-green-100'
              : 'hover:text-gray-600 hover:bg-gray-100'">
            <AnalyticsIcon class="w-4 h-4 text-green-600" /> <span class="text-green-600">Analytic Dashboard</span>
          </router-link>
        </li>

        <li>
          <router-link to="/super-admin/pending-user-approval"
            class="flex items-center gap-2 p-2 rounded transition text-sm font-['Poppins']"
            :class="isActive('/super-admin/pending-user-approval')
              ? 'font-semibold text-green-600 bg-green-100'
              : 'hover:text-gray-600 hover:bg-gray-100'">
            <ApprovalIcon class="w-4 h-4 text-green-600" /> <span class="text-green-600">Pending User Approval</span>
          </router-link>
        </li>

        <li>
          <router-link to="/super-admin/settings"
            class="flex items-center gap-2 p-2 rounded transition text-sm font-['Poppins']"
            :class="isActive('/super-admin/settings')
              ? 'font-semibold text-green-600 bg-green-100'
              : 'hover:text-gray-600 hover:bg-gray-100'">
            <SettingsIcon class="w-4 h-4 text-green-600" /> <span class="text-green-600">Settings</span>
          </router-link>
        </li>
      </ul>
    </nav>

    <!-- Logout at the bottom -->
    <div class="border-t border-gray-200 pt-2 mt-2 flex-shrink-0">
      <button @click="confirmLogout"
        class="flex items-center gap-2 w-full text-left p-2 rounded transition text-sm font-['Poppins'] hover:text-red-600 hover:bg-red-100">
        <LogOutIcon class="w-4 h-4 text-green-600" /> <span class="text-green-600">Logout</span>
      </button>
    </div>

    <!-- Logout Confirmation Modal - Positioned like a notification -->
    <div v-if="showLogoutConfirmation" class="fixed top-4 right-4 z-50 max-w-sm w-full p-4">
      <!-- Modal without backdrop -->
      <div class="bg-white/98 rounded-xl shadow-2xl p-6 text-gray-900 border border-gray-300 backdrop-blur-sm animate-fade-in">
        <div class="flex items-center mb-4">
          <div class="flex-shrink-0 w-10 h-10 bg-red-100 rounded-full flex items-center justify-center mr-3">
            <LogOutIcon class="w-5 h-5 text-red-600" />
          </div>
          <h3 class="text-lg font-semibold text-gray-900">
            Confirm Logout
          </h3>
        </div>
        
        <p class="text-sm text-gray-600 mb-6">
          Are you sure you want to logout? You will be redirected to the login page.
        </p>
        
        <div class="flex space-x-3">
          <button
            @click="cancelLogout"
            class="flex-1 px-4 py-2 text-sm font-medium bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors border border-gray-300"
          >
            Cancel
          </button>
          <button
            @click="logout"
            class="flex-1 px-4 py-2 text-sm font-medium bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors border border-red-600"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  </aside>
</template>
