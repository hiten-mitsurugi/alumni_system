<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="$emit('close')">
    <div :class="[
      'w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-lg shadow-lg',
      themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white'
    ]">
      <div :class="[
        'p-6 border-b',
        themeStore.isDarkMode ? 'border-gray-700' : 'border-gray-200'
      ]">
        <h2 :class="[
          'text-xl font-semibold',
          themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
        ]">
          {{ membership ? 'Edit Membership' : 'Add Membership' }}
        </h2>
      </div>

      <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
        <!-- Organization Name -->
        <div>
          <label :class="[
            'block text-sm font-medium mb-2',
            themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
          ]">
            Organization Name *
          </label>
          <input
            v-model="formData.organization_name"
            type="text"
            required
            :class="[
              'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
              themeStore.isDarkMode 
                ? 'bg-gray-700 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-900'
            ]"
            placeholder="e.g., Philippine Computer Society"
          />
        </div>

        <!-- Position -->
        <div>
          <label :class="[
            'block text-sm font-medium mb-2',
            themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
          ]">
            Position/Role
          </label>
          <input
            v-model="formData.position"
            type="text"
            :class="[
              'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
              themeStore.isDarkMode 
                ? 'bg-gray-700 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-900'
            ]"
            placeholder="e.g., Board Member, Active Member"
          />
        </div>

        <!-- Membership Type -->
        <div>
          <label :class="[
            'block text-sm font-medium mb-2',
            themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
          ]">
            Membership Type
          </label>
          <select
            v-model="formData.membership_type"
            :class="[
              'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
              themeStore.isDarkMode 
                ? 'bg-gray-700 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-900'
            ]"
          >
            <option value="">Select membership type</option>
            <option value="active">Active Member</option>
            <option value="inactive">Inactive Member</option>
            <option value="honorary">Honorary Member</option>
            <option value="lifetime">Lifetime Member</option>
          </select>
        </div>

        <!-- Date Range -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label :class="[
              'block text-sm font-medium mb-2',
              themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
            ]">
              Date Joined
            </label>
            <input
              v-model="formData.date_joined"
              type="date"
              :class="[
                'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                themeStore.isDarkMode 
                  ? 'bg-gray-700 border-gray-600 text-white' 
                  : 'bg-white border-gray-300 text-gray-900'
              ]"
            />
          </div>
          <div>
            <label :class="[
              'block text-sm font-medium mb-2',
              themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
            ]">
              Date Ended (if applicable)
            </label>
            <input
              v-model="formData.date_ended"
              type="date"
              :class="[
                'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                themeStore.isDarkMode 
                  ? 'bg-gray-700 border-gray-600 text-white' 
                  : 'bg-white border-gray-300 text-gray-900'
              ]"
            />
          </div>
        </div>

        <!-- Description -->
        <div>
          <label :class="[
            'block text-sm font-medium mb-2',
            themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
          ]">
            Description
          </label>
          <textarea
            v-model="formData.description"
            rows="3"
            :class="[
              'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
              themeStore.isDarkMode 
                ? 'bg-gray-700 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-900'
            ]"
            placeholder="Brief description of your role or involvement"
          ></textarea>
        </div>

        <!-- Privacy Setting -->
        <div>
          <label :class="[
            'block text-sm font-medium mb-2',
            themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
          ]">
            Visibility
          </label>
          <select
            v-model="formData.visibility"
            :class="[
              'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
              themeStore.isDarkMode 
                ? 'bg-gray-700 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-900'
            ]"
          >
            <option value="public">Public</option>
            <option value="connections_only">Connections Only</option>
            <option value="private">Private</option>
          </select>
        </div>

        <!-- Form Actions -->
        <div :class="[
          'flex justify-end space-x-3 pt-4 border-t',
          themeStore.isDarkMode ? 'border-gray-700' : 'border-gray-200'
        ]">
          <button
            type="button"
            @click="$emit('close')"
            :class="[
              'px-4 py-2 text-sm font-medium rounded-md transition-colors',
              themeStore.isDarkMode
                ? 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
            ]"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="!formData.organization_name.trim()"
            :class="[
              'px-4 py-2 text-sm font-medium rounded-md transition-colors',
              formData.organization_name.trim()
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-400 text-gray-200 cursor-not-allowed'
            ]"
          >
            {{ membership ? 'Update' : 'Save' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'
import { useThemeStore } from '@/stores/theme'

const props = defineProps({
  membership: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

const themeStore = useThemeStore()

// Form data
const formData = ref({
  organization_name: '',
  position: '',
  membership_type: '',
  date_joined: '',
  date_ended: '',
  description: '',
  visibility: 'connections_only'
})

// Watch for changes in membership prop to populate form
watch(() => props.membership, (newMembership) => {
  if (newMembership) {
    formData.value = {
      organization_name: newMembership.organization_name || '',
      position: newMembership.position || '',
      membership_type: newMembership.membership_type || '',
      date_joined: newMembership.date_joined || '',
      date_ended: newMembership.date_ended || '',
      description: newMembership.description || '',
      visibility: newMembership.visibility || 'connections_only'
    }
  } else {
    // Reset form for new membership
    formData.value = {
      organization_name: '',
      position: '',
      membership_type: '',
      date_joined: '',
      date_ended: '',
      description: '',
      visibility: 'connections_only'
    }
  }
}, { immediate: true })

const handleSubmit = () => {
  if (!formData.value.organization_name.trim()) {
    return
  }

  // Clean up form data
  const cleanedData = { ...formData.value }
  
  // Remove empty strings for optional fields
  Object.keys(cleanedData).forEach(key => {
    if (cleanedData[key] === '') {
      cleanedData[key] = null
    }
  })

  emit('save', cleanedData)
}
</script>