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
  openModalFn,
  entityName = 'item',
  onSuccess = null,
  isSkill = false
}) {
  const add = () => {
    console.log(`➕ useProfileCrud: Adding new ${entityName}`)
    if (openModalFn) {
      openModalFn(null)
    }
  }

  const edit = (item) => {
    console.log(`✏️ useProfileCrud: Editing ${entityName}`, item)
    if (openModalFn) {
      openModalFn(item)
    }
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
      console.log(`💾 useProfileCrud: Saving ${entityName}`, {
        data,
        selectedItem: selectedItem.value,
        isEditing: !!selectedItem.value
      })
      
      if (selectedItem.value) {
        console.log(`✏️ Updating ${entityName} with ID:`, selectedItem.value.id)
        await updateApi(selectedItem.value.id, data)
      } else {
        console.log(`➕ Creating new ${entityName}`)
        await createApi(data)
      }

      console.log(`✅ ${entityName} saved successfully, closing modal...`)
      closeModalFn()
      
      console.log(`🔄 Refreshing profile data...`)
      if (isSkill) {
        await loadUserSkills()
      } else {
        await fetchProfile()
      }
      
      console.log(`🎉 ${entityName} save process complete`)
      if (onSuccess) onSuccess('saved')
    } catch (error) {
      console.error(`❌ Error saving ${entityName}:`, error)
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
