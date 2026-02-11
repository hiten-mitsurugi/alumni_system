import { openModal, openAddModal, openEditModal } from './useModals'

/**
 * Generic entity CRUD handlers factory
 * Creates add/edit/delete handlers for an entity type
 */
export function useEntityHandlers(entityType, {
  deleteApi,
  modalName,
  fetchProfile,
  confirmMessage = `Are you sure you want to delete this ${entityType}?`
}) {
  /**
   * Opens add modal for entity
   */
  const add = () => {
    openAddModal(modalName)
  }

  /**
   * Opens edit modal with selected entity
   */
  const edit = (item) => {
    openEditModal(modalName, item)
  }

  /**
   * Deletes an entity with confirmation
   */
  const remove = async (itemId) => {
    if (!confirm(confirmMessage)) {
      return
    }

    try {
      await deleteApi(itemId)
      await fetchProfile() // Refresh data
    } catch (error) {
      console.error(`Error deleting ${entityType}:`, error)
      alert(`Failed to delete ${entityType}`)
    }
  }

  return {
    add,
    edit,
    remove
  }
}
