<template>
  <div 
    v-if="isVisible"
    class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
    @click="closeModal"
  >
    <div 
      class="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto"
      @click.stop
    >
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h2 class="text-2xl font-bold text-gray-800">Edit Post</h2>
        <button 
          @click="closeModal"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="updatePost" class="p-6 space-y-6">
        <!-- Title (Optional) -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Title (Optional)
          </label>
          <input
            v-model="editForm.title"
            type="text"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            placeholder="Enter post title..."
          />
        </div>

        <!-- Content -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Content *
          </label>
          <textarea
            v-model="editForm.content"
            rows="8"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none"
            placeholder="What's on your mind?"
            required
          ></textarea>
        </div>

        <!-- Category -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Category *
          </label>
          <select
            v-model="editForm.content_category"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            required
          >
            <option value="">Select a category</option>
            <option 
              v-for="category in categories" 
              :key="category.value" 
              :value="category.value"
            >
              {{ category.icon }} {{ category.label }}
            </option>
          </select>
        </div>

        <!-- Actions -->
        <div class="flex justify-end space-x-4 pt-4">
          <button
            type="button"
            @click="closeModal"
            class="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="isLoading || !editForm.content.trim()"
            class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
          >
            <span v-if="isLoading" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Updating...
            </span>
            <span v-else>Update Post</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'

// Props
const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  post: {
    type: Object,
    default: null
  },
  categories: {
    type: Array,
    required: true
  }
})

// Emits
const emit = defineEmits(['close', 'update'])

// State
const isLoading = ref(false)
const editForm = reactive({
  title: '',
  content: '',
  content_category: ''
})

// Watch for post changes to populate form
watch(() => props.post, (newPost) => {
  if (newPost) {
    editForm.title = newPost.title || ''
    editForm.content = newPost.content || ''
    editForm.content_category = newPost.content_category || ''
  }
}, { immediate: true })

// Methods
const closeModal = () => {
  emit('close')
}

const updatePost = async () => {
  if (!editForm.content.trim()) return

  isLoading.value = true
  
  try {
    await emit('update', {
      id: props.post.id,
      title: editForm.title,
      content: editForm.content,
      content_category: editForm.content_category
    })
    
    closeModal()
  } catch (error) {
    console.error('Failed to update post:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* Prevent body scroll when modal is open */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>