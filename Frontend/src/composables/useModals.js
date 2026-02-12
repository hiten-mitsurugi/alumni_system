import { ref, reactive } from 'vue'

export function useModals() {
  // Modal visibility states
  const modals = reactive({
    coverPhoto: false,
    profilePicture: false,
    profile: false,
    education: false,
    workHistory: false,
    skills: false,
    achievements: false,
    memberships: false,
    recognitions: false,
    trainings: false,
    publications: false,
    certificates: false,
    careerEnhancement: false
  })

  // Selected items for editing
  const selectedItems = reactive({
    education: null,
    workHistory: null,
    skills: null,
    achievements: null,
    memberships: null,
    recognitions: null,
    trainings: null,
    publications: null,
    certificates: null
  })

  /**
   * Opens a modal
   * @param {string} modalName - Name of the modal to open
   * @param {Object} item - Optional item to edit
   */
  const openModal = (modalName, item = null) => {
    console.log(`🔓 useModals: Opening modal "${modalName}"`, { item })
    
    if (modals.hasOwnProperty(modalName)) {
      modals[modalName] = true
      
      // Set selected item if applicable
      if (selectedItems.hasOwnProperty(modalName) && item) {
        selectedItems[modalName] = item
        console.log(`✅ useModals: Set selectedItems.${modalName}`, item)
      } else if (selectedItems.hasOwnProperty(modalName)) {
        selectedItems[modalName] = null
        console.log(`🔄 useModals: Cleared selectedItems.${modalName}`)
      }
    } else {
      console.warn(`⚠️ useModals: Modal "${modalName}" not found in modals object`)
    }
  }

  /**
   * Closes a modal
   * @param {string} modalName - Name of the modal to close
   */
  const closeModal = (modalName) => {
    if (modals.hasOwnProperty(modalName)) {
      modals[modalName] = false
      
      // Clear selected item if applicable
      if (selectedItems.hasOwnProperty(modalName)) {
        selectedItems[modalName] = null
      }
    }
  }

  /**
   * Closes all modals
   */
  const closeAllModals = () => {
    Object.keys(modals).forEach(key => {
      modals[key] = false
    })
    Object.keys(selectedItems).forEach(key => {
      selectedItems[key] = null
    })
  }

  /**
   * Opens edit modal with selected item
   * @param {string} modalName - Modal name
   * @param {Object} item - Item to edit
   */
  const openEditModal = (modalName, item) => {
    openModal(modalName, item)
  }

  /**
   * Opens add modal (no selected item)
   * @param {string} modalName - Modal name
   */
  const openAddModal = (modalName) => {
    openModal(modalName, null)
  }

  return {
    modals,
    selectedItems,
    openModal,
    closeModal,
    closeAllModals,
    openEditModal,
    openAddModal
  }
}
