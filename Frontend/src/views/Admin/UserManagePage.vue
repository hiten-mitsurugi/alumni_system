<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import api from '@/services/api';
import UserFilters from '@/components/UserFilters.vue';
import ApprovedUsersTable from '@/components/ApprovedUsersTable.vue';
import { websocketService } from '@/services/websocket';
import CreateUserModal from '@/components/CreateUserModal.vue';
import ViewUserModal from '@/components/ViewUserModal.vue';

// Modal control
const showViewModal = ref(false);
const showCreateModal = ref(false);
const selectedUser = ref(null);

// User data
const approvedUsers = ref([]);

// Filters
const filters = ref({
  search: '',
  employment_status: '',
  year_graduated: '',
  program: '',
  status: '',
  gender: ''
});

// Pagination
const currentPage = ref(1);
const usersPerPage = 7;

const totalPages = computed(() =>
  Math.ceil(approvedUsers.value.length / usersPerPage)
);

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * usersPerPage;
  return approvedUsers.value.slice(start, start + usersPerPage);
});

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
};

// Fetch users
const fetchApprovedUsers = async () => {
  try {
    const params = { ...filters.value };
    const res = await api.get('/approved-users/', { params });
    approvedUsers.value = Array.isArray(res.data) ? res.data : [];
    currentPage.value = 1;
  } catch (error) {
    console.error('Failed to fetch users:', error);
    approvedUsers.value = [];
  }
};

// Filter handler
const handleFilters = (newFilters) => {
  filters.value = { ...newFilters };
  fetchApprovedUsers();
};

// View user modal
const openViewModal = (user) => {
  selectedUser.value = user;
  showViewModal.value = true;
};

const closeViewModal = () => {
  selectedUser.value = null;
  showViewModal.value = false;
};

// Create user modal
const openCreateModal = () => {
  showCreateModal.value = true;
};

const closeCreateModal = () => {
  showCreateModal.value = false;
  fetchApprovedUsers();
};

// Actions
const deleteUser = async (user) => {
  try {
    await api.post(`/reject-user/${user.id}/`);
    approvedUsers.value = approvedUsers.value.filter(u => u.id !== user.id);
  } catch (error) {
    console.error('Failed to delete user:', error);
  }
};

const blockUser = async (user) => {
  try {
    await api.post(`/block-user/${user.id}/`);
    fetchApprovedUsers();
  } catch (error) {
    console.error('Failed to block user:', error);
  }
};

const unblockUser = async (user) => {
  try {
    await api.post(`/unblock-user/${user.id}/`);
    fetchApprovedUsers();
  } catch (error) {
    console.error('Failed to unblock user:', error);
  }
};

// WebSocket listener
const handleWebSocketMessage = (data) => {
  if (
    data.message.includes('blocked') ||
    data.message.includes('unblocked') ||
    data.message.includes('created')
  ) {
    fetchApprovedUsers();
  }
};

// Lifecycle
onMounted(() => {
  fetchApprovedUsers();
  websocketService.connect();
  websocketService.addListener(handleWebSocketMessage);
});

onUnmounted(() => {
  websocketService.removeListener(handleWebSocketMessage);
});
</script>

<template>
  <div class="p-6 bg-gray-100 min-h-screen">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-800">Approved Users</h1>
      <button
        @click="openCreateModal"
        class="bg-green-700 hover:bg-green-800 text-white px-4 py-2 rounded-lg shadow-md transition-all duration-200"
      >
        + Create User
      </button>
    </div>

    <!-- Filters -->
    <UserFilters @apply-filters="handleFilters" />

    <!-- Table -->
    <ApprovedUsersTable
      :users="paginatedUsers"
      :search="filters.search"
      @view-user="openViewModal"
      @delete-user="deleteUser"
      @block-user="blockUser"
      @unblock-user="unblockUser"
    />

    <!-- Pagination -->
    <div class="flex justify-center mt-6">
      <button
        class="px-4 py-2 mx-1 bg-gray-300 hover:bg-gray-400 rounded disabled:opacity-50"
        :disabled="currentPage === 1"
        @click="changePage(currentPage - 1)"
      >
        Prev
      </button>
      <span class="px-4 py-2 font-medium text-gray-700">
        {{ currentPage }} / {{ totalPages }}
      </span>
      <button
        class="px-4 py-2 mx-1 bg-gray-300 hover:bg-gray-400 rounded disabled:opacity-50"
        :disabled="currentPage === totalPages"
        @click="changePage(currentPage + 1)"
      >
        Next
      </button>
    </div>

    <!-- Modals -->
    <ViewUserModal :show="showViewModal" :user="selectedUser" @close="closeViewModal" />
    <CreateUserModal v-if="showCreateModal" @close="closeCreateModal" />
  </div>
</template>
