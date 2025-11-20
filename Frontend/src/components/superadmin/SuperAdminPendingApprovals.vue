<template>
  <div :class="['rounded-lg shadow-sm border', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
    <!-- Header -->
    <div :class="['p-6 border-b', themeStore.isAdminDark() ? 'border-gray-700' : 'border-gray-200']">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-yellow-900' : 'bg-yellow-100']">
            <UserCheck :class="['w-6 h-6', themeStore.isAdminDark() ? 'text-yellow-400' : 'text-yellow-600']" />
          </div>
          <div>
            <h3 :class="['text-lg font-semibold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
              Pending Alumni Approvals
            </h3>
            <p :class="['text-sm', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
              {{ pendingUsers.length }} registration{{ pendingUsers.length !== 1 ? 's' : '' }} awaiting review
            </p>
          </div>
        </div>
        <button
          @click="$emit('refresh')"
          :disabled="loading"
          :class="[
            'text-sm transition-colors disabled:opacity-50',
            themeStore.isAdminDark() ? 'text-orange-400 hover:text-orange-300' : 'text-orange-600 hover:text-orange-700'
          ]"
        >
          <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': loading }" />
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="p-6">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-8">
        <Loader class="w-8 h-8 mx-auto animate-spin text-orange-600" />
        <p :class="['mt-2 text-sm', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
          Loading approvals...
        </p>
      </div>

      <!-- Empty State -->
      <div v-else-if="pendingUsers.length === 0" class="text-center py-8">
        <CheckCircle :class="['w-12 h-12 mx-auto mb-3', themeStore.isAdminDark() ? 'text-green-400' : 'text-green-600']" />
        <p :class="['text-sm font-medium', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
          All caught up!
        </p>
        <p :class="['text-xs mt-1', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
          No pending alumni registrations at this time.
        </p>
      </div>

      <!-- Approvals List -->
      <div v-else class="space-y-4">
        <div
          v-for="user in pendingUsers"
          :key="user.id"
          :class="[
            'p-4 rounded-lg border transition-all',
            themeStore.isAdminDark() 
              ? 'bg-gray-900 border-gray-700 hover:border-orange-600' 
              : 'bg-gray-50 border-gray-200 hover:border-orange-400'
          ]"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-2">
                <h4 :class="['font-semibold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
                  {{ user.name }}
                </h4>
                <span :class="[
                  'px-2 py-0.5 text-xs rounded-full',
                  themeStore.isAdminDark() 
                    ? 'bg-yellow-900 text-yellow-300' 
                    : 'bg-yellow-100 text-yellow-800'
                ]">
                  {{ user.status }}
                </span>
              </div>
              <p :class="['text-sm mt-1', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
                {{ user.email }}
              </p>
              <div class="flex items-center space-x-4 mt-2 text-xs">
                <span :class="themeStore.isAdminDark() ? 'text-gray-500' : 'text-gray-500'">
                  <span class="font-medium">Program:</span> {{ user.program }}
                </span>
                <span :class="themeStore.isAdminDark() ? 'text-gray-500' : 'text-gray-500'">
                  <span class="font-medium">Year:</span> {{ user.yearGraduated }}
                </span>
                <span :class="themeStore.isAdminDark() ? 'text-gray-500' : 'text-gray-500'">
                  <span class="font-medium">Submitted:</span> {{ formatDate(user.submittedAt) }}
                </span>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex space-x-2 ml-4">
              <button
                @click="handleApprove(user.id)"
                :disabled="processingUsers.has(user.id)"
                :class="[
                  'px-3 py-1.5 text-xs font-medium rounded-md transition-colors disabled:opacity-50',
                  themeStore.isAdminDark()
                    ? 'bg-green-900 text-green-300 hover:bg-green-800'
                    : 'bg-green-100 text-green-700 hover:bg-green-200'
                ]"
              >
                <Check v-if="!processingUsers.has(user.id)" class="w-4 h-4" />
                <Loader v-else class="w-4 h-4 animate-spin" />
              </button>
              <button
                @click="handleReject(user.id)"
                :disabled="processingUsers.has(user.id)"
                :class="[
                  'px-3 py-1.5 text-xs font-medium rounded-md transition-colors disabled:opacity-50',
                  themeStore.isAdminDark()
                    ? 'bg-red-900 text-red-300 hover:bg-red-800'
                    : 'bg-red-100 text-red-700 hover:bg-red-200'
                ]"
              >
                <X v-if="!processingUsers.has(user.id)" class="w-4 h-4" />
                <Loader v-else class="w-4 h-4 animate-spin" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { UserCheck, RefreshCw, CheckCircle, Check, X, Loader } from 'lucide-vue-next'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

defineProps({
  pendingUsers: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['approve-user', 'reject-user', 'refresh'])

const processingUsers = ref(new Set())

const handleApprove = async (userId) => {
  processingUsers.value.add(userId)
  try {
    await emit('approve-user', userId)
  } finally {
    processingUsers.value.delete(userId)
  }
}

const handleReject = async (userId) => {
  processingUsers.value.add(userId)
  try {
    await emit('reject-user', userId)
  } finally {
    processingUsers.value.delete(userId)
  }
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  try {
    return new Date(date).toLocaleDateString()
  } catch {
    return 'Invalid'
  }
}
</script>
