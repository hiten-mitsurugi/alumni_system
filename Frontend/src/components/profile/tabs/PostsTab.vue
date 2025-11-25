<template>
  <div class="space-y-4">
    <!-- Loading State -->
    <div v-if="loading" class="bg-white rounded-lg shadow p-8 text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto"></div>
      <p class="text-gray-500 mt-4">Loading posts...</p>
    </div>

    <!-- Posts List -->
    <div v-else-if="posts.length > 0" class="space-y-4">
      <PostCard
        v-for="post in posts"
        :key="post.id"
        :post="post"
        :categories="categories"
        :current-user-id="authStore.user.id"
        @copy-link="handleCopyLink"
        @repost="handleRepost"
      />
    </div>

    <!-- Empty State -->
    <div v-else class="bg-white rounded-lg shadow p-12 text-center">
      <svg class="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
      </svg>
      <h3 class="text-xl font-semibold text-gray-700 mb-2">No posts yet</h3>
      <p class="text-gray-500">This user hasn't shared any posts.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, defineProps } from 'vue';
import { useAuthStore } from '@/stores/auth';
import axios from 'axios';
import PostCard from '@/components/posting/PostCard.vue';

const props = defineProps({
  userId: {
    type: Number,
    default: null
  }
});

const authStore = useAuthStore();
const posts = ref([]);
const loading = ref(true);
const categories = ref([]);

// Use the same backend URL logic as AlumniHome
const getBackendBaseUrl = () => {
  const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
  const hostname = window.location.hostname;
  const host = (hostname === 'localhost' || hostname === '127.0.0.1') ? hostname : hostname;
  return `${protocol}//${host}:8000`;
};
const BASE_URL = getBackendBaseUrl();

const fetchPosts = async () => {
  try {
    loading.value = true;
    console.log('🔄 PostsTab - Fetching posts for userId:', props.userId);
    console.log('🔄 PostsTab - Current user:', authStore.user?.id);
    console.log('🔄 PostsTab - Type of props.userId:', typeof props.userId, 'Value:', props.userId);

    const response = await axios.get(`${BASE_URL}/api/posts/`, {
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    });

    console.log('✅ PostsTab - All posts response:', response.data);
    const allPosts = response.data.results || response.data;
    console.log('📊 PostsTab - Total posts from API:', allPosts.length);

    // Determine which user ID to filter by - ensure it's a number
    const targetUserId = Number(props.userId || authStore.user.id);
    console.log('🎯 PostsTab - Filtering for user ID:', targetUserId);
    console.log('🎯 PostsTab - Type of targetUserId:', typeof targetUserId);

    // Filter posts by userId - this includes both original posts and reposts by this user
    posts.value = allPosts.filter(post => {
      const postUserId = Number(post.user.id);
      console.log(`   - Post ${post.id} (type: ${post.post_type || 'original'}) by user ${postUserId}`);
      console.log(`   - Content preview: "${(post.content || post.shared_text || '').substring(0, 50)}"`);
      console.log(`   - Comparison: ${postUserId} === ${targetUserId} = ${postUserId === targetUserId}`);
      return postUserId === targetUserId;
    });

    console.log(`✅ PostsTab - Filtered ${posts.value.length} posts (original + reposts) for user ${targetUserId}`);
    console.log('📝 PostsTab - Posts breakdown:', {
      original: posts.value.filter(p => !p.post_type || p.post_type === 'original').length,
      reposts: posts.value.filter(p => p.post_type === 'repost').length,
      shared: posts.value.filter(p => p.post_type === 'shared').length
    });

  } catch (error) {
    console.error('❌ PostsTab - Error fetching posts:', error);
    console.error('❌ PostsTab - Error response:', error.response?.data);
    posts.value = [];
  } finally {
    loading.value = false;
  }
};

const handleCopyLink = (postId) => {
  const link = `${window.location.origin}/post/${postId}`;
  navigator.clipboard.writeText(link);
  console.log('📋 Post link copied:', link);
};

const handleRepost = async (repostData) => {
  try {
    console.log('🔄 Post reposted successfully from profile:', repostData);

    // Show success notification
    const privacyText = repostData.visibility === 'public' ? 'publicly' :
                       repostData.visibility === 'alumni_only' ? 'to alumni only' :
                       'privately';
    console.log(`✅ Post reposted ${privacyText}!`);

    // Refresh posts to show the new repost
    await fetchPosts();

  } catch (error) {
    console.error('❌ Failed to handle repost from profile:', error);
  }
};

// Watch for userId changes and refetch
watch(() => props.userId, (newUserId, oldUserId) => {
  console.log('👀 PostsTab - userId changed from', oldUserId, 'to', newUserId);
  if (newUserId !== oldUserId) {
    fetchPosts();
  }
});

onMounted(() => {
  console.log('🚀 PostsTab - Component mounted with userId:', props.userId);
  fetchPosts();
});
</script>


