<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
      <!-- Header -->
      <div class="modal-header">
        <h3 class="modal-title">
          <i class="fas fa-eye text-blue-500"></i>
          Survey Preview
        </h3>
        <button @click="$emit('close')" class="close-button">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <!-- Body -->
      <div class="modal-body">
        <div class="survey-info">
          <div class="info-row">
            <span class="label">Survey Name:</span>
            <span class="value font-semibold">{{ survey.name }}</span>
          </div>

          <div v-if="survey.description" class="info-row">
            <span class="label">Description:</span>
            <p class="value text-gray-700 dark:text-gray-300">
              {{ survey.description }}
            </p>
          </div>

          <div class="info-row">
            <span class="label">Status:</span>
            <span :class="['status-badge', `status-${survey.status}`]">
              {{ formatStatus(survey.status) }}
            </span>
          </div>

          <div class="info-row">
            <span class="label">Response Count:</span>
            <span class="value">
              <i class="fas fa-users text-blue-500"></i>
              {{ survey.response_count }} responses
            </span>
          </div>

          <div class="info-row">
            <span class="label">Published:</span>
            <span class="value">
              {{ survey.is_published ? '✅ Yes' : '❌ No' }}
            </span>
          </div>

          <div class="info-row">
            <span class="label">Accepting Responses:</span>
            <span class="value">
              {{ survey.accepting_responses ? '✅ Yes' : '❌ No' }}
            </span>
          </div>

          <div v-if="survey.start_at" class="info-row">
            <span class="label">Start Date:</span>
            <span class="value">{{ formatDateTime(survey.start_at) }}</span>
          </div>

          <div v-if="survey.end_at" class="info-row">
            <span class="label">End Date:</span>
            <span class="value">{{ formatDateTime(survey.end_at) }}</span>
          </div>

          <div class="info-row">
            <span class="label">Public Link:</span>
            <div class="flex items-center gap-2 flex-1">
              <input
                :value="survey.public_url"
                readonly
                class="url-input flex-1"
                @click="$event.target.select()"
              />
              <button
                @click="copyLink"
                class="copy-btn"
              >
                <i class="fas fa-copy"></i>
              </button>
            </div>
          </div>
        </div>

        <div class="alert-info">
          <i class="fas fa-info-circle"></i>
          <p>
            This is a read-only preview. To modify the survey, use Survey Management.
            You can only copy and share this link.
          </p>
        </div>
      </div>

      <!-- Footer -->
      <div class="modal-footer">
        <button @click="$emit('close')" class="btn-secondary">
          Close
        </button>
        <button @click="openInNewTab" class="btn-primary">
          <i class="fas fa-external-link-alt"></i>
          Open Survey
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useToast } from '@/composables/useToast'
import surveyService from '@/services/surveyService'

const props = defineProps({
  survey: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close'])
const { showToast } = useToast()

const formatStatus = (status) => {
  const statusMap = {
    active: 'Active',
    scheduled: 'Scheduled',
    expired: 'Expired',
    closed: 'Closed',
    draft: 'Draft'
  }
  return statusMap[status] || status
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  })
}

const copyLink = async () => {
  try {
    const success = await surveyService.copySurveyLinkToClipboard(props.survey.public_slug)
    if (success) {
      showToast('Link copied to clipboard!', 'success')
    } else {
      throw new Error('Copy failed')
    }
  } catch (error) {
    showToast('Failed to copy link', 'error')
  }
}

const openInNewTab = () => {
  window.open(props.survey.public_url, '_blank')
}
</script>
