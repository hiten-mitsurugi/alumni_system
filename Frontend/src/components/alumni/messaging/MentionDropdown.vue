<template>
  <div 
    v-if="isVisible && filteredMembers.length > 0"
    class="absolute bottom-full mb-2 left-0 right-0 bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto z-50"
  >
    <div class="p-2 text-xs text-gray-500 font-medium border-b border-gray-100">
      Mention group members
    </div>
    <div
      v-for="(member, index) in filteredMembers"
      :key="member.id"
      @click="selectMember(member)"
      @mouseenter="hoveredIndex = index"
      :class="[
        'flex items-center p-3 cursor-pointer transition-colors duration-200',
        hoveredIndex === index || selectedIndex === index 
          ? 'bg-blue-50 border-l-2 border-blue-500' 
          : 'hover:bg-gray-50'
      ]"
    >
      <img 
        :src="getProfilePictureUrl(member)" 
        :alt="member.first_name"
        class="w-8 h-8 rounded-full object-cover mr-3 border border-gray-200"
      />
      <div class="flex-1 min-w-0">
        <div class="font-medium text-gray-900 truncate">
          {{ member.first_name }} {{ member.last_name }}
        </div>
        <div class="text-sm text-gray-500 truncate">
          @{{ member.username }}
        </div>
      </div>
      <div class="ml-2 text-blue-600">
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
          <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/>
        </svg>
      </div>
    </div>
    
    <div v-if="filteredMembers.length === 0 && query" class="p-3 text-sm text-gray-500 text-center">
      No members found matching "{{ query }}"
    </div>
    
    <div class="p-2 text-xs text-gray-400 border-t border-gray-100 text-center">
      Use ↑↓ to navigate, Enter to select, Esc to close
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  members: {
    type: Array,
    default: () => []
  },
  query: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['select-member', 'close'])

// State
const hoveredIndex = ref(-1)
const selectedIndex = ref(0)

// Computed
const filteredMembers = computed(() => {
  if (!props.query) return props.members
  
  const query = props.query.toLowerCase()
  return props.members.filter(member => {
    // Search in multiple fields for better matching
    const username = member.username.toLowerCase()
    const firstName = member.first_name.toLowerCase()
    const lastName = member.last_name.toLowerCase()
    const fullName = `${firstName} ${lastName}`
    const fullNameUnderscore = `${firstName}_${lastName}`
    
    return username.includes(query) ||
           firstName.includes(query) ||
           lastName.includes(query) ||
           fullName.includes(query) ||
           fullNameUnderscore.includes(query)
  })
})

// Watch for visibility changes to reset selection
watch(() => props.isVisible, (visible) => {
  if (visible) {
    selectedIndex.value = 0
    hoveredIndex.value = -1
  }
})

// Watch for query changes to reset selection
watch(() => props.query, () => {
  selectedIndex.value = 0
  hoveredIndex.value = -1
})

// Methods
const selectMember = (member) => {
  emit('select-member', member)
}

const handleKeyDown = (event) => {
  if (!props.isVisible || filteredMembers.value.length === 0) return
  
  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      selectedIndex.value = Math.min(selectedIndex.value + 1, filteredMembers.value.length - 1)
      hoveredIndex.value = selectedIndex.value
      break
      
    case 'ArrowUp':
      event.preventDefault()
      selectedIndex.value = Math.max(selectedIndex.value - 1, 0)
      hoveredIndex.value = selectedIndex.value
      break
      
    case 'Enter':
      event.preventDefault()
      if (filteredMembers.value[selectedIndex.value]) {
        selectMember(filteredMembers.value[selectedIndex.value])
      }
      break
      
    case 'Escape':
      event.preventDefault()
      emit('close')
      break
  }
}

const getProfilePictureUrl = (member) => {
  const BASE_URL = 'http://127.0.0.1:8000'
  const pic = member?.profile_picture
  return pic
    ? (pic.startsWith('http') ? pic : `${BASE_URL}${pic}`)
    : '/default-avatar.png'
}

// Lifecycle
onMounted(() => {
  document.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
})

// Expose methods for parent component
defineExpose({
  handleKeyDown
})
</script>

<style scoped>
/* Custom scrollbar for the dropdown */
.max-h-48::-webkit-scrollbar {
  width: 6px;
}

.max-h-48::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.max-h-48::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.max-h-48::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
