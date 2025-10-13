<template>
  <div class="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-sm transition-shadow">
    <!-- Field Label -->
    <div class="flex items-center justify-between mb-2">
      <label class="text-sm font-medium text-gray-700">
        {{ fieldLabels[fieldName] || fieldName }}
      </label>
      
      <!-- Privacy and Edit Controls (only for own profile) -->
      <div v-if="isOwnProfile" class="flex items-center gap-2">
        <!-- Privacy/Visibility Toggle -->
        <button 
          @click="toggleVisibilityMenu"
          :class="visibilityButtonClass"
          class="p-1.5 rounded-lg transition-colors"
          :title="`Privacy: ${visibilityDisplay}`"
        >
          <component :is="visibilityIcon" class="w-4 h-4" />
        </button>
        
        <!-- Edit Button -->
        <button 
          @click="startEditing"
          class="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
          title="Edit field"
        >
          <PencilIcon class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Privacy Dropdown Menu -->
    <div 
      v-if="showVisibilityMenu" 
      class="absolute z-10 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg"
      @click.stop
    >
      <div class="p-2">
        <div class="text-xs font-medium text-gray-500 mb-2">Who can see this field?</div>
        <button
          v-for="option in visibilityOptions"
          :key="option.value"
          @click="changeVisibility(option.value)"
          :class="[
            'w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors text-left',
            fieldData?.visibility === option.value 
              ? 'bg-blue-50 text-blue-700' 
              : 'hover:bg-gray-50 text-gray-700'
          ]"
        >
          <component :is="option.icon" class="w-4 h-4 mr-2" />
          <div>
            <div class="font-medium">{{ option.label }}</div>
            <div class="text-xs text-gray-500">{{ option.description }}</div>
          </div>
        </button>
      </div>
    </div>

    <!-- Field Value Display/Edit -->
    <div class="relative">
      <!-- Edit Mode -->
      <div v-if="isEditing" class="space-y-2">
        <!-- Text Input -->
        <textarea
          v-if="isTextArea"
          v-model="editValue"
          @keydown.enter.ctrl="saveField"
          @keydown.escape="cancelEdit"
          class="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          :rows="3"
          :placeholder="`Enter ${fieldLabels[fieldName] || fieldName}...`"
        />
        <input
          v-else
          v-model="editValue"
          @keydown.enter="saveField"
          @keydown.escape="cancelEdit"
          :type="getInputType()"
          class="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          :placeholder="`Enter ${fieldLabels[fieldName] || fieldName}...`"
        />
        
        <!-- Edit Controls -->
        <div class="flex justify-end gap-2">
          <button
            @click="cancelEdit"
            class="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="saveField"
            class="px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Save
          </button>
        </div>
      </div>

      <!-- Display Mode -->
      <div v-else class="min-h-[2rem] flex items-center">
        <!-- Field is visible -->
        <div v-if="fieldData?.is_visible !== false" class="flex-1">
          <!-- URL fields (show as links) -->
          <a 
            v-if="isUrlField && fieldValue"
            :href="fieldValue"
            target="_blank"
            class="text-blue-600 hover:text-blue-700 break-all"
          >
            {{ fieldValue }}
          </a>
          
          <!-- Choice fields (show display value) -->
          <span v-else-if="isChoiceField && fieldValue?.display" class="text-gray-900">
            {{ fieldValue.display }}
          </span>
          
          <!-- Regular fields -->
          <span 
            v-else-if="fieldValue" 
            :class="[
              'text-gray-900',
              isTextArea ? 'whitespace-pre-wrap' : ''
            ]"
          >
            {{ formatFieldValue(fieldValue) }}
          </span>
          
          <!-- Empty state for own profile -->
          <span v-else-if="isOwnProfile" class="text-gray-400 italic">
            Click edit to add {{ fieldLabels[fieldName] || fieldName }}
          </span>
          
          <!-- Empty state for others -->
          <span v-else class="text-gray-400 italic">
            Not provided
          </span>
        </div>

        <!-- Field is hidden -->
        <div v-else class="flex-1">
          <span class="text-gray-400 italic">
            🔒 Hidden from you
          </span>
        </div>
      </div>
    </div>

    <!-- Privacy Status Indicator -->
    <div v-if="isOwnProfile && fieldData?.visibility" class="mt-2 flex items-center text-xs text-gray-500">
      <component :is="visibilityIcon" class="w-3 h-3 mr-1" />
      {{ visibilityDisplay }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { 
  PencilIcon, 
  GlobeAltIcon, 
  UserGroupIcon, 
  UsersIcon, 
  LockClosedIcon 
} from '@heroicons/vue/24/outline'

const props = defineProps({
  fieldName: String,
  fieldData: Object,
  isOwnProfile: Boolean,
  fieldLabels: Object,
  isTextArea: Boolean
})

const emit = defineEmits(['update-field', 'toggle-visibility'])

// State
const isEditing = ref(false)
const editValue = ref('')
const showVisibilityMenu = ref(false)

// Privacy options
const visibilityOptions = [
  {
    value: 'public',
    label: 'Public',
    description: 'Anyone can see this',
    icon: GlobeAltIcon
  },
  {
    value: 'alumni_only',
    label: 'Alumni Only',
    description: 'Only verified alumni',
    icon: UserGroupIcon
  },
  {
    value: 'connections_only',
    label: 'Connections Only',
    description: 'Only your connections',
    icon: UsersIcon
  },
  {
    value: 'private',
    label: 'Private',
    description: 'Only you can see this',
    icon: LockClosedIcon
  }
]

// Computed properties
const fieldValue = computed(() => props.fieldData?.value)

const isUrlField = computed(() => {
  return ['linkedin_url', 'facebook_url', 'twitter_url', 'instagram_url', 'website_url'].includes(props.fieldName)
})

const isChoiceField = computed(() => {
  return fieldValue.value && typeof fieldValue.value === 'object' && fieldValue.value.display
})

const visibilityDisplay = computed(() => {
  const option = visibilityOptions.find(opt => opt.value === props.fieldData?.visibility)
  return option?.label || 'Alumni Only'
})

const visibilityIcon = computed(() => {
  const option = visibilityOptions.find(opt => opt.value === props.fieldData?.visibility)
  return option?.icon || UserGroupIcon
})

const visibilityButtonClass = computed(() => {
  const visibility = props.fieldData?.visibility || 'alumni_only'
  const classes = {
    public: 'text-green-600 hover:text-green-700 hover:bg-green-50',
    alumni_only: 'text-blue-600 hover:text-blue-700 hover:bg-blue-50',
    connections_only: 'text-purple-600 hover:text-purple-700 hover:bg-purple-50',
    private: 'text-gray-600 hover:text-gray-700 hover:bg-gray-50'
  }
  return classes[visibility] || classes.alumni_only
})

// Methods
function getInputType() {
  if (props.fieldName === 'email') return 'email'
  if (props.fieldName === 'birth_date') return 'date'
  if (isUrlField.value) return 'url'
  return 'text'
}

function formatFieldValue(value) {
  if (!value) return ''
  
  // Format dates
  if (props.fieldName === 'birth_date' && typeof value === 'string') {
    try {
      return new Date(value).toLocaleDateString()
    } catch {
      return value
    }
  }
  
  return value
}

function startEditing() {
  if (!props.isOwnProfile) return
  
  isEditing.value = true
  editValue.value = isChoiceField.value 
    ? fieldValue.value?.value || '' 
    : fieldValue.value || ''
}

function cancelEdit() {
  isEditing.value = false
  editValue.value = ''
}

function saveField() {
  if (!editValue.value && editValue.value !== '') {
    cancelEdit()
    return
  }
  
  emit('update-field', props.fieldName, editValue.value)
  isEditing.value = false
  editValue.value = ''
}

function toggleVisibilityMenu() {
  showVisibilityMenu.value = !showVisibilityMenu.value
}

function changeVisibility(newVisibility) {
  emit('toggle-visibility', props.fieldName, newVisibility)
  showVisibilityMenu.value = false
}

// Close visibility menu when clicking outside
function handleClickOutside(event) {
  if (showVisibilityMenu.value && !event.target.closest('.relative')) {
    showVisibilityMenu.value = false
  }
}

// Watch for clicks outside
watch(showVisibilityMenu, (newValue) => {
  if (newValue) {
    document.addEventListener('click', handleClickOutside)
  } else {
    document.removeEventListener('click', handleClickOutside)
  }
})
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>