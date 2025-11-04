import { ref, nextTick } from 'vue'

export function useDraggableModals() {
  // State
  const isDragging = ref(false)
  const draggedModal = ref(null)
  const dragOffset = ref({ x: 0, y: 0 })
  const modalPositions = ref({
    category: { x: 0, y: 0 },
    question: { x: 0, y: 0 },
    analytics: { x: 0, y: 0 },
    export: { x: 0, y: 0 },
    categoryQuestions: { x: 0, y: 0 }
  })

  // Start drag on header mousedown
  const startDrag = (event, modalType) => {
    isDragging.value = true
    draggedModal.value = modalType

    const rect = event.target.closest('.draggable-modal').getBoundingClientRect()
    dragOffset.value = {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top
    }

    document.addEventListener('mousemove', onDrag)
    document.addEventListener('mouseup', stopDrag)
    event.preventDefault()
  }

  // Handle drag movement
  const onDrag = (event) => {
    if (!isDragging.value || !draggedModal.value) return

    const modal = document.querySelector(`[data-modal="${draggedModal.value}"]`)
    if (!modal) return

    const newX = event.clientX - dragOffset.value.x
    const newY = event.clientY - dragOffset.value.y

    // Keep modal within viewport bounds
    const maxX = window.innerWidth - modal.offsetWidth
    const maxY = window.innerHeight - modal.offsetHeight

    const clampedX = Math.max(0, Math.min(newX, maxX))
    const clampedY = Math.max(0, Math.min(newY, maxY))

    modalPositions.value[draggedModal.value] = { x: clampedX, y: clampedY }

    modal.style.transform = `translate(${clampedX}px, ${clampedY}px)`
    modal.style.position = 'fixed'
  }

  // Stop drag
  const stopDrag = () => {
    isDragging.value = false
    draggedModal.value = null
    document.removeEventListener('mousemove', onDrag)
    document.removeEventListener('mouseup', stopDrag)
  }

  // Reset modal position to origin
  const resetModalPosition = (modalType) => {
    modalPositions.value[modalType] = { x: 0, y: 0 }
    nextTick(() => {
      const modal = document.querySelector(`[data-modal="${modalType}"]`)
      if (modal) {
        modal.style.transform = 'translate(0px, 0px)'
        modal.style.position = 'relative'
      }
    })
  }

  return {
    isDragging,
    draggedModal,
    dragOffset,
    modalPositions,
    startDrag,
    onDrag,
    stopDrag,
    resetModalPosition
  }
}
