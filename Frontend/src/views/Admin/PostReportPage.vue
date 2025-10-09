<script setup>
import { ref, onMounted, watch } from 'vue'
import { useReports } from '@/composables/useReports'
import { formatDate, formatTimeAgo, getReasonLabel, getReasonColor } from '@/utils/reportHelpers'
import ReportActionModal from '@/components/admin/ReportActionModal.vue'
import ReportStatsCards from '@/components/admin/ReportStatsCards.vue'
import ReportFilters from '@/components/admin/ReportFilters.vue'
import ReportCard from '@/components/admin/ReportCard.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import NotificationToast from '@/components/common/NotificationToast.vue'

const {
  // State
  reportedPosts,
  loading,
  searchQuery,
  selectedCategory,
  selectedReportReason,
  selectedStatus,
  sortBy,
  hasMore,
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
} = useReports()

// Modal state
const actionModal = ref({
  show: false,
  report: null,
  action: '', // 'dismiss', 'remove', 'warn'
  note: ''
})

// Methods
const openActionModal = (report, action) => {
  actionModal.value = {
    show: true,
    report: report,
    action: action,
    note: ''
  }
}

const closeActionModal = () => {
  actionModal.value.show = false
}

const confirmAction = async () => {
  try {
    await takeAction(
      actionModal.value.report.id,
      actionModal.value.action,
      actionModal.value.note
    )
    
    actionModal.value.show = false
  } catch (error) {
    // Error is handled in the composable
  }
}

// Watchers for search debouncing
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
        <ReportStatsCards
          :total-reports="totalReports"
          :pending-reports="reportedPosts.length"
          :resolved-today="resolvedToday"
          :dismissed-today="dismissedToday"
        />
      </div>

      <!-- Filters -->
      <ReportFilters
        :search-query="searchQuery"
        :selected-category="selectedCategory"
        :selected-report-reason="selectedReportReason"
        :sort-by="sortBy"
        @update:search-query="searchQuery = $event"
        @update:selected-category="selectedCategory = $event"
        @update:selected-report-reason="selectedReportReason = $event"
        @update:sort-by="sortBy = $event"
        @refresh="refreshReports"
      />

      <!-- Reports List -->
      <div class="space-y-6">
        <LoadingSpinner 
          v-if="loading"
          :message="'Loading reported posts...'"
        />

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

        <ReportCard
          v-else
          v-for="report in filteredReports"
          :key="report.id"
          :report="report"
          @dismiss="dismissReport"
          @action="openActionModal"
        />
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
    <ReportActionModal
      v-if="actionModal.show"
      :report="actionModal.report"
      :action="actionModal.action"
      :note="actionModal.note"
      @update:note="actionModal.note = $event"
      @confirm="confirmAction"
      @cancel="closeActionModal"
    />

    <!-- Notification Toasts -->
    <NotificationToast
      v-if="successMessage"
      type="success"
      :message="successMessage"
      @close="clearMessages"
    />

    <NotificationToast
      v-if="errorMessage"
      type="error"
      :message="errorMessage"
      @close="clearMessages"
    />
  </div>
</template>
