<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h2 :class="[
          'text-2xl font-bold',
          isDark ? 'text-white' : 'text-slate-800'
        ]">Survey Analytics by Category</h2>
        <p :class="[
          isDark ? 'text-gray-400' : 'text-slate-600'
        ]">View detailed analytics, charts, and export reports for each survey category</p>
      </div>
    </div>

    <!-- Category Analytics List -->
    <div :class="[
      'rounded-xl shadow-sm border overflow-hidden',
      isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-slate-200'
    ]">
      <table class="min-w-full divide-y" :class="isDark ? 'divide-gray-700' : 'divide-slate-200'">
        <thead :class="isDark ? 'bg-gray-700' : 'bg-slate-50'">
          <tr>
            <th scope="col" :class="[
              'px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider',
              isDark ? 'text-gray-300' : 'text-slate-700'
            ]">
              Category
            </th>
            <th scope="col" :class="[
              'px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider',
              isDark ? 'text-gray-300' : 'text-slate-700'
            ]">
              Questions
            </th>
            <th scope="col" :class="[
              'px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider',
              isDark ? 'text-gray-300' : 'text-slate-700'
            ]">
              Responses
            </th>
            <th scope="col" :class="[
              'px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider',
              isDark ? 'text-gray-300' : 'text-slate-700'
            ]">
              Status
            </th>
            <th scope="col" :class="[
              'px-6 py-4 text-right text-xs font-semibold uppercase tracking-wider',
              isDark ? 'text-gray-300' : 'text-slate-700'
            ]">
              Actions
            </th>
          </tr>
        </thead>
        <tbody :class="[
          'divide-y',
          isDark ? 'divide-gray-700 bg-gray-800' : 'divide-slate-200 bg-white'
        ]">
          <tr
            v-for="category in categories"
            :key="category.id"
            :class="[
              'transition-colors',
              isDark ? 'hover:bg-gray-700' : 'hover:bg-slate-50'
            ]"
          >
            <td class="px-6 py-4">
              <div>
                <div :class="[
                  'font-medium',
                  isDark ? 'text-white' : 'text-slate-900'
                ]">
                  {{ category.name }}
                </div>
                <div v-if="category.description" :class="[
                  'text-sm mt-1',
                  isDark ? 'text-gray-400' : 'text-slate-500'
                ]">
                  {{ category.description.substring(0, 60) }}{{ category.description.length > 60 ? '...' : '' }}
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <span :class="[
                'px-2 py-1 text-xs font-medium rounded',
                isDark ? 'bg-blue-900 text-blue-300' : 'bg-blue-100 text-blue-800'
              ]">
                {{ getQuestionCount(category.id) }} questions
              </span>
            </td>
            <td class="px-6 py-4">
              <span :class="[
                'px-2 py-1 text-xs font-medium rounded',
                isDark ? 'bg-green-900 text-green-300' : 'bg-green-100 text-green-800'
              ]">
                {{ getResponseCount(category.id) }} responses
              </span>
            </td>
            <td class="px-6 py-4">
              <span :class="[
                'px-2 py-1 text-xs font-medium rounded',
                category.is_active
                  ? (isDark ? 'bg-green-900 text-green-300' : 'bg-green-100 text-green-800')
                  : (isDark ? 'bg-gray-700 text-gray-400' : 'bg-gray-100 text-gray-600')
              ]">
                {{ category.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="px-6 py-4 text-right space-x-2">
              <button
                @click="$emit('view-analytics', category)"
                class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-600 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md"
              >
                <BarChart3 class="w-4 h-4" />
                View Analytics
              </button>
              <button
                @click="$emit('export-excel', category)"
                class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-600 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md"
              >
                <Download class="w-4 h-4" />
                Export Excel
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="categories.length === 0" :class="[
        'text-center py-12',
        isDark ? 'text-gray-400' : 'text-slate-500'
      ]">
        <BarChart3 class="w-16 h-16 mx-auto mb-4 opacity-50" />
        <p>No categories available for analytics</p>
      </div>
    </div>

    <!-- Summary Cards -->
    <div v-if="analytics" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-8">
      <div :class="[
        'p-6 rounded-xl border',
        isDark
          ? 'bg-gradient-to-br from-gray-700 to-gray-800 border-gray-600'
          : 'bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200'
      ]">
        <div class="flex items-center justify-between mb-3">
          <h4 :class="[
            'text-sm font-semibold',
            isDark ? 'text-gray-300' : 'text-orange-600'
          ]">Total Questions</h4>
          <div :class="[
            'w-8 h-8 rounded-lg flex items-center justify-center',
            isDark ? 'bg-gray-600' : 'bg-orange-600'
          ]">
            <FileCheck class="w-4 h-4 text-white" />
          </div>
        </div>
        <p :class="[
          'text-3xl font-bold',
          isDark ? 'text-white' : 'text-orange-500'
        ]">{{ analytics.total_questions }}</p>
      </div>
      
      <div :class="[
        'p-6 rounded-xl border',
        isDark
          ? 'bg-gradient-to-br from-gray-700 to-gray-800 border-gray-600'
          : 'bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200'
      ]">
        <div class="flex items-center justify-between mb-3">
          <h4 :class="[
            'text-sm font-semibold',
            isDark ? 'text-gray-300' : 'text-orange-600'
          ]">Total Responses</h4>
          <div :class="[
            'w-8 h-8 rounded-lg flex items-center justify-center',
            isDark ? 'bg-gray-600' : 'bg-orange-600'
          ]">
            <TrendingUp class="w-4 h-4 text-white" />
          </div>
        </div>
        <p :class="[
          'text-3xl font-bold',
          isDark ? 'text-white' : 'text-orange-500'
        ]">{{ analytics.total_responses }}</p>
      </div>
      
      <div :class="[
        'p-6 rounded-xl border',
        isDark
          ? 'bg-gradient-to-br from-gray-700 to-gray-800 border-gray-600'
          : 'bg-gradient-to-br from-amber-50 to-amber-100 border-amber-200'
      ]">
        <div class="flex items-center justify-between mb-3">
          <h4 :class="[
            'text-sm font-semibold',
            isDark ? 'text-gray-300' : 'text-amber-900'
          ]">Active Users</h4>
          <div :class="[
            'w-8 h-8 rounded-lg flex items-center justify-center',
            isDark ? 'bg-gray-600' : 'bg-amber-600'
          ]">
            <Users class="w-4 h-4 text-white" />
          </div>
        </div>
        <p :class="[
          'text-3xl font-bold',
          isDark ? 'text-white' : 'text-amber-900'
        ]">{{ analytics.active_users }}</p>
      </div>
      
      <div :class="[
        'p-6 rounded-xl border',
        isDark
          ? 'bg-gradient-to-br from-gray-700 to-gray-800 border-gray-600'
          : 'bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200'
      ]">
        <div class="flex items-center justify-between mb-3">
          <h4 :class="[
            'text-sm font-semibold',
            isDark ? 'text-gray-300' : 'text-purple-900'
          ]">Completion Rate</h4>
          <div :class="[
            'w-8 h-8 rounded-lg flex items-center justify-center',
            isDark ? 'bg-gray-600' : 'bg-purple-600'
          ]">
            <TrendingUp class="w-4 h-4 text-white" />
          </div>
        </div>
        <p :class="[
          'text-3xl font-bold',
          isDark ? 'text-white' : 'text-purple-900'
        ]">{{ analytics.completion_rate }}%</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { BarChart3, Download, FileCheck, TrendingUp, Users } from 'lucide-vue-next'

const props = defineProps({
  categories: {
    type: Array,
    required: true
  },
  analytics: {
    type: Object,
    default: null
  },
  isDark: {
    type: Boolean,
    default: false
  }
})

defineEmits(['view-analytics', 'export-excel'])

const getQuestionCount = (categoryId) => {
  const category = props.categories.find(c => c.id === categoryId)
  return category?.question_count || 0
}

const getResponseCount = (categoryId) => {
  const category = props.categories.find(c => c.id === categoryId)
  return category?.response_count || 0
}
</script>
