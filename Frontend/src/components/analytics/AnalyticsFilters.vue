<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { Filter, X, Calendar, DollarSign, Users, GraduationCap } from 'lucide-vue-next'
import { analyticsService } from '@/services/analyticsService'

const props = defineProps({
  filters: {
    type: Object,
    required: true
  },
  appliedFilters: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['apply', 'clear'])

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isAdminDark?.() || false)

// Local filter state
const localFilters = ref({ ...props.filters })
const filterOptions = ref({
  programs: [],
  graduationYears: [],
  employmentStatuses: [],
  locations: [],
  genders: [],
  civilStatuses: []
})

const isLoading = ref(false)

// Computed
const hasChanges = computed(() => {
  return JSON.stringify(localFilters.value) !== JSON.stringify(props.filters)
})

// Methods
const loadFilterOptions = async () => {
  isLoading.value = true
  try {
    const options = await analyticsService.getFilterOptions()
    filterOptions.value = options
  } catch (error) {
    console.error('Failed to load filter options:', error)
  } finally {
    isLoading.value = false
  }
}

const applyFilters = () => {
  emit('apply', { ...localFilters.value })
}

const clearFilters = () => {
  localFilters.value = {
    programs: [],
    graduationYears: [],
    employmentStatus: [],
    location: [],
    gender: [],
    civilStatus: [],
    incomeRange: [0, 200000],
    skillsRatingRange: [1, 5],
    dateRange: {
      start: null,
      end: null
    }
  }
  emit('clear')
}

const removeFilter = (filterType, value = null) => {
  if (value === null) {
    // Clear entire filter
    if (filterType === 'incomeRange') {
      localFilters.value.incomeRange = [0, 200000]
    } else if (filterType === 'skillsRatingRange') {
      localFilters.value.skillsRatingRange = [1, 5]
    } else if (filterType === 'dateRange') {
      localFilters.value.dateRange = { start: null, end: null }
    } else {
      localFilters.value[filterType] = []
    }
  } else {
    // Remove specific value
    const index = localFilters.value[filterType].indexOf(value)
    if (index > -1) {
      localFilters.value[filterType].splice(index, 1)
    }
  }
}

const formatIncomeRange = (range) => {
  return `₱${parseInt(range[0]).toLocaleString()} - ₱${parseInt(range[1]).toLocaleString()}`
}

const formatDateRange = (range) => {
  if (!range.start || !range.end) return 'All dates'
  return `${new Date(range.start).toLocaleDateString()} - ${new Date(range.end).toLocaleDateString()}`
}

// Lifecycle
onMounted(() => {
  loadFilterOptions()
})

// Watch for prop changes
watch(() => props.filters, (newFilters) => {
  localFilters.value = { ...newFilters }
}, { deep: true })
</script>

<template>
  <div :class="['p-6 space-y-6', isDark ? 'bg-gray-800' : 'bg-gray-50']">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <Filter :class="['w-5 h-5', isDark ? 'text-blue-400' : 'text-blue-600']" />
        <h3 :class="['text-lg font-semibold', isDark ? 'text-white' : 'text-gray-900']">
          Analytics Filters
        </h3>
      </div>
      <div class="flex gap-2">
        <button
          @click="applyFilters"
          :disabled="!hasChanges"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            hasChanges
              ? isDark ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-blue-600 text-white hover:bg-blue-700'
              : isDark ? 'bg-gray-700 text-gray-400 cursor-not-allowed' : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          ]"
        >
          Apply Filters
        </button>
        <button
          @click="clearFilters"
          :class="['px-4 py-2 rounded-lg text-sm font-medium transition-colors', isDark ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' : 'bg-white text-gray-700 hover:bg-gray-50 border']"
        >
          Clear All
        </button>
      </div>
    </div>

    <!-- Filter Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <!-- Programs Filter -->
      <div>
        <label :class="['block text-sm font-medium mb-2', isDark ? 'text-gray-300' : 'text-gray-700']">
          <GraduationCap class="w-4 h-4 inline mr-1" />
          Programs
        </label>
        <select
          v-model="localFilters.programs"
          multiple
          :class="[
            'w-full p-2 border rounded-lg text-sm',
            isDark ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
          ]"
          size="4"
        >
          <option
            v-for="program in filterOptions.programs"
            :key="program.value"
            :value="program.value"
            :class="isDark ? 'bg-gray-700 text-white' : 'bg-white text-gray-900'"
          >
            {{ program.label }} ({{ program.count }})
          </option>
        </select>
      </div>

      <!-- Graduation Years Filter -->
      <div>
        <label :class="['block text-sm font-medium mb-2', isDark ? 'text-gray-300' : 'text-gray-700']">
          <Calendar class="w-4 h-4 inline mr-1" />
          Graduation Years
        </label>
        <select
          v-model="localFilters.graduationYears"
          multiple
          :class="[
            'w-full p-2 border rounded-lg text-sm',
            isDark ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
          ]"
          size="4"
        >
          <option
            v-for="year in filterOptions.graduationYears"
            :key="year.value"
            :value="year.value"
            :class="isDark ? 'bg-gray-700 text-white' : 'bg-white text-gray-900'"
          >
            {{ year.label }} ({{ year.count }})
          </option>
        </select>
      </div>

      <!-- Employment Status Filter -->
      <div>
        <label :class="['block text-sm font-medium mb-2', isDark ? 'text-gray-300' : 'text-gray-700']">
          Employment Status
        </label>
        <div class="space-y-2">
          <label
            v-for="status in filterOptions.employmentStatuses"
            :key="status.value"
            class="flex items-center"
          >
            <input
              type="checkbox"
              :value="status.value"
              v-model="localFilters.employmentStatus"
              :class="['mr-2', isDark ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300']"
            />
            <span :class="['text-sm', isDark ? 'text-gray-300' : 'text-gray-700']">
              {{ status.label }} ({{ status.count }})
            </span>
          </label>
        </div>
      </div>

      <!-- Location Filter -->
      <div>
        <label :class="['block text-sm font-medium mb-2', isDark ? 'text-gray-300' : 'text-gray-700']">
          Location
        </label>
        <div class="space-y-2">
          <label
            v-for="location in filterOptions.locations"
            :key="location.value"
            class="flex items-center"
          >
            <input
              type="checkbox"
              :value="location.value"
              v-model="localFilters.location"
              :class="['mr-2', isDark ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300']"
            />
            <span :class="['text-sm', isDark ? 'text-gray-300' : 'text-gray-700']">
              {{ location.label }} ({{ location.count }})
            </span>
          </label>
        </div>
      </div>

      <!-- Gender Filter -->
      <div>
        <label :class="['block text-sm font-medium mb-2', isDark ? 'text-gray-300' : 'text-gray-700']">
          <Users class="w-4 h-4 inline mr-1" />
          Gender
        </label>
        <div class="space-y-2">
          <label
            v-for="gender in filterOptions.genders"
            :key="gender.value"
            class="flex items-center"
          >
            <input
              type="checkbox"
              :value="gender.value"
              v-model="localFilters.gender"
              :class="['mr-2', isDark ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300']"
            />
            <span :class="['text-sm', isDark ? 'text-gray-300' : 'text-gray-700']">
              {{ gender.label }} ({{ gender.count }})
            </span>
          </label>
        </div>
      </div>

      <!-- Civil Status Filter -->
      <div>
        <label :class="['block text-sm font-medium mb-2', isDark ? 'text-gray-300' : 'text-gray-700']">
          Civil Status
        </label>
        <div class="space-y-2">
          <label
            v-for="status in filterOptions.civilStatuses"
            :key="status.value"
            class="flex items-center"
          >
            <input
              type="checkbox"
              :value="status.value"
              v-model="localFilters.civilStatus"
              :class="['mr-2', isDark ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300']"
            />
            <span :class="['text-sm', isDark ? 'text-gray-300' : 'text-gray-700']">
              {{ status.label }} ({{ status.count }})
            </span>
          </label>
        </div>
      </div>

      <!-- Income Range Filter -->
      <div>
        <label :class="['block text-sm font-medium mb-2', isDark ? 'text-gray-300' : 'text-gray-700']">
          <DollarSign class="w-4 h-4 inline mr-1" />
          Monthly Income Range
        </label>
        <div class="space-y-2">
          <input
            type="range"
            v-model.number="localFilters.incomeRange[0]"
            min="0"
            max="200000"
            step="5000"
            :class="['w-full', isDark ? 'accent-blue-500' : 'accent-blue-600']"
          />
          <input
            type="range"
            v-model.number="localFilters.incomeRange[1]"
            min="0"
            max="200000"
            step="5000"
            :class="['w-full', isDark ? 'accent-blue-500' : 'accent-blue-600']"
          />
          <p :class="['text-xs text-center', isDark ? 'text-gray-400' : 'text-gray-600']">
            {{ formatIncomeRange(localFilters.incomeRange) }}
          </p>
        </div>
      </div>

      <!-- Skills Rating Range Filter -->
      <div>
        <label :class="['block text-sm font-medium mb-2', isDark ? 'text-gray-300' : 'text-gray-700']">
          Skills Rating Range
        </label>
        <div class="space-y-2">
          <input
            type="range"
            v-model.number="localFilters.skillsRatingRange[0]"
            min="1"
            max="5"
            step="0.1"
            :class="['w-full', isDark ? 'accent-blue-500' : 'accent-blue-600']"
          />
          <input
            type="range"
            v-model.number="localFilters.skillsRatingRange[1]"
            min="1"
            max="5"
            step="0.1"
            :class="['w-full', isDark ? 'accent-blue-500' : 'accent-blue-600']"
          />
          <p :class="['text-xs text-center', isDark ? 'text-gray-400' : 'text-gray-600']">
            {{ localFilters.skillsRatingRange[0] }} - {{ localFilters.skillsRatingRange[1] }}
          </p>
        </div>
      </div>
    </div>

    <!-- Date Range Filter -->
    <div>
      <label :class="['block text-sm font-medium mb-2', isDark ? 'text-gray-300' : 'text-gray-700']">
        <Calendar class="w-4 h-4 inline mr-1" />
        Survey Response Date Range
      </label>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label :class="['block text-xs mb-1', isDark ? 'text-gray-400' : 'text-gray-600']">
            From Date
          </label>
          <input
            type="date"
            v-model="localFilters.dateRange.start"
            :class="[
              'w-full p-2 border rounded-lg text-sm',
              isDark ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
            ]"
          />
        </div>
        <div>
          <label :class="['block text-xs mb-1', isDark ? 'text-gray-400' : 'text-gray-600']">
            To Date
          </label>
          <input
            type="date"
            v-model="localFilters.dateRange.end"
            :class="[
              'w-full p-2 border rounded-lg text-sm',
              isDark ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
            ]"
          />
        </div>
      </div>
    </div>

    <!-- Active Filters Display -->
    <div v-if="Object.keys(appliedFilters).length > 0" class="border-t pt-4">
      <h4 :class="['text-sm font-medium mb-3', isDark ? 'text-gray-300' : 'text-gray-700']">
        Active Filters:
      </h4>
      <div class="flex flex-wrap gap-2">
        <!-- Program filters -->
        <span
          v-for="program in appliedFilters.programs || []"
          :key="`program-${program}`"
          :class="[
            'inline-flex items-center gap-1 px-2 py-1 rounded text-xs',
            isDark ? 'bg-blue-600 text-white' : 'bg-blue-100 text-blue-800'
          ]"
        >
          {{ program }}
          <button
            @click="removeFilter('programs', program)"
            :class="['hover:bg-opacity-20 rounded', isDark ? 'hover:bg-white' : 'hover:bg-black']"
          >
            <X class="w-3 h-3" />
          </button>
        </span>

        <!-- Employment status filters -->
        <span
          v-for="status in appliedFilters.employmentStatus || []"
          :key="`status-${status}`"
          :class="[
            'inline-flex items-center gap-1 px-2 py-1 rounded text-xs',
            isDark ? 'bg-green-600 text-white' : 'bg-green-100 text-green-800'
          ]"
        >
          {{ status }}
          <button
            @click="removeFilter('employmentStatus', status)"
            :class="['hover:bg-opacity-20 rounded', isDark ? 'hover:bg-white' : 'hover:bg-black']"
          >
            <X class="w-3 h-3" />
          </button>
        </span>

        <!-- Add other filter tags as needed -->
      </div>
    </div>
  </div>
</template>