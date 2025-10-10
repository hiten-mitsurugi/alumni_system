<script setup>
import AlumniLayout from '../../components/layouts/AlumniLayout.vue';
import { useAuthStore } from '../../stores/auth';
import api from '../../services/api';
import { ref, onMounted } from 'vue';

const authStore = useAuthStore();
const profile = ref(null);

const fetchProfile = async () => {
  try {
    const response = await api.get('/auth/profile/');
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
    await api.post('/auth/upload-profile-picture/', formData, {
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
  <AlumniLayout>
    <h2 class="text-xl font-semibold mb-4">Welcome, {{ authStore.user.first_name }}</h2>
    <div class="bg-white p-4 rounded shadow">
      <p class="mb-2"><strong>Account Status:</strong> {{ profile?.status || 'Loading...' }}</p>
      <img
        v-if="profile?.profile_picture"
        :src="profile.profile_picture"
        alt="Profile Picture"
        class="w-32 h-32 object-cover mb-4"
      />
      <input
        type="file"
        @change="uploadProfilePicture"
        accept=".jpeg,.jpg,.png"
        class="mb-4"
      />
      <p><strong>Email:</strong> {{ authStore.user.email }}</p>
      <p><strong>Program:</strong> {{ profile?.program }}</p>
      <p><strong>School ID:</strong> {{ profile?.school_id }}</p>
    </div>
  </AlumniLayout>
</template>
