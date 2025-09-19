<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick, provide } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import axios from 'axios';

// Import dedicated CSS file
import '@/components/css/AlumniHome.css';

// Import posting components
import PostCreateForm from '@/components/posting/PostCreateForm.vue';
import CategoryTabs from '@/components/posting/CategoryTabs.vue';
import PostCard from '@/components/posting/PostCard.vue';
import PostModal from '@/components/posting/PostModal.vue';
import NotificationToast from '@/components/posting/NotificationToast.vue';

// Import alumni components
import ProfileCard from '@/components/alumni/ProfileCard.vue';
import SuggestedConnectionsWidget from '@/components/profile/SuggestedConnectionsWidget.vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

// State
const posts = ref([]);
const searchQuery = ref('');
const activeTab = ref('all');
const selectedCategory = ref('all');
const selectedReaction = ref({});
const comments = ref({});
const showComments = ref({});
const notifications = ref([]);
const notification = ref(null);
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

// WebSocket connection
let postsSocket = null;

// Constants
const BASE_URL = 'http://127.0.0.1:8000';
const categories = [
  { value: 'all', label: 'All Posts', icon: '📋' },
  { value: 'discussion', label: 'Discussion', icon: '💬' },
  { value: 'announcement', label: 'Announcement', icon: '📢' },
  { value: 'event', label: 'Event', icon: '📅' },
  { value: 'news', label: 'News', icon: '📰' },
  { value: 'job', label: 'Job Posting', icon: '💼' },
  { value: 'others', label: 'Others', icon: '📝' }
];

const reactionTypes = [
  { type: 'like', emoji: '👍', label: 'Like' },
  { type: 'love', emoji: '❤️', label: 'Love' },
  { type: 'laugh', emoji: '😂', label: 'Laugh' },
  { type: 'wow', emoji: '😮', label: 'Wow' },
  { type: 'sad', emoji: '😢', label: 'Sad' },
  { type: 'angry', emoji: '😠', label: 'Angry' }
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
  
  const wsUrl = `ws://127.0.0.1:8000/ws/posts/feed/?token=${token}`;
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
      const currentReaction = selectedReaction.value[post.id];
      const serverReaction = post.reactions_summary?.user_reaction;
      
      // Only update if we don't have a recent user interaction
      if (currentReaction === undefined || currentReaction === null || currentReaction === serverReaction) {
        if (serverReaction) {
          selectedReaction.value[post.id] = serverReaction;
          console.log(`🎯 Initialized reaction for post ${post.id}: ${serverReaction}`);
        } else {
          selectedReaction.value[post.id] = null;
          console.log(`🧹 Cleared reaction state for post ${post.id}`);
        }
      } else {
        console.log(`⏭️ Preserving user reaction state for post ${post.id}: ${currentReaction} (server has: ${serverReaction})`);
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
    
    // Add files if any (backend expects 'media_files')
    if (postData.files && postData.files.length > 0) {
      postData.files.forEach((file, index) => {
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
      
      try {
        const response = await axios.delete(`${BASE_URL}/api/posts/posts/${postId}/react/`, {
          headers: { Authorization: `Bearer ${authStore.token}` }
        });
        
        console.log('✅ Reaction removed:', response.data);
        selectedReaction.value[postId] = null;
        console.log(`🎯 Frontend state updated: post ${postId} reaction cleared`);
        
      } catch (deleteError) {
        // Handle 404 - reaction doesn't exist in database but frontend thinks it does
        if (deleteError.response?.status === 404) {
          console.warn(`⚠️ Reaction ${reactionType} on post ${postId} not found in database - fixing frontend state`);
          
          // Reset frontend state to match database reality
          selectedReaction.value[postId] = null;
          
          showNotification('Reaction state synchronized', 'success');
        } else {
          throw deleteError; // Re-throw other errors
        }
      }
      
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
    
    // Don't call fetchPosts() here - let WebSocket handle updates
    console.log('🎯 Reaction updated, waiting for WebSocket confirmation');
    
  } catch (error) {
    console.error('❌ Failed to react to post:', error);
    
    // Enhanced error handling
    if (error.response?.status === 404 && error.config?.method === 'delete') {
      // This case is already handled above, but just in case
      selectedReaction.value[postId] = null;
      showNotification('Reaction state fixed', 'success');
    } else {
      showNotification('Failed to add reaction. Please try again.', 'error');
    }
  }
};

const addComment = async (postId, commentContent, parentId = null) => {
  try {
    console.log(`💬 Adding comment to post ${postId}:`, commentContent);
    
    const response = await axios.post(`${BASE_URL}/api/posts/posts/${postId}/comment/`, {
      content: commentContent,
      parent_id: parentId
    }, {
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
    console.log(`📡 WebSocket reaction update for post ${data.post_id}: ${data.action} ${data.reaction_type}`);
    
    // Only update selectedReaction if this is the current user's reaction
    if (data.user_id === authStore.user?.id) {
      if (data.action === 'removed') {
        selectedReaction.value[data.post_id] = null;
        console.log(`🧹 WebSocket: Cleared reaction state for post ${data.post_id}`);
      } else {
        selectedReaction.value[data.post_id] = data.reaction_type;
        console.log(`🎯 WebSocket: Set reaction for post ${data.post_id} to ${data.reaction_type}`);
      }
    }
    
    // Update reaction counts without full refresh to avoid race conditions
    const post = posts.value[postIndex];
    if (post && post.reactions_summary) {
      // Just update the count, don't override selectedReaction
      if (data.action === 'removed') {
        post.reactions_summary.total_count = Math.max(0, post.reactions_summary.total_count - 1);
      } else if (data.action === 'added') {
        post.reactions_summary.total_count = (post.reactions_summary.total_count || 0) + 1;
      }
      console.log(`📊 Updated reaction count for post ${data.post_id}: ${post.reactions_summary.total_count}`);
    }
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
  <div class="alumni-home-container min-h-screen bg-amber-50">
    <!-- Responsive Grid Layout -->
    <div class="alumni-home-grid">
      <!-- Left Sidebar: Profile Card -->
      <aside class="alumni-sidebar alumni-sidebar-left">
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
            <div class="bg-white rounded-lg sm:rounded-xl border border-gray-200 shadow-sm overflow-hidden">
              <div class="grid grid-cols-7 border-b border-gray-100">
                <button
                  v-for="category in categories"
                  :key="category.value"
                  @click="selectedCategory = category.value; activeTab = category.value"
                  :class="[
                    'flex items-center justify-center px-2 py-3 text-xs sm:text-sm font-medium transition-colors border-b-2 text-center',
                    selectedCategory === category.value
                      ? 'text-blue-600 border-blue-600 bg-blue-50'
                      : 'text-gray-600 border-transparent hover:text-blue-600 hover:bg-blue-50'
                  ]"
                >
                  <span class="truncate">{{ category.label }}</span>
                </button>
              </div>
            </div>

            <!-- Mobile Post Create Modal -->
            <div
              v-if="showCreateForm"
              class="md:hidden fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
              @click.self="showCreateForm = false"
            >
              <div class="bg-white rounded-xl w-full max-w-md max-h-[80vh] overflow-y-auto" @click.stop>
                <div class="p-4 border-b border-gray-200 flex items-center justify-between">
                  <h2 class="text-lg font-semibold">Create Post</h2>
                  <button 
                    @click.stop="showCreateForm = false" 
                    class="p-2 hover:bg-gray-100 rounded-full transition-colors duration-200 flex items-center justify-center"
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

            <!-- Desktop Post Create -->
            <div class="hidden md:block">
              <PostCreateForm
                :user-profile-picture="currentUser?.profile_picture"
                :categories="categories"
                :is-posting="isPosting"
                @create-post="handleCreatePost"
                ref="postCreateForm"
              />
            </div>

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
                <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Loading posts...</span>
              </div>
            </div>

            <!-- Empty State -->
            <div v-if="filteredPosts.length === 0 && !isLoading" class="text-center py-12">
              <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-8">
                <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                </svg>
                <h3 class="text-lg font-semibold text-gray-800 mb-2">No Posts Yet</h3>
                <p class="text-sm text-gray-600 mb-4">
                  {{ searchQuery ? 'Try different search terms' : 'Be the first to share something!' }}
                </p>
                <button
                  v-if="!searchQuery"
                  @click="showCreateForm = true"
                  class="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-medium text-sm rounded-lg hover:bg-blue-700 transition-colors"
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
      <aside class="alumni-sidebar alumni-sidebar-right">
        <div class="sidebar-content">
          <SuggestedConnectionsWidget @connect="handleConnect" />
        </div>
      </aside>
    </div>

    <!-- Mobile Layout: Stacked for mobile/tablet -->
    <div class="alumni-mobile-layout">
      <div class="mobile-content-wrapper">
        <!-- Mobile Profile Section -->
        <div class="space-y-4">
          <ProfileCard
            @edit-profile="editProfile"
            @view-profile="viewProfile"
          />
        </div>

        <!-- Mobile Main Content -->
        <div class="space-y-4 mt-6">
          <!-- Category Tabs -->
          <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
            <div class="grid grid-cols-4 sm:grid-cols-7 border-b border-gray-100">
              <button
                v-for="category in categories"
                :key="category.value"
                @click="selectedCategory = category.value; activeTab = category.value"
                :class="[
                  'flex items-center justify-center px-1 py-3 text-xs font-medium transition-colors border-b-2 text-center',
                  selectedCategory === category.value
                    ? 'text-blue-600 border-blue-600 bg-blue-50'
                    : 'text-gray-600 border-transparent hover:text-blue-600 hover:bg-blue-50'
                ]"
              >
                <span class="truncate">{{ category.label }}</span>
              </button>
            </div>
          </div>

          <!-- Create Post Button -->
          <div class="bg-white border border-gray-200 rounded-lg p-4">
            <button
              @click="showCreateForm = true"
              class="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-3 rounded-lg text-left transition-colors flex items-center space-x-3"
            >
              <img 
                :src="currentUser?.profile_picture || '/default-avatar.png'" 
                :alt="currentUser?.full_name || 'User'" 
                class="w-8 h-8 rounded-full object-cover"
              >
              <span class="text-gray-500">What's on your mind?</span>
            </button>
          </div>

          <!-- Posts Feed -->
          <div class="space-y-4">
            <div v-if="isLoading" class="flex justify-center py-8">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
            
            <div v-else-if="filteredPosts.length === 0" class="text-center py-8 text-gray-500">
              <p>No posts to show yet.</p>
              <p class="text-sm mt-2">Be the first to share something!</p>
            </div>
            
            <template v-else>
              <PostCard
                v-for="post in filteredPosts"
                :key="post.id"
                :post="post"
                :current-user-id="currentUser?.id"
                :categories="categories"
                :selected-reaction="selectedReaction[post.id]"
                @react="(reactionType) => reactToPost(post.id, reactionType)"
                @comment="() => { fetchCommentsForPost(post.id); showComments[post.id] = !showComments[post.id]; }"
                @share="sharePost"
                @copy-link="copyPostLink"
                @open-modal="openPostModal"
                @reaction-updated="handleReactionUpdated"
              />
            </template>
          </div>
        </div>

        <!-- Mobile Suggested Connections -->
        <div class="mt-6">
          <SuggestedConnectionsWidget @connect="handleConnect" />
        </div>
      </div>
    </div>

    <!-- Search Modal for Mobile -->
    <div v-if="showMobileSearch" class="fixed inset-0 bg-black/50 z-50 flex items-start pt-20">
      <div class="bg-white w-full mx-4 rounded-lg shadow-lg">
        <div class="p-4">
          <div class="relative">
            <input 
              v-model="searchQuery"
              type="text"
              placeholder="Search alumni, posts..."
              class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ref="mobileSearchInput"
            >
            <svg class="absolute left-3 top-3.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Notifications -->
    <div v-if="notification" class="fixed top-20 right-4 z-50 max-w-sm">
      <div
        :class="[
          'p-4 rounded-lg shadow-lg border-l-4',
          notification.type === 'success' ? 'bg-green-50 border-green-400 text-green-800' :
          notification.type === 'error' ? 'bg-red-50 border-red-400 text-red-800' :
          'bg-blue-50 border-blue-400 text-blue-800'
        ]"
      >
        <div class="flex items-center">
          <span class="flex-1">{{ notification.message }}</span>
          <button @click="notification = null" class="ml-2 text-gray-400 hover:text-gray-600">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Post Modal -->
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

    <!-- Post Modal -->
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

    <!-- Notifications -->
    <div v-if="notifications.length > 0" class="fixed top-20 right-4 z-50 space-y-2">
      <NotificationToast
        v-for="notif in notifications"
        :key="notif.id"
        :notification="notif"
        @dismiss="dismissNotification"
      />
    </div>
  </div>
</template>
