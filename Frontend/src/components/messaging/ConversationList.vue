<template>
  <div class="w-1/4 h-full border-r bg-white overflow-y-auto">
    <div class="p-4">
      <input v-model="searchQuery" placeholder="Search..." class="w-full p-2 border rounded" />
      <button @click="showProfileModal = true" class="mt-2 p-2 bg-blue-500 text-white rounded">Profile</button>
    </div>
    <div v-for="conv in filteredConversations" :key="conv.id" @click="emit('select-conversation', conv)" class="p-4 flex items-center hover:bg-gray-200 cursor-pointer">
      <img :src="conv.type === 'private' ? conv.user.profile.profile_picture : conv.group.group_picture" class="w-12 h-12 rounded-full mr-3" />
      <div>
        <p class="font-semibold">{{ conv.type === 'private' ? `${conv.user.first_name} ${conv.user.last_name}` : conv.group.name }}</p>
        <p class="text-sm text-gray-600">{{ conv.last_message }}</p>
      </div>
    </div>
    <ProfileModal v-if="showProfileModal" @close="showProfileModal = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../../services/api';
import ProfileModal from './ProfileModal.vue';

const emit = defineEmits(['select-conversation']);
const searchQuery = ref('');
const privateConversations = ref([]);
const groupConversations = ref([]);
const showProfileModal = ref(false);

const fetchConversations = async () => {
  const [privateRes, groupRes] = await Promise.all([
    api.get('/message/conversations/users/'),
    api.get('/message/group/')
  ]);
  privateConversations.value = privateRes.data.map(user => ({
    type: 'private', id: user.id, user, last_message: 'Last message'
  }));
  groupConversations.value = groupRes.data.map(group => ({
    type: 'group', id: group.id, group, last_message: 'Last message'
  }));
};

const filteredConversations = computed(() => {
  const all = [...privateConversations.value, ...groupConversations.value];
  return all.filter(conv =>
    (conv.type === 'private' ? `${conv.user.first_name} ${conv.user.last_name}` : conv.group.name)
      .toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

onMounted(fetchConversations);
</script>