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
          {{ training ? 'Edit Training' : 'Add Training' }}
        </h2>
      </div>

      <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
        <!-- Training Title -->
        <div>
          <label :class="[
            'block text-sm font-medium mb-2',
            themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
          ]">
            Training Title *
          </label>
          <input
            v-model="formData.title"
            type="text"
            required
            :class="[
              'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
              themeStore.isDarkMode 
                ? 'bg-gray-700 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-900'
            ]"
            placeholder="e.g., Advanced React Development"
          />
        </div>

        <!-- Organization -->
        <div>
          <label :class="[
            'block text-sm font-medium mb-2',
            themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
          ]">
            Organization *
          </label>
          <input
            v-model="formData.organization"
            type="text"
            required
            :class="[
              'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
              themeStore.isDarkMode 
                ? 'bg-gray-700 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-900'
            ]"
            placeholder="e.g., Tech Academy, Project Management Institute"
          />
        </div>

        <!-- Date Range -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label :class="[
              'block text-sm font-medium mb-2',
              themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
            ]">
              Start Date *
            </label>
            <input
              v-model="formData.date_start"
              type="date"
              required
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
              End Date
            </label>
            <input
              v-model="formData.date_end"
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

        <!-- Location -->
        <div>
          <label :class="[
            'block text-sm font-medium mb-2',
            themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
          ]">
            Location
          </label>
          <input
            v-model="formData.location"
            type="text"
            :class="[
              'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
              themeStore.isDarkMode 
                ? 'bg-gray-700 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-900'
            ]"
            placeholder="e.g., Manila, Philippines or Online"
          />
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
            :disabled="!formData.title.trim() || !formData.organization.trim() || !formData.date_start"
            :class="[
              'px-4 py-2 text-sm font-medium rounded-md transition-colors',
              (formData.title.trim() && formData.organization.trim() && formData.date_start)
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-400 text-gray-200 cursor-not-allowed'
            ]"
          >
            {{ training ? 'Update' : 'Save' }}
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
  training: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

const themeStore = useThemeStore()

// Form data
const formData = ref({
  title: '',
  organization: '',
  date_start: '',
  date_end: '',
  location: ''
})

// Remove skillsInput since skills_gained doesn't exist in backend
// const skillsInput = ref('')

// Watch for changes in training prop to populate form
watch(() => props.training, (newTraining) => {
  if (newTraining) {
    formData.value = {
      title: newTraining.title || '',
      organization: newTraining.organization || '',
      date_start: newTraining.date_start || '',
      date_end: newTraining.date_end || '',
      location: newTraining.location || ''
    }
  } else {
    // Reset form for new training
    formData.value = {
      title: '',
      organization: '',
      date_start: '',
      date_end: '',
      location: ''
    }
  }
}, { immediate: true })

const handleSubmit = () => {
  if (!formData.value.title.trim() || !formData.value.organization.trim() || !formData.value.date_start) {
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