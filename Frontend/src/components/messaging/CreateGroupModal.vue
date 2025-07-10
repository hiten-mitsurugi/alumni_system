<template>
  <div
    class="fixed inset-0 bg-black/50 backdrop-blur-sm bg-opacity-50 flex items-center justify-center z-50"
  >
    <div class="bg-white p-6 rounded shadow-lg w-1/3">
      <h2 class="text-lg font-semibold mb-4">Create Group Chat</h2>
      <input
        :value="groupName"
        @input="$emit('update:groupName', $event.target.value)"
        placeholder="Group Name"
        class="w-full p-2 border rounded mb-4"
      />
      <div class="mb-4">
        <label class="block mb-2">Select Members</label>
        <select
          :value="selectedMembers"
          @change="$emit('update:selectedMembers', Array.from($event.target.selectedOptions).map(o => parseInt(o.value)))"
          multiple
          class="w-full p-2 border rounded"
        >
          <option v-for="user in users" :key="user.id" :value="user.id">
            {{ user.username }}
          </option>
        </select>
      </div>
      <div class="flex gap-2">
        <button
          @click="$emit('createGroup')"
          class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
        >
          Create
        </button>
        <button
          @click="$emit('close')"
          class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps(['groupName', 'selectedMembers', 'users']);
</script>
