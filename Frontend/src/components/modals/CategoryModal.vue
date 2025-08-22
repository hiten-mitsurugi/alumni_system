<template>
  <teleport to="body">
    <div
      v-if="show"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      @click.self="$emit('close')"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900">
              {{ isEditing ? 'Edit Category' : 'Create New Category' }}
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
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
          <!-- Category Name -->
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700 mb-1">
              Category Name *
            </label>
            <input
              id="name"
              v-model="form.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              :class="{ 'border-red-500': errors.name }"
              placeholder="e.g., Personal Information"
            />
            <p v-if="errors.name" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
          </div>

          <!-- Description -->
          <div>
            <label for="description" class="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              id="description"
              v-model="form.description"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              :class="{ 'border-red-500': errors.description }"
              placeholder="Brief description of this category..."
            ></textarea>
            <p v-if="errors.description" class="mt-1 text-sm text-red-600">{{ errors.description }}</p>
          </div>

          <!-- Order -->
          <div>
            <label for="order" class="block text-sm font-medium text-gray-700 mb-1">
              Display Order *
            </label>
            <input
              id="order"
              v-model.number="form.order"
              type="number"
              min="1"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              :class="{ 'border-red-500': errors.order }"
              placeholder="1"
            />
            <p v-if="errors.order" class="mt-1 text-sm text-red-600">{{ errors.order }}</p>
            <p class="mt-1 text-xs text-gray-500">Lower numbers appear first</p>
          </div>

          <!-- Active Status -->
          <div class="flex items-center">
            <input
              id="is_active"
              v-model="form.is_active"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label for="is_active" class="ml-2 block text-sm text-gray-700">
              Active (visible to alumni)
            </label>
          </div>

          <!-- Error Display -->
          <div v-if="submitError" class="bg-red-50 border border-red-200 rounded-md p-3">
            <p class="text-sm text-red-800">{{ submitError }}</p>
          </div>

          <!-- Actions -->
          <div class="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              @click="$emit('close')"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <svg
                v-if="loading"
                class="animate-spin h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                ></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              {{ loading ? 'Saving...' : (isEditing ? 'Update Category' : 'Create Category') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </teleport>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { surveyService } from '@/services/surveyService'

export default {
  name: 'CategoryModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    category: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const loading = ref(false)
    const submitError = ref(null)
    const errors = ref({})
    
    const form = ref({
      name: '',
      description: '',
      order: 1,
      is_active: true
    })

    const isEditing = computed(() => !!props.category)

    // Watch for category prop changes
    watch(
      () => props.category,
      (newCategory) => {
        if (newCategory) {
          form.value = {
            name: newCategory.name || '',
            description: newCategory.description || '',
            order: newCategory.order || 1,
            is_active: newCategory.is_active ?? true
          }
        } else {
          resetForm()
        }
      },
      { immediate: true }
    )

    // Watch show prop to reset form when modal opens
    watch(
      () => props.show,
      (show) => {
        if (show && !props.category) {
          resetForm()
        }
        // Clear errors when modal opens
        if (show) {
          errors.value = {}
          submitError.value = null
        }
      }
    )

    const resetForm = () => {
      form.value = {
        name: '',
        description: '',
        order: 1,
        is_active: true
      }
      errors.value = {}
      submitError.value = null
    }

    const validateForm = () => {
      const newErrors = {}

      if (!form.value.name?.trim()) {
        newErrors.name = 'Category name is required'
      } else if (form.value.name.trim().length < 2) {
        newErrors.name = 'Category name must be at least 2 characters'
      } else if (form.value.name.trim().length > 100) {
        newErrors.name = 'Category name must be less than 100 characters'
      }

      if (form.value.description && form.value.description.length > 500) {
        newErrors.description = 'Description must be less than 500 characters'
      }

      if (!form.value.order || form.value.order < 1) {
        newErrors.order = 'Order must be a positive number'
      }

      errors.value = newErrors
      return Object.keys(newErrors).length === 0
    }

    const handleSubmit = async () => {
      if (!validateForm()) {
        return
      }

      try {
        loading.value = true
        submitError.value = null

        const categoryData = {
          name: form.value.name.trim(),
          description: form.value.description?.trim() || '',
          order: form.value.order,
          is_active: form.value.is_active
        }

        if (isEditing.value) {
          await surveyService.updateCategory(props.category.id, categoryData)
        } else {
          await surveyService.createCategory(categoryData)
        }

        emit('saved')
      } catch (error) {
        console.error('Error saving category:', error)
        
        if (error.response?.data) {
          const errorData = error.response.data
          
          // Handle field-specific errors
          if (typeof errorData === 'object') {
            errors.value = {}
            Object.keys(errorData).forEach(field => {
              if (field in form.value) {
                errors.value[field] = Array.isArray(errorData[field]) 
                  ? errorData[field][0] 
                  : errorData[field]
              } else {
                submitError.value = Array.isArray(errorData[field]) 
                  ? errorData[field][0] 
                  : errorData[field]
              }
            })
          } else {
            submitError.value = errorData.detail || errorData.message || 'Failed to save category'
          }
        } else {
          submitError.value = 'Network error. Please check your connection and try again.'
        }
      } finally {
        loading.value = false
      }
    }

    return {
      form,
      loading,
      submitError,
      errors,
      isEditing,
      handleSubmit,
      validateForm
    }
  }
}
</script>

<style scoped>
/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Form focus styles */
input:focus,
textarea:focus,
select:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Animation for modal */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>
