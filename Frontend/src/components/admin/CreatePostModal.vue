<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import axios from 'axios';

// Props and Emit
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  onClose: {
    type: Function,
    required: true,
  },
});
const emit = defineEmits(['postCreated']);

// Auth and State
const authStore = useAuthStore();
const title = ref('');
const content = ref('');
const category = ref('event');
const images = ref([]); // Support for multiple images
const error = ref('');
const BASE_URL = 'http://127.0.0.1:8000';

const categories = [
  'event',
  'news',
  'discussion',
  'announcement',
  'job',
  'others',
];

// Handle file input
const handleImageChange = (event) => {
  images.value = Array.from(event.target.files); // Multiple files
};

// Handle form submission
const handleSubmit = async () => {
  error.value = '';
  const formData = new FormData();
  formData.append('title', title.value);
  formData.append('content', content.value);
  formData.append('content_category', category.value);

  // Append all selected images
  images.value.forEach((file) => {
    formData.append('images', file); // Backend must support getlist('images')
  });

  try {
    const response = await axios.post(`${BASE_URL}/api/posting/posts/`, formData, {
      headers: {
        Authorization: `Bearer ${authStore.token}`,
        'Content-Type': 'multipart/form-data',
      },
    });

    emit('postCreated', response.data);
    props.onClose();
    title.value = '';
    content.value = '';
    images.value = [];
  } catch (err) {
    console.error('Error creating post:', err);
    error.value = 'Failed to create post. Please try again.';
  }
};
</script>

<template>
    <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
        <div class="relative bg-white rounded-lg shadow-xl w-full max-w-4xl p-8">

            <!-- Close Button -->
            <button @click="onClose" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
                aria-label="Close">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>

            <h2 class="text-xl font-semibold text-gray-800 mb-4">Create New Post</h2>

            <!-- Error Message -->
            <p v-if="error" class="text-red-500 text-sm mb-4">{{ error }}</p>

            <!-- Post Form -->
            <form @submit.prevent="handleSubmit" class="space-y-4">
                <!-- Title -->
                <div>
                    <label for="title" class="block text-sm font-medium text-gray-700">Title</label>
                    <input v-model="title" type="text" id="title"
                        class="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                        required />
                </div>

                <!-- Content -->
                <div>
                    <label for="content" class="block text-sm font-medium text-gray-700">Content</label>
                    <textarea v-model="content" id="content" rows="4"
                        class="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                        required></textarea>
                </div>

                <!-- Category -->
                <div>
                    <label for="category" class="block text-sm font-medium text-gray-700">Category</label>
                    <select v-model="category" id="category"
                        class="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500">
                        <option v-for="cat in categories" :key="cat" :value="cat">
                            {{ cat.charAt(0).toUpperCase() + cat.slice(1) }}
                        </option>
                    </select>
                </div>

                <!-- Image Upload -->
                <div>
                    <label for="image" class="block text-sm font-medium text-gray-700">Image (optional)</label>
                    <input id="image" type="file" multiple @change="handleImageChange"
                        class="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                        accept="image/*" />

                </div>

                <!-- Submit -->
                <div class="flex justify-end">
                    <button type="submit"
                        class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
                        Submit Post
                    </button>
                </div>
            </form>
        </div>
    </div>
</template>
