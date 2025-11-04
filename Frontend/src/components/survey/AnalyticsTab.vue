<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold text-slate-800">Survey Analytics</h2>
        <p class="text-slate-600">Comprehensive overview of survey performance and responses</p>
      </div>
    </div>

    <!-- Analytics Content -->
    <div v-if="analytics" class="space-y-6">
      <!-- Analytics Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="bg-gradient-to-br from-orange-50 to-orange-100 p-6 rounded-xl border border-orange-200 hover:shadow-lg transition-all duration-200">
          <div class="flex items-center justify-between mb-3">
            <h4 class="text-sm font-semibold text-orange-600">Total Questions</h4>
            <div class="w-8 h-8 bg-orange-600 rounded-lg flex items-center justify-center">
              <FileCheck class="w-4 h-4 text-white" />
            </div>
          </div>
          <p class="text-3xl font-bold text-orange-500">{{ analytics.total_questions }}</p>
          <p class="text-xs text-orange-600 mt-1">Active survey questions</p>
        </div>
        
        <div class="bg-gradient-to-br from-orange-50 to-orange-100 p-6 rounded-xl border border-orange-200 hover:shadow-lg transition-all duration-200">
          <div class="flex items-center justify-between mb-3">
            <h4 class="text-sm font-semibold text-orange-600">Total Responses</h4>
            <div class="w-8 h-8 bg-orange-600 rounded-lg flex items-center justify-center">
              <TrendingUp class="w-4 h-4 text-white" />
            </div>
          </div>
          <p class="text-3xl font-bold text-orange-500">{{ analytics.total_responses }}</p>
          <p class="text-xs text-orange-600 mt-1">Submitted answers</p>
        </div>
        
        <div class="bg-gradient-to-br from-amber-50 to-amber-100 p-6 rounded-xl border border-amber-200 hover:shadow-lg transition-all duration-200">
          <div class="flex items-center justify-between mb-3">
            <h4 class="text-sm font-semibold text-amber-900">Active Users</h4>
            <div class="w-8 h-8 bg-amber-600 rounded-lg flex items-center justify-center">
              <Users class="w-4 h-4 text-white" />
            </div>
          </div>
          <p class="text-3xl font-bold text-amber-700">{{ analytics.total_users_responded }}</p>
          <p class="text-xs text-amber-600 mt-1">Unique participants</p>
        </div>
        
        <div class="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl border border-purple-200 hover:shadow-lg transition-all duration-200">
          <div class="flex items-center justify-between mb-3">
            <h4 class="text-sm font-semibold text-purple-900">Completion Rate</h4>
            <div class="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
              <BarChart3 class="w-4 h-4 text-white" />
            </div>
          </div>
          <p class="text-3xl font-bold text-purple-700">{{ analytics.completion_rate }}%</p>
          <p class="text-xs text-purple-600 mt-1">Survey completion</p>
        </div>
      </div>

      <!-- Additional Analytics -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h3 class="text-lg font-semibold text-slate-800 mb-4">Response Trends</h3>
          <div class="text-center py-8 text-slate-500">
            <BarChart3 class="w-12 h-12 mx-auto mb-3 text-slate-300" />
            <p>Chart visualization would go here</p>
          </div>
        </div>
        
        <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h3 class="text-lg font-semibold text-slate-800 mb-4">Category Distribution</h3>
          <div class="text-center py-8 text-slate-500">
            <Calendar class="w-12 h-12 mx-auto mb-3 text-slate-300" />
            <p>Category breakdown would go here</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Analytics -->
    <div v-else class="text-center py-12">
      <div class="animate-spin rounded-full h-16 w-16 border-4 border-orange-200 border-t-orange-600 mx-auto mb-4"></div>
      <p class="text-slate-600 font-medium">Loading analytics data...</p>
    </div>
  </div>
</template>

<script setup>
import { HelpCircle, CheckCircle2, Users, TrendingUp, Loader, Clock, Folder, FileCheck, BarChart3, Calendar } from 'lucide-vue-next'

defineProps({
  analytics: {
    type: Object,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})
</script>
