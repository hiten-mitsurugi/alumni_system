<script setup>
import { ref, onMounted, onUnmounted, computed, provide } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useThemeStore } from '@/stores/theme';
import axios from 'axios';

// Import dedicated CSS file
import '@/components/css/AlumniHome.css';

// Import posting components
import PostCreateForm from '@/components/posting/PostCreateForm.vue';
import PostCard from '@/components/posting/PostCard.vue';
import PostModal from '@/components/posting/PostModal.vue';
import NotificationToast from '@/components/posting/NotificationToast.vue';

// Import alumni components
import ProfileCard from '@/components/alumni/ProfileCard.vue';
import SuggestedConnectionsWidget from '@/components/profile/SuggestedConnectionsWidget.vue';

// Props
const props = defineProps({
  sidebarExpanded: {
    type: Boolean,
    default: false
  }
})

const router = useRouter();
const authStore = useAuthStore();
const themeStore = useThemeStore();

// State
const posts = ref([]);
const searchQuery = ref('');
const activeTab = ref('all');
const selectedCategory = ref('all');
const selectedReaction = ref({});
const comments = ref({});
const notifications = ref([]);
const showCreateForm = ref(false);
const showMobileSearch = ref(false);
const isLoading = ref(false);
const isPosting = ref(false);

// Component refs
const postCreateForm = ref(null);

// Modal state
const showModal = ref(false);
const selectedPost = ref(null);
const currentPostIndex = ref(0);

// Current user computed
const currentUser = computed(() => authStore.user);

// Sidebar state computed
const sidebarExpanded = computed(() => props.sidebarExpanded);

// Icon component mapper
const getIconSVG = (iconName) => {
  const icons = {
    grid: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path></svg>`,
    chat: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>`,
    megaphone: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z"></path></svg>`,
    calendar: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>`,
    newspaper: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"></path></svg>`,
    briefcase: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0H8m8 0v2a2 2 0 002 2v8a2 2 0 01-2 2H6a2 2 0 01-2-2v-8a2 2 0 012-2V8a2 2 0 012-2z"></path></svg>`,
    document: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>`
  };
  return icons[iconName] || icons.document;
};

// WebSocket connection
let postsSocket = null;

// Constants
// Dynamically determine backend base URL and WebSocket URL
const getBackendBaseUrl = () => {
  // Use window.location.hostname and protocol, but default to port 8000 for backend
  const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
  const hostname = window.location.hostname;
  // If running on localhost, fallback to 127.0.0.1
  const host = (hostname === 'localhost' || hostname === '127.0.0.1') ? hostname : hostname;
  return `${protocol}//${host}:8000`;
};

const getProfilePictureUrl = (profilePicture) => {
  if (!profilePicture) return null;
  // If already a full URL, return as is
  if (profilePicture.startsWith('http://') || profilePicture.startsWith('https://')) {
    return profilePicture;
  }
  // If relative path, prepend dynamic base URL
  const BASE_URL = getBackendBaseUrl();
  return profilePicture.startsWith('/') ? `${BASE_URL}${profilePicture}` : `${BASE_URL}/${profilePicture}`;
};

const BASE_URL = getBackendBaseUrl();
const categories = [
  { value: 'all', label: 'All Posts', icon: 'grid' },
  { value: 'discussion', label: 'Discussion', icon: 'chat' },
  { value: 'announcement', label: 'Announcement', icon: 'megaphone' },
  { value: 'event', label: 'Event', icon: 'calendar' },
  { value: 'news', label: 'News', icon: 'newspaper' },
  { value: 'job', label: 'Job Posting', icon: 'briefcase' },
  { value: 'others', label: 'Others', icon: 'document' }
];

// Computed
const filteredPosts = computed(() => {
  let filtered = posts.value;

  if (activeTab.value !== 'all') {
    filtered = filtered.filter(post => post.content_category === activeTab.value);
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(post =>
      post.title?.toLowerCase().includes(query) ||
      post.content?.toLowerCase().includes(query) ||
      post.user?.first_name?.toLowerCase().includes(query) ||
      post.user?.last_name?.toLowerCase().includes(query)
    );
  }

  return filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
});

// WebSocket Functions
const connectWebSocket = () => {
  const token = authStore.token;
  if (!token) {
    console.error('No authentication token available for WebSocket connection');
    return;
  }

  // Use ws or wss depending on protocol
  const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const wsHost = window.location.hostname;
  const wsUrl = `${wsProtocol}://${wsHost}:8000/ws/posts/feed/?token=${token}`;
  postsSocket = new WebSocket(wsUrl);

  postsSocket.onopen = () => {
    console.log('✅ Connected to posts WebSocket');
    console.log('🔗 WebSocket URL:', wsUrl);
    console.log('👤 Connected as user:', authStore.user?.email);

    // Subscribe to post updates if posts are already loaded
    if (posts.value.length > 0) {
      console.log('📡 WebSocket connected, subscribing to existing posts...');
      subscribeToPostUpdates();
    }
  };

  postsSocket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('📨 Raw WebSocket message received:', data);

    // Handle successful post group join
    if (data.type === 'joined_post') {
      console.log('✅ Successfully joined post group:', data.post_id);
    }

    handleWebSocketMessage(data);
  };

  postsSocket.onclose = () => {
    console.log('Disconnected from posts WebSocket');
    // Only reconnect if user is still authenticated
    if (authStore.token) {
      setTimeout(connectWebSocket, 3000);
    }
  };

  postsSocket.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
};

const handleWebSocketMessage = (data) => {
  switch (data.type) {
    case 'new_post':
      fetchPosts(); // Refresh posts when new post is created
      break;
    case 'reaction_update':
      updatePostReaction(data);
      break;
    case 'new_comment':
      console.log('🔔 Received new_comment WebSocket message:', data);
      addNewComment(data);
      break;
  }
};

// API Functions
const fetchPosts = async () => {
  try {
    console.log('🔄 Fetching posts from API...');
    const response = await axios.get(`${BASE_URL}/api/posts/posts/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
      params: {
        category: activeTab.value !== 'all' ? activeTab.value : null,
        search: searchQuery.value || null
      }
    });

    console.log('✅ Posts response:', response.data);
    posts.value = response.data.results || response.data;
    console.log('📊 Loaded posts:', posts.value.length);

    // Initialize selectedReaction from backend user_reaction data
    posts.value.forEach(post => {
      if (post.reactions_summary && post.reactions_summary.user_reaction) {
        selectedReaction.value[post.id] = post.reactions_summary.user_reaction;
        console.log(`🎯 Initialized reaction for post ${post.id}: ${post.reactions_summary.user_reaction}`);
      } else {
        // Ensure no old reactions remain for posts without current user reactions
        selectedReaction.value[post.id] = null;
      }
    });

    console.log('🎯 Final selectedReaction state:', selectedReaction.value);

    // Subscribe to real-time updates for all loaded posts
    subscribeToPostUpdates();

  } catch (error) {
    console.error('❌ Failed to fetch posts:', error);
    console.error('Response:', error.response?.data);
    showNotification('Failed to load posts. Please try again.', 'error');
  }
};

// Function to subscribe to real-time updates for all loaded posts
const subscribeToPostUpdates = () => {
  if (postsSocket && postsSocket.readyState === WebSocket.OPEN) {
    posts.value.forEach(post => {
      console.log('📡 Subscribing to real-time updates for post:', post.id);
      postsSocket.send(JSON.stringify({
        type: 'join_post',
        post_id: post.id
      }));
    });
  } else {
    console.log('⚠️ WebSocket not ready, will subscribe when connected');
  }
};

const createPost = async (postData) => {
  try {
    console.log('📝 Creating new post:', postData);

    // Create FormData for file upload
    const formData = new FormData();

    // Add basic post data
    if (postData.title) {
      formData.append('title', postData.title);
    }
    formData.append('content', postData.content);
    formData.append('content_category', postData.category);

    // Add mentions if any
    if (postData.mentions && postData.mentions.length > 0) {
      formData.append('mentions', JSON.stringify(postData.mentions));
    }

    // Add files if any (backend expects 'media_files')
    if (postData.files && postData.files.length > 0) {
      postData.files.forEach((file) => {
        formData.append('media_files', file);
      });
    }

    const response = await axios.post(`${BASE_URL}/api/posts/posts/create/`, formData, {
      headers: {
        Authorization: `Bearer ${authStore.token}`,
        'Content-Type': 'multipart/form-data'
      }
    });

    console.log('✅ Post created successfully:', response.data);
    showNotification('Post created successfully! 🎉', 'success');
    showCreateForm.value = false; // Close the modal

    // Clear the form after successful creation
    if (postCreateForm.value?.clearForm) {
      postCreateForm.value.clearForm();
    }

    await fetchPosts(); // Refresh posts

  } catch (error) {
    console.error('❌ Failed to create post:', error);
    console.error('Error response:', error.response?.data);
    showNotification('Failed to create post. Please try again.', 'error');
  }
};

const handleCreatePost = async (postData) => {
  await createPost(postData);
};

// Sidebar functions - removed unused API calls

const connectPerson = async (personId) => {
  try {
    await axios.post(`${BASE_URL}/api/network/connect/${personId}/`, {}, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });
    showNotification('Connection request sent!', 'success');
  } catch (error) {
    console.error('Failed to send connection request:', error);
    showNotification('Failed to send connection request.', 'error');
  }
};

const handleConnect = async (personId) => {
  try {
    console.log('Handling connection for person:', personId);
    await connectPerson(personId);
    showNotification('Connection request sent!', 'success');
  } catch (error) {
    console.error('Failed to handle connection:', error);
    showNotification('Failed to send connection request.', 'error');
  }
};

const editProfile = () => {
  // Navigate to profile edit page or open edit modal
  router.push('/alumni/profile/edit');
};

const viewProfile = () => {
  // Navigate to profile view page
  router.push('/alumni/profile');
};

const reactToPost = async (postId, reactionType) => {
  try {
    console.log(`🎯 Reacting to post ${postId} with ${reactionType}`);

    const currentUserReaction = selectedReaction.value[postId];

    // If clicking the same reaction, remove it
    if (currentUserReaction === reactionType) {
      console.log(`🗑️ Removing reaction ${reactionType} from post ${postId}`);

      const response = await axios.delete(`${BASE_URL}/api/posts/posts/${postId}/react/`, {
        headers: { Authorization: `Bearer ${authStore.token}` }
      });

      console.log('✅ Reaction removed:', response.data);
      selectedReaction.value[postId] = null;

    } else {
      // Add or change reaction
      console.log(`➕ Adding/changing reaction ${reactionType} for post ${postId}`);

      const response = await axios.post(`${BASE_URL}/api/posts/posts/${postId}/react/`, {
        reaction_type: reactionType
      }, {
        headers: { Authorization: `Bearer ${authStore.token}` }
      });

      console.log('✅ Reaction response:', response.data);
      selectedReaction.value[postId] = reactionType;
    }

    // Refresh the specific post data
    await fetchPosts();

  } catch (error) {
    console.error('❌ Failed to react to post:', error);
    showNotification('Failed to add reaction. Please try again.', 'error');
  }
};

const addComment = async (postId, commentContent, parentId = null, mentions = []) => {
  try {
    console.log(`💬 Adding comment to post ${postId}:`, commentContent);

    const requestData = {
      content: commentContent,
      parent_id: parentId
    };
    
    // Add mentions if provided
    if (mentions && mentions.length > 0) {
      requestData.mentions = mentions;
    }

    const response = await axios.post(`${BASE_URL}/api/posts/posts/${postId}/comment/`, requestData, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });

    console.log('✅ Comment added:', response.data);
    showNotification('Comment added successfully! 💬', 'success');

    // Refresh comments for this post
    await fetchCommentsForPost(postId);
    await fetchPosts(); // Also refresh posts to update comment counts

  } catch (error) {
    console.error('❌ Failed to add comment:', error);
    showNotification('Failed to add comment. Please try again.', 'error');
  }
};

const fetchCommentsForPost = async (postId) => {
  try {
    console.log(`🔄 Fetching comments for post ${postId}`);
    const response = await axios.get(`${BASE_URL}/api/posts/posts/${postId}/comments/`, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });

    console.log('✅ Comments fetched:', response.data);
    comments.value[postId] = response.data.comments || response.data;

  } catch (error) {
    console.error('❌ Failed to fetch comments:', error);
  }
};

const sharePost = async (postId, shareText = '') => {
  try {
    console.log(`🔄 Sharing post ${postId} with text: "${shareText}"`);
    const response = await axios.post(`${BASE_URL}/api/posts/posts/${postId}/share/`, {
      shared_text: shareText
    }, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });

    console.log('✅ Post shared:', response.data);
    showNotification('Post shared successfully! 🚀', 'success');
    await fetchPosts();

  } catch (error) {
    console.error('❌ Failed to share post:', error);
    showNotification('Failed to share post. Please try again.', 'error');
  }
};

const copyPostLink = (postId) => {
  const postUrl = `${window.location.origin}/posts/${postId}`;
  navigator.clipboard.writeText(postUrl);
  showNotification('Post link copied to clipboard! 📋', 'success');
};

// Modal functions
const openPostModal = (post) => {
  selectedPost.value = post;
  currentPostIndex.value = filteredPosts.value.findIndex(p => p.id === post.id);
  showModal.value = true;

  // Load comments when opening modal
  fetchCommentsForPost(post.id);
};

const closePostModal = () => {
  showModal.value = false;
  selectedPost.value = null;
  currentPostIndex.value = 0;
};

const navigateToPost = (direction) => {
  const newIndex = direction === 'next'
    ? Math.min(currentPostIndex.value + 1, filteredPosts.value.length - 1)
    : Math.max(currentPostIndex.value - 1, 0);

  currentPostIndex.value = newIndex;
  selectedPost.value = filteredPosts.value[newIndex];
  fetchCommentsForPost(selectedPost.value.id);
};

// Real-time update handlers
const updatePostReaction = (data) => {
  console.log('🔔 Updating post reaction:', data);

  // Find the post and update its reaction data
  const postIndex = posts.value.findIndex(p => p.id === data.post_id);
  if (postIndex !== -1) {
    // Update the post's reaction counts
    fetchPosts(); // Simple approach: refresh all posts
  }
};

const addNewComment = (data) => {
  console.log('🔔 Adding new comment via WebSocket:', data);

  // Add comment to the comments array for this post
  if (!comments.value[data.post_id]) {
    comments.value[data.post_id] = [];
  }

  // Check if comment already exists to avoid duplicates
  const existingComment = comments.value[data.post_id].find(c => c.id === data.comment_id);
  if (!existingComment) {
    comments.value[data.post_id].push({
      id: data.comment_id,
      user: {
        id: data.user_id,
        first_name: data.user_name.split(' ')[0],
        last_name: data.user_name.split(' ').slice(1).join(' ')
      },
      content: data.content,
      parent_id: data.parent_id,
      created_at: data.timestamp,
      likes_count: 0,
      replies_count: 0
    });

    console.log('✅ New comment added via WebSocket');
  }

  // Also refresh posts to update comment counts
  fetchPosts();
};

const handleReactionUpdated = (postId, reactionType) => {
  console.log(`🎯 Reaction updated for post ${postId}: ${reactionType}`);
  selectedReaction.value[postId] = reactionType;
};

// Notification system
const showNotification = (message, type = 'info') => {
  notifications.value.unshift({
    id: Date.now(),
    message,
    type,
    timestamp: new Date().toISOString()
  });

  // Auto-remove notification after 5 seconds
  setTimeout(() => {
    dismissNotification(notifications.value[notifications.value.length - 1]);
  }, 5000);
};

const dismissNotification = (notification) => {
  const index = notifications.value.findIndex(n => n.id === notification.id);
  if (index > -1) {
    notifications.value.splice(index, 1);
  }
};

// Mobile search toggle
const toggleMobileSearch = () => {
  showMobileSearch.value = !showMobileSearch.value;
};

// Provide search functionality to child components (like navbar)
provide('searchQuery', searchQuery)
provide('toggleMobileSearch', toggleMobileSearch)

// Lifecycle
onMounted(() => {
  console.log('🚀 AlumniHome component mounted, initializing...');
  connectWebSocket();
  fetchPosts();
});

onUnmounted(() => {
  console.log('🔚 AlumniHome component unmounting, cleaning up...');
  if (postsSocket) {
    postsSocket.close();
  }
});
</script>

<template>
  <div :class="[
    'min-h-screen alumni-home-container',
    themeStore.isDarkMode ? 'bg-gray-900' : 'bg-white'
  ]">
    <!-- Desktop Layout (md and up) -->
    <div class="hidden md:block">
      <!-- Responsive Grid Layout -->
      <div class="alumni-home-grid">
        <!-- Left Sidebar: Profile Card -->
        <aside :class="[
          'alumni-sidebar alumni-sidebar-left transition-all duration-200',
          sidebarExpanded ? 'left-72' : 'left-24'
        ]">
          <div class="sidebar-content">
            <ProfileCard
              @edit-profile="editProfile"
              @view-profile="viewProfile"
            />
          </div>
        </aside>

        <!-- Center Column: Main Feed -->
        <main class="alumni-main-content">
          <div class="main-content-wrapper">
            <div class="space-y-4 md:space-y-6">
              <!-- Category Tabs -->
              <div :class="[
                'overflow-hidden border rounded-lg shadow-sm sm:rounded-xl backdrop-blur-sm',
                themeStore.isDarkMode
                  ? 'bg-gray-800/95 border-gray-700'
                  : 'bg-white/95 border-gray-200'
              ]">
                <div :class="[
                  'flex w-full',
                  themeStore.isDarkMode ? 'border-b border-gray-700/50' : 'border-b border-gray-200/50'
                ]">
                  <button
                    v-for="category in categories"
                    :key="category.value"
                    @click="selectedCategory = category.value; activeTab = category.value"
                    :class="[
                      'flex items-center justify-center px-3 py-3 text-xs sm:text-sm font-medium transition-all duration-300 border-b-2 text-center relative overflow-hidden group flex-1',
                      selectedCategory === category.value
                        ? themeStore.isDarkMode
                          ? 'text-orange-400 border-orange-400 bg-orange-400/10'
                          : 'text-orange-600 border-orange-500 bg-orange-50/80'
                        : themeStore.isDarkMode
                          ? 'text-gray-400 border-transparent hover:text-orange-400 hover:border-orange-400/50 hover:bg-orange-400/5'
                          : 'text-gray-600 border-transparent hover:text-orange-600 hover:border-orange-500/50 hover:bg-orange-50/50'
                    ]"
                  >
                    <!-- Subtle animation background -->
                    <div :class="[
                      'absolute inset-0 transform transition-transform duration-300 ease-out',
                      selectedCategory === category.value
                        ? 'scale-100 opacity-100'
                        : 'scale-95 opacity-0 group-hover:scale-100 group-hover:opacity-50',
                      themeStore.isDarkMode ? 'bg-gradient-to-r from-orange-400/5 to-orange-500/5' : 'bg-gradient-to-r from-orange-50 to-orange-100/50'
                    ]"></div>
                    <div class="flex flex-col items-center space-y-1 relative z-10">
                      <div :class="[
                        'transition-transform duration-200',
                        selectedCategory === category.value ? 'transform scale-110' : 'group-hover:transform group-hover:scale-105',
                        selectedCategory === category.value
                          ? (themeStore.isDarkMode ? 'text-orange-400' : 'text-orange-600')
                          : (themeStore.isDarkMode ? 'text-gray-500' : 'text-gray-400')
                      ]" v-html="getIconSVG(category.icon)"></div>
                      <span class="hidden text-xs truncate sm:block font-medium">{{ category.label }}</span>

                      <!-- Active indicator dot -->
                      <div v-if="selectedCategory === category.value" :class="[
                        'absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-1 h-1 rounded-full transition-all duration-300',
                        themeStore.isDarkMode ? 'bg-orange-400' : 'bg-orange-500'
                      ]"></div>
                    </div>
                  </button>
                </div>
              </div>

              <!-- Desktop Post Create -->
              <PostCreateForm
                :user-profile-picture="currentUser?.profile_picture"
                :categories="categories"
                :is-posting="isPosting"
                @create-post="handleCreatePost"
                ref="postCreateForm"
              />

              <!-- Posts Feed -->
              <div class="space-y-4 md:space-y-6">
                <PostCard
                  v-for="post in filteredPosts"
                  :key="post.id"
                  :post="post"
                  :categories="categories"
                  :selected-reaction="selectedReaction[post.id]"
                  :comments="comments[post.id] || post.recent_comments || []"
                  :user-profile-picture="currentUser?.profile_picture"
                  :current-user-id="currentUser?.id"
                  @react-to-post="reactToPost"
                  @add-comment="addComment"
                  @share-post="sharePost"
                  @copy-link="copyPostLink"
                  @open-modal="openPostModal"
                  @reaction-updated="handleReactionUpdated"
                />
              </div>

              <!-- Loading State -->
              <div v-if="isLoading" class="flex justify-center py-8">
                <div class="flex items-center space-x-2 text-gray-500">
                  <svg class="w-5 h-5 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Loading posts...</span>
                </div>
              </div>

              <!-- Empty State -->
              <div v-if="filteredPosts.length === 0 && !isLoading" class="py-12 text-center">
                <div :class="[
                  'p-8 border shadow-sm rounded-xl',
                  themeStore.isDarkMode
                    ? 'bg-gray-800 border-gray-700'
                    : 'bg-white border-gray-200'
                ]">
                  <svg :class="[
                    'w-12 h-12 mx-auto mb-4',
                    themeStore.isDarkMode ? 'text-gray-500' : 'text-gray-400'
                  ]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                  </svg>
                  <h3 :class="[
                    'mb-2 text-lg font-semibold',
                    themeStore.isDarkMode ? 'text-gray-200' : 'text-gray-800'
                  ]">No Posts Yet</h3>
                  <p :class="[
                    'mb-4 text-sm',
                    themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'
                  ]">
                    {{ searchQuery ? 'Try different search terms' : 'Be the first to share something!' }}
                  </p>
                  <button
                    v-if="!searchQuery"
                    @click="showCreateForm = true"
                    class="inline-flex items-center px-4 py-2 text-sm font-medium text-white transition-colors bg-orange-600 rounded-lg hover:bg-orange-500"
                  >
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                    Create Post
                  </button>
                </div>
              </div>
            </div>
          </div>
        </main>

        <!-- Right Sidebar: Suggested Connections -->
        <aside :class="[
          'alumni-sidebar alumni-sidebar-right transition-all duration-200',
          sidebarExpanded ? 'right-6' : 'right-6'
        ]">
          <div class="sidebar-content">
            <SuggestedConnectionsWidget @connect="handleConnect" />
          </div>
        </aside>
      </div>
    </div>

    <!-- Mobile Layout (below md) -->
    <div class="block md:hidden">
      <div class="w-full min-h-screen overflow-x-hidden">
        <div class="w-full">
          <div class="space-y-0 pb-4">
            <!-- Category Tabs (Mobile) -->
            <div :class="[
              'w-full shadow-sm backdrop-blur-sm border-t border-b border-l-0 border-r-0',
              themeStore.isDarkMode
                ? 'bg-gray-800/95 border-gray-700'
                : 'bg-white/95 border-gray-200'
            ]">
              <div :class="[
                'flex overflow-x-auto scrollbar-hide px-0',
                themeStore.isDarkMode ? '' : ''
              ]" style="scrollbar-width: none; -ms-overflow-style: none;">
                <button
                  v-for="category in categories"
                  :key="category.value"
                  @click="selectedCategory = category.value; activeTab = category.value"
                  :class="[
                    'flex items-center justify-center px-4 py-4 text-xs font-medium transition-all duration-300 border-b-2 text-center relative overflow-hidden group touch-manipulation flex-shrink-0 whitespace-nowrap min-w-0',
                    selectedCategory === category.value
                      ? themeStore.isDarkMode
                        ? 'text-orange-400 border-orange-400 bg-orange-400/10'
                        : 'text-orange-600 border-orange-500 bg-orange-50/80'
                      : themeStore.isDarkMode
                        ? 'text-gray-400 border-transparent hover:text-orange-400 hover:border-orange-400/50 hover:bg-orange-400/5'
                        : 'text-gray-600 border-transparent hover:text-orange-600 hover:border-orange-500/50 hover:bg-orange-50/50'
                  ]"
                  :style="{ minWidth: `${100 / categories.length}vw` }"
                  :aria-label="category.label"
                  :title="category.label"
                >
                  <!-- Subtle animation background -->
                  <div :class="[
                    'absolute inset-0 transform transition-transform duration-300 ease-out',
                    selectedCategory === category.value
                      ? 'scale-100 opacity-100'
                      : 'scale-95 opacity-0 group-hover:scale-100 group-hover:opacity-50',
                    themeStore.isDarkMode ? 'bg-gradient-to-r from-orange-400/5 to-orange-500/5' : 'bg-gradient-to-r from-orange-50 to-orange-100/50'
                  ]"></div>

                  <!-- Icon Only for Mobile -->
                  <div :class="[
                    'relative z-10 transition-transform duration-200 flex items-center justify-center',
                    selectedCategory === category.value ? 'transform scale-110' : 'group-hover:transform group-hover:scale-105',
                    selectedCategory === category.value
                      ? (themeStore.isDarkMode ? 'text-orange-400' : 'text-orange-600')
                      : (themeStore.isDarkMode ? 'text-gray-500' : 'text-gray-400')
                  ]">
                    <div class="w-5 h-5" v-html="getIconSVG(category.icon)"></div>
                  </div>

                  <!-- Active indicator dot -->
                  <div v-if="selectedCategory === category.value" :class="[
                    'absolute -bottom-0.5 left-1/2 transform -translate-x-1/2 w-2 h-0.5 rounded-full transition-all duration-300',
                    themeStore.isDarkMode ? 'bg-orange-400' : 'bg-orange-500'
                  ]"></div>
                </button>
              </div>
            </div>

            <!-- Mobile Post Create Section -->
            <div :class="[
              'w-full border-b px-4 py-3',
              themeStore.isDarkMode
                ? 'bg-gray-800/95 border-gray-700'
                : 'bg-white/95 border-gray-200'
            ]">
              <button
                @click="showCreateForm = true"
                :class="[
                  'w-full flex items-center space-x-3 p-3 rounded-lg transition-all duration-200 text-left',
                  themeStore.isDarkMode
                    ? 'bg-gray-700 hover:bg-gray-600 border border-gray-600'
                    : 'bg-gray-50 hover:bg-gray-100 border border-gray-200'
                ]"
              >
                <!-- User Avatar -->
                <img
                  :src="getProfilePictureUrl(currentUser?.profile_picture) || '/default-avatar.png'"
                  :alt="`${currentUser?.first_name} ${currentUser?.last_name}`"
                  class="w-10 h-10 rounded-full object-cover flex-shrink-0 border-2"
                  :class="themeStore.isDarkMode ? 'border-gray-600' : 'border-gray-200'"
                >

                <!-- Share Text -->
                <div :class="[
                  'flex-1 text-left',
                  themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
                ]">
                  <span class="text-base">Share your thoughts...</span>
                </div>

                <!-- Camera Icon -->
                <div :class="[
                  'flex-shrink-0',
                  themeStore.isDarkMode ? 'text-gray-500' : 'text-gray-400'
                ]">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
              </button>
            </div>

            <!-- Posts Feed (Mobile) -->
            <div class="w-full">
              <div v-if="isLoading" class="flex justify-center py-8">
                <div class="w-8 h-8 border-b-2 border-orange-600 rounded-full animate-spin"></div>
              </div>

              <div v-else-if="filteredPosts.length === 0" :class="[
                'py-8 text-center px-4',
                themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
              ]">
                <p>No posts to show yet.</p>
                <p class="mt-2 text-sm">Be the first to share something!</p>
                <button
                  @click="showCreateForm = true"
                  class="inline-flex items-center px-4 py-2 mt-4 text-sm font-medium text-white transition-colors bg-orange-600 rounded-lg hover:bg-orange-500"
                >
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  Create Post
                </button>
              </div>

              <div v-else class="divide-y" :class="themeStore.isDarkMode ? 'divide-gray-700' : 'divide-gray-200'">
                <PostCard
                  v-for="post in filteredPosts"
                  :key="post.id"
                  :post="post"
                  :current-user-id="currentUser?.id"
                  :categories="categories"
                  :selected-reaction="selectedReaction[post.id]"
                  :comments="comments[post.id] || post.recent_comments || []"
                  :user-profile-picture="currentUser?.profile_picture"
                  @react-to-post="reactToPost"
                  @add-comment="addComment"
                  @share-post="sharePost"
                  @copy-link="copyPostLink"
                  @open-modal="openPostModal"
                  @reaction-updated="handleReactionUpdated"
                />
              </div>
            </div>

            <!-- Mobile Post Create Modal -->
            <div
              v-if="showCreateForm"
              class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
              @click.self="showCreateForm = false"
            >
              <div class="bg-white rounded-xl w-full max-w-md max-h-[80vh] overflow-y-auto" @click.stop>
                <div class="flex items-center justify-between p-4 border-b border-gray-200">
                  <h2 class="text-lg font-semibold">Create Post</h2>
                  <button
                    @click.stop="showCreateForm = false"
                    class="flex items-center justify-center p-2 transition-colors duration-200 rounded-full hover:bg-gray-100"
                    aria-label="Close"
                  >
                    <svg class="w-5 h-5 text-gray-600 hover:text-gray-800" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <div class="p-4">
                  <PostCreateForm
                    :user-profile-picture="currentUser?.profile_picture"
                    :categories="categories"
                    :is-posting="isPosting"
                    @create-post="handleCreatePost"
                    ref="postCreateForm"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Post Modal (Single Instance) -->
    <PostModal
      v-if="showModal && selectedPost"
      :is-open="showModal"
      :post="selectedPost"
      :comments="comments[selectedPost.id] || []"
      :current-index="currentPostIndex"
      :total-posts="filteredPosts.length"
      :user-profile-picture="currentUser?.profile_picture"
      :categories="categories"
      :selected-reaction="selectedReaction[selectedPost.id]"
      :current-user-id="currentUser?.id"
      @close="closePostModal"
      @react-to-post="reactToPost"
      @add-comment="addComment"
      @share-post="sharePost"
      @copy-link="copyPostLink"
      @load-comments="fetchCommentsForPost"
      @navigate="navigateToPost"
      @reaction-updated="handleReactionUpdated"
    />

    <!-- Notifications (Single Instance) -->
    <div v-if="notifications.length > 0" class="fixed z-50 space-y-2 top-20 right-4">
      <NotificationToast
        v-for="notif in notifications"
        :key="notif.id"
        :notification="notif"
        @dismiss="dismissNotification"
      />
    </div>
  </div>
</template>
