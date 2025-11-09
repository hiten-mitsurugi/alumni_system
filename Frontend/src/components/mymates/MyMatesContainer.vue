<template>
  <div :class="themeStore.isDarkMode ? 'mymates-container h-full bg-gray-900' : 'mymates-container h-full bg-gray-50'">
    <!-- Header - Account for sidebar margin on mobile -->
    <div :class="themeStore.isDarkMode ? 'bg-gray-800 border-b border-gray-700 sticky top-0 z-40' : 'bg-white border-b border-gray-200 sticky top-0 z-40'">
      <div class="px-3 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-12 md:h-14">
          <div class="flex items-center space-x-3">
            <button
              @click="$router.go(-1)"
              :class="themeStore.isDarkMode 
                ? 'p-1.5 text-gray-400 hover:text-gray-200 hover:bg-gray-700 rounded-lg transition-colors' 
                : 'p-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors'"
            >
              <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <h1 :class="themeStore.isDarkMode ? 'text-sm sm:text-lg md:text-xl font-bold text-white' : 'text-sm sm:text-lg md:text-xl font-bold text-gray-900'">My Network</h1>
          </div>
          
          <!-- Network Stats - Hide on very small screens -->
          <div class="hidden sm:block">
            <NetworkStats :stats="stats" />
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content - Account for sidebar margin and constrain width on mobile -->
    <div class="px-3 sm:px-6 lg:px-8 py-4 sm:py-6">
      
      <!-- Mobile Stats (shown only on small screens) -->
      <div class="sm:hidden mb-6">
        <div :class="themeStore.isDarkMode ? 'bg-gray-800 rounded-lg shadow-sm border border-gray-700 p-3' : 'bg-white rounded-lg shadow-sm border border-gray-200 p-3'">
          <div class="flex justify-around text-center">
            <div>
              <div class="text-base font-semibold text-green-600">{{ stats.connectionsCount }}</div>
              <div :class="themeStore.isDarkMode ? 'text-xs text-gray-400' : 'text-xs text-gray-600'">Connections</div>
            </div>
            <div>
              <div class="text-base font-semibold text-green-600">{{ stats.followersCount }}</div>
              <div :class="themeStore.isDarkMode ? 'text-xs text-gray-400' : 'text-xs text-gray-600'">Followers</div>
            </div>
            <div>
              <div class="text-base font-semibold text-green-600">{{ stats.followingCount }}</div>
              <div :class="themeStore.isDarkMode ? 'text-xs text-gray-400' : 'text-xs text-gray-600'">Following</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Navigation Tabs - Mobile optimized with better spacing -->
      <div class="mb-4 sm:mb-6">
        <div :class="themeStore.isDarkMode ? 'flex space-x-2 sm:space-x-6 border-b border-gray-700 overflow-x-auto' : 'flex space-x-2 sm:space-x-6 border-b border-gray-200 overflow-x-auto'">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'py-2 sm:py-3 px-2 sm:px-1 border-b-2 font-medium text-xs sm:text-sm whitespace-nowrap transition-colors flex-shrink-0',
              activeTab === tab.id
                ? 'border-green-500 text-green-600'
                : (themeStore.isDarkMode 
                  ? 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300')
            ]"
          >
            {{ tab.label }}
            <span v-if="tab.count > 0" class="ml-1 bg-green-100 text-green-800 py-0.5 px-1 sm:scroll-px-4 rounded-full text-xs">
              {{ tab.count }}
            </span>
          </button>
        </div>
      </div>

      <!-- Dynamic Content Based on Active Tab -->
      <component 
        :is="currentComponent"
        v-bind="currentComponentProps"
        @view-profile="handleViewProfile"
        @message="handleMessage"
        @remove-connection="handleRemoveConnection"
        @accept-invitation="handleAcceptInvitation"
        @ignore-invitation="handleIgnoreInvitation"
        @connect-suggestion="handleConnectSuggestion"
        @follow-back="handleFollowBack"
        @unfollow="handleUnfollow"
      />

    </div>

    <!-- Success/Error Notifications -->
    <div v-if="notification" class="fixed top-20 right-4 z-50 max-w-sm">
      <div
        :class="[
          'p-4 rounded-lg shadow-lg border-l-4',
          notification.type === 'success' ? (themeStore.isDarkMode ? 'bg-green-900 border-green-400 text-green-200' : 'bg-green-50 border-green-400 text-green-800') :
          notification.type === 'error' ? (themeStore.isDarkMode ? 'bg-red-900 border-red-400 text-red-200' : 'bg-red-50 border-red-400 text-red-800') :
          (themeStore.isDarkMode ? 'bg-blue-900 border-blue-400 text-blue-200' : 'bg-blue-50 border-blue-400 text-blue-800')
        ]"
      >
        <div class="flex items-center">
          <span class="flex-1">{{ notification.message }}</span>
          <button @click="notification = null" :class="themeStore.isDarkMode ? 'ml-2 text-gray-400 hover:text-gray-200' : 'ml-2 text-gray-400 hover:text-gray-600'">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useNetworking } from '@/composables/useNetworking';
import { useThemeStore } from '@/stores/theme';

// Components
import NetworkStats from './NetworkStats.vue';
import ConnectionsList from './ConnectionsList.vue';
import InvitationsList from './InvitationsList.vue';
import SuggestionsList from './SuggestionsList.vue';
import FollowersList from './FollowersList.vue';
import FollowingList from './FollowingList.vue';

// Import external stylesheet
import './mymates-styles.css';

const router = useRouter();
const themeStore = useThemeStore();

// Use the networking composable
const {
  connections,
  pendingInvitations,
  suggestions,
  followers,
  following,
  loading,
  stats,
  refreshAllData,
  acceptInvitation,
  ignoreInvitation,
  connectToSuggestion,
  removeConnection,
  followBack,
  unfollowUser
} = useNetworking();

// Local state
const activeTab = ref('connections');
const notification = ref(null);

// Tab configuration
const tabs = computed(() => [
  { 
    id: 'connections', 
    label: 'Connections', 
    count: connections.value.length 
  },
  { 
    id: 'invitations', 
    label: 'Invitations', 
    count: pendingInvitations.value.length 
  },
  { 
    id: 'suggestions', 
    label: 'Suggestions', 
    count: suggestions.value.length 
  },
  { 
    id: 'followers', 
    label: 'Followers', 
    count: followers.value.length 
  },
  { 
    id: 'following', 
    label: 'Following', 
    count: following.value.length 
  }
]);

// Dynamic component management
const componentMap = {
  connections: ConnectionsList,
  invitations: InvitationsList,
  suggestions: SuggestionsList,
  followers: FollowersList,
  following: FollowingList
};

const currentComponent = computed(() => componentMap[activeTab.value]);

const currentComponentProps = computed(() => {
  const propsMap = {
    connections: { connections: connections.value },
    invitations: { invitations: pendingInvitations.value },
    suggestions: { suggestions: suggestions.value },
    followers: { followers: followers.value },
    following: { following: following.value }
  };
  
  return propsMap[activeTab.value] || {};
});

// Event handlers
const handleViewProfile = (user) => {
  if (user.username) {
    router.push({
      name: 'AlumniProfile',
      params: { userIdentifier: user.username }
    });
  } else {
    showNotification('Unable to view profile at this time.', 'error');
  }
};

const handleMessage = (connection) => {
  // Placeholder for messaging functionality
  showNotification('Messaging feature coming soon!', 'info');
  // router.push(`/alumni/messaging?user=${connection.username}`);
};

const handleRemoveConnection = async (connection) => {
  if (!confirm(`Are you sure you want to remove ${connection.name} from your connections?`)) {
    return;
  }
  
  try {
    const result = await removeConnection(connection);
    showNotification(result.message, 'success');
  } catch (error) {
    showNotification(error.message, 'error');
  }
};

const handleAcceptInvitation = async (invitation) => {
  try {
    const result = await acceptInvitation(invitation);
    showNotification(result.message, 'success');
  } catch (error) {
    showNotification(error.message, 'error');
  }
};

const handleIgnoreInvitation = async (invitation) => {
  try {
    const result = await ignoreInvitation(invitation);
    showNotification(result.message, 'success');
  } catch (error) {
    showNotification(error.message, 'error');
  }
};

const handleConnectSuggestion = async (suggestion) => {
  try {
    const result = await connectToSuggestion(suggestion);
    showNotification(result.message, 'success');
  } catch (error) {
    showNotification(error.message, 'error');
  }
};

const handleFollowBack = async (follower) => {
  try {
    const result = await followBack(follower);
    showNotification(result.message, 'success');
  } catch (error) {
    showNotification(error.message, 'error');
  }
};

const handleUnfollow = async (user) => {
  if (!confirm(`Are you sure you want to unfollow ${user.name}?`)) {
    return;
  }
  
  try {
    const context = activeTab.value === 'followers' ? 'followers' : 'following';
    const result = await unfollowUser(user, context);
    showNotification(result.message, 'success');
  } catch (error) {
    showNotification(error.message, 'error');
  }
};

// Utility functions
const showNotification = (message, type = 'info') => {
  notification.value = { message, type };
  
  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    notification.value = null;
  }, 5000);
};

// Lifecycle
onMounted(async () => {
  console.log('🚀 MyMates container mounted, loading network data...');
  
  try {
    await refreshAllData();
    console.log('✅ Network data loaded successfully');
  } catch (error) {
    console.error('❌ Failed to load network data:', error);
    showNotification('Failed to load network data. Please refresh the page.', 'error');
  }
});
</script>

<style>
/* Styles are imported from mymates-styles.css */
</style>
