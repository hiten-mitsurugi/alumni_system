<template>
  <div
    v-if="analytics"
    class="fixed inset-0 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4"
  >
    <div 
      :class="[
        'draggable-modal relative bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden',
        isDragging && draggedModal === 'analytics' ? 'dragging' : ''
      ]"
      data-modal="analytics"
      @click.stop
      :style="{ transform: `translate(${modalPosition.x}px, ${modalPosition.y}px)` }"
    >
      <div 
        :class="[
          'bg-gradient-to-r from-purple-600 to-pink-600 p-6 select-none flex items-center justify-between',
          isDragging && draggedModal === 'analytics' ? 'cursor-grabbing' : 'cursor-move'
        ]"
        @mousedown="$emit('startDrag', $event, 'analytics')"
      >
        <div>
          <h3 class="text-xl font-bold text-white flex items-center gap-2">
            <BarChart3 class="w-5 h-5 opacity-70" />
            Survey Analytics Dashboard
          </h3>
          <p class="text-purple-100 text-sm mt-1">Comprehensive overview of survey performance and responses</p>
        </div>
        <button
          @click="$emit('resetPosition', 'analytics')"
          class="text-purple-200 hover:text-white p-1 rounded transition-colors"
          title="Reset position"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
        </button>
      </div>
      
      <div class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div class="bg-gradient-to-br from-orange-50 to-orange-100 p-6 rounded-xl border border-orange-200 hover:shadow-lg transition-all duration-200 cursor-default">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-semibold text-orange-600">Total Questions</h4>
              <div class="w-8 h-8 bg-orange-600 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
              </div>
            </div>
            <p class="text-3xl font-bold text-orange-500">{{ analytics.total_questions }}</p>
            <p class="text-xs text-orange-600 mt-1">Active survey questions</p>
          </div>
          
          <div class="bg-gradient-to-br from-orange-50 to-orange-100 p-6 rounded-xl border border-orange-200 hover:shadow-lg transition-all duration-200 cursor-default">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-semibold text-orange-600">Total Responses</h4>
              <div class="w-8 h-8 bg-orange-600 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                </svg>
              </div>
            </div>
            <p class="text-3xl font-bold text-orange-500">{{ analytics.total_responses }}</p>
            <p class="text-xs text-orange-600 mt-1">Submitted answers</p>
          </div>
          
          <div class="bg-gradient-to-br from-amber-50 to-amber-100 p-6 rounded-xl border border-amber-200 hover:shadow-lg transition-all duration-200 cursor-default">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-semibold text-amber-900">Active Users</h4>
              <div class="w-8 h-8 bg-amber-600 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
                </svg>
              </div>
            </div>
            <p class="text-3xl font-bold text-amber-700">{{ analytics.total_users_responded }}</p>
            <p class="text-xs text-amber-600 mt-1">Unique participants</p>
          </div>
          
          <div class="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl border border-purple-200 hover:shadow-lg transition-all duration-200 cursor-default">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-semibold text-purple-900">Completion Rate</h4>
              <div class="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
              </div>
            </div>
            <p class="text-3xl font-bold text-purple-700">{{ analytics.completion_rate }}%</p>
            <p class="text-xs text-purple-600 mt-1">Survey completion</p>
          </div>
        </div>
        
        <div class="flex justify-end pt-6 border-t border-slate-200">
          <button
            @click="$emit('close')"
            class="px-6 py-3 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors cursor-pointer"
          >
            Close Dashboard
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { BarChart3 } from 'lucide-vue-next'

defineProps({
  analytics: {
    type: Object,
    default: null
  },
  isDragging: {
    type: Boolean,
    default: false
  },
  draggedModal: {
    type: String,
    default: null
  },
  modalPosition: {
    type: Object,
    default: () => ({ x: 0, y: 0 })
  }
})

defineEmits(['close', 'startDrag', 'resetPosition'])
</script>

<style scoped>
.draggable-modal.dragging {
  cursor: grabbing;
  user-select: none;
}
</style>
