<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="show" class="fixed inset-0 bg-black/50 z-40" @click="$emit('close')"></div>
    </Transition>
    <Transition name="scale">
      <div
        v-if="show"
        :style="modalPosition"
        @mousedown="$emit('drag-start', $event)"
        class="fixed bg-white rounded-xl shadow-2xl border border-slate-200 z-50 w-full max-w-lg cursor-move transform transition-transform duration-200"
      >
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-gradient-to-r from-slate-50 to-slate-100 rounded-t-xl cursor-default" @mousedown.stop>
          <h3 class="text-lg font-semibold text-slate-800">Export Survey Data</h3>
          <button
            @click="$emit('close')"
            class="p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-200 rounded-lg transition-all duration-200 cursor-pointer"
          >
            <X class="w-5 h-5" />
          </button>
        </div>

        <!-- Content -->
        <div class="px-6 py-6 space-y-5 max-h-[60vh] overflow-y-auto">
          <!-- Export Format -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-3">Export Format <span class="text-red-500">*</span></label>
            <div class="grid grid-cols-2 gap-3">
              <label class="flex items-center gap-3 p-3 border-2 rounded-lg cursor-pointer transition-all duration-200" :class="exportFormat === 'json' ? 'border-orange-500 bg-orange-50' : 'border-slate-200 hover:border-slate-300'">
                <input
                  v-model="exportFormat"
                  type="radio"
                  value="json"
                  class="w-4 h-4 text-orange-600 focus:ring-orange-500 cursor-pointer"
                />
                <div>
                  <p class="font-medium text-slate-700">JSON</p>
                  <p class="text-xs text-slate-500">Structured data format</p>
                </div>
              </label>
              <label class="flex items-center gap-3 p-3 border-2 rounded-lg cursor-pointer transition-all duration-200" :class="exportFormat === 'excel' ? 'border-orange-500 bg-orange-50' : 'border-slate-200 hover:border-slate-300'">
                <input
                  v-model="exportFormat"
                  type="radio"
                  value="excel"
                  class="w-4 h-4 text-orange-600 focus:ring-orange-500 cursor-pointer"
                />
                <div>
                  <p class="font-medium text-slate-700">Excel</p>
                  <p class="text-xs text-slate-500">Spreadsheet format</p>
                </div>
              </label>
            </div>
          </div>

          <!-- Category Filter -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">Filter by Category</label>
            <select
              v-model="exportCategory"
              class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-slate-800"
            >
              <option value="">All Categories</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }} ({{ cat.question_count }} questions)
              </option>
            </select>
            <p class="text-slate-500 text-xs mt-1">Leave empty to export all questions</p>
          </div>

          <!-- Date Range -->
          <div class="space-y-3">
            <p class="block text-sm font-medium text-slate-700">Date Range</p>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs text-slate-600 mb-1">From</label>
                <input
                  v-model="exportDateFrom"
                  type="date"
                  class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-slate-800"
                />
              </div>
              <div>
                <label class="block text-xs text-slate-600 mb-1">To</label>
                <input
                  v-model="exportDateTo"
                  type="date"
                  class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-slate-800"
                />
              </div>
            </div>
            <p class="text-slate-500 text-xs">Leave empty to include all dates</p>
          </div>

          <!-- Profile Fields to Export -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-3">Include Profile Fields</label>
            <div class="space-y-2 max-h-40 overflow-y-auto">
              <label v-for="field in availableProfileFields" :key="field" class="flex items-center gap-2 p-2 hover:bg-slate-50 rounded cursor-pointer">
                <input
                  :checked="exportProfileFields.includes(field)"
                  type="checkbox"
                  @change="toggleProfileField(field)"
                  class="w-4 h-4 rounded border-slate-300 text-orange-600 focus:ring-orange-500 cursor-pointer"
                />
                <span class="text-sm text-slate-700">{{ formatFieldName(field) }}</span>
              </label>
            </div>
          </div>

          <!-- Export Summary -->
          <div class="p-4 bg-slate-50 rounded-lg border border-slate-200">
            <h4 class="text-sm font-semibold text-slate-800 mb-2">Export Summary</h4>
            <div class="space-y-1 text-sm text-slate-600">
              <p>Format: <span class="font-semibold text-slate-800">{{ exportFormat.toUpperCase() }}</span></p>
              <p>Category: <span class="font-semibold text-slate-800">{{ exportCategory ? 'Filtered' : 'All' }}</span></p>
              <p>Profile Fields: <span class="font-semibold text-slate-800">{{ exportProfileFields.length }}</span></p>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex gap-3 px-6 py-4 border-t border-slate-200 bg-slate-50 rounded-b-xl cursor-default" @mousedown.stop>
          <button
            @click="$emit('close')"
            class="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-100 transition-all duration-200 font-medium cursor-pointer"
          >
            Cancel
          </button>
          <button
            @click="$emit('export', exportConfig)"
            :disabled="isExporting"
            class="flex-1 px-4 py-2 bg-gradient-to-r from-orange-600 to-orange-500 text-white rounded-lg hover:from-orange-500 hover:to-orange-600 transition-all duration-200 font-medium cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <Download v-if="!isExporting" class="w-4 h-4" />
            <Loader v-else class="w-4 h-4 animate-spin" />
            {{ isExporting ? 'Exporting...' : 'Export Now' }}
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { X, Download, Loader } from 'lucide-vue-next'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  categories: {
    type: Array,
    required: true
  },
  isDragging: {
    type: Boolean,
    default: false
  },
  modalPosition: {
    type: Object,
    default: () => ({
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)'
    })
  },
  isExporting: {
    type: Boolean,
    default: false
  },
  exportFormat: {
    type: String,
    default: 'json'
  },
  exportCategory: {
    type: [String, Number],
    default: ''
  },
  exportDateFrom: {
    type: String,
    default: ''
  },
  exportDateTo: {
    type: String,
    default: ''
  },
  exportProfileFields: {
    type: Array,
    default: () => ['name', 'email', 'graduation_year']
  }
})

defineEmits(['close', 'drag-start', 'reset-position', 'export'])

const availableProfileFields = [
  'name',
  'email',
  'graduation_year',
  'current_position',
  'company',
  'phone',
  'location'
]

const formatFieldName = (field) => {
  return field
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const toggleProfileField = (field) => {
  const index = props.exportProfileFields.indexOf(field)
  if (index > -1) {
    props.exportProfileFields.splice(index, 1)
  } else {
    props.exportProfileFields.push(field)
  }
}

const exportConfig = computed(() => ({
  format: props.exportFormat,
  category: props.exportCategory,
  dateFrom: props.exportDateFrom,
  dateTo: props.exportDateTo,
  profileFields: props.exportProfileFields
}))
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.scale-enter-active,
.scale-leave-active {
  transition: all 0.3s ease;
}

.scale-enter-from,
.scale-leave-to {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.95);
}
</style>
