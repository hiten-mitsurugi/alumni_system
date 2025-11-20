<template>
  <div :class="['rounded-lg shadow-sm border', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
    <!-- Header -->
    <div :class="['p-6 border-b', themeStore.isAdminDark() ? 'border-gray-700' : 'border-gray-200']">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div :class="['p-2 rounded-lg', themeStore.isAdminDark() ? 'bg-yellow-900' : 'bg-yellow-100']">
            <Clock :class="['w-6 h-6', themeStore.isAdminDark() ? 'text-yellow-400' : 'text-yellow-600']" />
          </div>
          <div>
            <h3 :class="['text-lg font-semibold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
              Pending User Approvals
            </h3>
            <p :class="['text-sm', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
              Alumni registrations waiting for approval
            </p>
          </div>
        </div>
        <div class="flex items-center space-x-3">
          <span :class="[
            'px-3 py-1 rounded-full text-sm font-medium',
            themeStore.isAdminDark() ? 'bg-yellow-900 text-yellow-300' : 'bg-yellow-100 text-yellow-800'
          ]">
            {{ pendingUsers.length }} pending
          </span>
          <button 
            @click="$emit('refresh')"
            :disabled="loading"
            :class="['text-sm hover:underline disabled:opacity-50', themeStore.isAdminDark() ? 'text-blue-400' : 'text-blue-600']"
          >
            <RefreshCw class="w-4 h-4 inline mr-1" :class="{ 'animate-spin': loading }" />
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="p-6">
      <div class="space-y-4">
        <div v-for="i in 3" :key="i" class="animate-pulse">
          <div class="flex items-center space-x-4">
            <div class="h-12 w-12 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
            <div class="flex-1 space-y-2">
              <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>
              <div class="h-3 bg-gray-300 dark:bg-gray-600 rounded w-1/2"></div>
            </div>
            <div class="flex space-x-2">
              <div class="h-8 w-16 bg-gray-300 dark:bg-gray-600 rounded"></div>
              <div class="h-8 w-16 bg-gray-300 dark:bg-gray-600 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="pendingUsers.length === 0" class="p-12 text-center">
      <div class="mx-auto w-24 h-24 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mb-4">
        <CheckCircle class="w-12 h-12 text-green-600 dark:text-green-400" />
      </div>
      <h4 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
        All Caught Up!
      </h4>
      <p class="text-gray-600 dark:text-gray-400">
        No pending user approvals at this time.
      </p>
    </div>

    <!-- Pending Users List -->
    <div v-else class="p-6">
      <div class="space-y-4">
        <div
          v-for="user in pendingUsers"
          :key="user.id"
          :class="[
            'p-4 rounded-lg border transition-all',
            themeStore.isAdminDark() 
              ? 'bg-gray-900 border-gray-700 hover:border-blue-600' 
              : 'bg-gray-50 border-gray-200 hover:border-blue-400'
          ]"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-2">
                <h4 :class="['font-semibold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">
                  {{ getUserName(user) }}
                </h4>
                <span :class="[
                  'px-2 py-0.5 text-xs rounded-full',
                  themeStore.isAdminDark() 
                    ? 'bg-yellow-900 text-yellow-300' 
                    : 'bg-yellow-100 text-yellow-800'
                ]">
                  Pending Review
                </span>
              </div>
              <p :class="['text-sm mt-1', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600']">
                {{ user.email }}
              </p>
              <div class="flex items-center space-x-4 mt-2 text-xs">
                <span :class="themeStore.isAdminDark() ? 'text-gray-500' : 'text-gray-500'">
                  <span class="font-medium">Type:</span> {{ getUserTypeLabel(user.user_type) }}
                </span>
                <span :class="themeStore.isAdminDark() ? 'text-gray-500' : 'text-gray-500'">
                  <span class="font-medium">Registered:</span> {{ formatDate(user.date_joined) }}
                </span>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex space-x-2 ml-4">
              <button
                @click="handleApproveUser(user.id)"
                :disabled="processingUsers.has(user.id)"
                :class="[
                  'px-3 py-1.5 text-xs font-medium rounded-md transition-colors disabled:opacity-50',
                  themeStore.isAdminDark()
                    ? 'bg-green-900 text-green-300 hover:bg-green-800'
                    : 'bg-green-100 text-green-700 hover:bg-green-200'
                ]"
              >
                <Check class="w-4 h-4" />
              </button>
              <button
                @click="handleRejectUser(user.id)"
                :disabled="processingUsers.has(user.id)"
                :class="[
                  'px-3 py-1.5 text-xs font-medium rounded-md transition-colors disabled:opacity-50',
                  themeStore.isAdminDark()
                    ? 'bg-red-900 text-red-300 hover:bg-red-800'
                    : 'bg-red-100 text-red-700 hover:bg-red-200'
                ]"
              >
                <X class="w-4 h-4" />
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
import { 
  Clock, CheckCircle, Check, X, RefreshCw
} from 'lucide-vue-next'
import { useThemeStore } from '@/stores/theme'

// Theme store
const themeStore = useThemeStore()

// Props
const props = defineProps({
  pendingUsers: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits([
  'approve-user', 'reject-user', 'refresh'
])

// Local state
const processingUsers = ref(new Set())

// Methods
const handleApproveUser = async (userId) => {
  processingUsers.value.add(userId)
  try {
    await emit('approve-user', userId)
  } finally {
    processingUsers.value.delete(userId)
  }
}

const handleRejectUser = async (userId) => {
  processingUsers.value.add(userId)
  try {
    await emit('reject-user', userId)
  } finally {
    processingUsers.value.delete(userId)
  }
}

const getUserName = (user) => {
  if (!user) return 'Unknown User'
  return `${user.first_name || ''} ${user.last_name || ''}`.trim() || 
         user.username || 
         'Anonymous'
}

const getUserTypeLabel = (userType) => {
  switch (userType) {
    case 1: return 'Admin'
    case 2: return 'Faculty'
    case 3: return 'Alumni'
    default: return 'Unknown'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  try {
    return new Date(dateString).toLocaleDateString()
  } catch {
    return 'Invalid Date'
  }
}
</script>