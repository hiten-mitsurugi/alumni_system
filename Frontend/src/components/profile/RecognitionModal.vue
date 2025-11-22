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
          {{ recognition ? 'Edit Recognition' : 'Add Recognition' }}
        </h2>
      </div>

      <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
        <!-- Title -->
        <div>
          <label :class="[
            'block text-sm font-medium mb-2',
            themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
          ]">
            Recognition Title *
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
            placeholder="e.g., Outstanding Community Volunteer"
          />
        </div>

        <!-- Awarded By -->
        <div>
          <label :class="[
            'block text-sm font-medium mb-2',
            themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
          ]">
            Awarded By *
          </label>
          <input
            v-model="formData.awarded_by"
            type="text"
            required
            :class="[
              'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
              themeStore.isDarkMode 
                ? 'bg-gray-700 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-900'
            ]"
            placeholder="e.g., City Government, Regional Youth Council"
          />
        </div>

        <!-- Category and Level -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label :class="[
              'block text-sm font-medium mb-2',
              themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
            ]">
              Category
            </label>
            <select
              v-model="formData.category"
              :class="[
                'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                themeStore.isDarkMode 
                  ? 'bg-gray-700 border-gray-600 text-white' 
                  : 'bg-white border-gray-300 text-gray-900'
              ]"
            >
              <option value="">Select category</option>
              <option value="community_service">Community Service</option>
              <option value="leadership">Leadership</option>
              <option value="volunteer">Volunteer Work</option>
              <option value="sports">Sports</option>
              <option value="arts">Arts & Culture</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label :class="[
              'block text-sm font-medium mb-2',
              themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
            ]">
              Level
            </label>
            <select
              v-model="formData.level"
              :class="[
                'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                themeStore.isDarkMode 
                  ? 'bg-gray-700 border-gray-600 text-white' 
                  : 'bg-white border-gray-300 text-gray-900'
              ]"
            >
              <option value="">Select level</option>
              <option value="local">Local</option>
              <option value="regional">Regional</option>
              <option value="national">National</option>
              <option value="international">International</option>
            </select>
          </div>
        </div>

        <!-- Date Awarded -->
        <div>
          <label :class="[
            'block text-sm font-medium mb-2',
            themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
          ]">
            Date Awarded
          </label>
          <input
            v-model="formData.date_awarded"
            type="date"
            :class="[
              'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
              themeStore.isDarkMode 
                ? 'bg-gray-700 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-900'
            ]"
          />
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
            placeholder="Describe what this recognition was for and its significance"
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
            :disabled="!formData.title.trim() || !formData.awarded_by.trim()"
            :class="[
              'px-4 py-2 text-sm font-medium rounded-md transition-colors',
              (formData.title.trim() && formData.awarded_by.trim())
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-400 text-gray-200 cursor-not-allowed'
            ]"
          >
            {{ recognition ? 'Update' : 'Save' }}
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
  recognition: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

const themeStore = useThemeStore()

// Form data
const formData = ref({
  title: '',
  awarded_by: '',
  category: '',
  level: '',
  date_awarded: '',
  description: '',
  visibility: 'connections_only'
})

// Watch for changes in recognition prop to populate form
watch(() => props.recognition, (newRecognition) => {
  if (newRecognition) {
    formData.value = {
      title: newRecognition.title || '',
      awarded_by: newRecognition.awarded_by || '',
      category: newRecognition.category || '',
      level: newRecognition.level || '',
      date_awarded: newRecognition.date_awarded || '',
      description: newRecognition.description || '',
      visibility: newRecognition.visibility || 'connections_only'
    }
  } else {
    // Reset form for new recognition
    formData.value = {
      title: '',
      awarded_by: '',
      category: '',
      level: '',
      date_awarded: '',
      description: '',
      visibility: 'connections_only'
    }
  }
}, { immediate: true })

const handleSubmit = () => {
  if (!formData.value.title.trim() || !formData.value.awarded_by.trim()) {
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