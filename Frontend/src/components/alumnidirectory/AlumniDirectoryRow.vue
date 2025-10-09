<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import axios from 'axios';

const props = defineProps({
  alumni: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['edit', 'delete']);

const router = useRouter();
const authStore = useAuthStore();
const BASE_URL = 'http://127.0.0.1:8000';

const deleting = ref(false);
const showDeleteConfirm = ref(false);

// Computed
const fullName = computed(() => {
  const parts = [
    props.alumni.first_name,
    props.alumni.middle_name,
    props.alumni.last_name
  ].filter(Boolean);
  return parts.join(' ');
});

const formattedBirthDate = computed(() => {
  if (!props.alumni.birth_date) return '-';
  return new Date(props.alumni.birth_date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
});

const genderDisplay = computed(() => {
  const genderMap = {
    'male': 'Male',
    'female': 'Female',
    'prefer_not_to_say': 'Prefer not to say'
  };
  return genderMap[props.alumni.gender] || props.alumni.gender;
});

// Methods
const viewProfile = () => {
  // Debug: Log the alumni data
  console.log('Clicked alumni data:', props.alumni)
  
  // Use the alumni's username for clean URLs
  console.log('Navigating to alumni username:', props.alumni.username)
  
  // Navigate to the alumni's profile using their username
  router.push({
    name: 'AlumniProfile',
    params: { userIdentifier: props.alumni.username }
  });
};

const handleEdit = () => {
  emit('edit', props.alumni);
};

const handleDeleteClick = () => {
  showDeleteConfirm.value = true;
};

const confirmDelete = async () => {
  deleting.value = true;
  try {
    await axios.delete(`${BASE_URL}/api/auth/alumni-directory/${props.alumni.id}/`, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });
    emit('delete');
    showDeleteConfirm.value = false;
  } catch (error) {
    console.error('❌ Failed to delete alumni:', error);
    alert('Failed to delete alumni entry. Please try again.');
  } finally {
    deleting.value = false;
  }
};

const cancelDelete = () => {
  showDeleteConfirm.value = false;
};
</script>

<template>
  <tr class="hover:bg-green-200 transition-colors duration-150">
    <!-- School ID -->
    <td class="px-6 py-4 whitespace-nowrap">
      <div class="text-sm font-medium text-gray-900">{{ alumni.school_id }}</div>
    </td>

    <!-- Full Name -->
    <td class="px-6 py-4 whitespace-nowrap">
      <div 
        @click="viewProfile"
        class="text-sm font-medium text-gray-900 cursor-pointer hover:text-green-600 hover:underline transition-colors"
        :title="`View ${fullName}'s profile`"
      >
        {{ fullName }}
      </div>
      <!--<div class="text-sm text-gray-500">{{ alumni.first_name }} {{ alumni.middle_name }} {{ alumni.last_name }}</div>-->
    </td>

    <!-- Program -->
    <td class="px-6 py-4">
      <div class="text-sm text-gray-900 max-w-xs">
        <span class="line-clamp-2">{{ alumni.program }}</span>
      </div>
    </td>

    <!-- Year Graduated -->
    <td class="px-6 py-4 whitespace-nowrap">
      <div class="text-sm text-gray-900 font-medium">{{ alumni.year_graduated }}</div>
    </td>

    <!-- Birth Date -->
    <td class="px-6 py-4 whitespace-nowrap">
      <div class="text-sm text-gray-900">{{ formattedBirthDate }}</div>
    </td>

    <!-- Gender -->
    <td class="px-6 py-4 whitespace-nowrap">
      <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full"
            :class="{
              'bg-blue-100 text-blue-800': alumni.gender === 'male',
              'bg-pink-100 text-pink-800': alumni.gender === 'female',
              'bg-gray-100 text-gray-800': alumni.gender === 'prefer_not_to_say'
            }">
        {{ genderDisplay }}
      </span>
    </td>

    <!-- Actions -->
    <td class="px-6 py-4 whitespace-nowrap text-center">
      <div v-if="!showDeleteConfirm" class="flex items-center justify-center space-x-2">
        <!-- View Profile Button -->
        <button
          @click="viewProfile"
          class="text-green-600 hover:text-green-800 hover:bg-green-200 p-2 rounded-lg transition-colors duration-200"
          title="View Profile"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </button>

        <!-- Edit Button -->
        <button
          @click="handleEdit"
          class="text-blue-600 hover:text-blue-800 hover:bg-blue-50 p-2 rounded-lg transition-colors duration-200"
          title="Edit Alumni"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </button>

        <!-- Delete Button -->
        <button
          @click="handleDeleteClick"
          class="text-red-600 hover:text-red-800 hover:bg-red-50 p-2 rounded-lg transition-colors duration-200"
          title="Delete Alumni"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>

      <!-- Delete Confirmation -->
      <div v-else class="flex items-center justify-center space-x-2">
        <span class="text-xs text-gray-600 mr-2">Delete?</span>
        <button
          @click="confirmDelete"
          :disabled="deleting"
          class="text-red-600 hover:text-red-800 hover:bg-red-50 p-1 rounded transition-colors duration-200 disabled:opacity-50"
          title="Confirm Delete"
        >
          <svg v-if="!deleting" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <div v-else class="w-4 h-4 border-2 border-red-600 border-t-transparent rounded-full animate-spin"></div>
        </button>
        <button
          @click="cancelDelete"
          :disabled="deleting"
          class="text-gray-600 hover:text-gray-800 hover:bg-green-200 p-1 rounded transition-colors duration-200 disabled:opacity-50"
          title="Cancel Delete"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </td>
  </tr>
</template>

<style scoped>
/* Line clamp utility for long program names */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Smooth transitions */
.transition-colors {
  transition: background-color 0.15s ease, color 0.15s ease;
}

/* Button hover effects */
button:hover:not(:disabled) {
  transform: translateY(-1px);
}

button:disabled {
  cursor: not-allowed;
}

/* Delete confirmation animation */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.flex.items-center.justify-center.space-x-2 {
  animation: slideIn 0.2s ease-out;
}
</style>
