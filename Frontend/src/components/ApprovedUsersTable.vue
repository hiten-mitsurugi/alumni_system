<template>
  <div class="overflow-x-auto">
    <table v-if="users.length" class="min-w-full bg-white rounded-xl shadow">
      <thead class="bg-green-700 text-white text-sm uppercase">
        <tr>
          <th class="p-4">Profile</th>
          <th class="p-4">First Name</th>
          <th class="p-4">Last Name</th>
          <th class="p-4">School ID</th>
          <th class="p-4">User Type</th>
          <th class="p-4">Email</th>
          <th class="p-4">Gender</th>
          <th class="p-4">Program</th>
          <th class="p-4">Year</th>
          <th class="p-4">Employment</th>
          <th class="p-4">Status</th>
          <th class="p-4">Last Login</th>
          <th class="p-4">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id" class="border-t hover:bg-gray-50">
          <td class="p-4">
            <img :src="user.profile_picture" class="w-10 h-10 rounded-full object-cover border" />
          </td>
          <td class="p-4">{{ user.first_name }}</td>
          <td class="p-4">{{ user.last_name }}</td>
          <td class="p-4">{{ user.school_id }}</td>
          <td class="p-4">{{ userType(user.user_type) }}</td>
          <td class="p-4">{{ user.email }}</td>
          <td class="p-4">{{ user.gender || 'N/A' }}</td>
          <td class="p-4">{{ user.program }}</td>
          <td class="p-4">{{ user.year_graduated }}</td>
          <td class="p-4">{{ formatEmployment(user.employment_status) }}</td>
          <td class="p-4">
            <span :class="user.is_active ? 'text-green-600 font-semibold' : 'text-red-500 font-semibold'">
              {{ user.is_active ? 'Active' : 'Blocked' }}
            </span>
          </td>
          <td class="p-4">{{ user.last_login ? new Date(user.last_login).toLocaleString() : 'Never' }}</td>
          <td class="p-4 flex items-center gap-2">
            <button @click="$emit('view-user', user)" title="View">
              <EyeIcon class="w-5 h-5 text-blue-600 hover:text-blue-800" />
            </button>
            <button v-if="user.is_active" @click="$emit('block-user', user)" title="Block">
              <BanIcon class="w-5 h-5 text-yellow-600 hover:text-yellow-800" />
            </button>
            <button v-else @click="$emit('unblock-user', user)" title="Unblock">
              <UnlockIcon class="w-5 h-5 text-green-600 hover:text-green-800" />
            </button>
            <button @click="$emit('delete-user', user)" title="Delete">
              <TrashIcon class="w-5 h-5 text-red-600 hover:text-red-800" />
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else class="text-center py-10 text-gray-400">No approved users found or user does not exist.</p>
  </div>
</template>

<script setup>
import { EyeIcon, TrashIcon, BanIcon, UnlockIcon } from 'lucide-vue-next';
defineProps({ users: Array, search: String });
defineEmits(['view', 'block', 'unblock', 'delete']);

function userType(type) {
  return type === 1 ? 'Super Admin' : type === 2 ? 'Admin' : 'Alumni';
}

function formatEmployment(status) {
  if (!status) return 'N/A';
  return status
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase());
}
</script>
