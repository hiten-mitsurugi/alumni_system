<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="$emit('close')">
    <div class="bg-white rounded-2xl shadow-2xl max-w-lg w-full mx-4 max-h-[90vh] overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-100">
        <h2 class="text-2xl font-bold text-gray-900">Create Group</h2>
        <button 
          @click="$emit('close')" 
          class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors"
        >
          <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <div class="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
        <!-- Group Picture Section -->
        <div class="flex flex-col items-center space-y-4">
          <div class="relative">
            <div 
              class="w-24 h-24 rounded-full border-4 border-purple-100 flex items-center justify-center cursor-pointer hover:border-purple-200 transition-colors overflow-hidden"
              :class="groupPicturePreview ? 'bg-gray-100' : 'bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500'"
              @click="triggerFileUpload"
            >
              <img 
                v-if="groupPicturePreview" 
                :src="groupPicturePreview" 
                alt="Group Picture" 
                class="w-full h-full object-cover"
              />
              <div v-else class="text-center">
                <!-- Modern Messenger-style group icon -->
                <svg class="w-12 h-12 text-white mx-auto" fill="currentColor" viewBox="0 0 24 24">
                  <!-- Main group circle -->
                  <circle cx="9" cy="9" r="3.5" opacity="0.9"/>
                  <!-- Second person circle -->
                  <circle cx="15.5" cy="7.5" r="2.8" opacity="0.7"/>
                  <!-- Third person circle -->
                  <circle cx="18" cy="13" r="2.3" opacity="0.8"/>
                  <!-- Group base -->
                  <path d="M9 14c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" opacity="0.9"/>
                  <path d="M15.5 12c-1.83 0-5.5.92-5.5 2.75V16h11v-1.25c0-1.83-3.67-2.75-5.5-2.75z" opacity="0.6"/>
                </svg>
              </div>
            </div>
            <button 
              @click="triggerFileUpload"
              class="absolute -bottom-1 -right-1 w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white hover:from-purple-600 hover:to-pink-600 transition-colors shadow-lg"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
            </button>
          </div>
          <input 
            ref="fileInput" 
            type="file" 
            accept="image/*" 
            @change="handleFileUpload" 
            class="hidden"
          />
          <p class="text-sm text-gray-500 text-center">
            Tap to add a group photo
          </p>
        </div>

        <!-- Group Name -->
        <div class="space-y-2">
          <label class="block text-sm font-semibold text-gray-700">Group Name</label>
          <input 
            v-model="groupName" 
            type="text" 
            placeholder="Enter group name..."
            class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
            maxlength="50"
          />
          <div class="flex justify-between text-xs text-gray-400">
            <span></span>
            <span>{{ groupName.length }}/50</span>
          </div>
        </div>

        <!-- Member Search -->
        <div class="space-y-2">
          <label class="block text-sm font-semibold text-gray-700">
            Add Members
            <span v-if="selectedMembers.length > 0" class="text-blue-600">({{ selectedMembers.length }} selected)</span>
          </label>
          <div class="relative">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Search people..."
              @input="handleSearch"
              class="w-full px-4 py-3 pl-10 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
            />
            <svg class="w-5 h-5 text-gray-400 absolute left-3 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
          </div>
        </div>

        <!-- Selected Members Display -->
        <div v-if="selectedMembers.length > 0" class="space-y-2">
          <label class="block text-sm font-semibold text-gray-700">Selected Members</label>
          <div class="flex flex-wrap gap-2">
            <div 
              v-for="member in selectedMemberObjects" 
              :key="member.id"
              class="flex items-center bg-blue-50 rounded-full pl-1 pr-3 py-1 border border-blue-200"
            >
              <img 
                v-if="member.profile_picture" 
                :src="member.profile_picture" 
                :alt="member.first_name"
                class="w-6 h-6 rounded-full mr-2 object-cover"
              />
              <div 
                v-else 
                class="w-6 h-6 rounded-full mr-2 bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center"
              >
                <span class="text-xs text-white font-medium">
                  {{ member.first_name.charAt(0) }}{{ member.last_name.charAt(0) }}
                </span>
              </div>
              <span class="text-sm font-medium text-gray-700">
                {{ member.first_name }} {{ member.last_name }}
              </span>
              <button 
                @click="removeMember(member.id)"
                class="ml-2 w-4 h-4 rounded-full bg-gray-300 hover:bg-red-500 hover:text-white transition-colors flex items-center justify-center"
              >
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Available Members List -->
        <div class="space-y-2">
          <div class="max-h-64 overflow-y-auto space-y-1">
            <!-- Loading state -->
            <div v-if="isSearching" class="text-center py-4">
              <div class="inline-block w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <span class="ml-2 text-sm text-gray-500">Searching...</span>
            </div>
            
            <!-- No results -->
            <div v-else-if="searchQuery && filteredAvailableUsers.length === 0" class="text-center py-4 text-gray-500">
              <svg class="w-8 h-8 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
              <p class="text-sm">No users found</p>
            </div>
            
            <!-- Search Results -->
            <div 
              v-for="user in filteredAvailableUsers" 
              :key="user.id"
              @click="toggleMember(user)"
              class="flex items-center p-3 rounded-xl hover:bg-gray-50 cursor-pointer transition-colors border border-transparent hover:border-gray-200"
            >
              <div class="relative mr-3">
                <img 
                  v-if="user.profile_picture" 
                  :src="user.profile_picture" 
                  :alt="user.first_name"
                  class="w-10 h-10 rounded-full object-cover"
                />
                <div 
                  v-else 
                  class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center"
                >
                  <span class="text-sm text-white font-medium">
                    {{ user.first_name.charAt(0) }}{{ user.last_name.charAt(0) }}
                  </span>
                </div>
                <!-- Selection indicator -->
                <div 
                  v-if="selectedMembers.includes(user.id)"
                  class="absolute -bottom-1 -right-1 w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center"
                >
                  <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                </div>
              </div>
              <div class="flex-1">
                <div class="font-medium text-gray-900">{{ user.first_name }} {{ user.last_name }}</div>
                <div class="text-sm text-gray-500">@{{ user.username }}</div>
              </div>
              <div class="ml-2">
                <div 
                  class="w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors"
                  :class="selectedMembers.includes(user.id) 
                    ? 'bg-blue-500 border-blue-500' 
                    : 'border-gray-300 hover:border-blue-400'"
                >
                  <svg 
                    v-if="selectedMembers.includes(user.id)"
                    class="w-3 h-3 text-white" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-100 bg-gray-50">
        <div class="flex justify-between items-center">
          <button 
            @click="$emit('close')" 
            class="px-6 py-2 text-gray-600 hover:text-gray-800 font-medium transition-colors"
          >
            Cancel
          </button>
          <button 
            @click="createGroup" 
            :disabled="!canCreateGroup"
            class="px-8 py-3 bg-blue-500 text-white font-semibold rounded-xl hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            <svg v-if="isCreating" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></svg>
            <span>{{ isCreating ? 'Creating...' : 'Create Group' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import api from '@/services/api'
import debounce from 'lodash/debounce'

const props = defineProps({
  availableMates: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'create-group'])

// Form data
const groupName = ref('')
const selectedMembers = ref([])
const groupPicture = ref(null)
const groupPicturePreview = ref(null)

// Search functionality
const searchQuery = ref('')
const searchResults = ref([])
const isSearching = ref(false)

// UI states
const isCreating = ref(false)
const fileInput = ref(null)

// Computed properties
const canCreateGroup = computed(() => {
  return groupName.value.trim().length > 0 && selectedMembers.value.length > 0 && !isCreating.value
})

const selectedMemberObjects = computed(() => {
  return allAvailableUsers.value.filter(user => selectedMembers.value.includes(user.id))
})

const allAvailableUsers = computed(() => {
  // Combine available mates with search results, avoiding duplicates
  const combined = [...props.availableMates]
  searchResults.value.forEach(user => {
    if (!combined.some(mate => mate.id === user.id)) {
      combined.push(user)
    }
  })
  return combined
})

const filteredAvailableUsers = computed(() => {
  if (!searchQuery.value) {
    return props.availableMates
  }
  return allAvailableUsers.value.filter(user => {
    const fullName = `${user.first_name} ${user.last_name}`.toLowerCase()
    const username = user.username.toLowerCase()
    const query = searchQuery.value.toLowerCase()
    return fullName.includes(query) || username.includes(query)
  })
})

// Helper function to get profile picture URL
const getProfilePictureUrl = (user) => {
  if (!user.profile_picture) return null
  if (user.profile_picture.startsWith('http')) return user.profile_picture
  return `http://localhost:8000${user.profile_picture}`
}

// Search function - using the same pattern as the main messaging component
async function search() {
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    isSearching.value = false
    return
  }

  isSearching.value = true
  try {
    const { data } = await api.get(`/message/search/?q=${encodeURIComponent(searchQuery.value)}`)
    
    // Process users with profile picture URLs
    const users = (data.users || []).map(u => ({
      ...u,
      profile_picture: getProfilePictureUrl(u)
    }))
    
    searchResults.value = users
  } catch (error) {
    console.error('Search error:', error)
    searchResults.value = []
  } finally {
    isSearching.value = false
  }
}

const debouncedSearch = debounce(search, 300)

const handleSearch = () => {
  debouncedSearch()
}

// Member management
const toggleMember = (user) => {
  const index = selectedMembers.value.indexOf(user.id)
  if (index > -1) {
    selectedMembers.value.splice(index, 1)
  } else {
    selectedMembers.value.push(user.id)
  }
}

const removeMember = (userId) => {
  const index = selectedMembers.value.indexOf(userId)
  if (index > -1) {
    selectedMembers.value.splice(index, 1)
  }
}

// File upload handling
const triggerFileUpload = () => {
  fileInput.value?.click()
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    groupPicture.value = file
    
    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      groupPicturePreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

// Create group - removed description field
const createGroup = async () => {
  if (!canCreateGroup.value) return
  
  isCreating.value = true
  try {
    const formData = new FormData()
    formData.append('name', groupName.value.trim())
    formData.append('members', JSON.stringify(selectedMembers.value))
    
    if (groupPicture.value) {
      formData.append('group_picture', groupPicture.value)
    }
    
    emit('create-group', formData)
  } catch (error) {
    console.error('Error creating group:', error)
  } finally {
    isCreating.value = false
  }
}

// Reset form when modal opens
watch(() => props.availableMates, () => {
  groupName.value = ''
  selectedMembers.value = []
  groupPicture.value = null
  groupPicturePreview.value = null
  searchQuery.value = ''
  searchResults.value = []
})
</script>

<style scoped>
/* Custom scrollbar for member list */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* Smooth transitions */
* {
  transition: all 0.2s ease;
}
</style>