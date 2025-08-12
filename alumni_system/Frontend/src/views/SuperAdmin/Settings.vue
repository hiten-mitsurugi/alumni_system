<!-- SuperAdmin Settings/Profile Page -->
<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { Camera, Save, User, Mail, Phone, MapPin, Calendar, GraduationCap } from 'lucide-vue-next';
import api from '@/services/api';

const authStore = useAuthStore();
const isLoading = ref(false);
const message = ref('');
const messageType = ref('');
const profilePictureFile = ref(null);
const profilePicturePreview = ref('');

// Form data
const profile = reactive({
  first_name: '',
  last_name: '',
  middle_name: '',
  email: '',
  contact_number: '',
  address: '',
  birth_date: '',
  program: '',
  school_id: '',
  gender: '',
  civil_status: ''
});

const BASE_URL = 'http://127.0.0.1:8000';

// Load current user data
onMounted(() => {
  if (authStore.user) {
    Object.assign(profile, {
      first_name: authStore.user.first_name || '',
      last_name: authStore.user.last_name || '',
      middle_name: authStore.user.middle_name || '',
      email: authStore.user.email || '',
      contact_number: authStore.user.contact_number || '',
      address: authStore.user.address || '',
      birth_date: authStore.user.birth_date || '',
      program: authStore.user.program || '',
      school_id: authStore.user.school_id || '',
      gender: authStore.user.gender || '',
      civil_status: authStore.user.civil_status || ''
    });
  }
});

const currentProfilePicture = computed(() => {
  if (profilePicturePreview.value) {
    return profilePicturePreview.value;
  }

  const pic = authStore.user?.profile_picture;
  if (pic && typeof pic === 'string') {
    return pic.startsWith('http') ? pic : `${BASE_URL}${pic}`;
  }

  // Return a default avatar SVG data URL when no profile picture is available
  return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='50' fill='%23e5e7eb'/%3E%3Cpath fill='%239ca3af' d='M50 45c-8.284 0-15-6.716-15-15s6.716-15 15-15 15 6.716 15 15-6.716 15-15 15zm0 5c16.569 0 30 13.431 30 30v10H20V80c0-16.569 13.431-30 30-30z'/%3E%3C/svg%3E";
});

const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    profilePictureFile.value = file;

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      profilePicturePreview.value = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

const updateProfile = async () => {
  isLoading.value = true;
  message.value = '';

  try {
    const formData = new FormData();

    // Add profile data
    Object.keys(profile).forEach(key => {
      if (profile[key] !== null && profile[key] !== undefined) {
        formData.append(key, profile[key]);
      }
    });

    // Add profile picture if selected
    if (profilePictureFile.value) {
      formData.append('profile_picture', profilePictureFile.value);
    }

    const response = await api.put('/user/profile/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    // Update auth store with new user data
    authStore.setUser(response.data);

    message.value = 'Profile updated successfully!';
    messageType.value = 'success';

    // Clear preview and file
    profilePictureFile.value = null;
    profilePicturePreview.value = '';

  } catch (error) {
    console.error('Error updating profile:', error);
    message.value = error.response?.data?.detail || 'Failed to update profile';
    messageType.value = 'error';
  } finally {
    isLoading.value = false;
  }
};

const triggerFileInput = () => {
  document.getElementById('profile-picture-input').click();
};
</script>

<template>
  <div class="max-w-4xl mx-auto p-6">
    <div class="bg-white rounded-lg shadow-lg overflow-hidden">
      <!-- Header -->
      <div class="bg-gradient-to-r from-green-600 to-green-700 p-6 text-white">
        <h1 class="text-3xl font-bold flex items-center gap-3">
          <User class="w-8 h-8" />
          Profile Settings
        </h1>
        <p class="mt-2 opacity-90">Manage your personal information and profile picture</p>
      </div>

      <!-- Content -->
      <div class="p-6">
        <!-- Success/Error Message -->
        <div v-if="message" class="mb-6 p-4 rounded-lg"
             :class="messageType === 'success' ? 'bg-green-100 text-green-700 border border-green-300' : 'bg-red-100 text-red-700 border border-red-300'">
          {{ message }}
        </div>

        <form @submit.prevent="updateProfile" class="space-y-6">
          <!-- Profile Picture Section -->
          <div class="flex flex-col items-center mb-8">
            <div class="relative">
              <img
                :src="currentProfilePicture"
                alt="Profile Picture"
                class="w-32 h-32 rounded-full border-4 border-green-200 object-cover shadow-lg"
              />
              <button
                type="button"
                @click="triggerFileInput"
                class="absolute bottom-2 right-2 bg-green-600 hover:bg-green-700 text-white p-2 rounded-full shadow-lg transition-colors"
              >
                <Camera class="w-4 h-4" />
              </button>
            </div>
            <input
              id="profile-picture-input"
              type="file"
              accept="image/*"
              @change="handleFileUpload"
              class="hidden"
            />
            <p class="mt-2 text-sm text-gray-600">Click the camera icon to change your profile picture</p>
          </div>

          <!-- Personal Information -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- First Name -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">First Name</label>
              <input
                v-model="profile.first_name"
                type="text"
                class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              />
            </div>

            <!-- Last Name -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
              <input
                v-model="profile.last_name"
                type="text"
                class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              />
            </div>

            <!-- Middle Name -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Middle Name</label>
              <input
                v-model="profile.middle_name"
                type="text"
                class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>

            <!-- Email -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                <Mail class="w-4 h-4 inline mr-1" />
                Email
              </label>
              <input
                v-model="profile.email"
                type="email"
                class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              />
            </div>

            <!-- Contact Number -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                <Phone class="w-4 h-4 inline mr-1" />
                Contact Number
              </label>
              <input
                v-model="profile.contact_number"
                type="tel"
                class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>

            <!-- Birth Date -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                <Calendar class="w-4 h-4 inline mr-1" />
                Birth Date
              </label>
              <input
                v-model="profile.birth_date"
                type="date"
                class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>

            <!-- Gender -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Gender</label>
              <select
                v-model="profile.gender"
                class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="">Select Gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="prefer_not_to_say">Prefer not to say</option>
              </select>
            </div>

            <!-- Civil Status -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Civil Status</label>
              <select
                v-model="profile.civil_status"
                class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="">Select Civil Status</option>
                <option value="single">Single</option>
                <option value="married">Married</option>
                <option value="widow">Widow</option>
              </select>
            </div>

            <!-- School ID -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">School ID</label>
              <input
                v-model="profile.school_id"
                type="text"
                class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                readonly
              />
            </div>

            <!-- Program -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                <GraduationCap class="w-4 h-4 inline mr-1" />
                Program
              </label>
              <input
                v-model="profile.program"
                type="text"
                class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>
          </div>

          <!-- Address -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              <MapPin class="w-4 h-4 inline mr-1" />
              Address
            </label>
            <textarea
              v-model="profile.address"
              rows="3"
              class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Enter your complete address"
            ></textarea>
          </div>

          <!-- Submit Button -->
          <div class="flex justify-end pt-6">
            <button
              type="submit"
              :disabled="isLoading"
              class="flex items-center gap-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              <Save class="w-5 h-5" />
              {{ isLoading ? 'Updating...' : 'Update Profile' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
