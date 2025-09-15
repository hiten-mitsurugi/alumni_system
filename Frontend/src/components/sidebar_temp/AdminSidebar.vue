<script setup>
import { computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth'; // ✅ Use alias
import { useMessagingNotificationStore } from '@/stores/messagingNotifications';

import {
  LogOut as LogOutIcon,
  LayoutDashboard as LayoutDashboardIcon,
  Users as UsersIcon,
  ClipboardList as ClipboardListIcon,
  Bell as BellIcon,
  FileText as FileTextIcon,
  ShieldCheck as ShieldCheckIcon,
  UserCheck as UserCheckIcon,
  Settings as SettingsIcon,
  MessageCircle as MessageCircleIcon
} from 'lucide-vue-next';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const messagingNotificationStore = useMessagingNotificationStore();

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
  }
});

const logout = async () => {
  // Cleanup messaging notifications on logout
  messagingNotificationStore.cleanup();
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

// Computed property for messaging badge count
const messagingBadgeCount = computed(() => {
  const count = messagingNotificationStore.totalUnreadCount;
  return count > 0 ? count.toString() : null;
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
          <router-link
            to="/admin"
            class="flex items-center gap-3 p-3 rounded transition transform text-lg"
            :class="isActive('/admin') && route.path === '/admin' 
              ? 'font-semibold text-green-600 scale-105 bg-green-100' 
              : 'hover:text-gray-600 hover:scale-105 hover:bg-gray-100'"
          >
            <LayoutDashboardIcon class="w-6 h-6" /> <span>Dashboard</span>
          </router-link>
        </li>
         <li>
          <router-link
            to="/admin/notification"
            class="flex items-center gap-3 p-3 rounded transition transform text-lg"
            :class="isActive('/admin/notification') 
              ? 'font-semibold text-green-600 scale-105 bg-green-100' 
              : 'hover:text-gray-600 hover:scale-105 hover:bg-gray-100'"
          >
            <BellIcon class="w-6 h-6" /> <span>Notification</span>
          </router-link>
        </li>
         <li>
          <router-link
            to="/admin/contents"
            class="flex items-center gap-3 p-3 rounded transition transform text-lg"
            :class="isActive('/admin/contents') 
              ? 'font-semibold text-green-600 scale-105 bg-green-100' 
              : 'hover:text-gray-600 hover:scale-105 hover:bg-gray-100'"
          >
            <FileTextIcon class="w-6 h-6" /> <span>Contents</span>
          </router-link>
        </li>
         <li>
          <router-link
            to="/admin/messaging"
            class="flex items-center gap-3 p-3 rounded transition transform text-lg relative"
            :class="isActive('/admin/messaging') 
              ? 'font-semibold text-green-600 scale-105 bg-green-100' 
              : 'hover:text-gray-600 hover:scale-105 hover:bg-gray-100'"
          >
            <MessageCircleIcon class="w-6 h-6" /> 
            <span>Messaging</span>
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
            to="/admin/post-approvals"
            class="flex items-center gap-3 p-3 rounded transition transform text-lg"
            :class="isActive('/admin/post-approvals') 
              ? 'font-semibold text-green-600 scale-105 bg-green-100' 
              : 'hover:text-gray-600 hover:scale-105 hover:bg-gray-100'"
          >
            <ShieldCheckIcon class="w-6 h-6" /> <span>Post Approvals</span>
          </router-link>
        </li>
           <li>
          <router-link
            to="/admin/pending-user-approval"
            class="flex items-center gap-3 p-3 rounded transition transform text-lg"
            :class="isActive('/admin/pending-user-approval') 
              ? 'font-semibold text-green-600 scale-105 bg-green-100' 
              : 'hover:text-gray-600 hover:scale-105 hover:bg-gray-100'"
          >
            <UserCheckIcon class="w-6 h-6" /> <span>Pending User Approval</span>
          </router-link>
        </li>
        <li>
          <router-link
            to="/admin/user-management"
            class="flex items-center gap-3 p-3 rounded transition transform text-lg"
            :class="isActive('/admin/user-management') 
              ? 'font-semibold text-green-600 scale-105 bg-green-100' 
              : 'hover:text-gray-600 hover:scale-105 hover:bg-gray-100'"
          >
            <UsersIcon class="w-6 h-6" /> <span>User Management</span>
          </router-link>
        </li>
       
        <li>
          <router-link
            to="/admin/survey-management"
            class="flex items-center gap-3 p-3 rounded transition transform text-lg"
            :class="isActive('/admin/survey-management') 
              ? 'font-semibold text-green-600 scale-105 bg-green-100' 
              : 'hover:text-gray-600 hover:scale-105 hover:bg-gray-100'"
          >
            <ClipboardListIcon class="w-6 h-6" /> <span>Survey Management</span>
          </router-link>
        </li>
       
        <li>
          <router-link
            to="/admin/settings"
            class="flex items-center gap-3 p-3 rounded transition transform text-lg"
            :class="isActive('/admin/settings') 
              ? 'font-semibold text-green-600 scale-105 bg-green-100' 
              : 'hover:text-gray-600 hover:scale-105 hover:bg-gray-100'"
          >
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
