import { ref } from 'vue'
import surveyService from '@/services/surveyService'

export function useCategoryManagement(categories) {
  // State
  const showCategoryModal = ref(false)
  const categoryForm = ref({
    id: null,
    name: '',
    description: '',
    order: 0,
    is_active: true
  })
  const selectedCategoryForModal = ref(null)
  const categoryQuestions = ref([])

  // Open modal for create or edit
  const openCategoryModal = (category = null) => {
    if (category) {
      categoryForm.value = { ...category }
    } else {
      categoryForm.value = {
        id: null,
        name: '',
        description: '',
        order: categories.value.length,
        is_active: true
      }
    }
    showCategoryModal.value = true
  }

  // Save category (create or update)
  const saveCategory = async () => {
    try {
      if (categoryForm.value.id) {
        await surveyService.updateCategory(categoryForm.value.id, categoryForm.value)
      } else {
        await surveyService.createCategory(categoryForm.value)
      }
      showCategoryModal.value = false
      await loadCategories()
    } catch (error) {
      console.error('Error saving category:', error)
    }
  }

  // Delete category
  const deleteCategory = async (id) => {
    if (confirm('Are you sure you want to delete this category and all its questions?')) {
      try {
        const categoryIndex = categories.value.findIndex(cat => cat.id === id)
        const removedCategory = categories.value[categoryIndex]
        if (categoryIndex !== -1) {
          categories.value.splice(categoryIndex, 1)
        }

        await surveyService.deleteCategory(id)
        await loadCategories()
      } catch (error) {
        console.error('Error deleting category:', error)
        const categoryIndex = categories.value.findIndex(cat => cat.id === id)
        if (removedCategory && categoryIndex !== -1) {
          categories.value.splice(categoryIndex, 0, removedCategory)
        }
      }
    }
  }

  // Select category and view its questions
  const selectCategory = async (category) => {
    selectedCategoryForModal.value = category
    try {
      const response = await surveyService.getQuestions(category.id)
      categoryQuestions.value = response.data
    } catch (error) {
      console.error('Error loading category questions:', error)
    }
  }

  // Stub for loadCategories - will be provided by parent
  const loadCategories = async () => {
    // This will be called from the composable that manages categories
  }

  return {
    showCategoryModal,
    categoryForm,
    selectedCategoryForModal,
    categoryQuestions,
    openCategoryModal,
    saveCategory,
    deleteCategory,
    selectCategory
  }
}
