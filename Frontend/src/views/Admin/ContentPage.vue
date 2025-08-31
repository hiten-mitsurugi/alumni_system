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

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

// State
const posts = ref([]);
const searchQuery = ref('');
const activeTab = ref('all');
const selectedReaction = ref({});
const comments = ref({});
const showComments = ref({});
const notifications = ref([]);

// Modal state
const showModal = ref(false);
const selectedPost = ref(null);
const currentPostIndex = ref(0);

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
    case 'post_pending_approval':
      if (authStore.user.user_type <= 2) { // Admin or SuperAdmin
        notifications.value.unshift({
          id: Date.now(),
          type: 'approval',
          message: data.message,
          timestamp: new Date().toISOString()
        });
      }
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
    console.log('📝 Creating new post...');
    const formData = new FormData();
    formData.append('content', postData.content);
    if (postData.title?.trim()) {
      formData.append('title', postData.title);
    }
    formData.append('content_category', postData.category);
    formData.append('visibility', 'public');
    
    // Add files if any
    postData.files.forEach((file, index) => {
      formData.append(`media_files`, file);
      console.log(`📎 Adding file ${index + 1}:`, file.name, file.size);
    });
    
    console.log('🚀 Sending post data...');
    const response = await axios.post(`${BASE_URL}/api/posts/posts/create/`, formData, {
      headers: { 
        Authorization: `Bearer ${authStore.token}`,
        'Content-Type': 'multipart/form-data'
      }
    });
    
    console.log('✅ Post created successfully:', response.data);
    
    // Add to posts list at the top
    posts.value.unshift(response.data);
    
    // Show success notification
    addNotification('Post created successfully!', 'success');
    
    // Refresh posts to get the latest data
    setTimeout(() => fetchPosts(), 500);
    
  } catch (error) {
    console.error('❌ Failed to create post:', error);
    console.error('Response:', error.response?.data);
    addNotification(`Failed to create post: ${error.response?.data?.detail || error.message}`, 'error');
  }
};

const reactToPost = async (postId, reactionType) => {
  try {
    const currentReaction = selectedReaction.value[postId];
    
    if (currentReaction === reactionType) {
      // Remove reaction
      await axios.delete(`${BASE_URL}/api/posts/posts/${postId}/react/`, {
        headers: { Authorization: `Bearer ${authStore.token}` }
      });
      selectedReaction.value[postId] = null;
    } else {
      // Add or update reaction
      await axios.post(`${BASE_URL}/api/posts/posts/${postId}/react/`, {
        reaction_type: reactionType
      }, {
        headers: { Authorization: `Bearer ${authStore.token}` }
      });
      selectedReaction.value[postId] = reactionType;
    }
    
    // Update post reaction count locally (will be updated via WebSocket too)
    const post = posts.value.find(p => p.id === postId);
    if (post) {
      // This will be properly updated when we get the WebSocket message
      await fetchPosts();
    }
    
  } catch (error) {
    console.error('Failed to react to post:', error);
  }
};

const addComment = async (postId, content) => {
  try {
    console.log('🔄 Adding comment via API...', { postId, content });
    const response = await axios.post(`${BASE_URL}/api/posts/posts/${postId}/comment/`, {
      content: content
    }, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });
    
    console.log('✅ Comment added successfully:', response.data);
    console.log('⏳ Waiting for WebSocket real-time update...');
    
    // Don't manually fetch comments - rely on WebSocket for real-time updates
    // The backend should broadcast a 'new_comment' WebSocket message that will
    // trigger addNewComment() function for real-time updates
    
  } catch (error) {
    console.error('❌ Failed to add comment:', error);
    
    // Show error notification
    notifications.value.unshift({
      id: Date.now(),
      type: 'error',
      message: 'Failed to add comment. Please try again.',
      timestamp: new Date().toISOString()
    });
  }
};

// Add function to fetch comments for a specific post
const fetchCommentsForPost = async (postId) => {
  try {
    console.log(`Fetching all comments for post ${postId}`);
    const response = await axios.get(`${BASE_URL}/api/posts/posts/${postId}/comments/`, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });
    
    if (response.data.comments) {
      comments.value[postId] = response.data.comments;
      console.log(`Loaded ${response.data.comments.length} comments for post ${postId}`);
      
      // Update the post's comment count to match actual comments
      const post = posts.value.find(p => p.id === postId);
      if (post) {
        post.comments_count = response.data.comments.length;
        console.log(`📊 Synchronized post comment count to: ${response.data.comments.length}`);
      }
    }
  } catch (error) {
    console.error('Failed to fetch comments for post:', error);
  }
};

const sharePost = async (postId) => {
  const shareText = prompt('Add a message to your share (optional):');
  if (shareText === null) return; // User cancelled
  
  try {
    await axios.post(`${BASE_URL}/api/posts/posts/${postId}/share/`, {
      shared_text: shareText
    }, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });
    
    notifications.value.unshift({
      id: Date.now(),
      type: 'success',
      message: 'Post shared successfully!',
      timestamp: new Date().toISOString()
    });
    
    // Refresh posts to show the shared post
    await fetchPosts();
    
  } catch (error) {
    console.error('Failed to share post:', error);
  }
};

const copyPostLink = (postId) => {
  const postUrl = `${window.location.origin}/admin/posts/${postId}`;
  navigator.clipboard.writeText(postUrl).then(() => {
    addNotification('Post link copied to clipboard!', 'success');
  });
};

// Utility Functions
const addNotification = (message, type = 'info') => {
  notifications.value.unshift({
    id: Date.now(),
    type: type,
    message: message,
    timestamp: new Date().toISOString()
  });
};

// Utility Functions
const formatTimeAgo = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now - date) / 1000);
  
  if (diffInSeconds < 60) return 'Just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
  
  return date.toLocaleDateString();
};

const handleFileSelect = (event) => {
  // This method is now handled by PostCreateForm component
};

const removeFile = (index) => {
  // This method is now handled by PostCreateForm component
};

const formatFileSize = (bytes) => {
  // This method is now handled by PostCreateForm component
};

const clearAllFiles = () => {
  // This method is now handled by PostCreateForm component
};

const handleImageError = (event) => {
  console.error('Image failed to load:', event.target.src);
  event.target.src = '/default-avatar.png'; // Fallback image
  event.target.alt = 'Image not available';
};

const toggleComments = (postId) => {
  showComments.value[postId] = !showComments.value[postId];
};

const updatePostReaction = (data) => {
  const post = posts.value.find(p => p.id === data.post_id);
  if (post) {
    // Update reaction counts based on WebSocket data
    fetchPosts(); // Simplified - in production you'd update locally
  }
};

const addNewComment = (data) => {
  console.log('📝 Processing new comment via WebSocket:', data);
  
  // Add new comment to the comments list
  if (!comments.value[data.post_id]) {
    comments.value[data.post_id] = [];
    console.log('📝 Created new comments array for post:', data.post_id);
  }
  
  // Check if comment already exists to prevent duplicates
  const existingComment = comments.value[data.post_id].find(c => c.id === data.comment_id);
  if (existingComment) {
    console.log('⚠️ Comment already exists, skipping duplicate:', data.comment_id);
    return;
  }
  
  // Create comment object matching the backend structure
  const newComment = {
    id: data.comment_id,
    user: { 
      id: data.user_id, 
      first_name: data.user_name.split(' ')[0] || data.user_name,
      last_name: data.user_name.split(' ').slice(1).join(' ') || '',
      full_name: data.user_name,
      profile_picture: null // We don't have this in WebSocket data
    },
    content: data.content,
    parent: data.parent_id,
    likes_count: 0,
    replies_count: 0,
    created_at: data.timestamp,
    updated_at: data.timestamp,
    edited_at: null,
    is_edited: false,
    time_since: 'Just now',
    replies: [],
    reactions_summary: null,
    can_edit: data.user_id === authStore.user.id,
    can_delete: data.user_id === authStore.user.id || authStore.user.user_type <= 2
  };
  
  comments.value[data.post_id].push(newComment);
  console.log('✅ Comment added to local state. Total comments for post', data.post_id + ':', comments.value[data.post_id].length);
  
  // Update the post's comment count to match actual comments array length
  const post = posts.value.find(p => p.id === data.post_id);
  if (post) {
    post.comments_count = comments.value[data.post_id].length;
    console.log('📊 Updated post comment count to match actual comments:', post.comments_count);
  }
  
  console.log('✅ Real-time comment update completed');
};

const dismissNotification = (id) => {
  notifications.value = notifications.value.filter(n => n.id !== id);
};

// Modal Functions
const openPostModal = (post) => {
  console.log('🔍 Opening modal for post:', post)
  selectedPost.value = post;
  currentPostIndex.value = filteredPosts.value.findIndex(p => p.id === post.id);
  showModal.value = true;
  
  // Subscribe to real-time updates for this specific post
  if (postsSocket && postsSocket.readyState === WebSocket.OPEN) {
    console.log('📡 Subscribing to real-time updates for post:', post.id);
    postsSocket.send(JSON.stringify({
      type: 'join_post',
      post_id: post.id
    }));
  }
  
  // Automatically load comments if not already loaded
  if (!comments.value[post.id] || comments.value[post.id].length === 0) {
    fetchCommentsForPost(post.id);
  }
  
  console.log('✅ Modal state:', { showModal: showModal.value, selectedPost: selectedPost.value?.id, currentIndex: currentPostIndex.value })
};

const closePostModal = () => {
  console.log('🔙 Closing modal for post:', selectedPost.value?.id);
  
  // Unsubscribe from real-time updates for this specific post
  if (postsSocket && postsSocket.readyState === WebSocket.OPEN && selectedPost.value) {
    console.log('📡 Unsubscribing from real-time updates for post:', selectedPost.value.id);
    postsSocket.send(JSON.stringify({
      type: 'leave_post',
      post_id: selectedPost.value.id
    }));
  }
  
  showModal.value = false;
  selectedPost.value = null;
  currentPostIndex.value = 0;
};

const navigateToPost = (direction) => {
  const newIndex = direction === 'prev' 
    ? Math.max(0, currentPostIndex.value - 1)
    : Math.min(filteredPosts.value.length - 1, currentPostIndex.value + 1);
  
  currentPostIndex.value = newIndex;
  selectedPost.value = filteredPosts.value[newIndex];
};

// Lifecycle
onMounted(() => {
  fetchPosts();
  connectWebSocket();
});

onUnmounted(() => {
  if (postsSocket) {
    postsSocket.close();
  }
});
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
    <!-- Header -->
    <div class="bg-white shadow-lg border-b-2 border-blue-100 sticky top-0 z-10">
      <div class="max-w-6xl mx-auto px-6 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-4xl font-bold text-slate-800 mb-2">Alumni Community Hub</h1>
            <p class="text-lg text-slate-600 font-medium">Connect, Share, and Stay Updated with Your Alumni Network</p>
          </div>
          
          <!-- Search -->
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search posts, announcements, events..."
              class="pl-16 pr-6 py-4 w-80 text-lg border-2 border-slate-300 rounded-2xl focus:ring-4 focus:ring-blue-300 focus:border-blue-500 shadow-lg"
            />
            <svg class="absolute left-5 top-1/2 transform -translate-y-1/2 w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
        
        <!-- Category Tabs -->
        <CategoryTabs 
          :categories="categories"
          :active-tab="activeTab"
          @category-change="activeTab = $event"
        />
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-6xl mx-auto px-6 py-8">
      <!-- Create Post Section -->
      <PostCreateForm 
        :user-profile-picture="authStore.user.profile_picture"
        :categories="categories"
        @create-post="createPost"
      />

      <!-- Posts Feed -->
      <div class="space-y-8">
        <PostCard
          v-for="post in filteredPosts"
          :key="post.id"
          :post="post"
          :categories="categories"
          :selected-reaction="selectedReaction[post.id]"
          :comments="comments[post.id] || post.recent_comments || []"
          :user-profile-picture="authStore.user.profile_picture"
          @react-to-post="reactToPost"
          @add-comment="addComment"
          @share-post="sharePost"
          @copy-link="copyPostLink"
          @open-modal="openPostModal"
        />
      </div>
      
      <!-- Empty State -->
      <div v-if="filteredPosts.length === 0" class="text-center py-20">
        <div class="bg-white rounded-3xl shadow-xl border-2 border-slate-100 p-12 max-w-lg mx-auto">
          <svg class="mx-auto h-20 w-20 text-slate-400 mb-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
          </svg>
          <h3 class="text-2xl font-bold text-slate-800 mb-3">No Posts Found</h3>
          <p class="text-lg text-slate-600 leading-relaxed">
            {{ searchQuery ? 'Try adjusting your search terms or exploring different categories.' : 'Share the first post with your alumni community and get the conversation started!' }}
          </p>
          <div v-if="!searchQuery" class="mt-6">
            <button
              class="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-bold text-lg rounded-2xl hover:from-blue-700 hover:to-blue-800 transition-all duration-300 shadow-lg transform hover:scale-105"
            >
              <svg class="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
              Create Your First Post
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Notifications -->
    <NotificationToast 
      :notifications="notifications"
      @dismiss="dismissNotification"
    />

    <!-- Post Modal -->
    <PostModal
      v-if="showModal && selectedPost"
      :is-open="showModal"
      :post="selectedPost"
      :comments="comments[selectedPost.id] || []"
      :current-index="currentPostIndex"
      :total-posts="filteredPosts.length"
      :user-profile-picture="authStore.user.profile_picture"
      :categories="categories"
      :selected-reaction="selectedReaction[selectedPost.id]"
      @close="closePostModal"
      @react-to-post="reactToPost"
      @add-comment="addComment"
      @share-post="sharePost"
      @copy-link="copyPostLink"
      @load-comments="fetchCommentsForPost"
      @navigate="navigateToPost"
    />
  </div>
</template>

<style scoped>
/* Custom scrollbar for category tabs */
.overflow-x-auto::-webkit-scrollbar {
  height: 6px;
}

.overflow-x-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Smooth transitions for all interactive elements */
.transition-all {
  transition: all 0.3s ease;
}

/* Enhanced hover effects */
button:hover:not(:disabled) {
  transform: translateY(-1px);
}

/* Focus states for accessibility */
input:focus, textarea:focus, select:focus, button:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Animation for notifications */
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.fixed.top-6.right-6 > div {
  animation: slideInRight 0.3s ease-out;
}

/* Reaction picker enhanced styling */
.group:hover .group-hover\:opacity-100 {
  opacity: 1;
  transform: translateY(-5px);
}

/* Enhanced card shadows */
.shadow-xl {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.shadow-2xl {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

/* Gradient text for enhanced visual appeal */
.bg-gradient-to-r {
  background-image: linear-gradient(to right, var(--tw-gradient-stops));
}

/* Enhanced spacing for better readability */
.leading-relaxed {
  line-height: 1.75;
}

/* Reaction picker positioning */
.group:hover .group-hover\:opacity-100 {
  opacity: 1;
}
</style>