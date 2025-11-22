<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useThemeStore } from '@/stores/theme';
import axios from 'axios';

// Import posting components
import PostCreateForm from '@/components/posting/PostCreateForm.vue';
import PostCard from '@/components/posting/PostCard.vue';
import PostModal from '@/components/posting/PostModal.vue';
import NotificationToast from '@/components/posting/NotificationToast.vue';

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
const isLoading = ref(false);

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
    case 'post_deleted':
      console.log('🗑️ Received post_deleted WebSocket message:', data);
      handlePostDeleted(data);
      break;
  }
};

// API Functions
const fetchPosts = async () => {
  try {
    isLoading.value = true;
    console.log('🔄 Fetching posts from API...');
    const response = await axios.get(`${BASE_URL}/api/posts/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
      params: {
        category: activeTab.value !== 'all' ? activeTab.value : null,
        search: searchQuery.value || null
      }
    });
    
    console.log('✅ Posts loaded successfully');
    
    // Handle both paginated and direct array responses
    if (Array.isArray(response.data)) {
      posts.value = response.data;
    } else if (response.data.results && Array.isArray(response.data.results)) {
      posts.value = response.data.results;
    } else {
      console.error('❌ Unexpected response format:', response.data);
      posts.value = [];
    }
    
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
    addNotification('Failed to load posts. Please try again.', 'error');
  } finally {
    isLoading.value = false;
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
    const response = await axios.post(`${BASE_URL}/api/posts/create/`, formData, {
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
    console.log('🔄 ReactToPost called with:', { postId, reactionType });
    const currentReaction = selectedReaction.value[postId];
    console.log('🔄 Current reaction:', currentReaction);
    
    if (currentReaction === reactionType) {
      // Remove reaction
      console.log('🗑️ Removing reaction...');
      await axios.delete(`${BASE_URL}/api/posts/${postId}/react/`, {
        headers: { Authorization: `Bearer ${authStore.token}` }
      });
      selectedReaction.value[postId] = null;
    } else {
      // Add or update reaction
      console.log('➕ Adding/updating reaction...', { reaction_type: reactionType });
      const requestData = { reaction_type: reactionType };
      console.log('📤 Sending request data:', requestData);
      
      await axios.post(`${BASE_URL}/api/posts/${postId}/react/`, requestData, {
        headers: { Authorization: `Bearer ${authStore.token}` }
      });
      selectedReaction.value[postId] = reactionType;
    }
    
    // Update post reaction count locally and wait for WebSocket update
    const post = posts.value.find(p => p.id === postId);
    if (post) {
      // Fetch fresh post data to ensure reactions_summary is updated
      try {
        const response = await axios.get(`${BASE_URL}/api/posts/${postId}/`, {
          headers: { Authorization: `Bearer ${authStore.token}` }
        });
        
        const postIndex = posts.value.findIndex(p => p.id === postId);
        if (postIndex !== -1) {
          posts.value[postIndex] = response.data;
          console.log('✅ Updated post with fresh reaction data after user reaction');
          
          // Ensure selectedReaction is synchronized with backend
          if (response.data.reactions_summary && response.data.reactions_summary.user_reaction) {
            selectedReaction.value[postId] = response.data.reactions_summary.user_reaction;
          } else {
            selectedReaction.value[postId] = null;
          }
        }
      } catch (error) {
        console.error('❌ Failed to fetch updated post after reaction:', error);
        // Fallback to refresh all posts
        await fetchPosts();
      }
    }
    
  } catch (error) {
    console.error('Failed to react to post:', error);
    console.error('Error response data:', error.response?.data);
  }
};

const addComment = async (postId, content) => {
  try {
    console.log('🔄 Adding comment via API...', { postId, content });
    const response = await axios.post(`${BASE_URL}/api/posts/${postId}/comment/`, {
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

const reactToComment = async (data) => {
  try {
    console.log('👍 Reacting to comment:', data);
    await axios.post(`${BASE_URL}/api/posts/comments/${data.commentId}/react/`, {
      reaction_type: data.reactionType
    }, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });

    console.log('✅ Comment reaction added');
    if (selectedPost.value) {
      await fetchCommentsForPost(selectedPost.value.id);
    }

  } catch (error) {
    console.error('❌ Failed to react to comment:', error);
    notifications.value.unshift({
      id: Date.now(),
      type: 'error',
      message: 'Failed to react to comment. Please try again.',
      timestamp: new Date().toISOString()
    });
  }
};

// Add function to fetch comments for a specific post
const fetchCommentsForPost = async (postId) => {
  try {
    console.log(`Fetching all comments for post ${postId}`);
    const response = await axios.get(`${BASE_URL}/api/posts/${postId}/comments/`, {
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
    await axios.post(`${BASE_URL}/api/posts/${postId}/share/`, {
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

const handleReactionUpdated = async (postId) => {
  console.log('🔄 Handling reaction update for post:', postId);
  try {
    // Refresh the specific post to get updated reaction data
    const response = await axios.get(`${BASE_URL}/api/posts/${postId}/`, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });
    
    // Find and update the post in the posts array
    const postIndex = posts.value.findIndex(p => p.id === postId);
    if (postIndex !== -1) {
      posts.value[postIndex] = response.data;
      console.log('✅ Post reaction data updated:', response.data.reactions_summary);
    }
    
    // Also update selectedPost if it's the same post
    if (selectedPost.value && selectedPost.value.id === postId) {
      selectedPost.value = response.data;
    }
  } catch (error) {
    console.error('Failed to refresh post data after reaction update:', error);
  }
};

// Post management event handlers
const handlePostDeleted = (data) => {
  console.log('🗑️ Handling post deletion:', data);
  
  // Extract post ID from the data
  const postId = data.postId || data.post_id;
  
  // Remove the post from the posts array
  const postIndex = posts.value.findIndex(p => p.id === postId);
  if (postIndex !== -1) {
    const removedPost = posts.value.splice(postIndex, 1)[0];
    console.log('✅ Post removed from feed:', removedPost.title || removedPost.content?.substring(0, 50));
  } else {
    console.log('⚠️ Post not found in current feed, may have been already removed');
  }
  
  // Also remove from filtered posts if it exists
  const filteredIndex = filteredPosts.value.findIndex(p => p.id === postId);
  if (filteredIndex !== -1) {
    console.log('✅ Post also removed from filtered view');
  }
  
  // Close modal if the deleted post was open
  if (selectedPost.value && selectedPost.value.id === postId) {
    console.log('🔙 Closing modal for deleted post');
    closePostModal();
  }
  
  // Clear any cached data for this post
  if (comments.value[postId]) {
    delete comments.value[postId];
    console.log('🧹 Cleared comments for deleted post');
  }
  
  if (selectedReaction.value[postId]) {
    delete selectedReaction.value[postId];
    console.log('🧹 Cleared reactions for deleted post');
  }
  
  // Show modern success notification
  addNotification(data.message || 'Post deleted successfully! ✨ The content has been permanently removed from the community feed.', 'success');
  
  // Force a fresh fetch to ensure consistency (but don't wait for it)
  setTimeout(() => {
    console.log('🔄 Performing background refresh to ensure data consistency');
    fetchPosts();
  }, 1000);
};

const handlePostPinned = async (data) => {
  console.log('📌 Handling post pin/unpin:', data);
  
  try {
    // Refresh the specific post to get updated pin status
    const response = await axios.get(`${BASE_URL}/api/posts/${data.postId}/`, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });
    
    // Find and update the post in the posts array
    const postIndex = posts.value.findIndex(p => p.id === data.postId);
    if (postIndex !== -1) {
      posts.value[postIndex] = response.data;
      console.log('✅ Post pin status updated');
    }
    
    // Also update selectedPost if it's the same post
    if (selectedPost.value && selectedPost.value.id === data.postId) {
      selectedPost.value = response.data;
    }
    
    // Show success notification
    addNotification(data.message || 'Post updated successfully', 'success');
    
    // Refresh the posts to show proper ordering (pinned posts first)
    await fetchPosts();
    
  } catch (error) {
    console.error('Failed to refresh post data after pin update:', error);
    addNotification('Failed to update post. Please refresh the page.', 'error');
  }
};

const handlePostReported = (data) => {
  console.log('🚩 Handling post report:', data);
  
  // Show success notification
  addNotification(data.message || 'Post reported successfully. Thank you for helping keep our community safe.', 'success');
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

const updatePostReaction = async (data) => {
  console.log('⚡ Received reaction update via WebSocket:', data);
  
  const post = posts.value.find(p => p.id === data.post_id);
  if (post) {
    console.log('🔄 Updating post reaction locally for post:', data.post_id);
    
    // Update selected reaction if it's for current user
    if (data.user_id === authStore.user.id) {
      if (data.action === 'removed') {
        selectedReaction.value[data.post_id] = null;
        console.log(`🗑️ Removed reaction for current user on post ${data.post_id}`);
      } else {
        selectedReaction.value[data.post_id] = data.reaction_type;
        console.log(`🎯 Updated reaction for current user on post ${data.post_id}: ${data.reaction_type}`);
      }
    }
    
    // Fetch fresh data from backend to get updated reactions_summary
    try {
      const response = await axios.get(`${BASE_URL}/api/posts/${data.post_id}/`, {
        headers: { Authorization: `Bearer ${authStore.token}` }
      });
      
      // Update the post with fresh data
      const postIndex = posts.value.findIndex(p => p.id === data.post_id);
      if (postIndex !== -1) {
        posts.value[postIndex] = response.data;
        console.log('✅ Updated post with fresh reaction data:', response.data.reactions_summary);
        
        // Also ensure selectedReaction is synchronized with backend data
        if (response.data.reactions_summary && response.data.reactions_summary.user_reaction) {
          selectedReaction.value[data.post_id] = response.data.reactions_summary.user_reaction;
        } else {
          selectedReaction.value[data.post_id] = null;
        }
      }
    } catch (error) {
      console.error('❌ Failed to fetch updated post data:', error);
      // Fallback: refresh all posts
      await fetchPosts();
    }
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
  <div :class="['min-h-screen transition-colors duration-200', themeStore.isAdminDark() ? 'bg-gray-900' : 'bg-gray-50']">
    <!-- Main Container with centered max-width -->
    <div class="max-w-4xl mx-auto px-4 py-6">
      <!-- Category Tabs -->
      <div :class="[
        'mb-6 overflow-hidden border rounded-lg shadow-sm backdrop-blur-sm',
        themeStore.isAdminDark() ? 'bg-gray-800/95 border-gray-700' : 'bg-white/95 border-gray-200'
      ]">
        <div :class="['flex w-full overflow-x-auto', themeStore.isAdminDark() ? 'border-b border-gray-700/50' : 'border-b border-gray-200/50']">
          <button
            v-for="category in categories"
            :key="category.value"
            @click="selectedCategory = category.value; activeTab = category.value"
            :class="[
              'flex items-center justify-center px-4 py-3 text-sm font-medium transition-all duration-300 border-b-2 whitespace-nowrap flex-shrink-0',
              selectedCategory === category.value
                ? themeStore.isAdminDark()
                  ? 'text-orange-400 border-orange-400 bg-orange-400/10'
                  : 'text-orange-600 border-orange-500 bg-orange-50/80'
                : themeStore.isAdminDark()
                  ? 'text-gray-400 border-transparent hover:text-orange-400 hover:border-orange-400/50 hover:bg-orange-400/5'
                  : 'text-gray-600 border-transparent hover:text-orange-600 hover:border-orange-500/50 hover:bg-orange-50/50'
            ]"
          >
            <span class="mr-2">{{ category.icon }}</span>
            {{ category.label }}
          </button>
        </div>
      </div>

      <!-- Create Post Form -->
      <div class="mb-6">
        <PostCreateForm 
          :user-profile-picture="authStore.user.profile_picture"
          :categories="categories"
          @create-post="createPost"
        />
      </div>

      <!-- Posts Feed -->
      <div class="space-y-6">
        <PostCard
          v-for="post in filteredPosts"
          :key="post.id"
          :post="post"
          :categories="categories"
          :selected-reaction="selectedReaction[post.id]"
          :comments="comments[post.id] || post.recent_comments || []"
          :user-profile-picture="authStore.user.profile_picture"
          :current-user-id="authStore.user.id"
          @react-to-post="reactToPost"
          @add-comment="addComment"
          @copy-link="copyPostLink"
          @open-modal="openPostModal"
          @reaction-updated="handleReactionUpdated"
          @deleted="handlePostDeleted"
          @pinned="handlePostPinned"
          @reported="handlePostReported"
        />
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex justify-center py-12">
        <div :class="['flex items-center space-x-2', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
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
          'p-8 border shadow-sm rounded-xl max-w-lg mx-auto',
          themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
        ]">
          <svg :class="['w-12 h-12 mx-auto mb-4', themeStore.isAdminDark() ? 'text-gray-500' : 'text-gray-400']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
          </svg>
          <h3 :class="['mb-2 text-lg font-semibold', themeStore.isAdminDark() ? 'text-gray-200' : 'text-gray-800']">
            No Posts Found
          </h3>
          <p :class="['text-sm', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
            {{ searchQuery ? 'Try adjusting your search terms or exploring different categories.' : 'Share the first post with your alumni community!' }}
          </p>
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
      :current-user-id="authStore.user.id"
      @close="closePostModal"
      @react-to-post="reactToPost"
      @add-comment="addComment"
      @react-to-comment="reactToComment"
      @copy-link="copyPostLink"
      @load-comments="fetchCommentsForPost"
      @navigate="navigateToPost"
      @reaction-updated="handleReactionUpdated"
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
</style>