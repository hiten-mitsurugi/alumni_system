/**
 * Composable for Profile CRUD Operations
 * Consolidates all add/edit/delete/save handlers for profile entities
 */
export function useProfileCrud({
  fetchProfile,
  loadUserSkills,
  createApi,
  updateApi,
  deleteApi,
  selectedItem,
  showModal,
  closeModalFn,
  entityName = 'item',
  onSuccess = null,
  isSkill = false
}) {
  const add = () => {
    selectedItem.value = null
    showModal.value = true
  }

  const edit = (item) => {
    selectedItem.value = item
    showModal.value = true
  }

  const remove = async (itemId) => {
    if (!confirm(`Are you sure you want to delete this ${entityName}?`)) {
      return
    }

    try {
      await deleteApi(itemId)
      if (isSkill) {
        await loadUserSkills()
      } else {
        await fetchProfile()
      }
      if (onSuccess) onSuccess('deleted')
    } catch (error) {
      console.error(`Error deleting ${entityName}:`, error)
      alert(`Failed to delete ${entityName}`)
    }
  }

  const save = async (data) => {
    try {
      if (selectedItem.value) {
        await updateApi(selectedItem.value.id, data)
      } else {
        await createApi(data)
      }

      closeModalFn()
      
      if (isSkill) {
        await loadUserSkills()
      } else {
        await fetchProfile()
      }
      
      if (onSuccess) onSuccess('saved')
    } catch (error) {
      console.error(`Error saving ${entityName}:`, error)
      const message = error.response?.data?.detail || error.message
      alert(`Failed to save ${entityName}: ` + message)
      throw error
    }
  }

  const close = () => {
    closeModalFn()
  }

  return {
    add,
    edit,
    remove,
    save,
    close
  }
}
