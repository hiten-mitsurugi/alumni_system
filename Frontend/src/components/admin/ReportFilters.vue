<script setup>
const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  },
  selectedCategory: {
    type: String,
    default: ''
  },
  selectedReportReason: {
    type: String,
    default: ''
  },
  sortBy: {
    type: String,
    default: 'newest'
  }
})

const emit = defineEmits(['update:searchQuery', 'update:selectedCategory', 'update:selectedReportReason', 'update:sortBy', 'refresh'])

const updateSearchQuery = (value) => {
  emit('update:searchQuery', value)
}

const updateSelectedCategory = (value) => {
  emit('update:selectedCategory', value)
}

const updateSelectedReportReason = (value) => {
  emit('update:selectedReportReason', value)
}

const updateSortBy = (value) => {
  emit('update:sortBy', value)
}

const handleRefresh = () => {
  emit('refresh')
}
</script>

<template>
  <div class="bg-white rounded-lg shadow-sm border p-4 mb-6">
    <div class="flex flex-wrap gap-4 items-center">
      <div class="flex-1 min-w-64">
        <input
          :value="searchQuery"
          @input="updateSearchQuery($event.target.value)"
          type="text"
          placeholder="Search reports by content, author, or reason..."
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <select
        :value="selectedCategory"
        @change="updateSelectedCategory($event.target.value)"
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
        :value="selectedReportReason"
        @change="updateSelectedReportReason($event.target.value)"
        class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <option value="">All Reasons</option>
        <option value="spam">Spam</option>
        <option value="harassment">Harassment</option>
        <option value="inappropriate">Inappropriate Content</option>
        <option value="fake_news">False Information</option>
        <option value="violence">Violence or Threats</option>
        <option value="other">Other</option>
      </select>

      <select
        :value="sortBy"
        @change="updateSortBy($event.target.value)"
        class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <option value="newest">Newest First</option>
        <option value="oldest">Oldest First</option>
        <option value="severity">By Severity</option>
      </select>

      <button
        @click="handleRefresh"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
        </svg>
        Refresh
      </button>
    </div>
  </div>
</template>