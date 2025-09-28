<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const authStore = useAuthStore()
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Reactive data
const reportedPosts = ref([])
const loading = ref(false)
const searchQuery = ref('')
const selectedCategory = ref('')
const selectedReportReason = ref('')
const selectedStatus = ref('pending') // pending, resolved, all
const sortBy = ref('newest')
const hasMore = ref(false)
const currentPage = ref(1)

// Stats
const resolvedToday = ref(0)
const dismissedToday = ref(0)
const totalReports = ref(0)

// Modal state
const showActionModal = ref(false)
const selectedReport = ref(null)
const actionType = ref('') // 'dismiss', 'remove', 'warn'
const actionNote = ref('')

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
    case 'severity':
      const severityOrder = { 'spam': 1, 'harassment': 2, 'hate_speech': 3, 'inappropriate_content': 4, 'misinformation': 5, 'other': 6 }
      filtered.sort((a, b) => severityOrder[a.reason] - severityOrder[b.reason])
      break
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

    const response = await axios.get(`${BASE_URL}/api/posts/reports/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
      params
    })

    console.log('📊 API Response:', response.data)

    if (page === 1) {
      reportedPosts.value = response.data.reports || []
    } else {
      reportedPosts.value = [...reportedPosts.value, ...(response.data.reports || [])]
    }

    // Update statistics from API response
    if (response.data.stats) {
      totalReports.value = response.data.stats.total_reports || 0
      resolvedToday.value = response.data.stats.resolved_today || 0
      dismissedToday.value = response.data.stats.dismissed_today || 0
    }

    hasMore.value = response.data.pagination?.has_more || false

    console.log('✅ Updated reports:', {
      count: reportedPosts.value.length,
      hasMore: hasMore.value,
      stats: response.data.stats
    })

  } catch (error) {
    console.error('❌ Error fetching reported posts:', error)
    errorMessage.value = 'Failed to load reported posts. Please try again.'
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    // These would be separate API endpoints for stats
    // For now, we'll use mock data or calculate from existing data
    resolvedToday.value = 8
    dismissedToday.value = 3
    totalReports.value = reportedPosts.value.length
  } catch (error) {
    console.error('Error fetching stats:', error)
  }
}

const dismissReport = async (reportId) => {
  try {
    console.log('🗑️ Dismissing report:', reportId)

    const response = await axios.post(`${BASE_URL}/api/posts/reports/${reportId}/action/`, {
      action: 'dismiss'
    }, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })

    console.log('✅ Report dismissed:', response.data)

    // Remove from reports list
    reportedPosts.value = reportedPosts.value.filter(report => report.id !== reportId)

    successMessage.value = response.data.message || 'Report dismissed successfully!'
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

const takeAction = (report, action) => {
  selectedReport.value = report
  actionType.value = action
  showActionModal.value = true
  actionNote.value = ''
}

const hideActionModal = () => {
  showActionModal.value = false
  selectedReport.value = null
  actionType.value = ''
  actionNote.value = ''
}

const confirmAction = async () => {
  try {
    console.log('🎯 Confirming action:', actionType.value, 'for report:', selectedReport.value.id)

    const response = await axios.post(`${BASE_URL}/api/posts/reports/${selectedReport.value.id}/action/`, {
      action: actionType.value,
      note: actionNote.value
    }, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })

    console.log('✅ Action confirmed:', response.data)

    // Remove from reports list
    reportedPosts.value = reportedPosts.value.filter(report => report.id !== selectedReport.value.id)

    const actionMessages = {
      'remove': 'Post removed and user notified!',
      'warn': 'User warned successfully!',
      'dismiss': 'Report dismissed successfully!'
    }

    successMessage.value = actionMessages[actionType.value] || response.data.message
    resolvedToday.value += 1
    totalReports.value = Math.max(0, totalReports.value - 1)

    hideActionModal()

    // Clear success message after 3 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)

  } catch (error) {
    console.error(`Error ${actionType.value}ing report:`, error)
    errorMessage.value = `Failed to ${actionType.value} report. Please try again.`
    setTimeout(() => {
      errorMessage.value = ''
    }, 5000)
  }
}

const refreshReports = () => {
  currentPage.value = 1
  fetchReportedPosts(1)
  fetchStats()
}

const loadMore = () => {
  currentPage.value += 1
  fetchReportedPosts(currentPage.value)
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatTimeAgo = (dateString) => {
  const now = new Date()
  const postDate = new Date(dateString)
  const diffMs = now - postDate
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 60) {
    return `${diffMins} minutes ago`
  } else if (diffHours < 24) {
    return `${diffHours} hours ago`
  } else {
    return `${diffDays} days ago`
  }
}

const getReasonLabel = (reason) => {
  const reasons = {
    'spam': 'Spam',
    'harassment': 'Harassment',
    'hate_speech': 'Hate Speech',
    'inappropriate_content': 'Inappropriate Content',
    'misinformation': 'Misinformation',
    'other': 'Other'
  }
  return reasons[reason] || reason
}

const getReasonColor = (reason) => {
  const colors = {
    'spam': 'bg-yellow-100 text-yellow-800',
    'harassment': 'bg-red-100 text-red-800',
    'hate_speech': 'bg-red-100 text-red-800',
    'inappropriate_content': 'bg-orange-100 text-orange-800',
    'misinformation': 'bg-purple-100 text-purple-800',
    'other': 'bg-gray-100 text-gray-800'
  }
  return colors[reason] || 'bg-gray-100 text-gray-800'
}

// Watchers
let searchTimeout = null

watch([searchQuery, selectedCategory, sortBy], () => {
  // Debounce search
  if (searchQuery.value) {
    clearTimeout(searchTimeout)
    searchTimeout = setTimeout(() => {
      // Re-filter happens automatically via computed property
    }, 300)
  }
})

// Lifecycle
onMounted(() => {
  fetchReportedPosts()
  fetchStats()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Post Reports</h1>
        <p class="text-gray-600">Review and moderate reported content from users</p>

        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
          <div class="bg-white rounded-lg p-4 shadow-sm border">
            <div class="flex items-center">
              <div class="p-2 bg-red-100 rounded-lg">
                <svg class="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.865-.833-2.635 0L4.179 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-600">Total Reports</p>
                <p class="text-2xl font-semibold text-gray-900">{{ totalReports }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg p-4 shadow-sm border">
            <div class="flex items-center">
              <div class="p-2 bg-yellow-100 rounded-lg">
                <svg class="h-6 w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-600">Pending</p>
                <p class="text-2xl font-semibold text-gray-900">{{ reportedPosts.length }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg p-4 shadow-sm border">
            <div class="flex items-center">
              <div class="p-2 bg-green-100 rounded-lg">
                <svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-600">Resolved Today</p>
                <p class="text-2xl font-semibold text-gray-900">{{ resolvedToday }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg p-4 shadow-sm border">
            <div class="flex items-center">
              <div class="p-2 bg-gray-100 rounded-lg">
                <svg class="h-6 w-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728"></path>
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-600">Dismissed Today</p>
                <p class="text-2xl font-semibold text-gray-900">{{ dismissedToday }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-white rounded-lg shadow-sm border p-4 mb-6">
        <div class="flex flex-wrap gap-4 items-center">
          <div class="flex-1 min-w-64">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search reports by content, author, or reason..."
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <select
            v-model="selectedCategory"
            class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Categories</option>
            <option value="event">Event</option>
            <option value="news">News</option>
            <option value="discussion">Discussion</option>
            <option value="announcement">Announcement</option>
            <option value="job">Job</option>
            <option value="others">Others</option>
          </select>

          <select
            v-model="selectedReportReason"
            class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Reasons</option>
            <option value="spam">Spam</option>
            <option value="harassment">Harassment</option>
            <option value="hate_speech">Hate Speech</option>
            <option value="inappropriate_content">Inappropriate Content</option>
            <option value="misinformation">Misinformation</option>
            <option value="other">Other</option>
          </select>

          <select
            v-model="sortBy"
            class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="severity">By Severity</option>
          </select>

          <button
            @click="refreshReports"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            Refresh
          </button>
        </div>
      </div>

      <!-- Reports List -->
      <div class="space-y-6">
        <div
          v-if="loading"
          class="flex justify-center items-center py-12"
        >
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span class="ml-3 text-gray-600">Loading reported posts...</span>
        </div>

        <div
          v-else-if="filteredReports.length === 0"
          class="text-center py-12 bg-white rounded-lg shadow-sm border"
        >
          <svg class="h-12 w-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <h3 class="text-lg font-medium text-gray-900 mb-2">No reports found</h3>
          <p class="text-gray-600">All reports have been resolved. Great job!</p>
        </div>

        <div
          v-else
          v-for="report in filteredReports"
          :key="report.id"
          class="bg-white rounded-lg shadow-sm border overflow-hidden"
        >
          <!-- Report Card -->
          <div class="p-6">
            <!-- Report Info -->
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                  <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.865-.833-2.635 0L4.179 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                  </svg>
                </div>
                <div>
                  <p class="font-semibold text-gray-900">Report #{{ report.id }}</p>
                  <p class="text-sm text-gray-500">Reported {{ formatDate(report.created_at) }}</p>
                </div>
              </div>

              <div class="flex items-center space-x-2">
                <span :class="['px-2 py-1 text-xs font-medium rounded-full', getReasonColor(report.reason)]">
                  {{ getReasonLabel(report.reason) }}
                </span>
                <span class="px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded-full">
                  REPORTED
                </span>
              </div>
            </div>

            <!-- Reported Post -->
            <div class="bg-gray-50 rounded-lg p-4 mb-4">
              <div class="flex items-start space-x-3 mb-3">
                <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                  <span class="text-xs font-medium text-gray-700">
                    {{ report.post.user.first_name[0] }}{{ report.post.user.last_name[0] }}
                  </span>
                </div>
                <div class="flex-1">
                  <p class="font-medium text-gray-900">{{ report.post.user.first_name }} {{ report.post.user.last_name }}</p>
                  <p class="text-sm text-gray-500">{{ formatDate(report.post.created_at) }}</p>
                </div>
                <span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                  {{ report.post.content_category.toUpperCase() }}
                </span>
              </div>

              <div>
                <h4 v-if="report.post.title" class="font-semibold text-gray-900 mb-2">{{ report.post.title }}</h4>
                <p class="text-gray-700 whitespace-pre-wrap">{{ report.post.content }}</p>
              </div>

              <div v-if="report.post.image" class="mt-3">
                <img
                  :src="report.post.image"
                  :alt="report.post.title || 'Post image'"
                  class="rounded-lg max-w-full h-auto max-h-48 object-cover"
                />
              </div>
            </div>

            <!-- Report Details -->
            <div class="mb-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
              <p class="text-sm text-gray-700">
                <strong>Report Reason:</strong> {{ getReasonLabel(report.reason) }}
              </p>
              <p v-if="report.description" class="text-sm text-gray-700 mt-1">
                <strong>Details:</strong> {{ report.description }}
              </p>
              <p class="text-sm text-gray-500 mt-1">
                Reported by {{ report.reporter?.first_name }} {{ report.reporter?.last_name }} • {{ formatTimeAgo(report.created_at) }}
              </p>
            </div>

            <!-- Action Buttons -->
            <div class="flex items-center justify-between pt-4 border-t border-gray-200">
              <div class="flex items-center space-x-4 text-sm text-gray-500">
                <span>Report ID: #{{ report.id }}</span>
                <span>•</span>
                <span>Post ID: #{{ report.post.id }}</span>
              </div>

              <div class="flex items-center space-x-3">
                <button
                  @click="dismissReport(report.id)"
                  class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors flex items-center gap-2"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728"></path>
                  </svg>
                  Dismiss
                </button>

                <button
                  @click="takeAction(report, 'warn')"
                  class="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors flex items-center gap-2"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.865-.833-2.635 0L4.179 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                  </svg>
                  Warn User
                </button>

                <button
                  @click="takeAction(report, 'remove')"
                  class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                  </svg>
                  Remove Post
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Load More Button -->
      <div
        v-if="hasMore && !loading"
        class="text-center mt-8"
      >
        <button
          @click="loadMore"
          class="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Load More Reports
        </button>
      </div>
    </div>

    <!-- Action Confirmation Modal -->
    <div
      v-if="actionModal.show"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="actionModal.show = false"
    >
      <div class="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4 p-6">
        <div class="text-center">
          <div
            :class="[
              'w-12 h-12 rounded-full mx-auto mb-4 flex items-center justify-center',
              actionModal.action === 'remove' ? 'bg-red-100' : actionModal.action === 'warn' ? 'bg-yellow-100' : 'bg-gray-100'
            ]"
          >
            <svg
              v-if="actionModal.action === 'remove'"
              class="w-6 h-6 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
            <svg
              v-else-if="actionModal.action === 'warn'"
              class="w-6 h-6 text-yellow-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.865-.833-2.635 0L4.179 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
            <svg
              v-else
              class="w-6 h-6 text-gray-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>

          <h3 class="text-lg font-semibold text-gray-900 mb-2">
            {{ actionModal.action === 'remove' ? 'Remove Post' : actionModal.action === 'warn' ? 'Warn User' : 'Confirm Action' }}
          </h3>

          <p class="text-gray-600 mb-6">
            <span v-if="actionModal.action === 'remove'">
              This will permanently remove the reported post. The user will be notified of this action. Are you sure?
            </span>
            <span v-else-if="actionModal.action === 'warn'">
              This will send a warning to the user about their post content. The report will be marked as resolved. Continue?
            </span>
            <span v-else>
              Are you sure you want to proceed with this action?
            </span>
          </p>

          <!-- Report Details -->
          <div v-if="actionModal.report" class="bg-gray-50 rounded-lg p-3 mb-6 text-left">
            <p class="text-sm text-gray-700">
              <strong>Report:</strong> {{ getReasonLabel(actionModal.report.reason) }}
            </p>
            <p v-if="actionModal.report.description" class="text-sm text-gray-700 mt-1">
              <strong>Details:</strong> {{ actionModal.report.description }}
            </p>
            <p class="text-sm text-gray-500 mt-1">
              By {{ actionModal.report.reporter?.first_name }} {{ actionModal.report.reporter?.last_name }}
            </p>
          </div>

          <div class="flex items-center justify-center space-x-3">
            <button
              @click="actionModal.show = false"
              class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
            <button
              @click="confirmAction"
              :class="[
                'px-4 py-2 rounded-lg text-white transition-colors',
                actionModal.action === 'remove'
                  ? 'bg-red-600 hover:bg-red-700'
                  : actionModal.action === 'warn'
                    ? 'bg-yellow-600 hover:bg-yellow-700'
                    : 'bg-blue-600 hover:bg-blue-700'
              ]"
            >
              {{ actionModal.action === 'remove' ? 'Remove Post' : actionModal.action === 'warn' ? 'Send Warning' : 'Confirm' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div
      v-if="successMessage"
      class="fixed top-4 right-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded z-50"
    >
      {{ successMessage }}
      <button @click="successMessage = ''" class="ml-2 text-green-700 hover:text-green-900">×</button>
    </div>

    <div
      v-if="errorMessage"
      class="fixed top-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded z-50"
    >
      {{ errorMessage }}
      <button @click="errorMessage = ''" class="ml-2 text-red-700 hover:text-red-900">×</button>
    </div>
  </div>
</template>
