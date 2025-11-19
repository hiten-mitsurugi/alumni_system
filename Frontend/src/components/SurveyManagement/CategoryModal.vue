<script setup>
import { ref, computed } from 'vue'
import { X } from 'lucide-vue-next'
import surveyService from '@/services/surveyService'
import { useThemeStore } from '@/stores/theme'

const props = defineProps({
  category: {
    type: Object,
    default: null
  },
  categoriesLength: {
    type: Number,
    default: 0
  },
  isDragging: Boolean,
  draggedModal: String,
  modalPosition: {
    type: Object,
    default: () => ({ x: 0, y: 0 })
  }
})

const emit = defineEmits(['close', 'save', 'startDrag', 'resetPosition'])

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isAdminDark?.())

const form = ref({
  id: null,
  name: '',
  description: '',
  order: 0,
  is_active: true,
  include_in_registration: false
})

// Initialize form when category prop changes
if (props.category) {
  form.value = { ...props.category }
} else {
  form.value.order = props.categoriesLength
}

const saveCategory = async () => {
  try {
    if (form.value.id) {
      await surveyService.updateCategory(form.value.id, form.value)
    } else {
      await surveyService.createCategory(form.value)
    }
    emit('save')
    emit('close')
  } catch (error) {
    console.error('Error saving category:', error)
  }
}
</script>

<template>
  <div
    class="fixed inset-0 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
  >
    <div 
      :class="[
        'draggable-modal relative rounded-2xl shadow-2xl w-full max-w-md',
        isDark ? 'bg-gray-800' : 'bg-white',
        isDragging && draggedModal === 'category' ? 'dragging' : ''
      ]"
      data-modal="category"
      @click.stop
      :style="{ transform: `translate(${modalPosition.x}px, ${modalPosition.y}px)` }"
    >
      <div 
        :class="[
          'bg-gradient-to-r from-orange-600 to-orange-500 p-6 rounded-t-2xl select-none flex items-center justify-between',
          isDragging && draggedModal === 'category' ? 'cursor-grabbing' : 'cursor-move'
        ]"
        @mousedown="emit('startDrag', $event, 'category')"
      >
        <div>
          <h3 class="text-xl font-bold text-white flex items-center gap-2">
            {{ category ? 'Edit Category' : 'Create New Category' }}
          </h3>
          <p class="text-orange-100 text-sm mt-1">
            {{ category ? 'Update category information' : 'Add a new survey category' }}
          </p>
        </div>
        <button
          @click="emit('resetPosition', 'category')"
          class="text-orange-200 hover:text-white p-1 rounded transition-colors"
          title="Reset position"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
      
      <form @submit.prevent="saveCategory" class="p-6 space-y-6">
        <div>
          <label :class="['block text-sm font-semibold mb-2', isDark ? 'text-gray-300' : 'text-slate-700']">Category Name *</label>
          <input
            v-model="form.name"
            type="text"
            required
            placeholder="e.g., Demographics, Employment, Education"
            :class="[
              'w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors',
              isDark ? 'bg-gray-700 border-gray-600 text-white' : 'border-slate-300'
            ]"
          />
        </div>
        
        <div>
          <label :class="['block text-sm font-semibold mb-2', isDark ? 'text-gray-300' : 'text-slate-700']">Description</label>
          <textarea
            v-model="form.description"
            rows="3"
            placeholder="Brief description of this category"
            :class="[
              'w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors resize-none',
              isDark ? 'bg-gray-700 border-gray-600 text-white' : 'border-slate-300'
            ]"
          ></textarea>
        </div>
        
        <div>
          <label :class="['block text-sm font-semibold mb-2', isDark ? 'text-gray-300' : 'text-slate-700']">Display Order</label>
          <input
            v-model.number="form.order"
            type="number"
            min="0"
            :class="[
              'w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors',
              isDark ? 'bg-gray-700 border-gray-600 text-white' : 'border-slate-300'
            ]"
          />
          <p :class="['text-xs mt-1', isDark ? 'text-gray-400' : 'text-slate-500']">Lower numbers appear first</p>
        </div>
        
        <div class="flex items-center">
          <input
            v-model="form.is_active"
            type="checkbox"
            id="is_active"
            class="h-4 w-4 text-orange-600 focus:ring-orange-500 border-slate-300 rounded cursor-pointer"
          />
          <label for="is_active" :class="['ml-3 block text-sm font-medium cursor-pointer', isDark ? 'text-gray-300' : 'text-slate-700']">
            Active Category
          </label>
        </div>

        <div class="flex items-center">
          <input
            v-model="form.include_in_registration"
            type="checkbox"
            id="include_in_registration"
            class="h-4 w-4 text-orange-600 focus:ring-orange-500 border-slate-300 rounded cursor-pointer"
          />
          <label for="include_in_registration" :class="['ml-3 block text-sm font-medium cursor-pointer', isDark ? 'text-gray-300' : 'text-slate-700']">
            Include in Registration Form
          </label>
        </div>
        <p :class="['text-xs -mt-4 ml-7', isDark ? 'text-gray-400' : 'text-slate-500']">
          Check this to make this category appear on the public registration form. Leave unchecked for tracer surveys or admin-only surveys.
        </p>
        
        <div :class="['flex justify-end gap-3 pt-4 border-t', isDark ? 'border-gray-700' : 'border-slate-200']">
          <button
            type="button"
            @click="emit('close')"
            :class="[
              'px-6 py-3 text-sm font-medium rounded-lg transition-colors cursor-pointer',
              isDark ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' : 'text-slate-700 bg-slate-100 hover:bg-slate-200'
            ]"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="px-6 py-3 text-sm font-medium text-white bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-600 rounded-lg transition-all duration-200 cursor-pointer shadow-md hover:shadow-lg"
          >
            {{ category ? 'Update Category' : 'Create Category' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
