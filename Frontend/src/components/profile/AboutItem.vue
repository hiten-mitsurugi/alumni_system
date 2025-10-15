<template>
  <div class="flex items-center py-3 hover:bg-gray-50 rounded-lg px-2 -mx-2 group">
    <!-- Icon -->
    <div class="flex-shrink-0 mr-4">
      <!-- Inline SVGs for social media brand icons -->
      <template v-if="fieldName === 'facebook_url'">
        <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24" class="w-5 h-5 text-blue-700"><path d="M22.675 0h-21.35c-.733 0-1.325.592-1.325 1.326v21.348c0 .733.592 1.326 1.325 1.326h11.495v-9.294h-3.128v-3.622h3.128v-2.672c0-3.1 1.893-4.788 4.659-4.788 1.325 0 2.463.099 2.797.143v3.24l-1.918.001c-1.504 0-1.797.715-1.797 1.763v2.313h3.587l-.467 3.622h-3.12v9.294h6.116c.73 0 1.323-.593 1.323-1.326v-21.349c0-.734-.593-1.326-1.324-1.326z"/></svg>
      </template>
      <template v-else-if="fieldName === 'twitter_url'">
        <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24" class="w-5 h-5 text-blue-500"><path d="M24 4.557a9.83 9.83 0 0 1-2.828.775 4.932 4.932 0 0 0 2.165-2.724c-.951.564-2.005.974-3.127 1.195a4.916 4.916 0 0 0-8.38 4.482c-4.083-.205-7.697-2.162-10.125-5.138a4.822 4.822 0 0 0-.664 2.475c0 1.708.87 3.216 2.188 4.099a4.904 4.904 0 0 1-2.229-.616c-.054 2.281 1.581 4.415 3.949 4.89a4.936 4.936 0 0 1-2.224.084c.627 1.956 2.444 3.377 4.6 3.417a9.867 9.867 0 0 1-6.102 2.104c-.396 0-.787-.023-1.175-.069a13.945 13.945 0 0 0 7.548 2.212c9.057 0 14.009-7.513 14.009-14.009 0-.213-.005-.425-.014-.636a10.012 10.012 0 0 0 2.457-2.548z"/></svg>
      </template>
      <template v-else-if="fieldName === 'linkedin_url'">
        <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24" class="w-5 h-5 text-blue-800"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.761 0 5-2.239 5-5v-14c0-2.761-2.239-5-5-5zm-11 19h-3v-10h3v10zm-1.5-11.268c-.966 0-1.75-.784-1.75-1.75s.784-1.75 1.75-1.75 1.75.784 1.75 1.75-.784 1.75-1.75 1.75zm13.5 11.268h-3v-5.604c0-1.337-.025-3.063-1.868-3.063-1.868 0-2.154 1.459-2.154 2.967v5.7h-3v-10h2.881v1.367h.041c.401-.761 1.379-1.563 2.841-1.563 3.039 0 3.6 2.001 3.6 4.601v5.595z"/></svg>
      </template>
      <template v-else-if="fieldName === 'instagram_url'">
        <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24" class="w-5 h-5 text-pink-500"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 1.366.062 2.633.334 3.608 1.308.974.974 1.246 2.242 1.308 3.608.058 1.266.069 1.646.069 4.85s-.012 3.584-.07 4.85c-.062 1.366-.334 2.633-1.308 3.608-.974.974-2.242 1.246-3.608 1.308-1.266.058-1.646.069-4.85.069s-3.584-.012-4.85-.07c-1.366-.062-2.633-.334-3.608-1.308-.974-.974-1.246-2.242-1.308-3.608-.058-1.266-.069-1.646-.069-4.85s.012-3.584.07-4.85c.062-1.366.334-2.633 1.308-3.608.974-.974 2.242-1.246 3.608-1.308 1.266-.058 1.646-.069 4.85-.069zm0-2.163c-3.259 0-3.667.012-4.947.07-1.276.058-2.687.334-3.678 1.325-.991.991-1.267 2.402-1.325 3.678-.058 1.28-.07 1.688-.07 4.947s.012 3.667.07 4.947c.058 1.276.334 2.687 1.325 3.678.991.991 2.402 1.267 3.678 1.325 1.28.058 1.688.07 4.947.07s3.667-.012 4.947-.07c1.276-.058 2.687-.334 3.678-1.325.991-.991 1.267-2.402 1.325-3.678.058-1.28.07-1.688.07-4.947s-.012-3.667-.07-4.947c-.058-1.276-.334-2.687-1.325-3.678-.991-.991-2.402-1.267-3.678-1.325-1.28-.058-1.688-.07-4.947-.07zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zm0 10.162a3.999 3.999 0 1 1 0-7.998 3.999 3.999 0 0 1 0 7.998zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>
      </template>
      <template v-else>
        <component 
          :is="iconComponent" 
          class="w-5 h-5 text-gray-600"
        />
      </template>
    </div>

    <!-- Content -->
    <div class="flex-grow min-w-0">
      <!-- Edit Mode -->
      <div v-if="isEditing" class="space-y-2">
        <!-- Dropdown for choice fields -->
        <select
          v-if="isChoiceField"
          v-model="editValue"
          @keydown.enter="saveField"
          @keydown.escape="cancelEdit"
          class="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          auto-focus
        >
          <option value="">Select {{ fieldLabel }}</option>
          <option 
            v-for="option in choiceOptions" 
            :key="option.value" 
            :value="option.value"
          >
            {{ option.label }}
          </option>
        </select>
        
        <!-- Textarea for text areas -->
        <textarea
          v-else-if="isTextArea"
          v-model="editValue"
          @keydown.enter.ctrl="saveField"
          @keydown.escape="cancelEdit"
          class="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          :rows="3"
          :placeholder="`Enter ${fieldLabel}...`"
          auto-focus
        />
        
        <!-- Regular input -->
        <input
          v-else
          v-model="editValue"
          @keydown.enter="saveField"
          @keydown.escape="cancelEdit"
          :type="inputType"
          class="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          :placeholder="`Enter ${fieldLabel}...`"
          auto-focus
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
      <div v-else class="flex items-center justify-between">
        <div class="flex-grow">
          <!-- URL fields (show as links) -->
          <a 
            v-if="isUrl && displayValue"
            :href="displayValue"
            target="_blank"
            class="text-blue-600 hover:text-blue-700 hover:underline break-all"
          >
            {{ displayValue }}
          </a>
          
          <!-- Regular fields -->
          <div v-else-if="displayValue" class="text-gray-900">
            <div class="font-medium text-sm text-gray-600 mb-1">{{ fieldLabel }}</div>
            <div :class="isTextArea ? 'whitespace-pre-wrap' : ''">
              {{ formatValue(displayValue) }}
            </div>
          </div>
          
          <!-- Empty state for own profile -->
          <div v-else-if="isOwnProfile" class="text-gray-400">
            <div class="font-medium text-sm text-gray-600 mb-1">{{ fieldLabel }}</div>
            <button @click="startEditing" class="text-blue-600 hover:text-blue-700 text-sm">
              Add {{ fieldLabel.toLowerCase() }}
            </button>
          </div>
        </div>

        <!-- Edit/Privacy controls for own profile -->
        <div v-if="isOwnProfile" class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <!-- Privacy indicator -->
          <div class="relative">
            <button 
              @click="toggleVisibilityMenu"
              :class="visibilityButtonClass"
              class="p-1 rounded transition-colors"
              :title="`Privacy: ${visibilityDisplay}`"
            >
              <EyeIcon v-if="(fieldData?.visibility || 'connections_only') === 'everyone'" class="w-4 h-4" />
              <LockClosedIcon v-else-if="(fieldData?.visibility || 'connections_only') === 'only_me'" class="w-4 h-4" />
              <ShieldCheckIcon v-else class="w-4 h-4" />
            </button>
            
            <!-- Privacy Menu - positioned relative to the privacy button -->
            <div 
              v-if="showVisibilityMenu" 
              class="absolute right-0 top-8 z-10 w-48 bg-white border border-gray-200 rounded-lg shadow-lg"
              @click.stop
            >
              <div class="p-2">
                <div class="text-xs font-medium text-gray-500 mb-2">Who can see this?</div>
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
          </div>
          
          <!-- Edit button -->
          <button 
            @click="startEditing"
            class="p-1 text-gray-500 hover:text-blue-600 rounded transition-colors"
            title="Edit"
          >
            <PencilIcon class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { 
  PencilIcon,
  GlobeAltIcon, 
  UserGroupIcon, 
  UsersIcon, 
  LockClosedIcon,
  EyeIcon,
  ShieldCheckIcon,
  PlusIcon,
  // Content icons
  DocumentTextIcon,
  BriefcaseIcon,
  EnvelopeIcon,
  PhoneIcon,
  DevicePhoneMobileIcon,
  MapPinIcon,
  HomeIcon,
  BuildingOfficeIcon,
  CakeIcon,
  UserIcon,
  HeartIcon
} from '@heroicons/vue/24/outline'

// Inline SVGs for brand icons
const LinkedInIcon = {
  template: `<svg xmlns='http://www.w3.org/2000/svg' fill='currentColor' viewBox='0 0 24 24' class='w-5 h-5'><path d='M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.761 0 5-2.239 5-5v-14c0-2.761-2.239-5-5-5zm-11 19h-3v-10h3v10zm-1.5-11.268c-.966 0-1.75-.784-1.75-1.75s.784-1.75 1.75-1.75 1.75.784 1.75 1.75-.784 1.75-1.75 1.75zm13.5 11.268h-3v-5.604c0-1.337-.025-3.063-1.868-3.063-1.868 0-2.154 1.459-2.154 2.967v5.7h-3v-10h2.881v1.367h.041c.401-.761 1.379-1.563 2.841-1.563 3.039 0 3.6 2.001 3.6 4.601v5.595z'/></svg>`
}
const FacebookIcon = {
  template: `<svg xmlns='http://www.w3.org/2000/svg' fill='currentColor' viewBox='0 0 24 24' class='w-5 h-5'><path d='M22.675 0h-21.35c-.733 0-1.325.592-1.325 1.326v21.348c0 .733.592 1.326 1.325 1.326h11.495v-9.294h-3.128v-3.622h3.128v-2.672c0-3.1 1.893-4.788 4.659-4.788 1.325 0 2.463.099 2.797.143v3.24l-1.918.001c-1.504 0-1.797.715-1.797 1.763v2.313h3.587l-.467 3.622h-3.12v9.294h6.116c.73 0 1.323-.593 1.323-1.326v-21.349c0-.734-.593-1.326-1.324-1.326z'/></svg>`
}
const TwitterIcon = {
  template: `<svg xmlns='http://www.w3.org/2000/svg' fill='currentColor' viewBox='0 0 24 24' class='w-5 h-5'><path d='M24 4.557a9.83 9.83 0 0 1-2.828.775 4.932 4.932 0 0 0 2.165-2.724c-.951.564-2.005.974-3.127 1.195a4.916 4.916 0 0 0-8.38 4.482c-4.083-.205-7.697-2.162-10.125-5.138a4.822 4.822 0 0 0-.664 2.475c0 1.708.87 3.216 2.188 4.099a4.904 4.904 0 0 1-2.229-.616c-.054 2.281 1.581 4.415 3.949 4.89a4.936 4.936 0 0 1-2.224.084c.627 1.956 2.444 3.377 4.6 3.417a9.867 9.867 0 0 1-6.102 2.104c-.396 0-.787-.023-1.175-.069a13.945 13.945 0 0 0 7.548 2.212c9.057 0 14.009-7.513 14.009-14.009 0-.213-.005-.425-.014-.636a10.012 10.012 0 0 0 2.457-2.548z'/></svg>`
}
const InstagramIcon = {
  template: `<svg xmlns='http://www.w3.org/2000/svg' fill='currentColor' viewBox='0 0 24 24' class='w-5 h-5'><path d='M12 2.163c3.204 0 3.584.012 4.85.07 1.366.062 2.633.334 3.608 1.308.974.974 1.246 2.242 1.308 3.608.058 1.266.069 1.646.069 4.85s-.012 3.584-.07 4.85c-.062 1.366-.334 2.633-1.308 3.608-.974.974-2.242 1.246-3.608 1.308-1.266.058-1.646.069-4.85.069s-3.584-.012-4.85-.07c-1.366-.062-2.633-.334-3.608-1.308-.974-.974-1.246-2.242-1.308-3.608-.058-1.266-.069-1.646-.069-4.85s.012-3.584.07-4.85c.062-1.366.334-2.633 1.308-3.608.974-.974 2.242-1.246 3.608-1.308 1.266-.058 1.646-.069 4.85-.069zm0-2.163c-3.259 0-3.667.012-4.947.07-1.276.058-2.687.334-3.678 1.325-.991.991-1.267 2.402-1.325 3.678-.058 1.28-.07 1.688-.07 4.947s.012 3.667.07 4.947c.058 1.276.334 2.687 1.325 3.678.991.991 2.402 1.267 3.678 1.325 1.28.058 1.688.07 4.947.07s3.667-.012 4.947-.07c1.276-.058 2.687-.334 3.678-1.325.991-.991 1.267-2.402 1.325-3.678.058-1.28.07-1.688.07-4.947s-.012-3.667-.07-4.947c-.058-1.276-.334-2.687-1.325-3.678-.991-.991-2.402-1.267-3.678-1.325-1.28-.058-1.688-.07-4.947-.07zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zm0 10.162a3.999 3.999 0 1 1 0-7.998 3.999 3.999 0 0 1 0 7.998zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z'/></svg>`
}

const props = defineProps({
  icon: String,
  fieldData: Object,
  fieldName: String,
  fieldLabel: String,
  isOwnProfile: Boolean,
  isTextArea: Boolean,
  isUrl: Boolean
})

// Choice field options
const genderChoices = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'non_binary', label: 'Non-binary' },
  { value: 'prefer_not_to_say', label: 'Prefer not to say' },
  { value: 'other', label: 'Other' }
]

const civilStatusChoices = [
  { value: 'single', label: 'Single' },
  { value: 'married', label: 'Married' },
  { value: 'separated', label: 'Separated' },
  { value: 'widowed', label: 'Widowed' }
]

const emit = defineEmits(['update-field', 'toggle-visibility'])

// State
const isEditing = ref(false)
const editValue = ref('')
const showVisibilityMenu = ref(false)

// Icon mapping
const iconMap = {
  'document-text': DocumentTextIcon,
  'briefcase': BriefcaseIcon,
  'envelope': EnvelopeIcon,
  'phone': PhoneIcon,
  'device-phone-mobile': DevicePhoneMobileIcon,
  'map-pin': MapPinIcon,
  'home': HomeIcon,
  'building-office': BuildingOfficeIcon,
  'cake': CakeIcon,
  'user': UserIcon,
  'heart': HeartIcon,
  'globe-alt': GlobeAltIcon,
  'linkedin': LinkedInIcon,
  'facebook': FacebookIcon,
  'twitter': TwitterIcon,
  'instagram': InstagramIcon
}

// Privacy options
const visibilityOptions = [
  {
    value: 'everyone',
    label: 'For Everyone',
    description: 'Anyone can see this',
    icon: EyeIcon
  },
  {
    value: 'connections_only',
    label: 'For Connections',
    description: 'Only your connections',
    icon: UsersIcon
  },
  {
    value: 'only_me',
    label: 'Only for Me',
    description: 'Only you can see this',
    icon: LockClosedIcon
  }
]

// Computed properties
const iconComponent = computed(() => {
  return iconMap[props.icon] || UserIcon
})

const isChoiceField = computed(() => {
  return ['gender', 'civil_status'].includes(props.fieldName)
})

const choiceOptions = computed(() => {
  if (props.fieldName === 'gender') return genderChoices
  if (props.fieldName === 'civil_status') return civilStatusChoices
  return []
})

const displayValue = computed(() => {
  if (!props.fieldData?.value) return null
  
        // If backend sends { value, display }, always show display in view mode
        if (typeof props.fieldData.value === 'object' && props.fieldData.value.display) {
          return props.fieldData.value.display
        }
        
        // If just a string, try to map to label for choice fields
        if (isChoiceField.value) {
          const choice = choiceOptions.value.find(option => option.value === props.fieldData.value)
          return choice ? choice.label : props.fieldData.value
        }
        
        return props.fieldData.value
})

const inputType = computed(() => {
  if (props.fieldName === 'email') return 'email'
  if (props.fieldName === 'birth_date') return 'date'
  if (props.isUrl) return 'url'
  return 'text'
})

const visibilityDisplay = computed(() => {
  const option = visibilityOptions.find(opt => opt.value === props.fieldData?.visibility)
  return option?.label || 'For Connections'
})

const visibilityIcon = computed(() => {
  const option = visibilityOptions.find(opt => opt.value === props.fieldData?.visibility)
  return option?.icon || UsersIcon
})

const visibilityButtonClass = computed(() => {
  const visibility = props.fieldData?.visibility || 'connections_only'
  const classes = {
    everyone: 'text-green-600 hover:text-green-700 hover:bg-green-50',
    connections_only: 'text-blue-600 hover:text-blue-700 hover:bg-blue-50',
    only_me: 'text-red-600 hover:text-red-700 hover:bg-red-50'
  }
  return classes[visibility] || classes.connections_only
})

// Methods
function formatValue(value) {
  if (!value) return ''
  
  // Format dates
  if (props.fieldName === 'birth_date' && typeof value === 'string') {
    try {
      return new Date(value).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    } catch {
      return value
    }
  }
  
  return value
}

function startEditing() {
  if (!props.isOwnProfile) return
  
  isEditing.value = true
  
  // For choice fields, use the raw value
  if (isChoiceField.value) {
    editValue.value = props.fieldData?.value || ''
  } else {
    // For other fields, handle object values
    editValue.value = typeof props.fieldData?.value === 'object' 
      ? props.fieldData.value?.value || '' 
      : props.fieldData?.value || ''
  }
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
</script>

<style scoped>
/* Custom styles if needed */
</style>