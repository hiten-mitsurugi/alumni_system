<template>
  <div
    class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
    @click="$emit('close')"
  >
    <div
      class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[600px] overflow-hidden"
      @click.stop
    >
      <!-- Header -->
      <div class="p-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.196-2.121M17 20H7m10 0v-2c0-5.523-3.582-10-8-10s-8 4.477-8 10v2m8-10a3 3 0 110-6 3 3 0 010 6zm0 10a3 3 0 110-6 3 3 0 010 6z" />
            </svg>
            Create Group Chat
          </h3>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 transition-colors duration-200"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div class="p-4 space-y-4">
        <!-- Group Name Input -->
        <div>
          <label for="group-name" class="block text-sm font-medium text-gray-700 mb-2">
            Group Name *
          </label>
          <input
            id="group-name"
            v-model="groupName"
            type="text"
            placeholder="Enter group name (e.g., Class of 2020 Reunion)"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
            maxlength="50"
          />
          <p class="text-xs text-gray-500 mt-1">{{ groupName.length }}/50 characters</p>
        </div>

        <!-- Group Description (Optional) -->
        <div>
          <label for="group-description" class="block text-sm font-medium text-gray-700 mb-2">
            Description (Optional)
          </label>
          <textarea
            id="group-description"
            v-model="groupDescription"
            placeholder="What's this group about?"
            rows="2"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 resize-none"
            maxlength="200"
          ></textarea>
          <p class="text-xs text-gray-500 mt-1">{{ groupDescription.length }}/200 characters</p>
        </div>

        <!-- Add Members Section -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Add Members
          </label>
          
          <!-- Search Members -->
          <div class="relative mb-3">
            <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search alumni mates..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
            />
          </div>

          <!-- Selected Members Count -->
          <div v-if="selectedMembers.length > 0" class="mb-3">
            <p class="text-sm text-green-600 font-medium">
              {{ selectedMembers.length }} member{{ selectedMembers.length !== 1 ? 's' : '' }} selected
            </p>
          </div>

          <!-- Members List -->
          <div class="max-h-64 overflow-y-auto border border-gray-200 rounded-lg">
            <div class="p-2">
              <div
                v-for="mate in filteredMates"
                :key="mate.id"
                @click="toggleMember(mate.id)"
                class="flex items-center space-x-3 p-2 hover:bg-gray-50 rounded-lg cursor-pointer transition-colors duration-200"
              >
                <!-- Checkbox -->
                <div class="flex-shrink-0">
                  <input
                    type="checkbox"
                    :checked="selectedMembers.includes(mate.id)"
                    class="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                    @click.stop
                  />
                </div>

                <!-- Avatar with Status -->
                <div class="relative flex-shrink-0">
                  <img
                    :src="mate.avatar"
                    :alt="mate.name"
                    class="w-8 h-8 rounded-full object-cover"
                  />
                  <div
                    :class="[
                      'absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full border border-white',
                      getStatusColor(mate.status)
                    ]"
                  />
                </div>

                <!-- Member Info -->
                <div class="flex-1 min-w-0">
                  <p class="font-medium text-gray-900 truncate">{{ mate.name }}</p>
                  <p class="text-sm text-gray-500 truncate">Class of {{ mate.graduationYear }}</p>
                </div>

                <!-- Status Badge -->
                <div class="flex-shrink-0">
                  <span
                    :class="[
                      'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                      mate.status === 'online' ? 'bg-green-100 text-green-800' :
                      mate.status === 'away' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    ]"
                  >
                    {{ mate.status }}
                  </span>
                </div>
              </div>

              <!-- No results message -->
              <div v-if="filteredMates.length === 0" class="text-center py-4 text-gray-500">
                <svg class="w-8 h-8 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <p class="text-sm">No mates found</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end gap-3 pt-4 border-t border-gray-200">
          <button
            @click="$emit('close')"
            class="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200"
          >
            Cancel
          </button>
          <button
            @click="handleCreateGroup"
            :disabled="!canCreateGroup"
            :class="[
              'px-4 py-2 rounded-lg transition-colors duration-200',
              canCreateGroup
                ? 'bg-green-600 hover:bg-green-700 text-white'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            ]"
          >
            Create Group
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  availableMates: Array
})

const emit = defineEmits(['close', 'create-group'])

// Form data
const groupName = ref('')
const groupDescription = ref('')
const selectedMembers = ref([])
const searchQuery = ref('')

// Computed properties
const filteredMates = computed(() => {
  if (!searchQuery.value) return props.availableMates
  
  return props.availableMates.filter(mate =>
    mate.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    mate.graduationYear.toString().includes(searchQuery.value)
  )
})

const canCreateGroup = computed(() => {
  return groupName.value.trim().length >= 3 && selectedMembers.value.length >= 1
})

// Methods
const toggleMember = (mateId) => {
  const index = selectedMembers.value.indexOf(mateId)
  if (index > -1) {
    selectedMembers.value.splice(index, 1)
  } else {
    selectedMembers.value.push(mateId)
  }
}

const getStatusColor = (status) => {
  switch (status) {
    case 'online': return 'bg-green-500'
    case 'away': return 'bg-yellow-500'
    case 'busy': return 'bg-red-500'
    default: return 'bg-gray-400'
  }
}

const handleCreateGroup = () => {
  if (!canCreateGroup.value) return

  const groupData = {
    name: groupName.value.trim(),
    description: groupDescription.value.trim(),
    members: selectedMembers.value
  }

  emit('create-group', groupData)
  
  // Reset form
  groupName.value = ''
  groupDescription.value = ''
  selectedMembers.value = []
  searchQuery.value = ''
}
</script>
