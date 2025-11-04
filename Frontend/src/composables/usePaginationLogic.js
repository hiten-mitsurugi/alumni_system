import { ref, computed } from 'vue'

export function usePaginationLogic(categories, questions) {
  // State
  const currentCategoryPage = ref(1)
  const currentQuestionPage = ref(1)
  const itemsPerPage = 6

  // Computed: Total pages
  const totalCategoryPages = computed(() => Math.ceil(categories.value.length / itemsPerPage))
  const totalQuestionPages = computed(() => Math.ceil(questions.value.length / itemsPerPage))

  // Computed: Paginated data
  const paginatedCategories = computed(() => {
    const start = (currentCategoryPage.value - 1) * itemsPerPage
    const end = start + itemsPerPage
    return categories.value.slice(start, end)
  })

  const paginatedQuestions = computed(() => {
    const start = (currentQuestionPage.value - 1) * itemsPerPage
    const end = start + itemsPerPage
    return questions.value.slice(start, end)
  })

  // Computed: Question pagination with smart ellipsis
  const questionsPageNumbers = computed(() => {
    const pages = []
    const total = totalQuestionPages.value
    const current = currentQuestionPage.value

    if (total <= 7) {
      for (let i = 1; i <= total; i++) {
        pages.push(i)
      }
    } else {
      if (current <= 4) {
        for (let i = 1; i <= 5; i++) pages.push(i)
        pages.push('...')
        pages.push(total)
      } else if (current >= total - 3) {
        pages.push(1)
        pages.push('...')
        for (let i = total - 4; i <= total; i++) pages.push(i)
      } else {
        pages.push(1)
        pages.push('...')
        for (let i = current - 1; i <= current + 1; i++) pages.push(i)
        pages.push('...')
        pages.push(total)
      }
    }

    return pages
  })

  // Computed: Filter out ellipsis
  const questionsPageButtons = computed(() => {
    return questionsPageNumbers.value.filter(page => page !== '...')
  })

  // Computed: Get ellipsis elements
  const questionsEllipsis = computed(() => {
    return questionsPageNumbers.value.filter(page => page === '...')
  })

  // Functions
  const goToCategoryPage = (page) => {
    if (page >= 1 && page <= totalCategoryPages.value) {
      currentCategoryPage.value = page
    }
  }

  const goToQuestionPage = (page) => {
    if (page >= 1 && page <= totalQuestionPages.value) {
      currentQuestionPage.value = page
    }
  }

  return {
    currentCategoryPage,
    currentQuestionPage,
    itemsPerPage,
    totalCategoryPages,
    totalQuestionPages,
    paginatedCategories,
    paginatedQuestions,
    questionsPageNumbers,
    questionsPageButtons,
    questionsEllipsis,
    goToCategoryPage,
    goToQuestionPage
  }
}
