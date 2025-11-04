<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="show" class="fixed inset-0 bg-black/50 z-40" @click="$emit('close')"></div>
    </Transition>
    <Transition name="scale">
      <div
        v-if="show"
        :style="modalPosition"
        @mousedown="$emit('drag-start', $event)"
        class="fixed bg-white rounded-xl shadow-2xl border border-slate-200 z-50 w-full max-w-md cursor-move transform transition-transform duration-200"
      >
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-gradient-to-r from-slate-50 to-slate-100 rounded-t-xl cursor-default" @mousedown.stop>
          <h3 class="text-lg font-semibold text-slate-800">
            {{ categoryForm.id ? 'Edit Category' : 'Create New Category' }}
          </h3>
          <button
            @click="$emit('close')"
            class="p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-200 rounded-lg transition-all duration-200 cursor-pointer"
          >
            <X class="w-5 h-5" />
          </button>
        </div>

        <!-- Form Content -->
        <div class="px-6 py-6 space-y-5 max-h-96 overflow-y-auto">
          <!-- Category Name -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">
              Category Name <span class="text-red-500">*</span>
            </label>
            <input
              v-model="categoryForm.name"
              type="text"
              placeholder="e.g., General Information, Professional Background"
              class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-slate-800 placeholder-slate-400"
            />
            <p v-if="errors.name" class="text-red-500 text-xs mt-1">{{ errors.name }}</p>
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">Description</label>
            <textarea
              v-model="categoryForm.description"
              placeholder="Optional: Describe what this category contains"
              rows="3"
              class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-slate-800 placeholder-slate-400 resize-none"
            ></textarea>
          </div>

          <!-- Order -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">Display Order</label>
            <input
              v-model.number="categoryForm.order"
              type="number"
              min="0"
              placeholder="0"
              class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-slate-800 placeholder-slate-400"
            />
            <p class="text-slate-500 text-xs mt-1">Lower numbers appear first</p>
          </div>

          <!-- Active Status -->
          <div class="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
            <div>
              <p class="text-sm font-medium text-slate-700">Active</p>
              <p class="text-xs text-slate-500 mt-1">Include this category in surveys</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                v-model="categoryForm.is_active"
                type="checkbox"
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-slate-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-orange-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-orange-600"></div>
            </label>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex gap-3 px-6 py-4 border-t border-slate-200 bg-slate-50 rounded-b-xl cursor-default" @mousedown.stop>
          <button
            @click="$emit('close')"
            class="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-100 transition-all duration-200 font-medium cursor-pointer"
          >
            Cancel
          </button>
          <button
            @click="handleSave"
            class="flex-1 px-4 py-2 bg-gradient-to-r from-orange-600 to-orange-500 text-white rounded-lg hover:from-orange-500 hover:to-orange-600 transition-all duration-200 font-medium cursor-pointer"
          >
            {{ categoryForm.id ? 'Update' : 'Create' }}
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import { X } from 'lucide-vue-next'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  category: {
    type: Object,
    default: null
  },
  isDragging: {
    type: Boolean,
    default: false
  },
  modalPosition: {
    type: Object,
    default: () => ({
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)'
    })
  }
})

const emit = defineEmits(['close', 'save', 'drag-start', 'reset-position'])

const categoryForm = ref({
  id: null,
  name: '',
  description: '',
  order: 0,
  is_active: true
})

const errors = ref({
  name: ''
})

watch(() => props.show, (newVal) => {
  if (newVal) {
    if (props.category) {
      categoryForm.value = {
        id: props.category.id,
        name: props.category.name,
        description: props.category.description || '',
        order: props.category.order || 0,
        is_active: props.category.is_active ?? true
      }
    } else {
      categoryForm.value = {
        id: null,
        name: '',
        description: '',
        order: 0,
        is_active: true
      }
    }
    errors.value = { name: '' }
  }
})

const handleSave = () => {
  errors.value = { name: '' }

  if (!categoryForm.value.name.trim()) {
    errors.value.name = 'Category name is required'
    return
  }

  emit('save', { ...categoryForm.value })
  emit('close')
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.scale-enter-active,
.scale-leave-active {
  transition: all 0.3s ease;
}

.scale-enter-from,
.scale-leave-to {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.95);
}
</style>
