<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
    <div class="bg-white p-8 rounded-2xl w-full max-w-4xl relative shadow-2xl overflow-y-auto max-h-[90vh]">
      <button class="absolute top-3 right-4 text-gray-500 hover:text-gray-700 text-3xl font-bold" @click="$emit('close')">
        &times;
      </button>

      <!-- Header: Profile Picture & Basic Info -->
      <div class="flex items-center space-x-6 mb-8">
        <img :src="getProfilePictureUrl(user)" class="w-24 h-24 rounded-full object-cover border-2 border-gray-300" />
        <div>
          <h2 class="text-2xl font-bold text-gray-800">{{ user.first_name }} {{ user.last_name }}</h2>
          <p class="text-base text-gray-600">{{ user.email }}</p>
          <p class="text-base text-gray-500">Type: {{ userType(user.user_type) }}</p>
        </div>
      </div>

      <!-- User Info Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 text-base text-gray-700">
        <div><strong>First Name:</strong> {{ user.first_name }}</div>
        <div><strong>Middle Name:</strong> {{ user.middle_name }}</div>
        <div><strong>Last Name:</strong> {{ user.last_name }}</div>
        <div><strong>Gender:</strong> {{ user.gender }}</div>
        <div><strong>Email:</strong> {{ user.email }}</div>
        <div><strong>School ID:</strong> {{ user.school_id }}</div>
        <div><strong>Program:</strong> {{ user.program }}</div>
        <div><strong>Year Graduated:</strong> {{ user.year_graduated }}</div>
        <div><strong>Employment Status:</strong> {{ user.employment_status }}</div>
        <div><strong>Contact Number:</strong> {{ user.contact_number }}</div>
        <div><strong>Civil Status:</strong> {{ user.civil_status }}</div>
        <div><strong>Birth Date:</strong> {{ user.birth_date }}</div>
        <div class="sm:col-span-2"><strong>Address:</strong> {{ user.address }}</div>
        <div>
          <strong>Account Status:</strong>
          <span :class="user.is_active ? 'text-green-600 font-semibold' : 'text-red-500 font-semibold'">
            {{ user.is_active ? 'Active' : 'Blocked' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

defineProps({
  user: Object,
  show: Boolean
});

defineEmits(['close']);

// Helper function to get profile picture URL (same logic as AlumniNavbar)
const getProfilePictureUrl = (entity) => {
  const BASE_URL = 'http://127.0.0.1:8000' // Same as AlumniNavbar
  const pic = entity?.profile_picture
  return pic
    ? (pic.startsWith('http') ? pic : `${BASE_URL}${pic}`)
    : '/default-avatar.png'
};

function userType(type) {
  return type === 1 ? 'Super Admin' : type === 2 ? 'Admin' : 'Alumni';
}
</script>
