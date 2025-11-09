<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth' // ✅ Use alias
import { useMessagingNotificationStore } from '@/stores/messagingNotifications'
import { settingsService } from '@/services/settingsService'
import { useThemeStore } from '@/stores/theme'

import {
  LogOut as LogOutIcon,
  LayoutDashboard as LayoutDashboardIcon,
  Users as UsersIcon,
  ClipboardList as ClipboardListIcon,
  FileText as FileTextIcon,
  ShieldCheck as ShieldCheckIcon,
  UserCheck as UserCheckIcon,
  Settings as SettingsIcon,
  MessageCircle as MessageCircleIcon,
  AlertTriangle as AlertTriangleIcon,
  Camera as CameraIcon,
  ChevronDown as ChevronDownIcon
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const messagingNotificationStore = useMessagingNotificationStore()
const themeStore = useThemeStore()

const BASE_URL = 'http://127.0.0.1:8000'

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

// Submenu state for Settings: show when Settings clicked or when route is a settings route
const settingsOpen = ref(route.path.startsWith('/admin/settings'))

watch(() => route.path, (p) => {
  if (p.startsWith('/admin/settings')) settingsOpen.value = true
})

const toggleSettings = (e) => {
  // prevent the outer link default if passed an event
  if (e && e.preventDefault) e.preventDefault()
  settingsOpen.value = !settingsOpen.value
  if (settingsOpen.value) {
    // navigate to base settings page if opening
    router.push('/admin/settings').catch(() => {})
  }
}

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
    
    // Clear the file input
    event.target.value = '';
    
    console.log('Profile picture updated successfully');
  } catch (error) {
    console.error('Failed to upload profile picture:', error);
    alert('Failed to upload profile picture: ' + (error.message || 'Unknown error'));
  }
};
</script>

<template>
  <aside :class="['w-full sm:w-[220px] md:w-[240px] lg:w-[260px] min-h-screen max-h-screen overflow-y-auto p-2 sm:p-3 flex flex-col border-r', themeStore.isAdminDark() ? 'bg-gray-900 text-gray-100 border-gray-700' : 'bg-white text-gray-800 border-gray-200']">
    <!-- Profile Section -->
    <div class="flex flex-col items-center mb-3 sm:mb-4" v-if="user && user.first_name">
      <div class="relative">
        <img :src="profilePicture" alt="Profile Picture"
          class="w-12 sm:w-16 md:w-18 h-12 sm:h-16 md:h-18 rounded-full border-2 border-white object-cover mb-1" />
        <label for="profilePictureUpload"
               class="absolute bottom-0 right-0 bg-blue-600 text-white p-1 rounded-full hover:bg-blue-700 transition-colors cursor-pointer">
          <CameraIcon class="w-3 h-3" />
        </label>
        <input type="file"
               id="profilePictureUpload"
               accept="image/*"
               @change="handleProfilePictureUpload"
               class="hidden">
      </div>
      <h2 :class="['text-sm sm:text-base font-semibold text-center leading-tight', themeStore.isAdminDark() ? 'text-gray-100' : 'text-gray-900']">{{ user.first_name }} {{ user.last_name }}</h2>
      <p :class="['text-xs sm:text-sm', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">{{ userTypeLabel }}</p>
    </div>

    <!-- Navigation -->
    <nav class="flex-grow overflow-y-auto">
  <ul class="space-y-1 sm:space-y-2">
        <li>
          <router-link
            to="/admin"
            class="flex items-center gap-2 p-2 rounded transition text-sm"
            :class="isActive('/admin') && route.path === '/admin' 
              ? (themeStore.isAdminDark() ? 'font-semibold text-orange-400 bg-orange-900/40' : 'font-semibold text-orange-600 bg-orange-100') 
              : (themeStore.isAdminDark() ? 'hover:text-gray-200 hover:bg-gray-800/50' : 'hover:text-gray-600 hover:bg-gray-100')"
          >
            <LayoutDashboardIcon class="w-4 h-4" /> <span>Dashboard</span>
          </router-link>
        </li>
         <li>
          <router-link
            to="/admin/contents"
            class="flex items-center gap-2 p-2 rounded transition text-sm"
            :class="isActive('/admin/contents') 
              ? (themeStore.isAdminDark() ? 'font-semibold text-orange-400 bg-orange-900/40' : 'font-semibold text-orange-600 bg-orange-100') 
              : (themeStore.isAdminDark() ? 'hover:text-gray-200 hover:bg-gray-800/50' : 'hover:text-gray-600 hover:bg-gray-100')"
          >
            <FileTextIcon class="w-4 h-4" /> <span>Contents</span>
          </router-link>
        </li>
         <li>
          <router-link
            to="/admin/messaging"
            class="flex items-center gap-2 p-2 rounded transition text-sm relative"
            :class="isActive('/admin/messaging') 
              ? (themeStore.isAdminDark() ? 'font-semibold text-orange-400 bg-orange-900/40' : 'font-semibold text-orange-600 bg-orange-100') 
              : (themeStore.isAdminDark() ? 'hover:text-gray-200 hover:bg-gray-800/50' : 'hover:text-gray-600 hover:bg-gray-100')"
          >
            <MessageCircleIcon class="w-4 h-4" />
    <span>Messaging</span>
            <!-- Badge for unread messages -->
    <span v-if="messagingBadgeCount" 
      :class="['absolute top-0.5 right-0.5 text-xs rounded-full h-4 w-4 flex items-center justify-center', themeStore.isAdminDark() ? 'bg-red-500 text-white' : 'bg-red-500 text-white']">
              {{ messagingBadgeCount }}
            </span>
          </router-link>
        </li>
        <!-- <li>
          <router-link
            to="/admin/survey"
            class="flex items-center gap-2 p-2 rounded transition text-sm"
            :class="isActive('/admin/survey') 
              ? 'font-semibold text-green-600 bg-green-100' 
              : 'hover:text-gray-600 hover:bg-gray-100'"
          >
            <ClipboardListIcon class="w-4 h-4" /> <span>Survey</span>
          </router-link>
        </li> -->
        
        <li>
          <router-link
            to="/admin/user-management"
            class="flex items-center gap-2 p-2 rounded transition text-sm"
            :class="isActive('/admin/user-management') 
              ? (themeStore.isAdminDark() ? 'font-semibold text-orange-400 bg-orange-900/40' : 'font-semibold text-orange-600 bg-orange-100') 
              : (themeStore.isAdminDark() ? 'hover:text-gray-200 hover:bg-gray-800/50' : 'hover:text-gray-600 hover:bg-gray-100')"
          >
            <UsersIcon class="w-4 h-4" /> <span>Users</span>
          </router-link>
        </li>
        <li>
          <router-link
            to="/admin/pending-user-approval"
            class="flex items-center gap-2 p-2 rounded transition text-sm"
            :class="isActive('/admin/pending-user-approval') 
              ? (themeStore.isAdminDark() ? 'font-semibold text-orange-400 bg-orange-900/40' : 'font-semibold text-orange-600 bg-orange-100') 
              : (themeStore.isAdminDark() ? 'hover:text-gray-200 hover:bg-gray-800/50' : 'hover:text-gray-600 hover:bg-gray-100')"
          >
            <UserCheckIcon class="w-4 h-4" /> <span>Pending</span>
          </router-link>
        </li>
        <li>
          <router-link
            to="/admin/post-reports"
            class="flex items-center gap-2 p-2 rounded transition text-sm"
            :class="isActive('/admin/post-reports') 
              ? (themeStore.isAdminDark() ? 'font-semibold text-orange-400 bg-orange-900/40' : 'font-semibold text-orange-600 bg-orange-100') 
              : (themeStore.isAdminDark() ? 'hover:text-gray-200 hover:bg-gray-800/50' : 'hover:text-gray-600 hover:bg-gray-100')"
          >
            <AlertTriangleIcon class="w-4 h-4" /> <span>Reports</span>
          </router-link>
        </li>
        <li>
          <button @click="toggleSettings"
            class="flex items-center gap-2 w-full text-left p-2 rounded transition text-sm justify-between"
            :class="isActive('/admin/settings') ? (themeStore.isAdminDark() ? 'font-semibold text-orange-400 bg-orange-900/40' : 'font-semibold text-orange-600 bg-orange-100') : (themeStore.isAdminDark() ? 'hover:text-gray-200 hover:bg-gray-800/50' : 'hover:text-gray-600 hover:bg-gray-100')">
            <div class="flex items-center gap-2">
              <SettingsIcon class="w-4 h-4" />
              <span>Settings</span>
            </div>
            <ChevronDownIcon :class="['w-4 h-4 transition-transform duration-200', settingsOpen ? 'rotate-180' : '']" />
          </button>

          <!-- Submenu shown when settingsOpen is true -->
          <ul v-if="settingsOpen" class="pl-6 mt-1 space-y-1">
            <li><router-link :to="{ name: 'AdminSettings', params: { section: 'profile' } }" :class="['block text-sm py-1 rounded px-2', themeStore.isAdminDark() ? 'hover:bg-gray-800/50' : 'hover:bg-gray-100']">Profile</router-link></li>
            <li><router-link :to="{ name: 'AdminSettings', params: { section: 'account' } }" :class="['block text-sm py-1 rounded px-2', themeStore.isAdminDark() ? 'hover:bg-gray-800/50' : 'hover:bg-gray-100']">Account & Security</router-link></li>
            <li><router-link :to="{ name: 'AdminSettings', params: { section: 'appearance' } }" :class="['block text-sm py-1 rounded px-2', themeStore.isAdminDark() ? 'hover:bg-gray-800/50' : 'hover:bg-gray-100']">Appearance</router-link></li>
          </ul>
        </li>
      </ul>
    </nav>

    <!-- Logout at the bottom -->
    <div :class="['border-t pt-2 mt-2 flex-shrink-0', themeStore.isAdminDark() ? 'border-gray-700' : 'border-gray-200']">
      <button @click="confirmLogout"
        :class="['flex items-center gap-2 w-full text-left p-2 rounded transition text-sm', themeStore.isAdminDark() ? 'hover:text-red-400 hover:bg-red-800/40' : 'hover:text-red-600 hover:bg-red-100']">
        <LogOutIcon class="w-4 h-4" /> <span>Logout</span>
      </button>
    </div>

    <!-- Logout Confirmation Modal - Positioned like a notification -->
    <div v-if="showLogoutConfirmation" class="fixed top-4 right-4 z-50 max-w-sm w-full p-4">
      <!-- Modal without backdrop -->
      <div :class="['rounded-xl shadow-2xl p-6 border backdrop-blur-sm animate-fade-in', themeStore.isAdminDark() ? 'bg-gray-800/98 text-white border-gray-600' : 'bg-white/98 text-gray-900 border-gray-300']">
        <div class="flex items-center mb-4">
          <div :class="['flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center mr-3', themeStore.isAdminDark() ? 'bg-red-900/40' : 'bg-red-100']">
            <LogOutIcon :class="['w-5 h-5', themeStore.isAdminDark() ? 'text-red-400' : 'text-red-600']" />
          </div>
          <h3 :class="['text-lg font-semibold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
            Confirm Logout
          </h3>
        </div>
        
        <p :class="['text-sm mb-6', themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-600']">
          Are you sure you want to logout? You will be redirected to the login page.
        </p>
        
        <div class="flex space-x-3">
          <button
            @click="cancelLogout"
            :class="['flex-1 px-4 py-2 text-sm font-medium rounded-lg transition-colors border', themeStore.isAdminDark() ? 'bg-gray-700/80 text-gray-300 hover:bg-gray-600 border-gray-600' : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border-gray-300']"
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
