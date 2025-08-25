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
  <aside class="bg-green-700 text-white w-70 min-h-screen p-4">
    <!-- Profile Section -->
    <div class="flex flex-col items-center mb-6" v-if="user && user.first_name">
      <img :src="profilePicture" alt="Profile Picture"
           class="w-20 h-20 rounded-full border-2 border-white object-cover mb-2" />
      <h2 class="text-lg font-semibold">{{ user.first_name }} {{ user.last_name }}</h2>
      <p class="text-sm text-gray-300">{{ userTypeLabel }}</p>
    </div>

    <!-- Navigation -->
    <nav>
      <ul class="space-y-2">
        <li>
          <router-link
            to="/admin"
            class="flex items-center gap-2 p-2 rounded"
            :class="isActive('/admin') && route.path === '/admin' ? 'bg-gray-900 font-semibold' : 'hover:bg-green-800'"
          >
            <LayoutDashboardIcon class="w-5 h-5" /> Dashboard
          </router-link>
        </li>
         <li>
          <router-link
            to="/admin/notification"
            class="flex items-center gap-2 p-2 rounded"
            :class="isActive('/admin/notification') ? 'bg-gray-900 font-semibold' : 'hover:bg-green-800'"
          >
            <BellIcon class="w-5 h-5" /> Notification
          </router-link>
        </li>
         <li>
          <router-link
            to="/admin/contents"
            class="flex items-center gap-2 p-2 rounded"
            :class="isActive('/admin/contents') ? 'bg-gray-900 font-semibold' : 'hover:bg-green-800'"
          >
            <FileTextIcon class="w-5 h-5" /> Contents
          </router-link>
        </li>
         <li>
          <router-link
            to="/admin/messaging"
            class="flex items-center gap-2 p-2 rounded relative"
            :class="isActive('/admin/messaging') ? 'bg-gray-900 font-semibold' : 'hover:bg-green-800'"
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
            to="/admin/post-approvals"
            class="flex items-center gap-2 p-2 rounded"
            :class="isActive('/admin/post-approvals') ? 'bg-gray-900 font-semibold' : 'hover:bg-green-800'"
          >
            <ShieldCheckIcon class="w-5 h-5" /> Post Approvals
          </router-link>
        </li>
           <li>
          <router-link
            to="/admin/pending-user-approval"
            class="flex items-center gap-2 p-2 rounded"
            :class="isActive('/admin/pending-user-approval') ? 'bg-gray-900 font-semibold' : 'hover:bg-green-800'"
          >
            <UserCheckIcon class="w-5 h-5" /> Pending User Approval
          </router-link>
        </li>
        <li>
          <router-link
            to="/admin/user-management"
            class="flex items-center gap-2 p-2 rounded"
            :class="isActive('/admin/user-management') ? 'bg-gray-900 font-semibold' : 'hover:bg-green-800'"
          >
            <UsersIcon class="w-5 h-5" /> User Management
          </router-link>
        </li>
       
        <li>
          <router-link
            to="/admin/survey-management"
            class="flex items-center gap-2 p-2 rounded"
            :class="isActive('/admin/survey-management') ? 'bg-gray-900 font-semibold' : 'hover:bg-green-800'"
          >
            <ClipboardListIcon class="w-5 h-5" /> Survey Management
          </router-link>
        </li>
       
        <li>
          <router-link
            to="/admin/settings"
            class="flex items-center gap-2 p-2 rounded"
            :class="isActive('/admin/settings') ? 'bg-gray-900 font-semibold' : 'hover:bg-green-800'"
          >
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
