<script setup>
import { formatDate, formatTimeAgo, getReasonLabel, getReasonColor } from '@/utils/reportHelpers'

const props = defineProps({
  report: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['dismiss', 'action'])

const handleDismiss = () => {
  emit('dismiss', props.report.id)
}

const handleAction = (action) => {
  emit('action', props.report, action)
}
</script>

<template>
  <div class="bg-white rounded-lg shadow-sm border overflow-hidden">
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
            {{ report.post.content_category?.toUpperCase() }}
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
            @click="handleDismiss"
            class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors flex items-center gap-2"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728"></path>
            </svg>
            Dismiss
          </button>

          <button
            @click="handleAction('warn')"
            class="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors flex items-center gap-2"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.865-.833-2.635 0L4.179 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
            Warn User
          </button>

          <button
            @click="handleAction('remove')"
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
</template>