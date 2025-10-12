import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { reportsService } from '@/services/reportsService'

export function useReports() {
  const authStore = useAuthStore()
  
  // Reactive data
  const reportedPosts = ref([])
  const loading = ref(false)
  const searchQuery = ref('')
  const selectedCategory = ref('')
  const selectedReportReason = ref('')
  const selectedStatus = ref('pending')
  const sortBy = ref('newest')
  const hasMore = ref(false)
  const currentPage = ref(1)
  
  // Stats
  const resolvedToday = ref(0)
  const dismissedToday = ref(0)
  const totalReports = ref(0)
  
  // Messages
  const successMessage = ref('')
  const errorMessage = ref('')

  // Computed
  const filteredReports = computed(() => {
    let filtered = [...reportedPosts.value]

    // Search filter
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      filtered = filtered.filter(report =>
        report.post.content.toLowerCase().includes(query) ||
        report.post.user.full_name?.toLowerCase().includes(query) ||
        `${report.post.user.first_name} ${report.post.user.last_name}`.toLowerCase().includes(query) ||
        (report.post.title && report.post.title.toLowerCase().includes(query)) ||
        report.reason.toLowerCase().includes(query)
      )
    }

    // Category filter
    if (selectedCategory.value) {
      filtered = filtered.filter(report => report.post.content_category === selectedCategory.value)
    }

    // Report reason filter
    if (selectedReportReason.value) {
      filtered = filtered.filter(report => report.reason === selectedReportReason.value)
    }

    // Sort
    switch (sortBy.value) {
      case 'oldest':
        filtered.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
        break
      case 'severity': {
        const severityOrder = { 'spam': 1, 'harassment': 2, 'hate_speech': 3, 'inappropriate_content': 4, 'misinformation': 5, 'other': 6 }
        filtered.sort((a, b) => severityOrder[a.reason] - severityOrder[b.reason])
        break
      }
      default: // newest
        filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    }

    return filtered
  })

  // Methods
  const fetchReportedPosts = async (page = 1) => {
    try {
      loading.value = true

      const params = {
        page,
        page_size: 10,
        status: selectedStatus.value === 'all' ? 'all' : 'pending'
      }

      if (selectedReportReason.value !== 'all') {
        params.reason = selectedReportReason.value
      }

      console.log('🔍 Fetching reported posts with params:', params)

      const response = await reportsService.getReports(params)

      console.log('📊 API Response:', response)
      console.log('📊 Reports data:', response.reports)
      console.log('📊 Stats data:', response.stats)
      
      if (!response.reports || !Array.isArray(response.reports)) {
        console.error('❌ Invalid response format - reports should be an array:', response)
      }

      if (page === 1) {
        reportedPosts.value = response.reports || []
      } else {
        reportedPosts.value = [...reportedPosts.value, ...(response.reports || [])]
      }
      
      console.log('📋 Updated reportedPosts.value:', reportedPosts.value.length, 'items')
      console.log('📋 First report:', reportedPosts.value[0])

      // Update statistics from API response
      if (response.stats) {
        totalReports.value = response.stats.total_reports || 0
        resolvedToday.value = response.stats.resolved_today || 0
        dismissedToday.value = response.stats.dismissed_today || 0
      }

      hasMore.value = response.pagination?.has_more || false

      console.log('✅ Updated reports:', {
        count: reportedPosts.value.length,
        hasMore: hasMore.value,
        stats: response.stats
      })

    } catch (error) {
      console.error('❌ Error fetching reported posts:', error)
      errorMessage.value = 'Failed to load reported posts. Please try again.'
    } finally {
      loading.value = false
    }
  }

  const dismissReport = async (reportId) => {
    try {
      console.log('🗑️ Dismissing report:', reportId)

      const response = await reportsService.takeAction(reportId, { action: 'dismiss' })

      console.log('✅ Report dismissed:', response)

      // Remove from reports list
      reportedPosts.value = reportedPosts.value.filter(report => report.id !== reportId)

      successMessage.value = response.message || 'Report dismissed successfully!'
      dismissedToday.value += 1
      totalReports.value = Math.max(0, totalReports.value - 1)

      // Clear success message after 3 seconds
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)

    } catch (error) {
      console.error('Error dismissing report:', error)
      errorMessage.value = 'Failed to dismiss report. Please try again.'
      setTimeout(() => {
        errorMessage.value = ''
      }, 5000)
    }
  }

  const takeAction = async (reportId, action, note = '') => {
    try {
      console.log('🎯 Taking action:', action, 'for report:', reportId)

      const response = await reportsService.takeAction(reportId, {
        action: action,
        note: note
      })

      console.log('✅ Action confirmed:', response)

      // Remove from reports list
      reportedPosts.value = reportedPosts.value.filter(report => report.id !== reportId)

      const actionMessages = {
        'remove': 'Post removed and user notified!',
        'warn': 'User warned successfully!',
        'dismiss': 'Report dismissed successfully!'
      }

      successMessage.value = actionMessages[action] || response.message
      resolvedToday.value += 1
      totalReports.value = Math.max(0, totalReports.value - 1)

      // Clear success message after 3 seconds
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)

      return response

    } catch (error) {
      console.error(`Error ${action}ing report:`, error)
      errorMessage.value = `Failed to ${action} report. Please try again.`
      setTimeout(() => {
        errorMessage.value = ''
      }, 5000)
      throw error
    }
  }

  const refreshReports = () => {
    currentPage.value = 1
    fetchReportedPosts(1)
  }

  const loadMore = () => {
    currentPage.value += 1
    fetchReportedPosts(currentPage.value)
  }

  const clearMessages = () => {
    successMessage.value = ''
    errorMessage.value = ''
  }

  return {
    // State
    reportedPosts,
    loading,
    searchQuery,
    selectedCategory,
    selectedReportReason,
    selectedStatus,
    sortBy,
    hasMore,
    currentPage,
    resolvedToday,
    dismissedToday,
    totalReports,
    successMessage,
    errorMessage,
    
    // Computed
    filteredReports,
    
    // Methods
    fetchReportedPosts,
    dismissReport,
    takeAction,
    refreshReports,
    loadMore,
    clearMessages
  }
}