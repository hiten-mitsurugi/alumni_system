<script setup>
import { useThemeStore } from '@/stores/theme'
import { getReasonLabel } from '@/utils/reportHelpers'

// Stores
const themeStore = useThemeStore()

const props = defineProps({
  report: {
    type: Object,
    required: true
  },
  action: {
    type: String,
    required: true
  },
  note: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:note', 'confirm', 'cancel'])

const updateNote = (value) => {
  emit('update:note', value)
}

const handleConfirm = () => {
  emit('confirm')
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="handleCancel">
    <div :class="['rounded-xl shadow-2xl max-w-md w-full mx-4 p-6', 
                  themeStore.isAdminDark() ? 'bg-gray-800' : 'bg-white']">
      <div class="text-center">
        <div
          :class="[
            'w-12 h-12 rounded-full mx-auto mb-4 flex items-center justify-center',
            action === 'remove' ? 'bg-red-100' : action === 'warn' ? 'bg-yellow-100' : 'bg-gray-100'
          ]"
        >
          <svg
            v-if="action === 'remove'"
            class="w-6 h-6 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
          </svg>
          <svg
            v-else-if="action === 'warn'"
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

        <h3 :class="['text-lg font-semibold mb-2', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
          {{ action === 'remove' ? 'Remove Post' : action === 'warn' ? 'Warn User' : 'Confirm Action' }}
        </h3>

        <p :class="['mb-6', themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-600']">
          <span v-if="action === 'remove'">
            This will permanently remove the reported post. The user will be notified of this action. Are you sure?
          </span>
          <span v-else-if="action === 'warn'">
            This will send a warning to the user about their post content. The report will be marked as resolved. Continue?
          </span>
          <span v-else>
            Are you sure you want to proceed with this action?
          </span>
        </p>

        <!-- Report Details -->
        <div v-if="report" class="bg-gray-50 rounded-lg p-3 mb-6 text-left">
          <p class="text-sm text-gray-700">
            <strong>Report:</strong> {{ getReasonLabel(report.reason) }}
          </p>
          <p v-if="report.description" class="text-sm text-gray-700 mt-1">
            <strong>Details:</strong> {{ report.description }}
          </p>
          <p class="text-sm text-gray-500 mt-1">
            By {{ report.reporter?.first_name }} {{ report.reporter?.last_name }}
          </p>
        </div>

        <!-- Note Input (optional) -->
        <div v-if="action === 'warn' || action === 'remove'" class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Add a note (optional):
          </label>
          <textarea
            :value="note"
            @input="updateNote($event.target.value)"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Add additional notes or reason for this action..."
          ></textarea>
        </div>

        <div class="flex items-center justify-center space-x-3">
          <button
            @click="handleCancel"
            class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="handleConfirm"
            :class="[
              'px-4 py-2 rounded-lg text-white transition-colors',
              action === 'remove'
                ? 'bg-red-600 hover:bg-red-700'
                : action === 'warn'
                  ? 'bg-yellow-600 hover:bg-yellow-700'
                  : 'bg-blue-600 hover:bg-blue-700'
            ]"
          >
            {{ action === 'remove' ? 'Remove Post' : action === 'warn' ? 'Send Warning' : 'Confirm' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>