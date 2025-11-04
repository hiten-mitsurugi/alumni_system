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
        class="fixed bg-white rounded-xl shadow-2xl border border-slate-200 z-50 w-full max-w-3xl cursor-move transform transition-transform duration-200"
      >
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-gradient-to-r from-slate-50 to-slate-100 rounded-t-xl cursor-default" @mousedown.stop>
          <h3 class="text-lg font-semibold text-slate-800">Survey Analytics Dashboard</h3>
          <button
            @click="$emit('close')"
            class="p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-200 rounded-lg transition-all duration-200 cursor-pointer"
          >
            <X class="w-5 h-5" />
          </button>
        </div>

        <!-- Content -->
        <div class="px-6 py-6 max-h-[60vh] overflow-y-auto">
          <!-- Analytics Cards Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Total Questions Card -->
            <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border border-blue-200 p-5">
              <div class="flex items-start justify-between">
                <div>
                  <p class="text-blue-600 text-sm font-medium">Total Questions</p>
                  <p class="text-3xl font-bold text-blue-700 mt-2">{{ analytics.total_questions || 0 }}</p>
                </div>
                <div class="bg-blue-200 rounded-lg p-2">
                  <HelpCircle class="w-5 h-5 text-blue-600" />
                </div>
              </div>
            </div>

            <!-- Total Responses Card -->
            <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-lg border border-green-200 p-5">
              <div class="flex items-start justify-between">
                <div>
                  <p class="text-green-600 text-sm font-medium">Total Responses</p>
                  <p class="text-3xl font-bold text-green-700 mt-2">{{ analytics.total_responses || 0 }}</p>
                </div>
                <div class="bg-green-200 rounded-lg p-2">
                  <CheckCircle2 class="w-5 h-5 text-green-600" />
                </div>
              </div>
            </div>

            <!-- Active Users Card -->
            <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg border border-purple-200 p-5">
              <div class="flex items-start justify-between">
                <div>
                  <p class="text-purple-600 text-sm font-medium">Active Users</p>
                  <p class="text-3xl font-bold text-purple-700 mt-2">{{ analytics.active_users || 0 }}</p>
                </div>
                <div class="bg-purple-200 rounded-lg p-2">
                  <Users class="w-5 h-5 text-purple-600" />
                </div>
              </div>
            </div>

            <!-- Completion Rate Card -->
            <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg border border-orange-200 p-5">
              <div class="flex items-start justify-between">
                <div>
                  <p class="text-orange-600 text-sm font-medium">Completion Rate</p>
                  <p class="text-3xl font-bold text-orange-700 mt-2">{{ analytics.completion_rate || 0 }}%</p>
                </div>
                <div class="bg-orange-200 rounded-lg p-2">
                  <TrendingUp class="w-5 h-5 text-orange-600" />
                </div>
              </div>
            </div>
          </div>

          <!-- Additional Stats -->
          <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Average Response Time -->
            <div class="bg-slate-50 rounded-lg p-4 border border-slate-200">
              <div class="flex items-center gap-3 mb-2">
                <Clock class="w-4 h-4 text-slate-400" />
                <p class="text-sm font-medium text-slate-600">Average Response Time</p>
              </div>
              <p class="text-2xl font-bold text-slate-800">{{ analytics.avg_response_time || 'N/A' }}</p>
            </div>

            <!-- Total Categories -->
            <div class="bg-slate-50 rounded-lg p-4 border border-slate-200">
              <div class="flex items-center gap-3 mb-2">
                <Folder class="w-4 h-4 text-slate-400" />
                <p class="text-sm font-medium text-slate-600">Total Categories</p>
              </div>
              <p class="text-2xl font-bold text-slate-800">{{ analytics.total_categories || 0 }}</p>
            </div>
          </div>

          <!-- Recent Activity -->
          <div v-if="analytics.questions_added_today || analytics.responses_this_week" class="mt-6 p-4 bg-slate-50 rounded-lg border border-slate-200">
            <h4 class="text-sm font-semibold text-slate-800 mb-3">Quick Stats</h4>
            <div class="grid grid-cols-2 gap-3 text-sm">
              <div v-if="analytics.questions_added_today" class="flex items-center justify-between">
                <span class="text-slate-600">Questions added today:</span>
                <span class="font-semibold text-green-600">+{{ analytics.questions_added_today }}</span>
              </div>
              <div v-if="analytics.responses_this_week" class="flex items-center justify-between">
                <span class="text-slate-600">Responses this week:</span>
                <span class="font-semibold text-blue-600">+{{ analytics.responses_this_week }}</span>
              </div>
              <div v-if="analytics.users_online" class="flex items-center justify-between">
                <span class="text-slate-600">Users online:</span>
                <span class="font-semibold text-purple-600">{{ analytics.users_online }}</span>
              </div>
              <div v-if="analytics.rate_change" class="flex items-center justify-between">
                <span class="text-slate-600">Rate change:</span>
                <span :class="['font-semibold', analytics.rate_change >= 0 ? 'text-green-600' : 'text-red-600']">
                  {{ analytics.rate_change >= 0 ? '+' : '' }}{{ analytics.rate_change }}%
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex gap-3 px-6 py-4 border-t border-slate-200 bg-slate-50 rounded-b-xl cursor-default" @mousedown.stop>
          <button
            @click="$emit('close')"
            class="w-full px-4 py-2 bg-gradient-to-r from-orange-600 to-orange-500 text-white rounded-lg hover:from-orange-500 hover:to-orange-600 transition-all duration-200 font-medium cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { HelpCircle, CheckCircle2, Users, TrendingUp, Clock, Folder, X } from 'lucide-vue-next'

defineProps({
  show: {
    type: Boolean,
    required: true
  },
  analytics: {
    type: Object,
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
  }
})

defineEmits(['close', 'drag-start', 'reset-position'])
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
