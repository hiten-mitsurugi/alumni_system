<script setup>
defineProps({
  user: Object,
  show: Boolean
});
defineEmits(['close', 'approve', 'reject']);

// Helper function to get profile picture URL (same logic as AlumniNavbar)
const getProfilePictureUrl = (entity) => {
  const BASE_URL = 'http://127.0.0.1:8000' // Same as AlumniNavbar
  const pic = entity?.profile_picture
  return pic
    ? (pic.startsWith('http') ? pic : `${BASE_URL}${pic}`)
    : '/default-avatar.png'
};

const userType = (type) => type === 1 ? 'Super Admin' : type === 2 ? 'Admin' : 'Alumni';
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
    <div class="bg-white p-6 rounded-xl w-full max-w-3xl relative shadow-xl overflow-y-auto max-h-[90vh]">
      <button class="absolute top-2 right-2 text-gray-500 hover:text-gray-700 text-2xl" @click="$emit('close')">
        &times;
      </button>

      <div class="flex items-center space-x-4 mb-6">
        <img :src="getProfilePictureUrl(user)" alt="Profile" class="w-20 h-20 rounded-full object-cover border" />
        <div>
          <h2 class="text-xl font-semibold">{{ user.first_name }} {{ user.last_name }}</h2>
          <p class="text-sm text-gray-500">{{ user.email }}</p>
          <p class="text-sm text-gray-400">Type: {{ userType(user.user_type) }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
        <div><strong>First Name:</strong> {{ user.first_name }}</div>
        <div><strong>Middle Name:</strong> {{ user.middle_name }}</div>
        <div><strong>Last Name:</strong> {{ user.last_name }}</div>
        <div><strong>Email:</strong> {{ user.email }}</div>
        <div><strong>School ID:</strong> {{ user.school_id }}</div>
        <div><strong>Program:</strong> {{ user.program }}</div>
        <div><strong>Year Graduated:</strong> {{ user.year_graduated }}</div>
        <div><strong>Employment Status:</strong> {{ user.employment_status }}</div>
        <div><strong>Contact Number:</strong> {{ user.contact_number }}</div>
        <div><strong>Civil Status:</strong> {{ user.civil_status }}</div>
        <div><strong>Birth Date:</strong> {{ user.birth_date }}</div>
        <div><strong>Address:</strong> {{ user.address }}</div>
        <div>
          <strong>Government ID:</strong>
          <a :href="user.government_id" target="_blank" class="text-blue-500 underline">View ID</a>
        </div>
      </div>

      <div class="mt-6 flex justify-end space-x-4">
        <button @click="$emit('reject')" class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">Reject</button>
        <button @click="$emit('approve')" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">Approve</button>
      </div>
    </div>
  </div>
</template>
