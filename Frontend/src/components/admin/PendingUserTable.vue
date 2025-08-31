<script setup>
import { watch } from 'vue';

const props = defineProps({
  users: Array,
  paginatedUsers: Array,
  currentPage: Number,
  totalPages: Number
});

const emit = defineEmits(['view-user', 'change-page']);

watch(() => props.paginatedUsers, (val) => {
  console.log('paginatedUsers:', val);
}, { immediate: true });
</script>

<template>
  <div class="overflow-x-auto">
    <table
      v-if="users.length"
      class="min-w-full bg-white rounded-xl shadow overflow-hidden"
    >
      <thead class="bg-green-700 text-white text-left text-sm uppercase">
        <tr>
          <th class="p-4">#</th>
          <th class="p-4">Profile</th>
          <th class="p-4">First Name</th>
          <th class="p-4">Last Name</th>
          <th class="p-4">School ID</th>
          <th class="p-4">Program</th>
          <th class="p-4">Year Graduated</th>
          <th class="p-4">Employment Status</th>
          <th class="p-4">Action</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(user, index) in paginatedUsers"
          :key="user.id || index"
          class="border-t hover:bg-gray-50"
        >
          <td class="p-4 font-mono text-sm text-gray-400">
            {{ (currentPage - 1) * 7 + index + 1 }}
          </td>
          <td class="p-4">
            <img
              :src="user.profile_picture || 'https://via.placeholder.com/40'"
              alt="Profile"
              class="w-10 h-10 rounded-full object-cover border"
            />
          </td>
          <td class="p-4">{{ user.first_name }}</td>
          <td class="p-4">{{ user.last_name }}</td>
          <td class="p-4">{{ user.school_id }}</td>
          <td class="p-4">{{ user.program }}</td>
          <td class="p-4">{{ user.year_graduated }}</td>
          <td class="p-4">{{ user.employment_status }}</td>
          <td class="p-4">
            <button
              @click="emit('view-user', user)"
              class="text-blue-600 hover:underline text-sm"
            >
              View
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-else class="text-center py-10 text-gray-400">
      No pending approvals found or still loading...
    </p>

    <!-- Pagination -->
    <div v-if="users.length > 0" class="mt-6 flex justify-center space-x-2">
      <button
        @click="emit('change-page', currentPage - 1)"
        :disabled="currentPage === 1"
        class="px-3 py-1 bg-gray-300 hover:bg-gray-400 text-sm rounded disabled:opacity-50"
      >
        Previous
      </button>

      <button
        v-for="page in totalPages"
        :key="page"
        @click="emit('change-page', page)"
        :class="[ 'px-3 py-1 rounded text-sm',
          page === currentPage
            ? 'bg-green-700 text-white'
            : 'bg-gray-200 hover:bg-gray-300'
        ]"
      >
        {{ page }}
      </button>

      <button
        @click="emit('change-page', currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="px-3 py-1 bg-gray-300 hover:bg-gray-400 text-sm rounded disabled:opacity-50"
      >
        Next
      </button>
    </div>
  </div>
</template>
