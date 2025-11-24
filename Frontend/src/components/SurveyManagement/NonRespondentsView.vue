<template>
  <div class="space-y-6">
    <!-- Main Table Card -->
    <div class="rounded-xl shadow-lg bg-white">
      <!-- Header with Search and Actions -->
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-lg font-semibold text-gray-900">Alumni Who Haven't Responded</h3>
          
          <!-- Action Buttons -->
          <div class="flex items-center gap-3">
            <!-- Remind All -->
            <button
              @click="remindAll"
              :disabled="loading || filteredNonRespondents.length === 0 || sending"
              class="flex items-center gap-2 px-6 py-2 rounded-lg shadow-sm transition-all duration-200 border bg-orange-600 hover:bg-orange-700 text-white border-orange-600 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              <svg v-if="!sending" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
              </svg>
              <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ sending ? 'Sending...' : `Remind All (${filteredNonRespondents.length})` }}</span>
            </button>
          </div>
        </div>

        <!-- Search and Filters -->
        <div class="flex items-center gap-3">
          <!-- Search -->
          <div class="flex-1 max-w-md">
            <div class="relative">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search by name or email..."
                class="w-full pl-10 pr-4 py-2 border border-gray-300 bg-white text-gray-900 placeholder-gray-500 rounded-lg shadow-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all"
              />
              <svg class="absolute left-3 top-2.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
            </div>
          </div>

          <!-- Program Filter -->
          <select
            v-model="filters.program"
            @change="applyFilters"
            class="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">All Programs</option>
            <option v-for="program in availablePrograms" :key="program" :value="program">{{ program }}</option>
          </select>

          <!-- Year Graduated Filter -->
          <input
            v-model="filters.year_graduated"
            @input="applyFilters"
            type="number"
            placeholder="Year Graduated"
            class="w-32 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-orange-500 focus:border-orange-500"
          />

          <!-- Clear Filters -->
          <button
            v-if="filters.program || filters.year_graduated"
            @click="clearFilters"
            class="px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded-lg transition"
          >
            Clear
          </button>
        </div>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto">
        <table v-if="filteredNonRespondents.length" class="min-w-full">
          <thead class="text-white text-sm uppercase bg-orange-600">
            <tr>
              <th class="p-4 text-left">Name</th>
              <th class="p-4 text-left">Email</th>
              <th class="p-4 text-left">Program</th>
              <th class="p-4 text-center">Year Graduated</th>
              <th class="p-4 text-left">Contact</th>
              <th class="p-4 text-left">Last Login</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="user in filteredNonRespondents"
              :key="user.id"
              class="border-t hover:bg-orange-50 transition-colors duration-200"
            >
              <td class="p-4 text-gray-900">{{ user.full_name || `${user.first_name} ${user.last_name}` }}</td>
              <td class="p-4 text-gray-600 text-sm">{{ user.email }}</td>
              <td class="p-4 text-gray-900">{{ user.program || 'N/A' }}</td>
              <td class="p-4 text-center text-gray-900">{{ user.year_graduated || 'N/A' }}</td>
              <td class="p-4 text-gray-600 text-sm">{{ user.contact_number || 'N/A' }}</td>
              <td class="p-4 text-gray-600 text-sm">{{ formatLastLogin(user.last_login) }}</td>
            </tr>
          </tbody>
        </table>

        <!-- Loading State -->
        <div v-else-if="loading" class="text-center py-12">
          <svg class="w-8 h-8 animate-spin mx-auto mb-2 text-orange-600" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="text-gray-500 text-sm">Loading non-respondents...</p>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-12">
          <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          <p class="text-gray-500">{{ error || 'All alumni have responded to this survey! 🎉' }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '@/services/api';

const props = defineProps({
  form: {
    type: Object,
    required: true
  }
});

// State
const loading = ref(false);
const sending = ref(false);
const error = ref(null);
const nonRespondents = ref([]);
const statistics = ref({
  total_alumni: 0,
  total_respondents: 0,
  total_non_respondents: 0,
  response_rate: 0
});
const searchQuery = ref('');
const filters = ref({
  program: '',
  year_graduated: ''
});

// Computed
const availablePrograms = computed(() => {
  const programs = nonRespondents.value.map(u => u.program).filter(Boolean);
  return Array.from(new Set(programs)).sort();
});

const filteredNonRespondents = computed(() => {
  let result = nonRespondents.value;

  if (searchQuery.value) {
    const search = searchQuery.value.toLowerCase();
    result = result.filter(user =>
      user.first_name?.toLowerCase().includes(search) ||
      user.last_name?.toLowerCase().includes(search) ||
      user.email?.toLowerCase().includes(search) ||
      user.full_name?.toLowerCase().includes(search)
    );
  }

  return result;
});

// Methods
const fetchNonRespondents = async () => {
  if (!props.form?.id) return;

  loading.value = true;
  error.value = null;

  try {
    const params = {};
    if (filters.value.program) params.program = filters.value.program;
    if (filters.value.year_graduated) params.year_graduated = filters.value.year_graduated;

    const response = await api.get(`/survey/${props.form.id}/non-respondents/`, { params });
    
    nonRespondents.value = response.data.non_respondents || [];
    statistics.value = response.data.statistics || {};
  } catch (err) {
    console.error('Failed to fetch non-respondents:', err);
    error.value = err.response?.data?.error || 'Failed to load non-respondents';
    nonRespondents.value = [];
  } finally {
    loading.value = false;
  }
};

const applyFilters = () => {
  fetchNonRespondents();
};

const clearFilters = () => {
  filters.value = { program: '', year_graduated: '' };
  applyFilters();
};



const remindAll = async () => {
  const count = filteredNonRespondents.value.length;
  if (!confirm(`Send survey reminders to ${count} non-respondent${count > 1 ? 's' : ''}?`)) return;

  sending.value = true;

  try {
    const payload = { filters: {} };
    if (filters.value.program) payload.filters.program = filters.value.program;
    if (filters.value.year_graduated) payload.filters.year_graduated = filters.value.year_graduated;

    const response = await api.post(`/survey/${props.form.id}/notify-non-respondents/`, payload);
    const { notified, skipped, message } = response.data;

    alert(`✅ ${message}\n\nNotified: ${notified}\nSkipped: ${skipped}`);
    await fetchNonRespondents();
  } catch (err) {
    console.error('Failed to send reminders:', err);
    alert(`Failed: ${err.response?.data?.error || err.message}`);
  } finally {
    sending.value = false;
  }
};

const formatLastLogin = (lastLogin) => {
  if (!lastLogin) return 'Never';
  const date = new Date(lastLogin);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
};

onMounted(() => {
  fetchNonRespondents();
});
</script>
