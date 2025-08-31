<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

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
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  GraduationCap as GraduationCapIcon
} from 'lucide-vue-next';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const isCollapsed = ref(false);

const BASE_URL = 'http://127.0.0.1:8000';

const menuItems = [
  { name: 'Dashboard', icon: LayoutDashboardIcon, route: '/admin', description: 'Main dashboard overview' },
  { name: 'User Management', icon: UsersIcon, route: '/admin/user-management', description: 'Manage system users' },
  { name: 'Survey Management', icon: ClipboardListIcon, route: '/admin/survey-management', description: 'Create and manage surveys' },
  { name: 'Notification', icon: BellIcon, route: '/admin/notification', description: 'Send notifications' },
  { name: 'Contents', icon: FileTextIcon, route: '/admin/contents', description: 'Manage content' },
  { name: 'Post Approvals', icon: ShieldCheckIcon, route: '/admin/post-approvals', description: 'Approve user posts' },
  { name: 'Pending User Approval', icon: UserCheckIcon, route: '/admin/pending-user-approval', description: 'Approve new users' }
];

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};

const navigateTo = (route) => {
  router.push(route);
};

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

const logout = () => {
  authStore.logout();
  router.push('/login');
};

const user = computed(() => authStore.user || {});

const profilePicture = computed(() => {
  const pic = user.value.profile_picture;
  console.log('AdminSidebar - Computing profile picture:', pic);
  console.log('AdminSidebar - User data:', user.value);

  if (pic && typeof pic === 'string' && pic !== 'null') {
    const fullUrl = pic.startsWith('http') ? pic : `${BASE_URL}${pic}`;
    console.log('AdminSidebar - Using profile picture:', fullUrl);
    return fullUrl;
  }

  console.log('AdminSidebar - Using default profile picture');
  return '/default-profile.png';
});

const userTypeLabel = computed(() => {
  switch (user.value.user_type) {
    case 1: return 'Super Admin';
    case 2: return 'Admin';
    case 3: return 'Alumni';
    default: return 'Unknown';
  }
});

const isActive = (path) => {
  return route.path === path || (path !== '/admin' && route.path.startsWith(path));
};
</script>

<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Sidebar -->
    <div 
      :class="[
        'bg-gradient-to-b from-green-600 to-green-700 text-white transition-all duration-300 ease-in-out shadow-xl flex flex-col',
        isCollapsed ? 'w-16' : 'w-72'
      ]"
    >
      <!-- Header -->
      <div class="p-4 border-b border-green-500">
        <div class="flex items-center justify-between">
          <div v-if="!isCollapsed" class="flex items-center space-x-3">
            <div class="p-2 bg-green-500 rounded-lg">
              <GraduationCapIcon class="w-6 h-6" />
            </div>
            <div>
              <h1 class="font-bold text-lg">Admin Portal</h1>
              <p class="text-green-200 text-xs">Management System</p>
            </div>
          </div>
          <button
            @click="toggleSidebar"
            class="text-white hover:bg-green-500 p-2 rounded-lg transition-colors"
          >
            <ChevronRightIcon v-if="isCollapsed" class="w-4 h-4" />
            <ChevronLeftIcon v-else class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- Navigation Menu -->
      <nav class="flex-1 p-4">
        <ul class="space-y-2">
          <li v-for="item in menuItems" :key="item.name">
            <button
              @click="navigateTo(item.route)"
              :class="[
                'w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200',
                isActive(item.route) 
                  ? 'bg-white text-green-600 shadow-md font-semibold' 
                  : 'text-white hover:bg-green-500 hover:shadow-md'
              ]"
              :title="isCollapsed ? item.description : ''"
            >
              <component 
                :is="item.icon" 
                class="w-5 h-5 flex-shrink-0"
              />
              <span v-if="!isCollapsed" class="font-medium">{{ item.name }}</span>
            </button>
          </li>
        </ul>
      </nav>

      <!-- User Profile Section -->
      <div class="border-t border-green-500 p-4">
        <div v-if="!isCollapsed" class="mb-4">
          <div class="flex items-center space-x-3 mb-3">
            <div class="w-10 h-10 bg-green-400 rounded-full flex items-center justify-center">
              <img 
                v-if="profilePicture !== '/default-profile.png'"
                :src="profilePicture" 
                alt="Profile Picture"
                class="w-10 h-10 rounded-full object-cover"
                @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='flex'"
              />
              <span 
                class="text-white font-bold text-sm"
                :class="{ 'hidden': profilePicture !== '/default-profile.png' }"
              >
                {{ user.first_name?.charAt(0) || 'A' }}
              </span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-white truncate">
                {{ user.first_name }} {{ user.last_name }}
              </p>
              <p class="text-xs text-green-200 truncate">
                {{ userTypeLabel }}
              </p>
            </div>
          </div>
        </div>
        
        <!-- Settings -->
        <button
          @click="navigateTo('/admin/settings')"
          :class="[
            'w-full flex items-center space-x-3 px-4 py-2 rounded-lg transition-all duration-200 mb-2',
            isActive('/admin/settings') 
              ? 'bg-white text-green-600' 
              : 'text-white hover:bg-green-500'
          ]"
          :title="isCollapsed ? 'Settings' : ''"
        >
          <SettingsIcon class="w-5 h-5" />
          <span v-if="!isCollapsed" class="font-medium">Settings</span>
        </button>

        <!-- Logout Button -->
        <button
          @click="logout"
          :class="[
            'w-full flex items-center space-x-3 px-4 py-2 rounded-lg transition-all duration-200',
            'text-red-200 hover:bg-red-500 hover:text-white'
          ]"
          :title="isCollapsed ? 'Logout' : ''"
        >
          <LogOutIcon class="w-5 h-5" />
          <span v-if="!isCollapsed" class="font-medium">Logout</span>
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Optional: Breadcrumb or Page Header -->
      <header class="bg-white shadow-sm border-b px-6 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-semibold text-gray-800">
              {{ menuItems.find(item => isActive(item.route))?.name || 'Admin Portal' }}
            </h2>
            <p class="text-sm text-gray-500 mt-1">
              {{ menuItems.find(item => isActive(item.route))?.description || 'Manage your admin dashboard' }}
            </p>
          </div>
          <div class="flex items-center space-x-4">
            <div class="text-sm text-gray-600">
              Welcome, {{ user.first_name }}
            </div>
          </div>
        </div>
      </header>

      <!-- Content Area -->
      <main class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50">
        <div class="container mx-auto px-6 py-8">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>
