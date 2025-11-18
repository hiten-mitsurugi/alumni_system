import { ref } from 'vue'
import surveyService from '@/services/surveyService'

export function useForms() {
  const forms = ref([])
  const loading = ref(false)
  const error = ref(null)

  const loadForms = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await surveyService.getForms()
      forms.value = response.data
    } catch (err) {
      error.value = err.message
      console.error('Error loading forms:', err)
    } finally {
      loading.value = false
    }
  }

  const createForm = async (formData) => {
    loading.value = true
    error.value = null
    try {
      const response = await surveyService.createForm(formData)
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Error creating form:', err)
      console.error('Response data:', err.response?.data)
      console.error('Request payload:', formData)
      return null
    } finally {
      loading.value = false
    }
  }

  const updateForm = async (formId, formData) => {
    loading.value = true
    error.value = null
    try {
      const response = await surveyService.updateForm(formId, formData)
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Error updating form:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  const deleteForm = async (formId) => {
    loading.value = true
    error.value = null
    try {
      await surveyService.deleteForm(formId)
      return true
    } catch (err) {
      error.value = err.message
      console.error('Error deleting form:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  const publishForm = async (formId, publishData) => {
    loading.value = true
    error.value = null
    try {
      const response = await surveyService.publishForm(formId, publishData)
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Error publishing form:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  return {
    forms,
    loading,
    error,
    loadForms,
    createForm,
    updateForm,
    deleteForm,
    publishForm
  }
}
