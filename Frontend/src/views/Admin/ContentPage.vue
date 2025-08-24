<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import axios from 'axios';

// Import posting components
import PostCreateForm from '@/components/posting/PostCreateForm.vue';
import CategoryTabs from '@/components/posting/CategoryTabs.vue';
import PostCard from '@/components/posting/PostCard.vue';
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
    console.log('Connected to posts WebSocket');
  };
  
  postsSocket.onmessage = (event) => {
    const data = JSON.parse(event.data);
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
  } catch (error) {
    console.error('❌ Failed to fetch posts:', error);
    console.error('Response:', error.response?.data);
    showNotification('Failed to load posts. Please try again.', 'error');
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
    await axios.post(`${BASE_URL}/api/posts/posts/${postId}/comment/`, {
      content: content
    }, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });
    
    // Comments will be updated via WebSocket
    
  } catch (error) {
    console.error('Failed to add comment:', error);
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
  // Add new comment to the comments list
  if (!comments.value[data.post_id]) {
    comments.value[data.post_id] = [];
  }
  comments.value[data.post_id].push({
    id: data.comment_id,
    user: { id: data.user_id, name: data.user_name },
    content: data.content,
    created_at: data.timestamp
  });
};

const dismissNotification = (id) => {
  notifications.value = notifications.value.filter(n => n.id !== id);
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
          :comments="comments[post.id] || []"
          :user-profile-picture="authStore.user.profile_picture"
          @react-to-post="reactToPost"
          @add-comment="addComment"
          @share-post="sharePost"
          @copy-link="copyPostLink"
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