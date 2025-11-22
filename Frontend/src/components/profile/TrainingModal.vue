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
            v-model="formData.training_title"
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

        <!-- Conducted By -->
        <div>
          <label :class="[
            'block text-sm font-medium mb-2',
            themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
          ]">
            Conducted By *
          </label>
          <input
            v-model="formData.conducted_by"
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

        <!-- Training Type and Duration -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label :class="[
              'block text-sm font-medium mb-2',
              themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
            ]">
              Training Type
            </label>
            <select
              v-model="formData.training_type"
              :class="[
                'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                themeStore.isDarkMode 
                  ? 'bg-gray-700 border-gray-600 text-white' 
                  : 'bg-white border-gray-300 text-gray-900'
              ]"
            >
              <option value="">Select type</option>
              <option value="workshop">Workshop</option>
              <option value="seminar">Seminar</option>
              <option value="certification">Certification</option>
              <option value="bootcamp">Bootcamp</option>
              <option value="online_course">Online Course</option>
              <option value="conference">Conference</option>
            </select>
          </div>
          <div>
            <label :class="[
              'block text-sm font-medium mb-2',
              themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
            ]">
              Duration
            </label>
            <input
              v-model="formData.duration"
              type="text"
              :class="[
                'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                themeStore.isDarkMode 
                  ? 'bg-gray-700 border-gray-600 text-white' 
                  : 'bg-white border-gray-300 text-gray-900'
              ]"
              placeholder="e.g., 40 hours, 3 days, 1 week"
            />
          </div>
        </div>

        <!-- Date Completed and Certificate Number -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label :class="[
              'block text-sm font-medium mb-2',
              themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
            ]">
              Date Completed
            </label>
            <input
              v-model="formData.date_completed"
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
              Certificate Number
            </label>
            <input
              v-model="formData.certificate_number"
              type="text"
              :class="[
                'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                themeStore.isDarkMode 
                  ? 'bg-gray-700 border-gray-600 text-white' 
                  : 'bg-white border-gray-300 text-gray-900'
              ]"
              placeholder="e.g., REACT2023-001"
            />
          </div>
        </div>

        <!-- Skills Gained -->
        <div>
          <label :class="[
            'block text-sm font-medium mb-2',
            themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
          ]">
            Skills Gained
            <span class="text-xs text-gray-500">(Enter skills separated by commas)</span>
          </label>
          <input
            v-model="skillsInput"
            type="text"
            :class="[
              'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
              themeStore.isDarkMode 
                ? 'bg-gray-700 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-900'
            ]"
            placeholder="e.g., React, Redux, TypeScript"
          />
          <div v-if="formData.skills_gained && formData.skills_gained.length > 0" class="mt-2 flex flex-wrap gap-2">
            <span 
              v-for="(skill, index) in formData.skills_gained" 
              :key="index"
              class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full flex items-center"
            >
              {{ skill }}
              <button 
                type="button"
                @click="removeSkill(index)"
                class="ml-1 text-blue-600 hover:text-blue-800"
              >
                ×
              </button>
            </span>
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
            placeholder="Describe the training content, outcomes, and key learnings"
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
            :disabled="!formData.training_title.trim() || !formData.conducted_by.trim()"
            :class="[
              'px-4 py-2 text-sm font-medium rounded-md transition-colors',
              (formData.training_title.trim() && formData.conducted_by.trim())
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
  training_title: '',
  conducted_by: '',
  training_type: '',
  duration: '',
  date_completed: '',
  certificate_number: '',
  skills_gained: [],
  description: '',
  visibility: 'connections_only'
})

const skillsInput = ref('')

// Watch skills input for comma-separated values
watch(skillsInput, (newValue) => {
  if (newValue.includes(',')) {
    const skills = newValue.split(',').map(skill => skill.trim()).filter(skill => skill)
    const lastSkill = skills.pop() || ''
    
    // Add complete skills to the array
    skills.forEach(skill => {
      if (!formData.value.skills_gained.includes(skill)) {
        formData.value.skills_gained.push(skill)
      }
    })
    
    // Keep the last (incomplete) skill in the input
    skillsInput.value = lastSkill
  }
})

const removeSkill = (index) => {
  formData.value.skills_gained.splice(index, 1)
}

// Watch for changes in training prop to populate form
watch(() => props.training, (newTraining) => {
  if (newTraining) {
    formData.value = {
      training_title: newTraining.training_title || '',
      conducted_by: newTraining.conducted_by || '',
      training_type: newTraining.training_type || '',
      duration: newTraining.duration || '',
      date_completed: newTraining.date_completed || '',
      certificate_number: newTraining.certificate_number || '',
      skills_gained: newTraining.skills_gained || [],
      description: newTraining.description || '',
      visibility: newTraining.visibility || 'connections_only'
    }
    skillsInput.value = ''
  } else {
    // Reset form for new training
    formData.value = {
      training_title: '',
      conducted_by: '',
      training_type: '',
      duration: '',
      date_completed: '',
      certificate_number: '',
      skills_gained: [],
      description: '',
      visibility: 'connections_only'
    }
    skillsInput.value = ''
  }
}, { immediate: true })

const handleSubmit = () => {
  if (!formData.value.training_title.trim() || !formData.value.conducted_by.trim()) {
    return
  }

  // Add any remaining skill from input
  if (skillsInput.value.trim() && !formData.value.skills_gained.includes(skillsInput.value.trim())) {
    formData.value.skills_gained.push(skillsInput.value.trim())
  }

  // Clean up form data
  const cleanedData = { ...formData.value }
  
  // Remove empty strings for optional fields
  Object.keys(cleanedData).forEach(key => {
    if (cleanedData[key] === '' && key !== 'skills_gained') {
      cleanedData[key] = null
    }
  })

  emit('save', cleanedData)
}
</script>