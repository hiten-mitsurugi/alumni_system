<script setup>
import { ref, computed } from 'vue'
import surveyService from '@/services/surveyService'
import { useThemeStore } from '@/stores/theme'

const props = defineProps({
  categories: {
    type: Array,
    default: () => []
  },
  isDragging: Boolean,
  draggedModal: String,
  modalPosition: {
    type: Object,
    default: () => ({ x: 0, y: 0 })
  }
})

const emit = defineEmits(['close', 'startDrag', 'resetPosition'])

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isAdminDark?.())

const exportFormat = ref('xlsx')
const selectedCategories = ref([])
const startDate = ref('')
const endDate = ref('')
const includeProfileFields = ref({
  name: true,
  email: true,
  contact_number: true,
  address: true,
  year_graduated: true,
  course: true,
  current_occupation: true,
  company: true
})

const exporting = ref(false)

const handleExport = async () => {
  exporting.value = true
  try {
    const params = {
      format: exportFormat.value,
      categories: selectedCategories.value.join(','),
      start_date: startDate.value || undefined,
      end_date: endDate.value || undefined,
      include_profile: Object.keys(includeProfileFields.value)
        .filter(key => includeProfileFields.value[key])
        .join(',')
    }

    const response = await surveyService.exportResponses(params)
    
    const blob = new Blob([response.data], {
      type: exportFormat.value === 'xlsx' 
        ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        : 'text/csv'
    })
    
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `survey_responses_${new Date().toISOString().split('T')[0]}.${exportFormat.value}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    emit('close')
  } catch (error) {
    console.error('Export error:', error)
    alert('Failed to export data. Please try again.')
  } finally {
    exporting.value = false
  }
}

const toggleAllCategories = (e) => {
  if (e.target.checked) {
    selectedCategories.value = props.categories.map(cat => cat.id)
  } else {
    selectedCategories.value = []
  }
}

const toggleAllProfileFields = (e) => {
  const value = e.target.checked
  Object.keys(includeProfileFields.value).forEach(key => {
    includeProfileFields.value[key] = value
  })
}

const allCategoriesSelected = computed(() => {
  return selectedCategories.value.length === props.categories.length && props.categories.length > 0
})

const allProfileFieldsSelected = computed(() => {
  return Object.values(includeProfileFields.value).every(val => val)
})
</script>

<template>
  <div
    class="fixed inset-0 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4"
  >
    <div 
      :class="[
        'draggable-modal relative rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden',
        isDark ? 'bg-gray-800' : 'bg-white',
        isDragging && draggedModal === 'export' ? 'dragging' : ''
      ]"
      data-modal="export"
      @click.stop
      :style="{ transform: `translate(${modalPosition.x}px, ${modalPosition.y}px)` }"
    >
      <div 
        :class="[
          'bg-gradient-to-r from-green-600 to-green-500 p-6 select-none flex items-center justify-between',
          isDragging && draggedModal === 'export' ? 'cursor-grabbing' : 'cursor-move'
        ]"
        @mousedown="emit('startDrag', $event, 'export')"
      >
        <div>
          <h3 class="text-xl font-bold text-white flex items-center gap-2">
            Export Survey Responses
          </h3>
          <p class="text-green-100 text-sm mt-1">
            Download survey data in your preferred format
          </p>
        </div>
        <button
          @click="emit('resetPosition', 'export')"
          class="text-green-200 hover:text-white p-1 rounded transition-colors"
          title="Reset position"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
      
      <form @submit.prevent="handleExport" class="p-6 space-y-6 max-h-[calc(90vh-120px)] overflow-y-auto">
        <div class="space-y-4">
          <div>
            <label :class="['block text-sm font-semibold mb-3', isDark ? 'text-gray-300' : 'text-slate-700']">Export Format</label>
            <div class="grid grid-cols-2 gap-3">
              <label :class="[
                'flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all',
                exportFormat === 'xlsx' 
                  ? 'border-green-500 bg-green-50 dark:bg-green-900/20' 
                  : isDark ? 'border-gray-600 hover:border-gray-500' : 'border-slate-200 hover:border-slate-300'
              ]">
                <input
                  type="radio"
                  v-model="exportFormat"
                  value="xlsx"
                  class="h-4 w-4 text-green-600 focus:ring-green-500"
                />
                <span :class="['ml-3 font-medium', isDark ? 'text-gray-300' : 'text-slate-700']">Excel (.xlsx)</span>
              </label>
              <label :class="[
                'flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all',
                exportFormat === 'csv' 
                  ? 'border-green-500 bg-green-50 dark:bg-green-900/20' 
                  : isDark ? 'border-gray-600 hover:border-gray-500' : 'border-slate-200 hover:border-slate-300'
              ]">
                <input
                  type="radio"
                  v-model="exportFormat"
                  value="csv"
                  class="h-4 w-4 text-green-600 focus:ring-green-500"
                />
                <span :class="['ml-3 font-medium', isDark ? 'text-gray-300' : 'text-slate-700']">CSV (.csv)</span>
              </label>
            </div>
          </div>

          <div>
            <div class="flex items-center justify-between mb-3">
              <label :class="['block text-sm font-semibold', isDark ? 'text-gray-300' : 'text-slate-700']">Select Categories</label>
              <label class="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  :checked="allCategoriesSelected"
                  @change="toggleAllCategories"
                  class="h-4 w-4 text-green-600 focus:ring-green-500 rounded"
                />
                <span :class="['ml-2 text-xs font-medium', isDark ? 'text-gray-400' : 'text-slate-600']">Select All</span>
              </label>
            </div>
            <div :class="['grid grid-cols-1 md:grid-cols-2 gap-2 p-4 rounded-lg max-h-48 overflow-y-auto', isDark ? 'bg-gray-700' : 'bg-slate-50']">
              <label
                v-for="cat in categories"
                :key="cat.id"
                class="flex items-center p-2 hover:bg-slate-100 dark:hover:bg-gray-600 rounded cursor-pointer transition-colors"
              >
                <input
                  type="checkbox"
                  :value="cat.id"
                  v-model="selectedCategories"
                  class="h-4 w-4 text-green-600 focus:ring-green-500 rounded"
                />
                <span :class="['ml-2 text-sm', isDark ? 'text-gray-300' : 'text-slate-700']">{{ cat.name }}</span>
              </label>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label :class="['block text-sm font-semibold mb-2', isDark ? 'text-gray-300' : 'text-slate-700']">Start Date</label>
              <input
                type="date"
                v-model="startDate"
                :class="[
                  'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500',
                  isDark ? 'bg-gray-700 border-gray-600 text-white' : 'border-slate-300'
                ]"
              />
            </div>
            <div>
              <label :class="['block text-sm font-semibold mb-2', isDark ? 'text-gray-300' : 'text-slate-700']">End Date</label>
              <input
                type="date"
                v-model="endDate"
                :class="[
                  'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500',
                  isDark ? 'bg-gray-700 border-gray-600 text-white' : 'border-slate-300'
                ]"
              />
            </div>
          </div>

          <div>
            <div class="flex items-center justify-between mb-3">
              <label :class="['block text-sm font-semibold', isDark ? 'text-gray-300' : 'text-slate-700']">Include Profile Fields</label>
              <label class="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  :checked="allProfileFieldsSelected"
                  @change="toggleAllProfileFields"
                  class="h-4 w-4 text-green-600 focus:ring-green-500 rounded"
                />
                <span :class="['ml-2 text-xs font-medium', isDark ? 'text-gray-400' : 'text-slate-600']">Select All</span>
              </label>
            </div>
            <div :class="['grid grid-cols-2 gap-2 p-4 rounded-lg', isDark ? 'bg-gray-700' : 'bg-slate-50']">
              <label class="flex items-center p-2 hover:bg-slate-100 dark:hover:bg-gray-600 rounded cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  v-model="includeProfileFields.name"
                  class="h-4 w-4 text-green-600 focus:ring-green-500 rounded"
                />
                <span :class="['ml-2 text-sm', isDark ? 'text-gray-300' : 'text-slate-700']">Name</span>
              </label>
              <label class="flex items-center p-2 hover:bg-slate-100 dark:hover:bg-gray-600 rounded cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  v-model="includeProfileFields.email"
                  class="h-4 w-4 text-green-600 focus:ring-green-500 rounded"
                />
                <span :class="['ml-2 text-sm', isDark ? 'text-gray-300' : 'text-slate-700']">Email</span>
              </label>
              <label class="flex items-center p-2 hover:bg-slate-100 dark:hover:bg-gray-600 rounded cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  v-model="includeProfileFields.contact_number"
                  class="h-4 w-4 text-green-600 focus:ring-green-500 rounded"
                />
                <span :class="['ml-2 text-sm', isDark ? 'text-gray-300' : 'text-slate-700']">Contact Number</span>
              </label>
              <label class="flex items-center p-2 hover:bg-slate-100 dark:hover:bg-gray-600 rounded cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  v-model="includeProfileFields.address"
                  class="h-4 w-4 text-green-600 focus:ring-green-500 rounded"
                />
                <span :class="['ml-2 text-sm', isDark ? 'text-gray-300' : 'text-slate-700']">Address</span>
              </label>
              <label class="flex items-center p-2 hover:bg-slate-100 dark:hover:bg-gray-600 rounded cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  v-model="includeProfileFields.year_graduated"
                  class="h-4 w-4 text-green-600 focus:ring-green-500 rounded"
                />
                <span :class="['ml-2 text-sm', isDark ? 'text-gray-300' : 'text-slate-700']">Year Graduated</span>
              </label>
              <label class="flex items-center p-2 hover:bg-slate-100 dark:hover:bg-gray-600 rounded cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  v-model="includeProfileFields.course"
                  class="h-4 w-4 text-green-600 focus:ring-green-500 rounded"
                />
                <span :class="['ml-2 text-sm', isDark ? 'text-gray-300' : 'text-slate-700']">Course</span>
              </label>
              <label class="flex items-center p-2 hover:bg-slate-100 dark:hover:bg-gray-600 rounded cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  v-model="includeProfileFields.current_occupation"
                  class="h-4 w-4 text-green-600 focus:ring-green-500 rounded"
                />
                <span :class="['ml-2 text-sm', isDark ? 'text-gray-300' : 'text-slate-700']">Current Occupation</span>
              </label>
              <label class="flex items-center p-2 hover:bg-slate-100 dark:hover:bg-gray-600 rounded cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  v-model="includeProfileFields.company"
                  class="h-4 w-4 text-green-600 focus:ring-green-500 rounded"
                />
                <span :class="['ml-2 text-sm', isDark ? 'text-gray-300' : 'text-slate-700']">Company</span>
              </label>
            </div>
          </div>
        </div>
        
        <div :class="['flex justify-end gap-3 pt-6 border-t', isDark ? 'border-gray-700' : 'border-slate-200']">
          <button
            type="button"
            @click="emit('close')"
            :class="[
              'px-6 py-3 text-sm font-medium rounded-lg transition-colors',
              isDark ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' : 'text-slate-700 bg-slate-100 hover:bg-slate-200'
            ]"
            :disabled="exporting"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="px-6 py-3 text-sm font-medium text-white bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-600 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            :disabled="exporting"
          >
            <svg v-if="exporting" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ exporting ? 'Exporting...' : 'Export Data' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
