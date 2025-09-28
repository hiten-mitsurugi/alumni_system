<template>
  <div :class="[
    'p-6 min-h-screen',
    themeStore.isDarkMode ? 'bg-gray-900' : 'bg-gray-50'
  ]">
    <!-- Header -->
    <div class="mb-8">
      <h1 :class="[
        'text-3xl font-bold mb-2',
        themeStore.isDarkMode ? 'text-gray-200' : 'text-gray-800'
      ]">Admin Dashboard</h1>
      <p :class="[
        themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'
      ]">
        Monitor system activity and manage platform content
        <span v-if="lastUpdated" :class="[
          'text-sm',
          themeStore.isDarkMode ? 'text-gray-500' : 'text-gray-500'
        ]">
          • Last updated: {{ formatTime(lastUpdated) }}
        </span>
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="w-8 h-8 border-b-2 border-blue-600 rounded-full animate-spin"></div>
      <span :class="[
        'ml-3',
        themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'
      ]">Loading analytics...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" :class="[
      'rounded-lg p-4 mb-6 border',
      themeStore.isDarkMode
        ? 'bg-red-900/50 border-red-800'
        : 'bg-red-50 border-red-200'
    ]">
      <div class="flex items-center">
        <svg class="w-5 h-5 mr-2 text-red-400" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
        </svg>
        <span :class="[
          themeStore.isDarkMode ? 'text-red-200' : 'text-red-800'
        ]">{{ error }}</span>
      </div>
    </div>

    <!-- Main Dashboard Content -->
    <div v-else class="space-y-6">
      <!-- Quick Actions Bar -->
      <div :class="[
        'rounded-lg shadow-sm border p-4',
        themeStore.isDarkMode
          ? 'bg-gray-800 border-gray-700'
          : 'bg-white border-gray-200'
      ]">
        <div class="flex flex-wrap gap-4">
                    <button 
            @click="refreshData" 
            class="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            Refresh Data
          </button>
          
          <button 
            @click="testReportsEndpoint" 
            class="flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
            Test Reports API
          </button>

          <router-link
            to="/admin/user-management"
            class="flex items-center px-4 py-2 text-white transition-colors bg-green-600 rounded-lg hover:bg-green-700"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"/>
            </svg>
            Manage Users
          </router-link>

          <router-link
            to="/admin/contents"
            class="flex items-center px-4 py-2 text-white transition-colors bg-purple-600 rounded-lg hover:bg-purple-700"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/>
            </svg>
            Manage Content
          </router-link>
        </div>
      </div>

      <!-- Analytics Cards Grid -->
      <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        <!-- Total Users Card -->
        <div :class="[
          'rounded-lg shadow-sm border p-6',
          themeStore.isDarkMode
            ? 'bg-gray-800 border-gray-700'
            : 'bg-white border-gray-200'
        ]">
          <div class="flex items-center justify-between">
            <div>
              <p :class="[
                'text-sm mb-1',
                themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'
              ]">Total Users</p>
              <p :class="[
                'text-2xl font-bold',
                themeStore.isDarkMode ? 'text-gray-200' : 'text-gray-800'
              ]">{{ (analytics.totalUsers || 0).toLocaleString() }}</p>
              <p :class="[
                'text-xs mt-1',
                themeStore.isDarkMode ? 'text-green-400' : 'text-green-600'
              ]">
                +{{ analytics.recentRegistrations || 0 }} this week
              </p>
            </div>
            <div :class="[
              'p-3 rounded-full',
              themeStore.isDarkMode ? 'bg-blue-900/50' : 'bg-blue-100'
            ]">
              <svg :class="[
                'w-6 h-6',
                themeStore.isDarkMode ? 'text-blue-400' : 'text-blue-600'
              ]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- Active Users Card -->
        <div :class="[
          'rounded-lg shadow-sm border p-6',
          themeStore.isDarkMode
            ? 'bg-gray-800 border-gray-700'
            : 'bg-white border-gray-200'
        ]">
          <div class="flex items-center justify-between">
            <div>
              <p :class="[
                'text-sm mb-1',
                themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'
              ]">Active Users</p>
              <p :class="[
                'text-2xl font-bold',
                themeStore.isDarkMode ? 'text-gray-200' : 'text-gray-800'
              ]">{{ (analytics.activeUsers || 0).toLocaleString() }}</p>
              <p :class="[
                'text-xs mt-1',
                themeStore.isDarkMode ? 'text-blue-400' : 'text-blue-600'
              ]">
                {{ analytics.onlineUsers || 0 }} online now
              </p>
            </div>
            <div :class="[
              'p-3 rounded-full',
              themeStore.isDarkMode ? 'bg-green-900/50' : 'bg-green-100'
            ]">
              <svg :class="[
                'w-6 h-6',
                themeStore.isDarkMode ? 'text-green-400' : 'text-green-600'
              ]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- Total Posts Card -->
        <div :class="cardClasses">
          <div class="flex items-center justify-between">
            <div>
              <p :class="['text-sm mb-1', textSecondaryClasses]">Total Posts</p>
              <p :class="['text-2xl font-bold', textPrimaryClasses]">{{ (analytics.totalPosts || 0).toLocaleString() }}</p>
              <p :class="[
                'text-xs mt-1',
                themeStore.isDarkMode ? 'text-purple-400' : 'text-purple-600'
              ]">
                {{ analytics.weeklyPosts || 0 }} this week
              </p>
            </div>
            <div :class="[
              'p-3 rounded-full',
              themeStore.isDarkMode ? 'bg-purple-900/50' : 'bg-purple-100'
            ]">
              <svg :class="[
                'w-6 h-6',
                themeStore.isDarkMode ? 'text-purple-400' : 'text-purple-600'
              ]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- Post Reported Card -->
        <div :class="cardClasses">
          <div class="flex items-center justify-between">
            <div>
              <p :class="['text-sm mb-1', textSecondaryClasses]">Post Reported</p>
              <p :class="['text-2xl font-bold', textPrimaryClasses]">{{ (analytics.reportedPosts || 0).toLocaleString() }}</p>
              <p :class="[
                'text-xs mt-1',
                themeStore.isDarkMode ? 'text-orange-400' : 'text-orange-600'
              ]">
                Requires attention
              </p>
            </div>
            <div :class="[
              'p-3 rounded-full',
              themeStore.isDarkMode ? 'bg-orange-900/50' : 'bg-orange-100'
            ]">
              <svg :class="[
                'w-6 h-6',
                themeStore.isDarkMode ? 'text-orange-400' : 'text-orange-600'
              ]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.865-.833-2.635 0L4.179 16.5c-.77.833.192 2.5 1.732 2.5z"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Additional Metrics Grid -->
      <div class="grid grid-cols-1 gap-6 md:grid-cols-3">
        <!-- User Statistics -->
        <div :class="cardClasses">
          <h3 :class="['text-lg font-semibold mb-4', textPrimaryClasses]">User Statistics</h3>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span :class="['text-sm', textSecondaryClasses]">Pending Approvals</span>
              <span :class="[
                'font-medium',
                themeStore.isDarkMode ? 'text-orange-400' : 'text-orange-600'
              ]">{{ analytics.pendingApprovals || 0 }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span :class="['text-sm', textSecondaryClasses]">User Engagement</span>
              <span :class="[
                'font-medium',
                themeStore.isDarkMode ? 'text-blue-400' : 'text-blue-600'
              ]">{{ analytics.userEngagement || 0 }}%</span>
            </div>
            <div class="flex items-center justify-between">
              <span :class="['text-sm', textSecondaryClasses]">Activity Rate</span>
              <span :class="[
                'font-medium',
                themeStore.isDarkMode ? 'text-green-400' : 'text-green-600'
              ]">
                {{ (analytics.totalUsers && analytics.activeUsers) ? ((analytics.activeUsers / analytics.totalUsers) * 100).toFixed(1) : '0.0' }}%
              </span>
            </div>
          </div>
        </div>

        <!-- Post Analytics -->
        <div :class="cardClasses">
          <h3 :class="['text-lg font-semibold mb-4', textPrimaryClasses]">Post Analytics</h3>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span :class="['text-sm', textSecondaryClasses]">Post Report</span>
              <span :class="[
                'font-medium',
                themeStore.isDarkMode ? 'text-orange-400' : 'text-orange-600'
              ]">{{ analytics.reportedPosts || 0 }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span :class="['text-sm', textSecondaryClasses]">Total Posts</span>
              <span :class="[
                'font-medium',
                themeStore.isDarkMode ? 'text-blue-400' : 'text-blue-600'
              ]">{{ analytics.totalPosts || 0 }}</span>
            </div>
          </div>
        </div>

        <!-- System Health -->
        <div :class="cardClasses">
          <h3 :class="['text-lg font-semibold mb-4', textPrimaryClasses]">System Health</h3>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span :class="['text-sm', textSecondaryClasses]">System Status</span>
              <span :class="[
                'font-medium',
                themeStore.isDarkMode ? 'text-green-400' : 'text-green-600'
              ]">●</span>
            </div>
            <div class="flex items-center justify-between">
              <span :class="['text-sm', textSecondaryClasses]">API Response</span>
              <span :class="[
                'font-medium',
                themeStore.isDarkMode ? 'text-green-400' : 'text-green-600'
              ]">Healthy</span>
            </div>
            <div class="flex items-center justify-between">
              <span :class="['text-sm', textSecondaryClasses]">Auto Refresh</span>
              <span :class="[
                'font-medium',
                themeStore.isDarkMode ? 'text-blue-400' : 'text-blue-600'
              ]">30s</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Posts Section -->
      <div :class="[
        'rounded-lg shadow-sm border',
        themeStore.isDarkMode
          ? 'bg-gray-800 border-gray-700'
          : 'bg-white border-gray-200'
      ]">
        <div :class="[
          'p-6 border-b',
          themeStore.isDarkMode ? 'border-gray-600' : 'border-gray-200'
        ]">
          <div class="flex items-center justify-between">
            <h3 :class="['text-lg font-semibold', textPrimaryClasses]">Recent Posts</h3>
            <button
              @click="fetchRecentPosts"
              :class="['text-sm font-medium', linkClasses]"
            >
              Refresh
            </button>
          </div>
        </div>

        <!-- Posts Loading State -->
        <div v-if="postsLoading" class="p-6 text-center">
          <div class="w-6 h-6 mx-auto border-b-2 border-blue-600 rounded-full animate-spin"></div>
          <p :class="['mt-2', textSecondaryClasses]">Loading recent posts...</p>
        </div>

        <!-- Recent Posts List -->
        <div v-else-if="recentPosts.length > 0" :class="[
          'divide-y',
          themeStore.isDarkMode ? 'divide-gray-600' : 'divide-gray-200'
        ]">
          <div
            v-for="post in recentPosts"
            :key="post.id"
            :class="[
              'p-6 transition-colors',
              themeStore.isDarkMode
                ? 'hover:bg-gray-700'
                : 'hover:bg-gray-50'
            ]"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center mb-2 space-x-2">
                  <h4 :class="['font-medium', textPrimaryClasses]">{{ post.author?.first_name }} {{ post.author?.last_name }}</h4>
                  <span
                    :class="[
                      'px-2 py-1 rounded-full text-xs font-medium',
                      post.status === 'pending'
                        ? (themeStore.isDarkMode ? 'bg-yellow-900/50 text-yellow-300' : 'bg-yellow-100 text-yellow-800')
                        : post.status === 'approved'
                        ? (themeStore.isDarkMode ? 'bg-green-900/50 text-green-300' : 'bg-green-100 text-green-800')
                        : (themeStore.isDarkMode ? 'bg-red-900/50 text-red-300' : 'bg-red-100 text-red-800')
                    ]"
                  >
                    {{ post.status }}
                  </span>
                </div>
                <p :class="['text-sm mb-2', textSecondaryClasses]">{{ truncateText(post.content, 100) }}</p>
                <p :class="[
                  'text-xs',
                  themeStore.isDarkMode ? 'text-gray-500' : 'text-gray-500'
                ]">{{ formatTime(post.created_at) }}</p>
              </div>

              <!-- Quick Actions - Removed approval since posts are auto-approved -->
              <div class="flex ml-4 space-x-2">
                <button
                  @click="viewPost(post.id)"
                  class="px-3 py-1 text-xs text-white transition-colors bg-blue-600 rounded hover:bg-blue-700"
                >
                  View
                </button>
                <button
                  @click="declinePost(post.id)"
                  class="px-3 py-1 text-xs text-white transition-colors bg-red-600 rounded hover:bg-red-700"
                >
                  Decline
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- No Posts State -->
        <div :class="[
          'p-6 text-center',
          themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
        ]">
          <svg :class="[
            'w-12 h-12 mx-auto mb-4',
            themeStore.isDarkMode ? 'text-gray-600' : 'text-gray-300'
          ]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/>
          </svg>
          <p>No recent posts found</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useThemeStore } from '@/stores/theme';

const authStore = useAuthStore();
const themeStore = useThemeStore();

// Computed styles for theme reactivity
const cardClasses = computed(() => [
  'rounded-lg shadow-sm border p-6',
  themeStore.isDarkMode
    ? 'bg-gray-800 border-gray-700'
    : 'bg-white border-gray-200'
]);

const textPrimaryClasses = computed(() =>
  themeStore.isDarkMode ? 'text-gray-200' : 'text-gray-800'
);

const textSecondaryClasses = computed(() =>
  themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'
);

const linkClasses = computed(() =>
  themeStore.isDarkMode
    ? 'text-blue-400 hover:text-blue-300'
    : 'text-blue-600 hover:text-blue-800'
);

// Router
const router = useRouter();

// Reactive data
const loading = ref(false);
const postsLoading = ref(false);
const error = ref(null);
const lastUpdated = ref(null);
const refreshInterval = ref(null);

// Analytics data
const analytics = ref({
  totalUsers: 0,
  activeUsers: 0,
  pendingApprovals: 0,
  recentRegistrations: 0,
  onlineUsers: 0,
  totalPosts: 0,
  pendingPosts: 0,
  reportedPosts: 0,
  declinedPosts: 0,
  weeklyPosts: 0,
  userEngagement: 0,
  pendingActions: 0
});

// Recent posts data
const recentPosts = ref([]);

// Methods
const fetchAnalytics = async () => {
  loading.value = true;
  try {
    // Debug: Check if token exists
    console.log('Dashboard Debug: Token available:', !!authStore.token);
    console.log('Dashboard Debug: User available:', !!authStore.user);
    console.log('Dashboard Debug: User type:', authStore.user?.user_type);

    // Use the correct analytics endpoint
    const response = await fetch('/api/admin/analytics/', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      }
    });

    console.log('Dashboard Debug: Analytics response status:', response.status);

    if (response.ok) {
      const data = await response.json();
      console.log('Dashboard Debug: Analytics data received:', Object.keys(data));
      console.log('Dashboard Debug: Full analytics data:', data);

      // Map the response to our existing data structure
      analytics.value = {
        totalUsers: data.users?.total || 0,
        activeUsers: data.users?.active || 0,
        pendingApprovals: data.users?.pending_approvals || 0,
        recentRegistrations: data.users?.recent_registrations || 0,
        onlineUsers: data.users?.online_now || 0,
        totalPosts: data.posts?.total || 0,
        pendingPosts: data.posts?.pending || 0,
        reportedPosts: data.posts?.reported || data.reports?.pending || 0,
        approvedPosts: data.posts?.approved || 0,
        declinedPosts: data.posts?.declined || 0,
        weeklyPosts: data.posts?.weekly_posts || 0,
        approvalRate: data.posts?.approval_rate || 0,
        userEngagement: data.summary?.user_engagement || 0,
        pendingActions: data.summary?.pending_actions || 0
      };

      console.log('Dashboard Debug: Mapped reportedPosts value:', analytics.value.reportedPosts);

      error.value = null;
      lastUpdated.value = new Date();
    } else {
      // Log the specific error response
      const errorText = await response.text();
      console.error('Dashboard Debug: Analytics API error:', response.status, errorText);
      console.log('Dashboard Debug: Response headers:', Object.fromEntries(response.headers.entries()));

      // If analytics endpoint fails, try fallback
      console.log('Dashboard Debug: Trying fallback analytics method');
      await fetchAnalyticsLegacy();
    }
  } catch (err) {
    console.error('Dashboard Debug: Analytics fetch error:', err);
    // Fallback to individual API calls
    console.log('Dashboard Debug: Exception occurred, trying fallback method');
    await fetchAnalyticsLegacy();
  } finally {
    loading.value = false;
  }
};

const fetchAnalyticsLegacy = async () => {
  try {
    console.log('Dashboard Debug: Starting legacy analytics fetch');

    const [usersResponse, postsResponse, reportsResponse] = await Promise.all([
      fetch('/api/users/', {
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json'
        }
      }),
      fetch('/api/posts/', {
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json'
        }
      }),
      fetch('/api/posts/reports/?status=pending', {
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json'
        }
      }).catch(err => {
        console.error('Dashboard Debug: Reports API request failed:', err);
        return { ok: false, status: 'network_error' };
      })
    ]);

    console.log('Dashboard Debug: Users API status:', usersResponse.status);
    console.log('Dashboard Debug: Posts API status:', postsResponse.status);
    console.log('Dashboard Debug: Reports API status:', reportsResponse.status);
    
    // Log the actual URL being called
    console.log('Dashboard Debug: Reports URL called:', '/api/posts/reports/?status=pending');

    if (usersResponse.ok && postsResponse.ok) {
      // Check response content before parsing
      const usersText = await usersResponse.text();
      const postsText = await postsResponse.text();
      let reportsText = '{"results": [], "count": 0}'; // Default fallback

      // Only try to get reports if the response was successful
      if (reportsResponse.ok) {
        reportsText = await reportsResponse.text();
      } else {
        console.warn('Dashboard Debug: Reports API failed, using fallback data');
      }

      console.log('Dashboard Debug: Users response preview:', usersText.substring(0, 100));
      console.log('Dashboard Debug: Posts response preview:', postsText.substring(0, 100));
      console.log('Dashboard Debug: Reports response preview:', reportsText.substring(0, 100));

      try {
        const usersData = JSON.parse(usersText);
        const postsData = JSON.parse(postsText);
        const reportsData = JSON.parse(reportsText);

        console.log('Dashboard Debug: Users data type:', Array.isArray(usersData) ? 'array' : typeof usersData);
        console.log('Dashboard Debug: Posts data type:', Array.isArray(postsData) ? 'array' : typeof postsData);
        console.log('Dashboard Debug: Reports data type:', Array.isArray(reportsData) ? 'array' : typeof reportsData);
        console.log('Dashboard Debug: Reports data:', reportsData);

        // Calculate analytics from raw data
        const users = usersData.results || usersData;
        const posts = postsData.results || postsData;
        const reports = reportsData.results || reportsData;

        console.log('Dashboard Debug: Reports array length:', Array.isArray(reports) ? reports.length : 'not array');
        console.log('Dashboard Debug: Reports count:', reportsData.count);

        analytics.value = {
          totalUsers: users.length,
          activeUsers: users.filter(user => user.is_active).length,
          pendingApprovals: users.filter(user => user.user_type === 3 && !user.is_approved).length,
          recentRegistrations: users.filter(user => {
            const joinDate = new Date(user.date_joined);
            const weekAgo = new Date();
            weekAgo.setDate(weekAgo.getDate() - 7);
            return joinDate >= weekAgo;
          }).length,
          onlineUsers: users.filter(user => {
            if (!user.last_login) return false;
            const lastLogin = new Date(user.last_login);
            const fifteenMinutesAgo = new Date();
            fifteenMinutesAgo.setMinutes(fifteenMinutesAgo.getMinutes() - 15);
            return lastLogin >= fifteenMinutesAgo;
          }).length,
          totalPosts: posts.length,
          pendingPosts: posts.filter(post => post.status === 'pending').length,
          reportedPosts: Array.isArray(reports) ? reports.length : (reportsData.count || 0),
          approvedPosts: posts.filter(post => post.status === 'approved').length,
          declinedPosts: posts.filter(post => post.status === 'declined').length,
          weeklyPosts: posts.filter(post => {
            const postDate = new Date(post.created_at);
            const weekAgo = new Date();
            weekAgo.setDate(weekAgo.getDate() - 7);
            return postDate >= weekAgo;
          }).length,
          approvalRate: 0,
          userEngagement: 0,
          pendingActions: 0
        };

        console.log('Dashboard Debug: Final reportedPosts value:', analytics.value.reportedPosts);

        // Calculate derived metrics
        const totalReviewed = analytics.value.approvedPosts + analytics.value.declinedPosts;
        analytics.value.approvalRate = totalReviewed > 0 ?
          Math.round((analytics.value.approvedPosts / totalReviewed) * 100) : 0;

        analytics.value.userEngagement = analytics.value.activeUsers > 0 ?
          Math.round((analytics.value.onlineUsers / analytics.value.activeUsers) * 100) : 0;

        analytics.value.pendingActions = analytics.value.reportedPosts + analytics.value.pendingApprovals;

        error.value = null;
        lastUpdated.value = new Date();

      } catch (parseError) {
        console.error('Dashboard Debug: JSON parsing error:', parseError);
        console.log('Dashboard Debug: Users text was:', usersText);
        console.log('Dashboard Debug: Posts text was:', postsText);
        console.log('Dashboard Debug: Reports text was:', reportsText);
        throw parseError;
      }
    } else {
      // Handle individual API failures
      if (!usersResponse.ok) {
        const usersError = await usersResponse.text();
        console.error('Dashboard Debug: Users API error:', usersResponse.status, usersError);
      }
      if (!postsResponse.ok) {
        const postsError = await postsResponse.text();
        console.error('Dashboard Debug: Posts API error:', postsResponse.status, postsError);
      }
      if (!reportsResponse.ok) {
        const reportsError = await reportsResponse.text();
        console.error('Dashboard Debug: Reports API error:', reportsResponse.status, reportsError);
      }
      throw new Error('One or more API calls failed');
    }
  } catch (err) {
    console.error('Dashboard Debug: Legacy analytics fetch error:', err);
    error.value = 'Failed to load dashboard data. Please check your connection and try again.';
  }
};

const fetchRecentPosts = async () => {
  postsLoading.value = true;
  try {
    const response = await fetch('/api/posts/?ordering=-created_at&limit=10', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.ok) {
      const data = await response.json();
      recentPosts.value = data.results || data;
    } else {
      console.error('Failed to fetch recent posts');
    }
  } catch (err) {
    console.error('Recent posts fetch error:', err);
  } finally {
    postsLoading.value = false;
  }
};

// Test function to check reports endpoint
const testReportsEndpoint = async () => {
  console.log('Dashboard Debug: Testing reports endpoint directly...');
  try {
    const response = await fetch('/api/posts/reports/?status=pending', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('Dashboard Debug: Test Reports Response Status:', response.status);
    console.log('Dashboard Debug: Test Reports Response Headers:', Object.fromEntries(response.headers.entries()));
    
    if (response.ok) {
      const data = await response.json();
      console.log('Dashboard Debug: Test Reports Data:', data);
      return data;
    } else {
      const errorText = await response.text();
      console.error('Dashboard Debug: Test Reports Error:', errorText);
      return null;
    }
  } catch (err) {
    console.error('Dashboard Debug: Test Reports Exception:', err);
    return null;
  }
};

// Post approval/decline functions removed - posts are now auto-approved
// Admin moderates by directly deleting inappropriate posts

const viewPost = (postId) => {
  // Navigate to content page with specific post or open post modal
  router.push(`/admin/contents?post=${postId}`);
};

const refreshData = async () => {
  await Promise.all([fetchAnalytics(), fetchRecentPosts()]);
};

const formatTime = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now - date) / 1000);

  if (diffInSeconds < 60) {
    return 'Just now';
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60);
    return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600);
    return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
  } else {
    const days = Math.floor(diffInSeconds / 86400);
    return `${days} day${days !== 1 ? 's' : ''} ago`;
  }
};

const truncateText = (text, maxLength) => {
  if (!text) return '';
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
};

// Lifecycle hooks
onMounted(async () => {
  // Test the reports endpoint first
  await testReportsEndpoint();
  
  // Initial data fetch
  await refreshData();
  
  // Set up auto-refresh every 30 seconds
  refreshInterval.value = setInterval(() => {
    fetchAnalytics();
  }, 30000);
});onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value);
  }
});
</script>
