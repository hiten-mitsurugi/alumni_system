<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../../stores/auth';

// Import Lucide Vue icons (same as Admin and SuperAdmin)
import {
  LogOut as LogOutIcon,
  LayoutDashboard as DashboardIcon,
  User as ProfileIcon,
  MessageCircle as MessagesIcon,
  FileText as PostsIcon,
  BookOpen as DirectoryIcon,
  Calendar as EventsIcon,
  Briefcase as JobsIcon,
  Settings as SettingsIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  GraduationCap as GraduationCapIcon,
  Edit3 as EditIcon,
  Bell as BellIcon
} from 'lucide-vue-next';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const isCollapsed = ref(false);

const menuItems = [
  {
    name: 'Dashboard',
    icon: DashboardIcon,
    route: '/alumni/dashboard',
    description: 'Home'
  },
  {
    name: 'Profile',
    icon: ProfileIcon,
    route: '/alumni/profile',
    description: 'My Profile'
  },
  {
    name: 'Messages',
    icon: MessagesIcon,
    route: '/alumni/messages',
    description: 'Messages'
  },
  {
    name: 'Posts',
    icon: PostsIcon,
    route: '/alumni/posts',
    description: 'Posts & Feed'
  },
  {
    name: 'Directory',
    icon: DirectoryIcon,
    route: '/alumni/directory',
    description: 'Alumni Directory'
  },
  {
    name: 'Events',
    icon: EventsIcon,
    route: '/alumni/events',
    description: 'Events'
  },
  {
    name: 'Jobs',
    icon: JobsIcon,
    route: '/alumni/jobs',
    description: 'Job Opportunities'
  }
];

const navigateTo = (routePath) => {
  router.push(routePath);
};

const logout = () => {
  authStore.logout();
  router.push('/login');
};

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};

const isActive = (routePath) => {
  return route.path === routePath;
};
</script>

<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Sidebar -->
    <div 
      :class="[
        'bg-gradient-to-b from-green-600 to-green-800 text-white shadow-xl transition-all duration-300 ease-in-out',
        isCollapsed ? 'w-20' : 'w-64'
      ]"
    >
      <!-- Header -->
      <div class="p-4 border-b border-green-500">
        <div class="flex items-center justify-between">
          <div v-if="!isCollapsed" class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-white rounded-full flex items-center justify-center">
              <GraduationCapIcon class="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h1 class="text-lg font-bold">Alumni Portal</h1>
              <p class="text-green-200 text-sm">{{ authStore.user?.first_name || 'Alumni' }}</p>
            </div>
          </div>
          <div v-else class="flex justify-center">
            <div class="w-10 h-10 bg-white rounded-full flex items-center justify-center">
              <GraduationCapIcon class="w-6 h-6 text-green-600" />
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
              <span class="text-white font-bold">
                {{ authStore.user?.first_name?.charAt(0) || 'A' }}
              </span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-white truncate">
                {{ authStore.user?.first_name }} {{ authStore.user?.last_name }}
              </p>
              <p class="text-xs text-green-200 truncate">
                {{ authStore.user?.email }}
              </p>
            </div>
          </div>
        </div>
        
        <!-- Settings -->
        <button
          @click="navigateTo('/alumni/settings')"
          :class="[
            'w-full flex items-center space-x-3 px-4 py-2 rounded-lg transition-all duration-200 mb-2',
            isActive('/alumni/settings') 
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
              {{ menuItems.find(item => isActive(item.route))?.name || 'Alumni Portal' }}
            </h2>
            <p class="text-sm text-gray-600 mt-1">
              {{ menuItems.find(item => isActive(item.route))?.description || 'Welcome to your alumni portal' }}
            </p>
          </div>
          
          <!-- Quick Actions -->
          <div class="flex items-center space-x-3">
            <button 
              @click="navigateTo('/alumni/messages')"
              class="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
              title="Messages"
            >
              💬
            </button>
            <button 
              @click="navigateTo('/alumni/posts')"
              class="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
              title="Create Post"
            >
              ✏️
            </button>
            <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <span class="text-green-600 font-semibold text-sm">
                {{ authStore.user?.first_name?.charAt(0) || 'A' }}
              </span>
            </div>
          </div>
        </div>
      </header>

      <!-- Main Content Area -->
      <main class="flex-1 overflow-y-auto bg-gray-50 p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<style scoped>
/* Custom scrollbar for main content */
main::-webkit-scrollbar {
  width: 6px;
}

main::-webkit-scrollbar-track {
  background: #f1f5f9;
}

main::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

main::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
