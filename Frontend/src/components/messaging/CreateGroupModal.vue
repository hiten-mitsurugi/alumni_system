<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[600px] overflow-hidden" @click.stop>
      <div class="p-4 border-b border-gray-200">
        <h3 class="text-lg font-semibold text-gray-800">Create Group Chat</h3>
      </div>
      <div class="p-4 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Group Name</label>
          <input v-model="groupName" type="text" class="w-full p-2 border border-gray-300 rounded-lg" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Members</label>
          <div class="max-h-64 overflow-y-auto border border-gray-200 rounded-lg">
            <div v-for="mate in availableMates" :key="mate.id" class="flex items-center p-2">
              <input type="checkbox" :value="mate.id" v-model="selectedMembers" class="mr-2" />
              <span>{{ `${mate.first_name} ${mate.last_name}` }}</span>
            </div>
          </div>
        </div>
        <div class="flex justify-end gap-2">
          <button @click="$emit('close')" class="px-4 py-2 bg-gray-200 rounded-lg">Cancel</button>
          <button @click="create" class="px-4 py-2 bg-green-500 text-white rounded-lg" :disabled="!groupName || selectedMembers.length === 0">Create</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

defineProps({
  availableMates: Array,
});
const emit = defineEmits(['close', 'create-group']);

const groupName = ref('');
const selectedMembers = ref([]);

function create() {
  if (groupName.value && selectedMembers.value.length > 0) {
    emit('create-group', {
      name: groupName.value,
      members: selectedMembers.value,
    });
  }
}
</script>