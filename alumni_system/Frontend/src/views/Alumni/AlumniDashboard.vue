<script setup>
import { useAuthStore } from '../../stores/auth';
import api from '../../services/api';
import { ref, onMounted } from 'vue';

const authStore = useAuthStore();
const profile = ref(null);

const fetchProfile = async () => {
  try {
    const response = await api.get('/profile/');
    profile.value = response.data;
  } catch (err) {
    console.error('Failed to fetch profile:', err);
  }
};

const uploadProfilePicture = async (event) => {
  const file = event.target.files[0];
  if (!file || !['image/jpeg', 'image/jpg', 'image/png'].includes(file.type)) {
    alert('Please upload a valid image (JPEG, JPG, PNG)');
    return;
  }
  const formData = new FormData();
  formData.append('profile_picture', file);
  try {
    await api.post('/upload-profile-picture/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    fetchProfile();
  } catch (err) {
    console.error('Failed to upload profile picture:', err);
  }
};

onMounted(() => {
  fetchProfile();
});
</script>

<template>
  <div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- Welcome Card -->
      <div class="bg-white rounded-lg shadow-sm border p-6">
        <div class="flex items-center space-x-4 mb-4">
          <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
            <span class="text-2xl">👋</span>
          </div>
          <div>
            <h2 class="text-xl font-semibold text-gray-800">
              Welcome back, {{ authStore.user.first_name }}!
            </h2>
            <p class="text-gray-600">Great to see you in the alumni network</p>
          </div>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="bg-white rounded-lg shadow-sm border p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Quick Stats</h3>
        <div class="grid grid-cols-2 gap-4">
          <div class="text-center">
            <div class="text-2xl font-bold text-green-600">5</div>
            <div class="text-sm text-gray-600">Messages</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-blue-600">12</div>
            <div class="text-sm text-gray-600">Posts</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Profile Information -->
    <div class="bg-white rounded-lg shadow-sm border p-6 mb-6">
      <div class="flex justify-between items-start mb-4">
        <h3 class="text-lg font-semibold text-gray-800">Profile Information</h3>
        <button class="text-green-600 hover:text-green-800 text-sm font-medium">
          Edit Profile
        </button>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Account Status</label>
            <div class="flex items-center space-x-2">
              <span class="w-2 h-2 bg-green-500 rounded-full"></span>
              <span class="text-sm text-green-700 font-medium">
                {{ profile?.status || 'Active' }}
              </span>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <p class="text-gray-900">{{ authStore.user.email }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Program</label>
            <p class="text-gray-900">{{ profile?.program || 'Not specified' }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">School ID</label>
            <p class="text-gray-900">{{ profile?.school_id || 'Not specified' }}</p>
          </div>
        </div>

        <div class="flex flex-col items-center space-y-4">
          <div class="relative">
            <img
              v-if="profile?.profile_picture"
              :src="profile.profile_picture"
              alt="Profile Picture"
              class="w-32 h-32 object-cover rounded-full border-4 border-green-100"
            />
            <div v-else class="w-32 h-32 bg-gray-200 rounded-full border-4 border-green-100 flex items-center justify-center">
              <span class="text-4xl text-gray-400">👤</span>
            </div>
            <button class="absolute bottom-0 right-0 bg-green-600 hover:bg-green-700 text-white p-2 rounded-full shadow-lg transition-colors">
              <span class="text-sm">📷</span>
            </button>
          </div>
          
          <input
            type="file"
            @change="uploadProfilePicture"
            accept=".jpeg,.jpg,.png"
            class="hidden"
            ref="fileInput"
          />
          
          <button
            @click="$refs.fileInput.click()"
            class="text-green-600 hover:text-green-800 text-sm font-medium"
          >
            Change Photo
          </button>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <button 
        @click="$router.push('/alumni/messages')"
        class="bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg p-4 text-left transition-colors group"
      >
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-blue-100 group-hover:bg-blue-200 rounded-lg flex items-center justify-center">
            <span class="text-lg">💬</span>
          </div>
          <div>
            <h4 class="font-medium text-gray-800">Messages</h4>
            <p class="text-sm text-gray-600">Connect with alumni</p>
          </div>
        </div>
      </button>

      <button 
        @click="$router.push('/alumni/posts')"
        class="bg-green-50 hover:bg-green-100 border border-green-200 rounded-lg p-4 text-left transition-colors group"
      >
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-green-100 group-hover:bg-green-200 rounded-lg flex items-center justify-center">
            <span class="text-lg">📝</span>
          </div>
          <div>
            <h4 class="font-medium text-gray-800">Create Post</h4>
            <p class="text-sm text-gray-600">Share with community</p>
          </div>
        </div>
      </button>

      <button 
        @click="$router.push('/alumni/directory')"
        class="bg-purple-50 hover:bg-purple-100 border border-purple-200 rounded-lg p-4 text-left transition-colors group"
      >
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-purple-100 group-hover:bg-purple-200 rounded-lg flex items-center justify-center">
            <span class="text-lg">📖</span>
          </div>
          <div>
            <h4 class="font-medium text-gray-800">Alumni Directory</h4>
            <p class="text-sm text-gray-600">Find classmates</p>
          </div>
        </div>
      </button>
    </div>

    <!-- Recent Activity -->
    <div class="bg-white rounded-lg shadow-sm border p-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">Recent Activity</h3>
      <div class="space-y-4">
        <div class="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
          <span class="text-lg">🎉</span>
          <div>
            <p class="text-sm text-gray-800">Welcome to the Alumni Network!</p>
            <p class="text-xs text-gray-500">Start by updating your profile and connecting with fellow graduates</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
