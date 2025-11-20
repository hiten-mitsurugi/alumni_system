import { ref } from 'vue'
import surveyService from '@/services/surveyService'

export function useSections() {
  const sections = ref([])
  const loading = ref(false)
  const error = ref(null)

  const loadSections = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await surveyService.getCategories()
      sections.value = response.data
    } catch (err) {
      error.value = err.message
      console.error('Error loading sections:', err)
    } finally {
      loading.value = false
    }
  }

  const createSection = async (sectionData) => {
    loading.value = true
    error.value = null
    try {
      const response = await surveyService.createCategory(sectionData)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.name?.[0] || err.response?.data?.detail || err.message
      console.error('Error creating section:', err)
      console.error('Response data:', JSON.stringify(err.response?.data, null, 2))
      console.error('Request payload:', JSON.stringify(sectionData, null, 2))
      alert(error.value)
      return null
    } finally {
      loading.value = false
    }
  }

  const updateSection = async (sectionId, sectionData) => {
    loading.value = true
    error.value = null
    try {
      console.log('useSections: Updating section', sectionId, 'with data:', JSON.stringify(sectionData, null, 2))
      const response = await surveyService.updateCategory(sectionId, sectionData)
      console.log('useSections: Update response:', JSON.stringify(response.data, null, 2))
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      console.error('Error updating section:', err)
      console.error('Error response:', err.response?.data)
      console.error('Error status:', err.response?.status)
      alert('Failed to update section: ' + error.value)
      return null
    } finally {
      loading.value = false
    }
  }

  const deleteSection = async (sectionId) => {
    loading.value = true
    error.value = null
    try {
      await surveyService.deleteCategory(sectionId)
      return true
    } catch (err) {
      error.value = err.message
      console.error('Error deleting section:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    sections,
    loading,
    error,
    loadSections,
    createSection,
    updateSection,
    deleteSection
  }
}
