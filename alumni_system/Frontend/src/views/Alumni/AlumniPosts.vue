<script setup>
import { ref, onMounted } from 'vue';
import AlumniLayout from '../../components/layouts/AlumniLayout.vue';
// import api from '../../services/api';

const posts = ref([]);
const newPost = ref('');
const showNewPostModal = ref(false);
const newPostTitle = ref('');
const selectedCategory = ref('general');
const postImage = ref(null);

// Mock data for posts
const mockPosts = ref([
  {
    id: 1,
    author: 'John Smith',
    author_email: 'john@example.com',
    author_avatar: '👨‍💼',
    title: 'Great opportunity at Tech Corp!',
    content: 'Just started my new job at Tech Corp. They\'re looking for more CS graduates. Feel free to reach out if interested!',
    category: 'job',
    timestamp: '2024-01-15 14:30:00',
    likes: 15,
    comments: 3,
    image: null,
    liked: false
  },
  {
    id: 2,
    author: 'Jane Doe',
    author_email: 'jane@example.com',
    author_avatar: '👩‍💼',
    title: 'Alumni Reunion Planning',
    content: 'Hey everyone! We\'re planning our 5-year reunion. Who\'s interested in joining the organizing committee?',
    category: 'event',
    timestamp: '2024-01-14 10:15:00',
    likes: 28,
    comments: 7,
    image: null,
    liked: true
  },
  {
    id: 3,
    author: 'Maria Garcia',
    author_email: 'maria@example.com',
    author_avatar: '👩‍🔬',
    title: 'Congratulations to Class of 2023!',
    content: 'Just saw the graduation ceremony photos. So proud of our newest alumni! Welcome to the family! 🎓',
    category: 'general',
    timestamp: '2024-01-10 16:45:00',
    likes: 42,
    comments: 12,
    image: null,
    liked: false
  }
]);

const categories = [
  { value: 'general', label: 'General', icon: '💬' },
  { value: 'job', label: 'Job Opportunities', icon: '💼' },
  { value: 'event', label: 'Events', icon: '📅' },
  { value: 'achievement', label: 'Achievements', icon: '🏆' },
  { value: 'networking', label: 'Networking', icon: '🤝' }
];

const createPost = () => {
  if (!newPost.value.trim() || !newPostTitle.value.trim()) return;
  
  const post = {
    id: Date.now(),
    author: 'You',
    author_email: 'you@example.com',
    author_avatar: '👤',
    title: newPostTitle.value,
    content: newPost.value,
    category: selectedCategory.value,
    timestamp: new Date().toISOString(),
    likes: 0,
    comments: 0,
    image: postImage.value,
    liked: false,
    isOwner: true
  };
  
  mockPosts.value.unshift(post);
  
  // Reset form
  newPost.value = '';
  newPostTitle.value = '';
  selectedCategory.value = 'general';
  postImage.value = null;
  showNewPostModal.value = false;
};

const likePost = (postId) => {
  const post = mockPosts.value.find(p => p.id === postId);
  if (post) {
    if (post.liked) {
      post.likes--;
      post.liked = false;
    } else {
      post.likes++;
      post.liked = true;
    }
  }
};

const handleImageUpload = (event) => {
  const file = event.target.files[0];
  if (file && ['image/jpeg', 'image/jpg', 'image/png'].includes(file.type)) {
    const reader = new FileReader();
    reader.onload = (e) => {
      postImage.value = e.target.result;
    };
    reader.readAsDataURL(file);
  } else {
    alert('Please upload a valid image (JPEG, JPG, PNG)');
  }
};

const formatDate = (timestamp) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffInHours = (now - date) / (1000 * 60 * 60);
  
  if (diffInHours < 1) {
    return 'Just now';
  } else if (diffInHours < 24) {
    return `${Math.floor(diffInHours)}h ago`;
  } else {
    return date.toLocaleDateString();
  }
};

const getCategoryInfo = (category) => {
  return categories.find(c => c.value === category) || categories[0];
};

onMounted(() => {
  posts.value = mockPosts.value;
});
</script>

<template>
  <AlumniLayout>
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">Posts & Feed</h1>
          <p class="text-gray-600">Share updates and connect with the alumni community</p>
        </div>
        <button
          @click="showNewPostModal = true"
          class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
        >
          <span>✏️</span>
          <span>Create Post</span>
        </button>
      </div>

      <!-- Quick Post -->
      <div class="bg-white rounded-lg shadow-sm border p-4 mb-6">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
            <span class="text-green-600 font-semibold">👤</span>
          </div>
          <button
            @click="showNewPostModal = true"
            class="flex-1 bg-gray-100 hover:bg-gray-200 text-left px-4 py-3 rounded-full text-gray-500 transition-colors"
          >
            What's on your mind?
          </button>
        </div>
      </div>

      <!-- Posts Feed -->
      <div class="space-y-6">
        <div v-if="mockPosts.length === 0" class="text-center py-12">
          <span class="text-6xl mb-4 block">📝</span>
          <h3 class="text-lg font-medium text-gray-800 mb-2">No posts yet</h3>
          <p class="text-gray-600">Be the first to share something with the community!</p>
        </div>

        <article v-for="post in mockPosts" :key="post.id" class="bg-white rounded-lg shadow-sm border overflow-hidden">
          <!-- Post Header -->
          <div class="p-4 border-b border-gray-100">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                  <span class="text-lg">{{ post.author_avatar }}</span>
                </div>
                <div>
                  <h3 class="font-semibold text-gray-800">
                    {{ post.author }}
                    <span v-if="post.isOwner" class="text-green-600 text-sm">(You)</span>
                  </h3>
                  <div class="flex items-center space-x-2 text-sm text-gray-500">
                    <span>{{ formatDate(post.timestamp) }}</span>
                    <span>•</span>
                    <div class="flex items-center space-x-1">
                      <span>{{ getCategoryInfo(post.category).icon }}</span>
                      <span>{{ getCategoryInfo(post.category).label }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <button class="text-gray-400 hover:text-gray-600">
                <span class="text-lg">⋯</span>
              </button>
            </div>
          </div>

          <!-- Post Content -->
          <div class="p-4">
            <h2 class="text-lg font-semibold text-gray-800 mb-2">{{ post.title }}</h2>
            <p class="text-gray-700 leading-relaxed">{{ post.content }}</p>
            
            <!-- Post Image -->
            <div v-if="post.image" class="mt-4">
              <img :src="post.image" alt="Post image" class="w-full rounded-lg max-h-96 object-cover">
            </div>
          </div>

          <!-- Post Actions -->
          <div class="px-4 py-3 bg-gray-50 border-t border-gray-100">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-6">
                <button
                  @click="likePost(post.id)"
                  :class="[
                    'flex items-center space-x-2 text-sm transition-colors',
                    post.liked ? 'text-red-600' : 'text-gray-600 hover:text-red-600'
                  ]"
                >
                  <span class="text-lg">{{ post.liked ? '❤️' : '🤍' }}</span>
                  <span>{{ post.likes }} {{ post.likes === 1 ? 'Like' : 'Likes' }}</span>
                </button>
                
                <button class="flex items-center space-x-2 text-sm text-gray-600 hover:text-blue-600 transition-colors">
                  <span class="text-lg">💬</span>
                  <span>{{ post.comments }} {{ post.comments === 1 ? 'Comment' : 'Comments' }}</span>
                </button>
                
                <button class="flex items-center space-x-2 text-sm text-gray-600 hover:text-green-600 transition-colors">
                  <span class="text-lg">🔄</span>
                  <span>Share</span>
                </button>
              </div>
              
              <button class="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-800 transition-colors">
                <span class="text-lg">🔖</span>
                <span>Save</span>
              </button>
            </div>
          </div>
        </article>
      </div>

      <!-- New Post Modal -->
      <div v-if="showNewPostModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold">Create New Post</h3>
            <button @click="showNewPostModal = false" class="text-gray-400 hover:text-gray-600">
              ✕
            </button>
          </div>
          
          <form @submit.prevent="createPost">
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">Post Title</label>
              <input
                v-model="newPostTitle"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="What's your post about?"
                required
              >
            </div>
            
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">Category</label>
              <select 
                v-model="selectedCategory"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option v-for="category in categories" :key="category.value" :value="category.value">
                  {{ category.icon }} {{ category.label }}
                </option>
              </select>
            </div>
            
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">Content</label>
              <textarea
                v-model="newPost"
                rows="6"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Share your thoughts with the alumni community..."
                required
              ></textarea>
            </div>
            
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">Add Image (Optional)</label>
              <input
                type="file"
                @change="handleImageUpload"
                accept=".jpeg,.jpg,.png"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
              <div v-if="postImage" class="mt-2">
                <img :src="postImage" alt="Preview" class="w-full h-32 object-cover rounded-lg">
              </div>
            </div>
            
            <div class="flex justify-end space-x-3">
              <button
                type="button"
                @click="showNewPostModal = false"
                class="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
              >
                Create Post
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </AlumniLayout>
</template>

<style scoped>
/* Custom scrollbar for modal */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
