import { ref, nextTick } from 'vue'

export function useDraggable() {
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

  const onDrag = (event) => {
    if (!isDragging.value || !draggedModal.value) return
    
    const modal = document.querySelector(`[data-modal="${draggedModal.value}"]`)
    if (!modal) return
    
    const newX = event.clientX - dragOffset.value.x
    const newY = event.clientY - dragOffset.value.y
    
    const maxX = window.innerWidth - modal.offsetWidth
    const maxY = window.innerHeight - modal.offsetHeight
    
    const clampedX = Math.max(0, Math.min(newX, maxX))
    const clampedY = Math.max(0, Math.min(newY, maxY))
    
    modalPositions.value[draggedModal.value] = { x: clampedX, y: clampedY }
    
    modal.style.transform = `translate(${clampedX}px, ${clampedY}px)`
    modal.style.position = 'fixed'
  }

  const stopDrag = () => {
    isDragging.value = false
    draggedModal.value = null
    document.removeEventListener('mousemove', onDrag)
    document.removeEventListener('mouseup', stopDrag)
  }

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

  const cleanup = () => {
    document.removeEventListener('mousemove', onDrag)
    document.removeEventListener('mouseup', stopDrag)
  }

  return {
    isDragging,
    draggedModal,
    modalPositions,
    startDrag,
    resetModalPosition,
    cleanup
  }
}
