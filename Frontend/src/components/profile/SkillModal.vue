<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
      <!-- Modal Header -->
      <div class="flex items-center justify-between p-6 border-b">
        <h3 class="text-lg font-semibold text-gray-900">
          {{ isEditing ? 'Edit Skill' : 'Add Skill' }}
        </h3>
        <button 
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Modal Body -->
      <div class="p-6">
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Category (Required First) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Category *
            </label>
            <select
              v-model="form.category"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">Select category</option>
              <option value="technical">Technical</option>
              <option value="soft_skills">Soft Skills</option>
              <option value="languages">Languages</option>
              <option value="tools">Tools & Software</option>
              <option value="other">Other</option>
            </select>
          </div>

          <!-- Skill Name -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Skill Name *
            </label>
            <input
              v-model="form.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Enter skill name"
            />
          </div>

          <!-- Proficiency Level -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Proficiency Level
            </label>
            <select
              v-model="form.proficiency"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">Select proficiency</option>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
              <option value="expert">Expert</option>
            </select>
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Description (Optional)
            </label>
            <textarea
              v-model="form.description"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Describe your experience with this skill..."
            ></textarea>
          </div>

          <!-- Form Actions -->
          <div class="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              @click="$emit('close')"
              class="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              <span v-if="loading" class="animate-spin mr-2">⟳</span>
              {{ isEditing ? 'Update' : 'Save' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'

const props = defineProps({
  skill: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

const loading = ref(false)
const isEditing = ref(false)

const form = reactive({
  name: '',
  category: '',
  proficiency: '',
  description: ''
})

// Initialize form data if editing
if (props.skill) {
  isEditing.value = true
  Object.keys(form).forEach(key => {
    if (props.skill[key] !== undefined) {
      form[key] = props.skill[key]
    }
  })
}

const handleSubmit = async () => {
  loading.value = true
  
  try {
    const skillData = { ...form }
    
    // Convert empty strings to null for optional fields (category is now required)
    if (!skillData.proficiency) skillData.proficiency = null
    if (!skillData.description) skillData.description = null
    
    emit('save', skillData)
  } catch (error) {
    console.error('Error saving skill:', error)
  } finally {
    loading.value = false
  }
}
</script>