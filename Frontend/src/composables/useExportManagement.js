import { ref } from 'vue'
import surveyService from '@/services/surveyService'

export function useExportManagement(categories) {
  // State
  const showExportModal = ref(false)
  const isExporting = ref(false)
  const exportFormat = ref('xlsx')
  const exportCategory = ref('')
  const includeInactive = ref(false)
  const exportDateFrom = ref('')
  const exportDateTo = ref('')
  const exportProfileFields = ref([
    'first_name', 'last_name', 'email', 'program',
    'year_graduated', 'student_id', 'birth_date', 'user_type'
  ])

  // Export data
  const exportData = async () => {
    if (isExporting.value) return

    try {
      isExporting.value = true

      const exportParams = {
        format: exportFormat.value,
        category_id: exportCategory.value || null,
        date_from: exportDateFrom.value || null,
        date_to: exportDateTo.value || null,
        include_profile_fields: exportProfileFields.value
      }

      const response = await surveyService.exportResponses(exportParams)

      // Handle file download
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url

      // Set filename based on format
      const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
      const extension = exportFormat.value === 'xlsx' ? 'xlsx' : 'csv'
      const filename = `survey_responses_${timestamp}.${extension}`

      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)

      // Close modal
      showExportModal.value = false

      console.log('Export completed successfully!')
    } catch (error) {
      console.error('Error exporting data:', error)
      alert('Failed to export data. Please try again.')
    } finally {
      isExporting.value = false
    }
  }

  return {
    showExportModal,
    isExporting,
    exportFormat,
    exportCategory,
    includeInactive,
    exportDateFrom,
    exportDateTo,
    exportProfileFields,
    exportData
  }
}
