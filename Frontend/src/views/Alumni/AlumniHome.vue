<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import axios from 'axios';

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
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-7xl mx-auto px-2 sm:px-4 lg:px-8">
        <div class="flex items-center justify-between h-14 md:h-16">
          <!-- Left section -->
          <div class="flex items-center space-x-2 sm:space-x-4 flex-1">
            <h1 class="text-base sm:text-lg md:text-xl font-bold text-gray-900">Home</h1>
          </div>
          
          <!-- Search (desktop only) -->
          <div class="hidden md:flex flex-1 max-w-md mx-8">
            <div class="relative w-full">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search alumni, posts..."
                class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
              <svg class="absolute left-3 top-2.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
          
          <!-- Right section -->
          <div class="flex items-center space-x-1 sm:space-x-3 flex-1 justify-end">
            <button
              @click="showMobileSearch = !showMobileSearch"
              class="md:hidden p-1.5 sm:p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
            <button
              @click="showCreateForm = !showCreateForm"
              class="md:hidden p-1.5 sm:p-2 text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
            >
              <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </button>
            
            <!-- Notifications -->
            <button class="p-1.5 sm:p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
              <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5-5-5 5h5zm0 0v5" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="relative min-h-screen">
      <!-- Left Sidebar: Profile Card (Fixed) -->
      <aside class="hidden lg:block fixed left-32 top-36 w-96 h-[calc(100vh-10rem)] overflow-y-auto z-10">
        <div class="p-4">
          <ProfileCard
            @edit-profile="editProfile"
            @view-profile="viewProfile"
          />
        </div>
      </aside>

      <!-- Center Column: Main Feed (Scrollable) - Desktop Only -->
      <main class="hidden lg:block lg:ml-[28rem] lg:mr-[26rem]">
        <div class="max-w-3xl mx-auto px-4 sm:px-6 py-4 md:py-6">
          <div class="space-y-4 md:space-y-6">
            <!-- Category Tabs -->
            <div class="bg-white rounded-lg sm:rounded-xl border border-gray-200 shadow-sm overflow-hidden">
              <div class="flex overflow-x-auto scrollbar-hide border-b border-gray-100">
                <button
                  v-for="category in categories"
                  :key="category.value"
                  @click="selectedCategory = category.value; activeTab = category.value"
                  :class="[
                    'flex items-center space-x-2 px-3 md:px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors border-b-2 flex-shrink-0',
                    selectedCategory === category.value
                      ? 'text-blue-600 border-blue-600 bg-blue-50'
                      : 'text-gray-600 border-transparent hover:text-blue-600 hover:bg-blue-50'
                  ]"
                >
                  <span>{{ category.label }}</span>
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

      <!-- Right Sidebar: Suggested Connections (Fixed) -->
      <aside class="hidden lg:block fixed right-6 top-36 w-96 h-[calc(100vh-10rem)] overflow-y-auto z-10">
        <div class="p-4">
          <SuggestedConnectionsWidget @connect="handleConnect" />
        </div>
      </aside>

      <!-- Mobile Layout: Stacked for mobile/tablet -->
      <div class="lg:hidden">
        <div class="max-w-full mx-auto px-2 sm:px-4 py-4 md:py-6 space-y-4 md:space-y-6">
          <!-- Category Tabs -->
          <div class="bg-white rounded-lg sm:rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            <div class="flex overflow-x-auto scrollbar-hide border-b border-gray-100">
              <button
                v-for="category in categories"
                :key="category.value"
                @click="selectedCategory = category.value; activeTab = category.value"
                :class="[
                  'flex items-center space-x-2 px-3 md:px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors border-b-2 flex-shrink-0',
                  selectedCategory === category.value
                    ? 'text-blue-600 border-blue-600 bg-blue-50'
                    : 'text-gray-600 border-transparent hover:text-blue-600 hover:bg-blue-50'
                ]"
              >
                <span>{{ category.label }}</span>
              </button>
            </div>
          </div>

          <!-- Suggested Connections Widget - Mobile -->
          <div class="block">
            <SuggestedConnectionsWidget @connect="handleConnect" />
          </div>

          <!-- Desktop Post Create (hidden on mobile, shown on tablet) -->
          <div class="hidden md:block lg:hidden">
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
        </div>
      </div>
    </div>

    <!-- Mobile Search Modal -->
    <div v-if="showMobileSearch" class="md:hidden fixed inset-0 bg-black/50 z-50" @click="showMobileSearch = false">
      <div class="bg-white m-4 rounded-xl p-4" @click.stop>
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
  </div>
</template>

<style scoped>
/* Hide scrollbar for category tabs */
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

/* Custom scrollbar for sidebar */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Smooth transitions */
.transition-colors {
  transition: all 0.2s ease;
}

/* Mobile optimizations */
@media (max-width: 1024px) {
  .lg\:flex-row {
    flex-direction: column;
  }
  
  .lg\:max-w-2xl {
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  /* Compact spacing on mobile */
  .space-y-4 > :not([hidden]) ~ :not([hidden]) {
    margin-top: 0.75rem;
  }
  
  .space-y-2 > :not([hidden]) ~ :not([hidden]) {
    margin-top: 0.5rem;
  }
  
  /* Ensure full width usage on mobile */
  .max-w-7xl {
    max-width: 100%;
  }
  
  /* Mobile container adjustments */
  .px-2 {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
  }
  
  .py-2 {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
  
  /* Touch-friendly buttons */
  button {
    min-height: 40px;
    min-width: 40px;
  }
  
  /* Compact text */
  .text-lg {
    font-size: 1rem;
    line-height: 1.5rem;
  }
  
  .text-xl {
    font-size: 1.125rem;
    line-height: 1.75rem;
  }
  
  /* Main feed adjustments for mobile */
  main {
    width: 100% !important;
    max-width: 100% !important;
  }
  
  /* Category tabs mobile optimization */
  .flex.overflow-x-auto button {
    min-width: auto;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
  }
  
  /* Hide category labels on very small screens, show only icons */
  @media (max-width: 480px) {
    .hidden.sm\\:inline {
      display: none !important;
    }
    
    .space-x-1 {
      gap: 0.25rem;
    }
  }
  
  /* Modal adjustments */
  .fixed.inset-0 .max-w-md {
    max-width: calc(100vw - 2rem);
    margin: 1rem;
  }
}

/* Ensure proper stacking */
.sticky {
  position: -webkit-sticky;
  position: sticky;
}

/* Prevent horizontal overflow */
* {
  box-sizing: border-box;
}

.min-h-screen {
  min-height: 100vh;
  overflow-x: hidden;
}

/* Post card hover effects */
@media (hover: hover) {
  .hover\:bg-gray-50:hover {
    background-color: #f9fafb;
  }
  
  .hover\:bg-gray-200:hover {
    background-color: #e5e7eb;
  }
}

/* Loading states */
.loading {
  opacity: 0.7;
  pointer-events: none;
}

/* Compact create post button */
.bg-gray-100 {
  background-color: #f3f4f6;
}

.bg-gray-100:hover {
  background-color: #e5e7eb;
}

/* Sidebar styles - Updated widths for better layout */
.lg\:w-80 {
  width: 20rem;
  max-width: 20rem;
}

.lg\:w-64 {
  width: 16rem;
  max-width: 16rem;
}

.lg\:max-w-xl {
  max-width: 36rem;
}

/* Legacy width classes */
.lg\:w-72 {
  width: 18rem;
  max-width: 18rem;
}

.w-80 {
  width: 20rem;
  max-width: 20rem;
}

/* Animation for modal */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.fixed.inset-0.bg-black\/50 > div {
  animation: fadeIn 0.2s ease-out;
}
</style>
