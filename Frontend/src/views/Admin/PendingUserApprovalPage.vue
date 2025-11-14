<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import api from '@/services/api';
import PendingUserTable from '@/components/admin/PendingUserTable.vue';
import PendingUserView from '@/components/admin/PendingUserView.vue';
import NotificationToast from '@/components/admin/NotificationToast.vue';
import { websocketService } from '@/services/websocket';
import { useThemeStore } from '@/stores/theme';

const themeStore = useThemeStore();

const pendingUsers = ref([]);
const selectedUser = ref(null);
const showModal = ref(false);

const currentPage = ref(1);
const usersPerPage = 7;

const totalPages = computed(() =>
  Math.ceil(pendingUsers.value.length / usersPerPage)
);

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * usersPerPage;
  return pendingUsers.value.slice(start, start + usersPerPage);
});

const fetchPendingUsers = async () => {
  try {
  const res = await api.get('/auth/pending-alumni/');
    pendingUsers.value = Array.isArray(res.data) ? res.data : [];
  } catch (error) {
    console.error('Failed to fetch pending users:', error);
    pendingUsers.value = [];
  }
};

const openModal = (user) => {
  selectedUser.value = user;
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  selectedUser.value = null;
};

const approveUser = async () => {
  if (!selectedUser.value) return;

  // Store user details before potential modal close
  const userEmail = selectedUser.value.email;
  const userId = selectedUser.value.id;

  try {
  console.log('Attempting to approve user:', userId);
  // Backend mounts auth_app under /api/auth/, our api client prefixes /api
  const response = await api.post(`/auth/approve-user/${userId}/`);
    console.log('Approval response:', response.data);
    console.log('Response status:', response.status);

    // Check if response is successful (200-299 range)
    if (response.status >= 200 && response.status < 300) {
      // Remove from pending list immediately
      pendingUsers.value = pendingUsers.value.filter(u => u.id !== userId);
      closeModal();

      // Show success message based on backend response
      const message = response.data.message || 'User approved successfully';
      if (response.data.email_sent) {
        alert(`✅ ${message}\n📧 Confirmation email sent to ${userEmail}`);
      } else {
        const emailError = response.data.email_error ? `\n\nEmail error: ${response.data.email_error}` : '';
        alert(`✅ ${message}\n⚠️ Email notification failed to send.${emailError}`);
      }
    } else {
      throw new Error(`Unexpected response status: ${response.status}`);
    }

  } catch (error) {
    console.error('Failed to approve user:', error);
    console.error('Error response:', error.response?.data);
    console.error('Error status:', error.response?.status);
    console.error('Full error object:', error);

    // More detailed error message
    let errorMessage = 'Failed to approve user. Please try again.';
    if (error.response?.data?.error) {
      errorMessage = `Failed to approve user: ${error.response.data.error}`;
    } else if (error.response?.status === 404) {
      errorMessage = 'User not found or already approved.';
    } else if (error.response?.status === 500) {
      errorMessage = 'Server error occurred. Please try again later.';
    }

    alert(`❌ ${errorMessage}`);
  }
};

const rejectUser = async () => {
  if (!selectedUser.value) return;

  if (!confirm(`Are you sure you want to reject ${selectedUser.value.first_name} ${selectedUser.value.last_name}'s application?\n\nThis will:\n- Delete their account permanently\n- Send them an email notification\n- They will need to reapply`)) {
    return;
  }

  // Store user details before closeModal() sets selectedUser to null
  const userEmail = selectedUser.value.email;
  const userId = selectedUser.value.id;

  try {
  const response = await api.post(`/auth/reject-user/${userId}/`);
    pendingUsers.value = pendingUsers.value.filter(u => u.id !== userId);
    closeModal();

    // Show success message with email status
    if (response.data.email_sent) {
      alert(`✅ User application rejected.\n📧 Notification email sent to ${userEmail}`);
    } else {
      alert(`✅ User application rejected.\n⚠️ Email notification failed to send.`);
    }
  } catch (error) {
    console.error('Failed to reject user:', error);
    alert('❌ Failed to reject user. Please try again.');
  }
};

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) currentPage.value = page;
};

const handleWebSocketMessage = (data) => {
  try {
    // Add comprehensive safety checks for data structure
    if (!data || typeof data !== 'object') {
      console.log('PendingUserApprovalPage: Invalid WebSocket data received:', data);
      return;
    }

    // Try multiple ways to extract the message
    let message = '';
    if (data.message && typeof data.message === 'string') {
      message = data.message;
    } else if (data.data?.message && typeof data.data.message === 'string') {
      message = data.data.message;
    } else if (typeof data === 'string') {
      message = data;
    }

    // Only proceed if we have a valid string message
    if (message && typeof message === 'string') {
      if (message.includes('New alumni registered') ||
          message.includes('approved') ||
          message.includes('rejected')) {
        fetchPendingUsers(); // Refresh list on relevant events
      }
    } else {
      console.log('PendingUserApprovalPage: No valid message found in WebSocket data:', data);
    }
  } catch (error) {
    console.error('PendingUserApprovalPage: Error handling WebSocket message:', error, 'Data:', data);
  }
};

onMounted(() => {
  fetchPendingUsers();
  websocketService.addListener(handleWebSocketMessage);
});

onUnmounted(() => {
  websocketService.removeListener(handleWebSocketMessage);
});
</script>

<template>
  <div :class="['p-6 min-h-screen', themeStore.isAdminDark() ? 'bg-gray-900' : 'bg-gray-100']">
    <h1 :class="['text-2xl font-bold mb-6', themeStore.isAdminDark() ? 'text-white' : 'text-gray-800']">Pending User Approvals</h1>

    <PendingUserTable
      :users="pendingUsers"
      :paginatedUsers="paginatedUsers"
      :currentPage="currentPage"
      :totalPages="totalPages"
      @view-user="openModal"
      @change-page="changePage"
    />

    <PendingUserView
      :user="selectedUser"
      :show="showModal"
      @close="closeModal"
      @approve="approveUser"
      @reject="rejectUser"
    />

    <NotificationToast />
  </div>
</template>
