<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth'; // ✅ Use alias
import { useMessagingNotificationStore } from '@/stores/messagingNotifications';
import { useThemeStore } from '@/stores/theme';
import axios from 'axios';

import {
  LogOut as LogOutIcon,
  LayoutDashboard as LayoutDashboardIcon,
  Users as UsersIcon,
  FileText as FileTextIcon,
  ShieldCheck as ShieldCheckIcon,
  UserCheck as UserCheckIcon,
  Settings as SettingsIcon,
  MessageCircle as MessageCircleIcon,
  X as XIcon
} from 'lucide-vue-next';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const messagingNotificationStore = useMessagingNotificationStore();
const themeStore = useThemeStore();

// Logout modal state
const showLogoutModal = ref(false);

// Reports count
const reportedPostsCount = ref(0);

const BASE_URL = 'http://127.0.0.1:8000';

onMounted(async () => {
  // Initialize theme
  themeStore.initializeTheme();

  if (!authStore.user && authStore.token) {
    try {
      await authStore.fetchUser();
    } catch (error) {
      console.error('Failed to fetch user:', error);
      authStore.logout();
      router.push('/login');
    }
  }

  // Initialize messaging notification store for admin
  console.log('🔧 AdminSidebar: Component mounted, checking initialization...');
  console.log('🔧 AdminSidebar: Auth user:', authStore.user?.id);
  console.log('🔧 AdminSidebar: Store initialized:', messagingNotificationStore.isInitialized);

  if (authStore.user && !messagingNotificationStore.isInitialized) {
    console.log('🔧 AdminSidebar: Initializing messaging notification store...');
    await messagingNotificationStore.initialize();
    console.log('🔧 AdminSidebar: Store initialization complete');
  } else if (!authStore.user) {
    console.log('🔧 AdminSidebar: No user found, skipping store initialization');
  } else {
    console.log('🔧 AdminSidebar: Store already initialized');
  }

// 🔧 ENHANCEMENT: Force refresh counts to ensure real-time accuracy
  if (authStore.user) {
    console.log('🔄 AdminSidebar: Force refreshing notification counts...');
    await messagingNotificationStore.forceRefresh();
    await fetchReportedPostsCount();
  }
});

// Function to fetch reported posts count
const fetchReportedPostsCount = async () => {
  try {
    if (!authStore.token || !authStore.user) return;

    // Check if user is admin
    if (!authStore.user.user_type || ![1, 2].includes(authStore.user.user_type)) return;

    const response = await axios.get(`${BASE_URL}/api/posts/reports/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
      params: { status: 'pending', page_size: 1 }
    });

    reportedPostsCount.value = response.data.stats?.total_reports || 0;
  } catch (error) {
    console.error('Error fetching reported posts count:', error);
    reportedPostsCount.value = 0;
  }
};

// Modal functions
const openLogoutModal = () => {
  showLogoutModal.value = true;
};

const closeLogoutModal = () => {
  showLogoutModal.value = false;
};

const confirmLogout = async () => {
  try {
    // Cleanup messaging notifications on logout
    messagingNotificationStore.cleanup();
    await authStore.logoutWithAPI();
    showLogoutModal.value = false;
    router.push('/login');
  } catch (error) {
    console.error('Logout error:', error);
    // Still navigate to login even if API call fails
    showLogoutModal.value = false;
    router.push('/login');
  }
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

// Computed property for messaging badge count
const messagingBadgeCount = computed(() => {
  const count = messagingNotificationStore.totalUnreadCount;
  return count > 0 ? count.toString() : null;
});

const isActive = (path) => route.path.startsWith(path);
</script>

<template>
  <aside class="w-70 min-h-screen p-4 transition-colors duration-200"
         :class="themeStore.isDarkMode ? 'bg-gray-800 text-white' : 'bg-green-700 text-white'">
    <!-- Profile Section -->
    <div class="flex flex-col items-center mb-6" v-if="user && user.first_name">
      <img :src="profilePicture" alt="Profile Picture"
           class="w-20 h-20 rounded-full border-2 border-white object-cover mb-2" />
      <h2 class="text-lg font-semibold">{{ user.first_name }} {{ user.last_name }}</h2>
      <p class="text-sm" :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-300'">{{ userTypeLabel }}</p>
    </div>

    <!-- Navigation -->
    <nav>
      <ul class="space-y-2">
        <li>
          <router-link
            to="/admin"
            class="flex items-center gap-2 p-2 rounded transition-colors duration-150"
            :class="isActive('/admin') && route.path === '/admin' ?
              (themeStore.isDarkMode ? 'bg-gray-700 font-semibold' : 'bg-gray-900 font-semibold') :
              (themeStore.isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-green-800')"
          >
            <LayoutDashboardIcon class="w-5 h-5" /> Dashboard
          </router-link>
        </li>
        <li>
          <router-link
            to="/admin/user-management"
            class="flex items-center gap-2 p-2 rounded transition-colors duration-150"
            :class="isActive('/admin/user-management') ?
              (themeStore.isDarkMode ? 'bg-gray-700 font-semibold' : 'bg-gray-900 font-semibold') :
              (themeStore.isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-green-800')"
          >
            <UsersIcon class="w-5 h-5" /> User Management
          </router-link>
        </li>
        <li>
          <router-link
            to="/admin/messaging"
            class="flex items-center gap-2 p-2 rounded relative transition-colors duration-150"
            :class="isActive('/admin/messaging') ?
              (themeStore.isDarkMode ? 'bg-gray-700 font-semibold' : 'bg-gray-900 font-semibold') :
              (themeStore.isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-green-800')"
          >
            <MessageCircleIcon class="w-5 h-5" />
            Messaging
            <!-- Badge for unread messages -->
            <div
              v-if="messagingBadgeCount"
              class="ml-auto bg-red-500 text-white text-xs px-2 py-1 rounded-full font-semibold shadow-sm min-w-[20px] text-center"
            >
              {{ messagingBadgeCount }}
            </div>
          </router-link>
        </li>
        <li>
          <router-link
            to="/admin/contents"
            class="flex items-center gap-2 p-2 rounded transition-colors duration-150"
            :class="isActive('/admin/contents') ?
              (themeStore.isDarkMode ? 'bg-gray-700 font-semibold' : 'bg-gray-900 font-semibold') :
              (themeStore.isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-green-800')"
          >
            <FileTextIcon class="w-5 h-5" /> Contents
          </router-link>
        </li>
        <li>
          <router-link
            to="/admin/post-reports"
            class="flex items-center gap-2 p-2 rounded relative transition-colors duration-150"
            :class="isActive('/admin/post-reports') ?
              (themeStore.isDarkMode ? 'bg-gray-700 font-semibold' : 'bg-gray-900 font-semibold') :
              (themeStore.isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-green-800')"
          >
            <ShieldCheckIcon class="w-5 h-5" />
            Post Reports
            <!-- Badge for pending reports -->
            <div
              v-if="reportedPostsCount > 0"
              class="ml-auto bg-red-500 text-white text-xs px-2 py-1 rounded-full font-semibold shadow-sm min-w-[20px] text-center"
            >
              {{ reportedPostsCount }}
            </div>
          </router-link>
        </li>
        <li>
          <router-link
            to="/admin/pending-user-approval"
            class="flex items-center gap-2 p-2 rounded transition-colors duration-150"
            :class="isActive('/admin/pending-user-approval') ?
              (themeStore.isDarkMode ? 'bg-gray-700 font-semibold' : 'bg-gray-900 font-semibold') :
              (themeStore.isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-green-800')"
          >
            <UserCheckIcon class="w-5 h-5" /> Pending User Approval
          </router-link>
        </li>
        <li>
          <router-link
            to="/admin/settings"
            class="flex items-center gap-2 p-2 rounded transition-colors duration-150"
            :class="isActive('/admin/settings') ?
              (themeStore.isDarkMode ? 'bg-gray-700 font-semibold' : 'bg-gray-900 font-semibold') :
              (themeStore.isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-green-800')"
          >
            <SettingsIcon class="w-5 h-5" /> Settings
          </router-link>
        </li>
        <li>
          <button @click="openLogoutModal"
                  class="flex items-center gap-2 w-full text-left p-2 rounded transition-colors duration-150"
                  :class="themeStore.isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-green-800'">
            <LogOutIcon class="w-5 h-5" /> Logout
          </button>
        </li>
      </ul>
    </nav>
  </aside>

  <!-- Logout Confirmation Modal -->
  <div v-if="showLogoutModal"
       class="fixed inset-0 z-50 flex items-center justify-center pointer-events-none">

    <!-- Modal -->
    <div class="relative bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 p-6 mx-4 max-w-sm w-full transform transition-all pointer-events-auto"
         @click.stop>
      <!-- Header -->
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
          Confirm Logout
        </h3>
        <button @click="closeLogoutModal"
                class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
          <XIcon class="w-5 h-5" />
        </button>
      </div>

      <!-- Content -->
      <div class="mb-6">
        <p class="text-gray-600 dark:text-gray-300">
          Are you sure you want to log out? You will need to sign in again to access your account.
        </p>
      </div>

      <!-- Actions -->
      <div class="flex gap-3 justify-end">
        <button @click="closeLogoutModal"
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors">
          Cancel
        </button>
        <button @click="confirmLogout"
                class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors">
          Logout
        </button>
      </div>
    </div>
  </div>
</template>
