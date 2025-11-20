<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth'; // ✅ Using alias
import { useThemeStore } from '@/stores/theme';

import {
  LogOut as LogOutIcon,
  LayoutDashboard as DashboardIcon,
  UserCog as UserManagementIcon,
  ListChecks as SurveyIcon,
  BookOpenText as DirectoryIcon,
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
const themeStore = useThemeStore();

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

// Settings dropdown functionality
const settingsOpen = ref(route.path.startsWith('/super-admin/settings'))

const toggleSettings = (e) => {
  e.preventDefault()
  settingsOpen.value = !settingsOpen.value
  if (settingsOpen.value) {
    // navigate to base settings page if opening
    router.push('/super-admin/settings/profile').catch(() => {})
  }
}

// Watch for route changes to update settings submenu state
watch(() => route.path, (p) => {
  if (p.startsWith('/super-admin/settings')) settingsOpen.value = true
})

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
  <aside :class="['w-full sm:w-[220px] md:w-[240px] lg:w-[260px] min-h-screen max-h-screen overflow-y-auto p-2 sm:p-3 flex flex-col border-r font-[\'Poppins\']', themeStore.isAdminDark() ? 'bg-gray-900 text-gray-100 border-gray-700' : 'bg-white text-gray-800 border-gray-200']">
    <!-- Profile Section -->
    <div class="flex flex-col items-center mb-3 sm:mb-4" v-if="user && user.first_name">
      <div class="relative">
        <img :src="profilePicture" alt="Profile Picture"
          class="w-12 sm:w-16 md:w-18 h-12 sm:h-16 md:h-18 rounded-full border-2 border-gray-900 object-cover mb-1" />
        <label for="profilePictureUploadSuperAdmin"
               class="absolute bottom-0 right-0 bg-orange-500 text-white p-1 rounded-full hover:bg-orange-600 transition-colors cursor-pointer">
          <CameraIcon class="w-3 h-3" />
        </label>
        <input type="file"
               id="profilePictureUploadSuperAdmin"
               accept="image/*"
               @change="handleProfilePictureUpload"
               class="hidden">
      </div>
      <h2 :class="['text-sm sm:text-base font-semibold text-center leading-tight font-[\'Poppins\']', themeStore.isAdminDark() ? 'text-gray-100' : 'text-gray-900']">{{ user.first_name }} {{ user.last_name }}</h2>
      <p :class="['text-xs sm:text-sm font-[\'Poppins\']', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">{{ userTypeLabel }}</p>
    </div>

    <!-- Navigation -->
  <nav class="flex-grow overflow-y-auto font-['Poppins']">
      <ul class="space-y-1 sm:space-y-2">
        <li>
          <router-link to="/super-admin"
            class="flex items-center gap-2 p-2 rounded transition text-sm font-['Poppins'] group"
            :class="isActive('/super-admin') && route.path === '/super-admin'
              ? (themeStore.isAdminDark() ? 'font-semibold text-orange-500 bg-orange-900/40' : 'font-semibold text-orange-600 bg-orange-100') 
              : (themeStore.isAdminDark() ? 'hover:text-gray-200 hover:bg-gray-800/50' : 'hover:text-gray-600 hover:bg-gray-100')">
            <DashboardIcon class="w-4 h-4" />
            <span>Dashboard</span>
          </router-link>
        </li>

        <li>
          <router-link to="/super-admin/user-management"
            class="flex items-center gap-2 p-2 rounded transition text-sm font-['Poppins'] group"
            :class="isActive('/super-admin/user-management')
              ? (themeStore.isAdminDark() ? 'font-semibold text-orange-500 bg-orange-900/40' : 'font-semibold text-orange-600 bg-orange-100') 
              : (themeStore.isAdminDark() ? 'hover:text-gray-200 hover:bg-gray-800/50' : 'hover:text-gray-600 hover:bg-gray-100')">
            <UserManagementIcon class="w-4 h-4" />
            <span>User Management</span>
          </router-link>
        </li>

        <li>
          <router-link to="/super-admin/survey-management"
            class="flex items-center gap-2 p-2 rounded transition text-sm font-['Poppins'] group"
            :class="isActive('/super-admin/survey-management')
              ? (themeStore.isAdminDark() ? 'font-semibold text-orange-500 bg-orange-900/40' : 'font-semibold text-orange-600 bg-orange-100') 
              : (themeStore.isAdminDark() ? 'hover:text-gray-200 hover:bg-gray-800/50' : 'hover:text-gray-600 hover:bg-gray-100')">
            <SurveyIcon class="w-4 h-4" />
            <span>Survey Management</span>
          </router-link>
        </li>

        <li>
          <router-link to="/super-admin/alumni-directory"
            class="flex items-center gap-2 p-2 rounded transition text-sm font-['Poppins'] group"
            :class="isActive('/super-admin/alumni-directory')
              ? (themeStore.isAdminDark() ? 'font-semibold text-orange-500 bg-orange-900/40' : 'font-semibold text-orange-600 bg-orange-100') 
              : (themeStore.isAdminDark() ? 'hover:text-gray-200 hover:bg-gray-800/50' : 'hover:text-gray-600 hover:bg-gray-100')">
            <DirectoryIcon class="w-4 h-4" />
            <span>Alumni Directory</span>
          </router-link>
        </li>

        <li>
          <router-link to="/super-admin/pending-user-approval"
            class="flex items-center gap-2 p-2 rounded transition text-sm font-['Poppins'] group"
            :class="isActive('/super-admin/pending-user-approval')
              ? (themeStore.isAdminDark() ? 'font-semibold text-orange-500 bg-orange-900/40' : 'font-semibold text-orange-600 bg-orange-100') 
              : (themeStore.isAdminDark() ? 'hover:text-gray-200 hover:bg-gray-800/50' : 'hover:text-gray-600 hover:bg-gray-100')">
            <ApprovalIcon class="w-4 h-4" />
            <span>Pending User Approval</span>
          </router-link>
        </li>

        <li>
          <!-- Settings Dropdown -->
          <div class="space-y-1">
            <button 
              @click="toggleSettings"
              class="w-full flex items-center gap-2 p-2 rounded transition text-sm font-['Poppins'] group"
              :class="settingsOpen ? (themeStore.isAdminDark() ? 'font-semibold text-orange-500 bg-orange-900/40' : 'font-semibold text-orange-600 bg-orange-100') 
                                    : (themeStore.isAdminDark() ? 'hover:text-gray-200 hover:bg-gray-800/50' : 'hover:text-gray-600 hover:bg-gray-100')"
            >
              <SettingsIcon class="w-4 h-4" />
              <span>Settings</span>
              <svg class="ml-auto w-4 h-4 transition-transform duration-200" 
                   :class="settingsOpen ? 'rotate-180' : ''"
                   fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
            </button>

            <!-- Settings Submenu -->
            <Transition 
              enter-active-class="transition-all duration-200"
              enter-from-class="opacity-0 max-h-0"
              enter-to-class="opacity-100 max-h-40"
              leave-active-class="transition-all duration-200"
              leave-from-class="opacity-100 max-h-40"
              leave-to-class="opacity-0 max-h-0"
            >
              <div v-show="settingsOpen" class="ml-4 overflow-hidden space-y-1">
                <router-link 
                  to="/super-admin/settings/profile" 
                  class="flex items-center gap-2 p-2 rounded transition text-sm font-['Poppins']"
                  :class="route.path === '/super-admin/settings/profile' 
                            ? (themeStore.isAdminDark() ? 'text-orange-400 bg-orange-900/30' : 'text-orange-600 bg-orange-50') 
                            : (themeStore.isAdminDark() ? 'text-gray-300 hover:text-gray-200 hover:bg-gray-800/50' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100')"
                >
                  Profile
                </router-link>
                
                <router-link 
                  to="/super-admin/settings/account" 
                  class="flex items-center gap-2 p-2 rounded transition text-sm font-['Poppins']"
                  :class="route.path === '/super-admin/settings/account' 
                            ? (themeStore.isAdminDark() ? 'text-orange-400 bg-orange-900/30' : 'text-orange-600 bg-orange-50') 
                            : (themeStore.isAdminDark() ? 'text-gray-300 hover:text-gray-200 hover:bg-gray-800/50' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100')"
                >
                  Account & Security
                </router-link>
                
                <router-link 
                  to="/super-admin/settings/appearance" 
                  class="flex items-center gap-2 p-2 rounded transition text-sm font-['Poppins']"
                  :class="route.path === '/super-admin/settings/appearance' 
                            ? (themeStore.isAdminDark() ? 'text-orange-400 bg-orange-900/30' : 'text-orange-600 bg-orange-50') 
                            : (themeStore.isAdminDark() ? 'text-gray-300 hover:text-gray-200 hover:bg-gray-800/50' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100')"
                >
                  Appearance
                </router-link>
              </div>
            </Transition>
          </div>
        </li>
      </ul>
    </nav>

    <!-- Logout at the bottom -->
    <div :class="['pt-2 mt-2 flex-shrink-0 border-t', themeStore.isAdminDark() ? 'border-gray-700' : 'border-gray-200']">
      <button @click="confirmLogout"
        :class="['flex items-center gap-2 w-full text-left p-2 rounded transition text-sm font-[\'Poppins\']', themeStore.isAdminDark() ? 'hover:text-red-400 hover:bg-red-900/40' : 'hover:text-red-600 hover:bg-red-100']">
        <LogOutIcon class="w-4 h-4" /> 
        <span>Logout</span>
      </button>
    </div>

    <!-- Logout Confirmation Modal - Positioned like a notification -->
    <div v-if="showLogoutConfirmation" class="fixed top-4 right-4 z-50 max-w-sm w-full p-4">
      <!-- Modal without backdrop -->
      <div :class="['rounded-xl shadow-2xl p-6 backdrop-blur-sm animate-fade-in', themeStore.isAdminDark() ? 'bg-gray-800/98 text-gray-100 border border-gray-600' : 'bg-white/98 text-gray-900 border border-gray-300']">
        <div class="flex items-center mb-4">
          <div :class="['flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center mr-3', themeStore.isAdminDark() ? 'bg-red-900/40' : 'bg-red-100']">
            <LogOutIcon class="w-5 h-5 text-red-600" />
          </div>
          <h3 :class="['text-lg font-semibold', themeStore.isAdminDark() ? 'text-gray-100' : 'text-gray-900']">
            Confirm Logout
          </h3>
        </div>
        
        <p :class="['text-sm mb-6', themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-600']">
          Are you sure you want to logout? You will be redirected to the login page.
        </p>
        
        <div class="flex space-x-3">
          <button
            @click="cancelLogout"
            :class="['flex-1 px-4 py-2 text-sm font-medium rounded-lg transition-colors border', themeStore.isAdminDark() ? 'bg-gray-700 text-gray-200 border-gray-600 hover:bg-gray-600' : 'bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200']"
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
