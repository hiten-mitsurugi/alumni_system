<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import api from '@/services/api';
import ApprovedUsersTable from '@/components/admin/ApprovedUsersTable.vue';
import { websocketService } from '@/services/websocket';
import CreateUserModal from '@/components/admin/CreateUserModal.vue';
import ViewUserModal from '@/components/admin/ViewUserModal.vue';

// Modal control
const showViewModal = ref(false);
const showCreateModal = ref(false);
const selectedUser = ref(null);   

// User data
const approvedUsers = ref([]);
const totalUsers = ref(0);

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
    const res = await api.get('/auth/approved-users/', { params });
    console.log('API Response:', res.data);
    approvedUsers.value = res.data.results || res.data;
    totalUsers.value = res.data.count || approvedUsers.value.length;
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
  if (confirm(`Are you sure you want to delete ${user.first_name} ${user.last_name}? This action cannot be undone.`)) {
    try {
      // Use the proper delete endpoint for approved users (UserViewSet DELETE method)
      await api.delete(`/auth/users/${user.id}/`);
      approvedUsers.value = approvedUsers.value.filter(u => u.id !== user.id);
      alert('User deleted successfully');
    } catch (error) {
      console.error('Failed to delete user:', error);
      alert('Failed to delete user. Please try again.');
    }
  }
};

const blockUser = async (user) => {
  if (confirm(`Are you sure you want to block ${user.first_name} ${user.last_name}? They will not be able to login.`)) {
    try {
      await api.post(`/auth/block-user/${user.id}/`);
      fetchApprovedUsers();
      alert('User blocked successfully');
    } catch (error) {
      console.error('Failed to block user:', error);
      alert('Failed to block user. Please try again.');
    }
  }
};

const unblockUser = async (user) => {
  if (confirm(`Are you sure you want to unblock ${user.first_name} ${user.last_name}? They will be able to login again.`)) {
    try {
      await api.post(`/auth/unblock-user/${user.id}/`);
      fetchApprovedUsers();
      alert('User unblocked successfully');
    } catch (error) {
      console.error('Failed to unblock user:', error);
      alert('Failed to unblock user. Please try again.');
    }
  }
};

// WebSocket listener
const handleWebSocketMessage = (message) => {
  console.log('UserManagePage received WebSocket message:', message);
  
  // Handle legacy string messages
  if (typeof message === 'string' || (message.message && typeof message.message === 'string')) {
    const msg = message.message || message;
    if (msg.includes('blocked') || msg.includes('unblocked') || msg.includes('created')) {
      fetchApprovedUsers();
    }
    return;
  }
  
  try {
    // Handle real-time status updates
    if (message.type === 'status_update') {
      const { user_id, status, last_seen, last_login } = message.data || message;
      console.log(`Updating status for user ${user_id} to ${status}`);
      
      // Find and update the user in the list
      const userIndex = approvedUsers.value.findIndex(user => user.id === user_id);
      if (userIndex !== -1) {
        // Update the user's real-time status
        if (!approvedUsers.value[userIndex].real_time_status) {
          approvedUsers.value[userIndex].real_time_status = {};
        }
        
        approvedUsers.value[userIndex].real_time_status.status = status;
        approvedUsers.value[userIndex].real_time_status.is_online = status === 'online';
        approvedUsers.value[userIndex].real_time_status.last_seen = last_seen;
        
        // Update last_login if provided
        if (last_login) {
          approvedUsers.value[userIndex].last_login = last_login;
        }
        
        // Also update profile status for backward compatibility
        if (!approvedUsers.value[userIndex].profile) {
          approvedUsers.value[userIndex].profile = {};
        }
        approvedUsers.value[userIndex].profile.status = status;
        approvedUsers.value[userIndex].profile.last_seen = last_seen;
        
        console.log(`Updated user ${user_id} status to ${status}`);
      } else {
        console.log(`User ${user_id} not found in current list`);
      }
    } else if (message.type === 'new_user') {
      // Refresh the user list when a new user registers
      fetchApprovedUsers();
    }
  } catch (error) {
    console.error('Error handling WebSocket message:', error);
  }
};

// Lifecycle
onMounted(() => {
  fetchApprovedUsers();
  websocketService.connect('notifications');
  websocketService.addListener('notifications', handleWebSocketMessage);
  
  // Refresh time formatting every minute
  setInterval(() => {
    // Trigger reactivity for time formatting without fetching data
    if (approvedUsers.value.length > 0) {
      approvedUsers.value = [...approvedUsers.value];
    }
  }, 60000); // Update every minute
});

onUnmounted(() => {
  websocketService.removeListener('notifications', handleWebSocketMessage);
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

    <!-- Enhanced Table with Integrated Filters -->
    <ApprovedUsersTable
      :users="paginatedUsers"
      :search="filters.search"
      @view-user="openViewModal"
      @delete-user="deleteUser"
      @block-user="blockUser"
      @unblock-user="unblockUser"
      @apply-filters="handleFilters"
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
