<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import PostCard from '@/components/admin/PostCard.vue';
import axios from 'axios';

const router = useRouter();
const authStore = useAuthStore();
const posts = ref([]);
const searchQuery = ref('');
const activeTab = ref('All Content');
const categories = [
  'All Content',
  'Event',
  'News',
  'Discussion',
  'Announcement',
  'Job',
  'Others',
];
const BASE_URL = 'http://127.0.0.1:8000';

const fetchPosts = async () => {
  try {
    const response = await axios.get(`${BASE_URL}/api/posting/posts/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    });
    posts.value = response.data.map(post => ({
      ...post,
      date: new Date(post.created_at).toLocaleDateString(),
      category: post.content_category.charAt(0).toUpperCase() + post.content_category.slice(1),
    }));
  } catch (error) {
    console.error('Failed to fetch posts:', error);
  }
};

const filteredPosts = () => {
  let filtered = posts.value;
  if (activeTab.value !== 'All Content') {
    filtered = filtered.filter(post => post.content_category.toLowerCase() === activeTab.value.toLowerCase());
  }
  if (searchQuery.value) {
    filtered = filtered.filter(post => 
      post.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      post.content.toLowerCase().includes(searchQuery.value.toLowerCase())
    );
  }
  return filtered;
};

const handleView = (post) => {
  router.push(`/admin/contents/${post.id}`);
};

const handleDelete = async (post) => {
  if (confirm(`Are you sure you want to delete "${post.title}"?`)) {
    try {
      await axios.delete(`${BASE_URL}/api/posting/posts/${post.id}/`, {
        headers: { Authorization: `Bearer ${authStore.token}` },
      });
      posts.value = posts.value.filter(p => p.id !== post.id);
    } catch (error) {
      console.error('Failed to delete post:', error);
    }
  }
};

onMounted(() => {
  fetchPosts();
});
</script>

<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex justify-between items-center mb-4">
      <div>
        <h1 class="text-2xl font-bold">Content Management</h1>
        <p class="text-sm text-gray-500">Create and manage news, events, jobs, and discussions</p>
      </div>
      <button
        @click="router.push('/admin/contents/create')"
        class="bg-green-600 text-white rounded px-4 py-2 flex items-center gap-2 hover:bg-green-700"
      >
        <span class="text-lg">+</span> Create New Post
      </button>
    </div>

    <!-- Search Bar -->
    <div class="relative mb-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search content..."
        class="w-full border border-gray-300 rounded p-2 pl-10"
      />
      <svg
        class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    </div>

    <!-- Tabs -->
    <div class="flex space-x-4 mb-6">
      <button
        v-for="tab in categories"
        :key="tab"
        @click="activeTab = tab"
        :class="[
          activeTab === tab ? 'border-b-2 border-green-600 font-semibold text-gray-900' : 'text-gray-500 hover:text-gray-700',
          'pb-2'
        ]"
      >
        {{ tab }}
      </button>
    </div>

    <!-- Posts List -->
    <div v-if="filteredPosts().length" class="space-y-4">
      <PostCard
        v-for="post in filteredPosts()"
        :key="post.id"
        :post="post"
        :on-view="handleView"
        :on-delete="handleDelete"
      />
    </div>
    <div v-else class="text-gray-500 text-center">
      No posts found.
    </div>
  </div>
</template>