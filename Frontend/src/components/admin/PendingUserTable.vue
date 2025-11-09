<script setup>
import { watch } from 'vue';
import { useThemeStore } from '@/stores/theme';

const themeStore = useThemeStore();

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
      :class="['min-w-full rounded-xl shadow overflow-hidden', themeStore.isAdminDark() ? 'bg-gray-800' : 'bg-white']"
    >
      <thead :class="['text-white text-left text-sm uppercase', themeStore.isAdminDark() ? 'bg-gray-700' : 'bg-orange-600']">
        <tr>
          <th class="p-4 w-16 text-center">#</th>
          <th class="p-4 w-20 text-center">Profile</th>
          <th class="p-4 w-32 text-left">First Name</th>
          <th class="p-4 w-32 text-left">Last Name</th>
          <th class="p-4 w-32 text-center">School ID</th>
          <th class="p-4 w-40 text-left">Program</th>
          <th class="p-4 w-24 text-center">Year Graduated</th>
          <th class="p-4 w-32 text-left">Employment Status</th>
          <th class="p-4 w-24 text-center">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(user, index) in paginatedUsers"
          :key="user.id || index"
          :class="['border-t', 
            themeStore.isAdminDark() 
              ? 'border-gray-700 hover:bg-gray-700' 
              : 'border-gray-200 hover:bg-gray-50']"
        >
          <td :class="['p-4 w-16 text-center font-mono text-sm', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-400']">
            {{ (currentPage - 1) * 7 + index + 1 }}
          </td>
          <td class="p-4 w-20">
            <div class="flex items-center justify-center">
              <img
                :src="user.profile_picture || '/default-avatar.png'"
                :alt="`${user.first_name} ${user.last_name}`"
                class="w-10 h-10 rounded-full object-cover border"
                @error="$event.target.src = '/default-avatar.png'"
              />
            </div>
          </td>
          <td :class="['p-4 w-32 text-left', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">{{ user.first_name }}</td>
          <td :class="['p-4 w-32 text-left', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">{{ user.last_name }}</td>
          <td :class="['p-4 w-32 text-center', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">{{ user.school_id }}</td>
          <td :class="['p-4 w-40 text-left', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">{{ user.program }}</td>
          <td :class="['p-4 w-24 text-center', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">{{ user.year_graduated }}</td>
          <td :class="['p-4 w-32 text-left', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">{{ user.employment_status }}</td>
          <td class="p-4 w-24">
            <div class="flex justify-center">
              <button
                @click="emit('view-user', user)"
                class="text-blue-600 hover:underline text-sm"
              >
                View
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <p :class="['text-center py-10', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-400']">
      No pending approvals found or still loading...
    </p>

    <!-- Pagination -->
    <div v-if="users.length > 0" class="mt-6 flex justify-center space-x-2">
      <button
        @click="emit('change-page', currentPage - 1)"
        :disabled="currentPage === 1"
        :class="['px-3 py-1 text-sm rounded disabled:opacity-50', 
          themeStore.isAdminDark() 
            ? 'bg-gray-700 hover:bg-gray-600 text-white' 
            : 'bg-gray-300 hover:bg-gray-400 text-gray-700']"
      >
        Previous
      </button>

      <button
        v-for="page in totalPages"
        :key="page"
        @click="emit('change-page', page)"
        :class="[ 'px-3 py-1 rounded text-sm',
          page === currentPage
            ? 'bg-orange-600 text-white'
            : themeStore.isAdminDark() 
              ? 'bg-gray-700 hover:bg-gray-600 text-white' 
              : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
        ]">
      >
        {{ page }}
      </button>

      <button
        @click="emit('change-page', currentPage + 1)"
        :disabled="currentPage === totalPages"
        :class="['px-3 py-1 text-sm rounded disabled:opacity-50', 
          themeStore.isAdminDark() 
            ? 'bg-gray-700 hover:bg-gray-600 text-white' 
            : 'bg-gray-300 hover:bg-gray-400 text-gray-700']"
      >
        Next
      </button>
    </div>
  </div>
</template>
