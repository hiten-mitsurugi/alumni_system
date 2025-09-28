<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useThemeStore } from '@/stores/theme';
import axios from 'axios';

// Import posting components
import PostCreateForm from '@/components/posting/PostCreateForm.vue';
import CategoryTabs from '@/components/posting/CategoryTabs.vue';
import PostCard from '@/components/posting/PostCard.vue';
import PostModal from '@/components/posting/PostModal.vue';
import EditPostModal from '@/components/modals/EditPostModal.vue';
import ReportPostModal from '@/components/modals/ReportPostModal.vue';
import NotificationToast from '@/components/posting/NotificationToast.vue';

const authStore = useAuthStore();
const themeStore = useThemeStore();

// State
const posts = ref([]);
const searchQuery = ref('');
const activeTab = ref('all');
const selectedReaction = ref({});
const comments = ref({});
const notifications = ref([]);

// Notification state (similar to SettingsPage)
const notification = ref({
  show: false,
  type: 'success', // 'success' or 'error'
  title: '',
  message: ''
});

// Modal state
const showModal = ref(false);
const selectedPost = ref(null);
const currentPostIndex = ref(0);

// Edit post modal
const showEditModal = ref(false);
const editingPost = ref(null);

// Report post modal
const showReportModal = ref(false);
const reportingPost = ref(null);

// WebSocket connection
let postsSocket = null;

// Constants
const BASE_URL = 'http://127.0.0.1:8000';
const categories = [
  { value: 'all', label: 'All Posts', icon: '📋' },
  { value: 'announcement', label: 'Announcement', icon: '📢' },
  { value: 'event', label: 'Event', icon: '📅' },
  { value: 'news', label: 'News', icon: '📰' },
  { value: 'discussion', label: 'Discussion', icon: '💬' },
  { value: 'job', label: 'Job Posting', icon: '💼' }
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
    console.log('🔑 Auth token:', authStore.token ? 'Present' : 'Missing');
    console.log('🌐 API URL:', `${BASE_URL}/api/posts/`);
    console.log('📋 Active tab:', activeTab.value);
    console.log('🔍 Search query:', searchQuery.value);

    const response = await axios.get(`${BASE_URL}/api/posts/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
      params: {
        category: activeTab.value !== 'all' ? activeTab.value : null,
        search: searchQuery.value || null
      }
    });

    console.log('✅ Posts response:', response.data);
    console.log('📄 Response status:', response.status);
    console.log('📊 Response data type:', typeof response.data);
    console.log('📋 Response data keys:', Object.keys(response.data));

    // Handle both paginated and non-paginated responses
    const postsData = response.data.results || response.data;
    posts.value = Array.isArray(postsData) ? postsData : [];

    console.log('📊 Loaded posts count:', posts.value.length);
    console.log('📝 Posts data:', posts.value);

    // Subscribe to real-time updates for all loaded posts
    subscribeToPostUpdates();

  } catch (error) {
    console.error('❌ Failed to fetch posts:', error);
    console.error('📄 Error status:', error.response?.status);
    console.error('📄 Error data:', error.response?.data);
    console.error('📄 Error message:', error.message);

    if (error.response?.status === 401) {
      showErrorMessage('Authentication Error', 'Please log in again to view posts.');
    } else if (error.response?.status === 403) {
      showErrorMessage('Access Denied', 'You do not have permission to view posts.');
    } else {
      showErrorMessage('Load Failed', 'Failed to load posts. Please try again.');
    }
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
    console.log('📊 Created post details:', {
      id: response.data.id,
      title: response.data.title,
      content: response.data.content,
      is_approved: response.data.is_approved,
      visibility: response.data.visibility,
      user: response.data.user
    });

    // Add to posts list at the top
    posts.value.unshift(response.data);
    console.log('📋 Posts array length after adding:', posts.value.length);
    console.log('🔝 First post in array:', posts.value[0]?.id);

    // Show success notification
    addNotification('Post created successfully!', 'success');

    // Immediately refresh posts to get the latest data
    console.log('🔄 Immediately refreshing posts...');
    await fetchPosts();

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
      await axios.delete(`${BASE_URL}/api/posts/${postId}/react/`, {
        headers: { Authorization: `Bearer ${authStore.token}` }
      });
      selectedReaction.value[postId] = null;
    } else {
      // Add or update reaction
      await axios.post(`${BASE_URL}/api/posts/${postId}/react/`, {
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

// Admin Control Functions
const editPost = async (postId) => {
  try {
    console.log('✏️ Opening edit modal for post:', postId);
    const post = posts.value.find(p => p.id === postId);
    if (post) {
      editingPost.value = post;
      showEditModal.value = true;
    }
  } catch (error) {
    console.error('Failed to initiate post edit:', error);
    showErrorMessage('Edit Failed', 'Failed to open edit dialog. Please try again.');
  }
};

const updatePost = async (updatedData) => {
  try {
    console.log('📝 Updating post:', updatedData);

    const response = await axios.put(`${BASE_URL}/api/posts/${updatedData.id}/edit/`, {
      title: updatedData.title,
      content: updatedData.content,
      content_category: updatedData.content_category
    }, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });

    console.log('✅ Post updated successfully:', response.data);

    // Update local state
    const postIndex = posts.value.findIndex(p => p.id === updatedData.id);
    if (postIndex !== -1) {
      // Update the post with the response data
      posts.value[postIndex] = { ...posts.value[postIndex], ...response.data.post };
    }

    showSuccessMessage('Post Updated!', 'The post has been updated successfully.');
    showEditModal.value = false;
    editingPost.value = null;

  } catch (error) {
    console.error('❌ Failed to update post:', error);
    const errorMsg = error.response?.data?.error || 'Failed to update post. Please try again.';
    showErrorMessage('Update Failed', errorMsg);
  }
};

const closeEditModal = () => {
  showEditModal.value = false;
  editingPost.value = null;
};

const deletePost = async (postId) => {
  try {
    console.log('🗑️ Deleting post:', postId);
    console.log('🔍 User details:', {
      userType: authStore.user?.user_type,
      userId: authStore.user?.id,
      token: authStore.token ? 'Token exists' : 'No token'
    });

    const response = await axios.delete(`${BASE_URL}/api/posts/${postId}/`, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });

    console.log('✅ Post deleted successfully:', response.data);

    // Remove the post from local state
    posts.value = posts.value.filter(post => post.id !== postId);

    showSuccessMessage('Post Deleted!', 'The post has been deleted successfully.');

  } catch (error) {
    console.error('❌ Failed to delete post:', error);
    console.error('Error response details:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      headers: error.response?.headers
    });

    let errorMsg = 'Failed to delete post. Please try again.';

    if (error.response?.status === 404) {
      errorMsg = 'Post not found. It may have already been deleted.';
      // Remove the post from local state since it doesn't exist
      posts.value = posts.value.filter(post => post.id !== postId);
    } else if (error.response?.status === 403) {
      errorMsg = 'Permission denied. Admin access required.';
    } else if (error.response?.data?.error) {
      errorMsg = error.response.data.error;
    }

    showErrorMessage('Delete Failed', errorMsg);
  }
};

const pinPost = async (postId) => {
  try {
    console.log('📌 Toggling pin status for post:', postId);

    const post = posts.value.find(p => p.id === postId);
    const action = post?.is_pinned ? 'unpin' : 'pin';

    const response = await axios.post(`${BASE_URL}/api/posts/${postId}/${action}/`, {}, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });

    console.log(`✅ Post ${action}ned successfully:`, response.data);

    // Update local state
    if (post) {
      post.is_pinned = !post.is_pinned;
    }

    const title = action === 'pin' ? 'Post Pinned!' : 'Post Unpinned!';
    const message = action === 'pin' ? 'Post has been pinned to the top.' : 'Post has been unpinned.';
    showSuccessMessage(title, message);

  } catch (error) {
    console.error('❌ Failed to toggle pin status:', error);
    const errorMsg = error.response?.data?.error || 'Failed to update pin status. Please try again.';
    showErrorMessage('Pin Failed', errorMsg);
  }
};

const featurePost = async (postId) => {
  try {
    console.log('⭐ Toggling feature status for post:', postId);

    const post = posts.value.find(p => p.id === postId);
    const action = post?.is_featured ? 'unfeature' : 'feature';

    const response = await axios.post(`${BASE_URL}/api/posts/${postId}/${action}/`, {}, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });

    console.log(`✅ Post ${action}d successfully:`, response.data);

    // Update local state
    if (post) {
      post.is_featured = !post.is_featured;
    }

    const title = action === 'feature' ? 'Post Featured!' : 'Post Unfeatured!';
    const message = action === 'feature' ? 'Post has been featured.' : 'Post has been removed from featured.';
    showSuccessMessage(title, message);

  } catch (error) {
    console.error('❌ Failed to toggle feature status:', error);
    const errorMsg = error.response?.data?.error || 'Failed to update feature status. Please try again.';
    showErrorMessage('Feature Failed', errorMsg);
  }
};

const reportPost = async (postId) => {
  console.log('🚨 Opening report modal for post:', postId);
  const post = posts.value.find(p => p.id === postId);
  if (post) {
    reportingPost.value = post;
    showReportModal.value = true;
  }
};

const submitReport = async (reportData) => {
  try {
    console.log('🚨 Submitting report for post:', reportingPost.value?.id, reportData);

    const response = await axios.post(`${BASE_URL}/api/posts/${reportingPost.value.id}/report/`, {
      reason: reportData.reason,
      details: reportData.details || '',
      reason_label: reportData.reasonLabel
    }, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });

    console.log('✅ Post reported successfully:', response.data);
    showSuccessMessage('Report Submitted!', `Thank you for reporting this post. Our moderation team will review it shortly.`);

    // Close modal
    showReportModal.value = false;
    reportingPost.value = null;

  } catch (error) {
    console.error('❌ Failed to report post:', error);
    const errorMsg = error.response?.data?.error || 'Failed to submit report. Please try again.';
    showErrorMessage('Report Failed', errorMsg);
  }
};

const closeReportModal = () => {
  showReportModal.value = false;
  reportingPost.value = null;
};

// Utility Functions
const showNotification = (type, title, message) => {
  notification.value = {
    show: true,
    type,
    title,
    message
  }

  // Auto-hide after 5 seconds
  setTimeout(() => {
    hideNotification()
  }, 5000)
}

const hideNotification = () => {
  notification.value.show = false
}

const showSuccessMessage = (title, message) => {
  showNotification('success', title, message)
}

const showErrorMessage = (title, message) => {
  showNotification('error', title, message)
}

const addNotification = (message, type = 'info') => {
  if (type === 'success') {
    showSuccessMessage('Success!', message)
  } else if (type === 'error') {
    showErrorMessage('Error!', message)
  } else {
    showNotification('info', 'Info', message)
  }
}

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
  <div class="min-h-screen transition-colors duration-200"
       :class="themeStore.isDarkMode ? 'bg-gray-900' : 'bg-gradient-to-br from-slate-50 to-blue-50'">
    <!-- Header -->
    <div class="shadow-lg border-b-2 sticky top-0 z-10 transition-colors duration-200 ml-2"
         :class="themeStore.isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-blue-100'">
      <div class="w-full px-6 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold mb-1 transition-colors duration-200"
                :class="themeStore.isDarkMode ? 'text-white' : 'text-slate-800'">
              Alumni Community Hub
            </h1>
            <p class="text-base font-medium transition-colors duration-200"
               :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-slate-600'">
              Connect, Share, and Stay Updated with Your Alumni Network
            </p>
          </div>

          <!-- Search -->
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search posts, announcements, events..."
              class="pl-16 pr-6 py-4 w-80 text-lg border-2 rounded-2xl focus:ring-4 shadow-lg transition-colors duration-200"
              :class="themeStore.isDarkMode
                ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:ring-blue-500 focus:border-blue-400'
                : 'bg-white border-slate-300 text-slate-900 placeholder-slate-400 focus:ring-blue-300 focus:border-blue-500'"
            />
            <svg class="absolute left-5 top-1/2 transform -translate-y-1/2 w-6 h-6 transition-colors duration-200"
                 :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-slate-400'"
                 fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
          @edit-post="editPost"
          @delete-post="deletePost"
          @pin-post="pinPost"
          @feature-post="featurePost"
          @report-post="reportPost"
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

    <!-- Edit Post Modal -->
    <EditPostModal
      :is-visible="showEditModal"
      :post="editingPost"
      :categories="categories"
      @close="closeEditModal"
      @update="updatePost"
    />

    <!-- Report Post Modal -->
    <ReportPostModal
      :is-visible="showReportModal"
      :post="reportingPost"
      @close="closeReportModal"
      @submit="submitReport"
    />

    <!-- Modern Notification Component (Similar to Settings Page) -->
    <div v-if="notification.show"
         class="fixed top-4 right-4 z-[9999] transform transition-all duration-300 ease-in-out"
         :class="notification.show ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'"
         style="position: fixed !important;">
      <div class="flex items-center gap-3 px-6 py-4 rounded-lg shadow-lg backdrop-blur-sm border"
           :class="notification.type === 'success'
             ? 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-700 text-green-800 dark:text-green-200'
             : 'bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-700 text-red-800 dark:text-red-200'">

        <!-- Success Icon -->
        <div v-if="notification.type === 'success'"
             class="flex-shrink-0 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
        </div>

        <!-- Error Icon -->
        <div v-else
             class="flex-shrink-0 w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
          <span class="text-white font-bold text-sm">!</span>
        </div>

        <!-- Message Content -->
        <div class="flex-1">
          <h4 class="font-semibold text-sm">{{ notification.title }}</h4>
          <p class="text-sm opacity-90">{{ notification.message }}</p>
        </div>

        <!-- Close Button -->
        <button @click="hideNotification"
                class="flex-shrink-0 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 transition-colors">
          <span class="sr-only">Close</span>
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
          </svg>
        </button>
      </div>
    </div>
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
