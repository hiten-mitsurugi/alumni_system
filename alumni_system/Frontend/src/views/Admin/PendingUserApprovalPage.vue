<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import api from '@/services/api';
import PendingUserTable from '@/components/PendingUserTable.vue';
import PendingUserView from '@/components/PendingUserView.vue';
import NotificationToast from '@/components/NotificationToast.vue';
import { websocketService } from '@/services/websocket';

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
    const res = await api.get('/pending-alumni/');
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
  try {
    await api.post(`/approve-user/${selectedUser.value.id}/`);
    pendingUsers.value = pendingUsers.value.filter(u => u.id !== selectedUser.value.id);
    closeModal();
  } catch (error) {
    console.error('Failed to approve user:', error);
  }
};

const rejectUser = async () => {
  if (!selectedUser.value) return;
  try {
    await api.post(`/reject-user/${selectedUser.value.id}/`);
    pendingUsers.value = pendingUsers.value.filter(u => u.id !== selectedUser.value.id);
    closeModal();
  } catch (error) {
    console.error('Failed to reject user:', error);
  }
};

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) currentPage.value = page;
};

const handleWebSocketMessage = (data) => {
  if (data.message.includes('New alumni registered') ||
      data.message.includes('approved') ||
      data.message.includes('rejected')) {
    fetchPendingUsers(); // Refresh list on relevant events
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
  <div class="p-6 bg-gray-100 min-h-screen">
    <h1 class="text-2xl font-bold mb-6">Pending User Approvals</h1>

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
