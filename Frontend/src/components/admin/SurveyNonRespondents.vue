<template>
  <div class="survey-non-respondents p-6">
    <!-- Header with Survey Selection -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
        Survey Non-Respondents Monitoring
      </h1>
      <p class="text-gray-600 dark:text-gray-400">
        Track and export alumni who haven't responded to surveys
      </p>
    </div>

    <!-- Survey Selection -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Select Survey to Monitor
      </label>
      <select
        v-model="selectedSurveyId"
        @change="loadNonRespondents"
        class="w-full md:w-1/2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
      >
        <option :value="null">-- Select a Survey --</option>
        <option v-for="survey in surveys" :key="survey.id" :value="survey.id">
          {{ survey.name }}
        </option>
      </select>
    </div>

    <!-- Statistics Card -->
    <div v-if="statistics" class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
        <div class="text-sm text-blue-600 dark:text-blue-400 font-medium">Total Alumni</div>
        <div class="text-2xl font-bold text-blue-900 dark:text-blue-300">
          {{ statistics.total_alumni }}
        </div>
      </div>
      
      <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
        <div class="text-sm text-green-600 dark:text-green-400 font-medium">Respondents</div>
        <div class="text-2xl font-bold text-green-900 dark:text-green-300">
          {{ statistics.total_respondents }}
        </div>
      </div>
      
      <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
        <div class="text-sm text-orange-600 dark:text-orange-400 font-medium">Non-Respondents</div>
        <div class="text-2xl font-bold text-orange-900 dark:text-orange-300">
          {{ statistics.total_non_respondents }}
        </div>
      </div>
      
      <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
        <div class="text-sm text-purple-600 dark:text-purple-400 font-medium">Response Rate</div>
        <div class="text-2xl font-bold text-purple-900 dark:text-purple-300">
          {{ statistics.response_rate }}%
        </div>
      </div>
    </div>

    <!-- Filters and Actions -->
    <div v-if="selectedSurveyId" class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
      <div class="flex flex-wrap gap-4 items-end">
        <!-- Program Filter -->
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Program
          </label>
          <input
            v-model="filters.program"
            type="text"
            placeholder="e.g., BSIT, BSCS"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          />
        </div>

        <!-- Year Graduated From -->
        <div class="flex-1 min-w-[150px]">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Year From
          </label>
          <input
            v-model.number="filters.year_graduated_from"
            type="number"
            placeholder="2020"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          />
        </div>

        <!-- Year Graduated To -->
        <div class="flex-1 min-w-[150px]">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Year To
          </label>
          <input
            v-model.number="filters.year_graduated_to"
            type="number"
            placeholder="2024"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          />
        </div>

        <!-- Apply Filters Button -->
        <button
          @click="loadNonRespondents"
          :disabled="loading"
          class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          Apply Filters
        </button>

        <!-- Clear Filters Button -->
        <button
          @click="clearFilters"
          :disabled="loading"
          class="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          Clear
        </button>

        <!-- Export CSV Button -->
        <button
          @click="exportToCSV"
          :disabled="loading || !nonRespondents.length"
          class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          📥 Export CSV
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <!-- Non-Respondents Table -->
    <div v-else-if="selectedSurveyId && nonRespondents.length > 0" class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
          Non-Respondents ({{ nonRespondents.length }})
        </h2>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Name
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Email
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Program
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Year Graduated
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Contact
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                Last Login
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="alumni in nonRespondents"
              :key="alumni.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-700 transition"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-white">
                  {{ alumni.full_name }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-600 dark:text-gray-400">
                  {{ alumni.email }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900 dark:text-white">
                  {{ alumni.program || 'N/A' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900 dark:text-white">
                  {{ alumni.year_graduated || 'N/A' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-600 dark:text-gray-400">
                  {{ alumni.contact_number || 'N/A' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-600 dark:text-gray-400">
                  {{ formatLastLogin(alumni.last_login) }}
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="selectedSurveyId && !loading" class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-12 text-center">
      <div class="text-6xl mb-4">🎉</div>
      <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
        All Alumni Have Responded!
      </h3>
      <p class="text-gray-600 dark:text-gray-400">
        There are no non-respondents for this survey with the current filters.
      </p>
    </div>

    <!-- No Survey Selected State -->
    <div v-else-if="!selectedSurveyId" class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-12 text-center">
      <div class="text-6xl mb-4">📊</div>
      <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
        Select a Survey to Monitor
      </h3>
      <p class="text-gray-600 dark:text-gray-400">
        Choose a survey from the dropdown above to view non-respondents.
      </p>
    </div>

    <!-- Notification Toasts -->
    <div class="fixed top-4 right-4 z-50 space-y-2">
      <NotificationToast
        v-for="notification in notifications"
        :key="notification.id"
        :type="notification.type"
        :message="notification.message"
        @close="removeNotification(notification.id)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import NotificationToast from '@/components/common/NotificationToast.vue'
import surveyService from '@/services/surveyService'

// Toast notification state
const notifications = ref([])

const showToast = (message, type = 'success') => {
  notifications.value.push({
    id: Date.now() + Math.random(),
    message,
    type
  })
}

const removeNotification = (id) => {
  const index = notifications.value.findIndex(n => n.id === id)
  if (index > -1) {
    notifications.value.splice(index, 1)
  }
}

// Data
const surveys = ref([])
const selectedSurveyId = ref(null)
const nonRespondents = ref([])
const statistics = ref(null)
const loading = ref(false)
const filters = ref({
  program: '',
  year_graduated_from: null,
  year_graduated_to: null
})

// Lifecycle
onMounted(() => {
  loadSurveys()
})

// Methods
async function loadSurveys() {
  try {
    const response = await surveyService.getSurveyForms()
    surveys.value = response.data.results || response.data
  } catch (error) {
    console.error('Failed to load surveys:', error)
    showToast('Failed to load surveys', 'error')
  }
}

async function loadNonRespondents() {
  if (!selectedSurveyId.value) {
    return
  }

  loading.value = true
  try {
    // Build filter object (only include non-empty values)
    const activeFilters = {}
    if (filters.value.program) {
      activeFilters.program = filters.value.program
    }
    if (filters.value.year_graduated_from) {
      activeFilters.year_graduated_from = filters.value.year_graduated_from
    }
    if (filters.value.year_graduated_to) {
      activeFilters.year_graduated_to = filters.value.year_graduated_to
    }

    const response = await surveyService.getSurveyNonRespondents(
      selectedSurveyId.value,
      activeFilters
    )

    nonRespondents.value = response.data.non_respondents || []
    statistics.value = response.data.statistics || null

    showToast(`Loaded ${nonRespondents.value.length} non-respondents`)
  } catch (error) {
    console.error('Failed to load non-respondents:', error)
    showToast('Failed to load non-respondents', 'error')
    nonRespondents.value = []
    statistics.value = null
  } finally {
    loading.value = false
  }
}

async function exportToCSV() {
  if (!selectedSurveyId.value) {
    return
  }

  try {
    const survey = surveys.value.find(s => s.id === selectedSurveyId.value)
    const surveyName = survey ? survey.name : 'survey'

    // Build filter object
    const activeFilters = {}
    if (filters.value.program) {
      activeFilters.program = filters.value.program
    }
    if (filters.value.year_graduated_from) {
      activeFilters.year_graduated_from = filters.value.year_graduated_from
    }
    if (filters.value.year_graduated_to) {
      activeFilters.year_graduated_to = filters.value.year_graduated_to
    }

    const success = await surveyService.downloadNonRespondentsCSV(
      selectedSurveyId.value,
      surveyName,
      activeFilters
    )

    if (success) {
      showToast('CSV exported successfully!')
    } else {
      showToast('Failed to export CSV', 'error')
    }
  } catch (error) {
    console.error('Export failed:', error)
    showToast('Failed to export CSV', 'error')
  }
}

function clearFilters() {
  filters.value = {
    program: '',
    year_graduated_from: null,
    year_graduated_to: null
  }
  loadNonRespondents()
}

function formatLastLogin(lastLogin) {
  if (!lastLogin) {
    return 'Never'
  }
  const date = new Date(lastLogin)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
/* Additional custom styles if needed */
</style>
