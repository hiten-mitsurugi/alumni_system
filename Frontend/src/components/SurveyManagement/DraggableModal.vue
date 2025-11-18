<template>
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
    @click.self="$emit('close')"
  >
    <div
      ref="modalRef"
      :class="[
        'bg-white rounded-lg shadow-xl max-h-[90vh] flex flex-col',
        large ? 'w-full max-w-4xl' : 'w-full max-w-2xl'
      ]"
    >
      <!-- Header (Draggable) -->
      <div
        ref="headerRef"
        class="flex items-center justify-between p-6 border-b border-gray-200 cursor-move bg-gray-50 rounded-t-lg"
        @mousedown="startDrag"
      >
        <h3 class="text-xl font-bold text-gray-900">{{ title }}</h3>
        <button
          @click="$emit('close')"
          class="text-gray-500 hover:text-gray-700 transition p-1"
          type="button"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- Content (Scrollable) -->
      <div class="p-6 overflow-y-auto flex-1">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  title: {
    type: String,
    required: true
  },
  large: {
    type: Boolean,
    default: false
  }
})

defineEmits(['close'])

const modalRef = ref(null)
const headerRef = ref(null)
const isDragging = ref(false)
const dragOffset = ref({ x: 0, y: 0 })

const startDrag = (event) => {
  isDragging.value = true
  const modal = modalRef.value
  if (!modal) return

  const rect = modal.getBoundingClientRect()
  dragOffset.value = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }

  document.addEventListener('mousemove', drag)
  document.addEventListener('mouseup', stopDrag)
}

const drag = (event) => {
  if (!isDragging.value) return
  
  const modal = modalRef.value
  if (!modal) return

  const x = event.clientX - dragOffset.value.x
  const y = event.clientY - dragOffset.value.y

  // Keep modal within viewport
  const maxX = window.innerWidth - modal.offsetWidth
  const maxY = window.innerHeight - modal.offsetHeight

  modal.style.position = 'fixed'
  modal.style.left = `${Math.max(0, Math.min(x, maxX))}px`
  modal.style.top = `${Math.max(0, Math.min(y, maxY))}px`
}

const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', drag)
  document.removeEventListener('mouseup', stopDrag)
}
</script>
