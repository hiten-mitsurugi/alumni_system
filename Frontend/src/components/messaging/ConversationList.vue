<template>
  <div class="w-1/3 bg-white border-r flex flex-col">
    <div class="p-4 bg-green-700 text-white flex justify-between items-center">
      <span class="font-semibold text-lg">Messages</span>
      <button @click="$emit('openGroupModal')" class="bg-green-500 px-2 py-1 rounded hover:bg-green-600">
        New Group
      </button>
    </div>
    <div class="p-2 flex gap-2 bg-gray-100">
      <button
        @click="$emit('changeTab', 'private')"
        :class="['flex-1 p-2 rounded', currentTab === 'private' ? 'bg-green-500 text-white' : 'bg-white']"
      >
        Personal Messages
      </button>
      <button
        @click="$emit('changeTab', 'group')"
        :class="['flex-1 p-2 rounded', currentTab === 'group' ? 'bg-green-500 text-white' : 'bg-white']"
      >
        Groups
      </button>
    </div>
    <div class="flex-1 overflow-y-auto">
      <ul v-if="currentTab === 'private'">
        <li
          v-for="user in users"
          :key="user.id"
          @click="$emit('selectConversation', 'private', user.id)"
          class="p-3 hover:bg-gray-100 cursor-pointer flex items-center"
          :class="{ 'bg-green-100': selectedConversation?.type === 'private' && selectedConversation.id === user.id }"
        >
          <img class="w-8 h-8 rounded-full mr-2" src="https://via.placeholder.com/32" alt="Avatar" />
          <span>{{ user.username }}</span>
        </li>
      </ul>
      <ul v-else>
        <li
          v-for="group in groups"
          :key="group.id"
          @click="$emit('selectConversation', 'group', group.id)"
          class="p-3 hover:bg-gray-100 cursor-pointer flex items-center"
          :class="{ 'bg-green-100': selectedConversation?.type === 'group' && selectedConversation.id === group.id }"
        >
          <span class="w-8 h-8 rounded-full mr-2 bg-green-500 flex items-center justify-center text-white font-bold">
            {{ group.name.charAt(0) }}
          </span>
          <span>{{ group.name }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
defineProps(['users', 'groups', 'currentTab', 'selectedConversation'])
</script>
