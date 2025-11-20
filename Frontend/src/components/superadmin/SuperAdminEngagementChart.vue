<template>
  <div :class="['rounded-lg shadow-sm border p-3 mb-6', themeStore.isAdminDark() ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200']">
    <div class="flex items-start justify-between mb-2">
      <div>
        <h3 :class="['text-sm font-semibold', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">Alumni Engagement Trend</h3>
        <p :class="['text-[10px]', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500']">
          Daily logins, posts & comments (last {{ rangeDays }} days)
        </p>
      </div>
      <div class="flex items-center space-x-2">
        <button
          v-for="opt in rangeOptions"
          :key="opt.days"
          @click="setRange(opt.days)"
          :class="[
            'px-1.5 py-0.5 rounded text-[10px] border',
            rangeDays === opt.days
              ? (themeStore.isAdminDark() ? 'bg-orange-600 border-orange-500 text-white' : 'bg-orange-600 border-orange-600 text-white')
              : (themeStore.isAdminDark() ? 'border-gray-600 text-gray-300 hover:bg-gray-700' : 'border-gray-300 text-gray-700 hover:bg-gray-100')
          ]"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex items-center justify-center h-24">
      <div class="text-xs" :class="themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-600'">Loading engagement data...</div>
    </div>

    <canvas v-show="!loading" ref="chartEl" class="w-full h-24"></canvas>

    <div class="mt-2 grid grid-cols-2 md:grid-cols-4 gap-1.5 text-[10px]">
      <div :class="metricClass">
        <p class="font-medium text-[9px]">Avg Posts/Day</p>
        <p class="text-sm font-bold">{{ avgResponses }}</p>
      </div>
      <div :class="metricClass">
        <p class="font-medium text-[9px]">Peak Posts</p>
        <p class="text-sm font-bold">{{ peakResponses }}</p>
      </div>
      <div :class="metricClass">
        <p class="font-medium text-[9px]">Avg Logins/Day</p>
        <p class="text-sm font-bold">{{ avgPosts }}</p>
      </div>
      <div :class="metricClass">
        <p class="font-medium text-[9px]">Peak Logins</p>
        <p class="text-sm font-bold">{{ peakPosts }}</p>
      </div>
    </div>

    <p class="mt-2 text-[9px] leading-relaxed" :class="themeStore.isAdminDark() ? 'text-gray-500' : 'text-gray-500'">
      Note: Historical login and comment events are limited – we approximate daily logins using each user's current last_login (only the most recent can be counted). For full multi‑day login & comment trends, add a backend event logging table (login, comment) and we will switch datasets to true historical values.
    </p>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { surveyService } from '@/services/surveyService'
import { postsService } from '@/services/postsService'
import { adminService } from '@/services/adminService'
import { Chart, LineController, LineElement, PointElement, LinearScale, TimeScale, CategoryScale, Filler, Tooltip, Legend } from 'chart.js'

Chart.register(LineController, LineElement, PointElement, LinearScale, TimeScale, CategoryScale, Filler, Tooltip, Legend)

const themeStore = useThemeStore()

// Props
const props = defineProps({
  autoRefreshMs: { type: Number, default: 60000 } // 1 min
})

// State
const loading = ref(false)
const rangeDays = ref(14)
const rangeOptions = [
  { label: '7d', days: 7 },
  { label: '14d', days: 14 },
  { label: '30d', days: 30 }
]

const chartEl = ref(null)
let chartInstance = null
let refreshTimer = null

// Derived metrics
const avgResponses = ref(0)
const peakResponses = ref(0)
const avgPosts = ref(0)
const peakPosts = ref(0)

const metricClass = [
  'p-1 rounded border text-center',
  themeStore.isAdminDark() ? 'bg-gray-900 border-gray-700 text-gray-300' : 'bg-gray-50 border-gray-200 text-gray-700'
]

const setRange = (days) => {
  rangeDays.value = days
  fetchAndRender()
}

const zeroFillDates = (days) => {
  const out = []
  const today = new Date()
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date()
    d.setDate(today.getDate() - i)
    out.push(d.toISOString().slice(0, 10))
  }
  return out
}

const aggregateCountsByDate = (items, dateField) => {
  const counts = {}
  items.forEach(it => {
    const ts = it[dateField]
    if (!ts) return
    const d = new Date(ts)
    const key = d.toISOString().slice(0, 10)
    counts[key] = (counts[key] || 0) + 1
  })
  return counts
}

const fetchAndRender = async () => {
  loading.value = true
  try {
    const [postsResult, usersResult] = await Promise.all([
      postsService.getPosts({ limit: 1000 }),
      adminService.getUsers({ limit: 1000 })
    ])

    const posts = Array.isArray(postsResult) ? postsResult : (postsResult.results || postsResult.items || postsResult.data || [])
    const users = Array.isArray(usersResult) ? usersResult : (usersResult.results || usersResult.items || usersResult.data || [])

    const allDates = zeroFillDates(rangeDays.value)

    // Posts per day
    const postCounts = aggregateCountsByDate(posts, 'created_at')
    const postSeries = allDates.map(d => postCounts[d] || 0)

    // Approximate logins per day (ONLY counts if last_login equals that date)
    const loginCounts = {}
    users.forEach(u => {
      if (!u.last_login) return
      const d = new Date(u.last_login).toISOString().slice(0, 10)
      // Only consider within range
      if (allDates.includes(d)) {
        loginCounts[d] = (loginCounts[d] || 0) + 1
      }
    })
    const loginSeries = allDates.map(d => loginCounts[d] || 0)

    // Comments per day (approx) — if post object holds comments_count but lacks per-day timestamps, we cannot derive historical trend. Placeholder zeros.
    const commentSeries = allDates.map(() => 0)

    // Metrics (reuse response metrics labels for now -> rename to Posts)
    const sum = arr => arr.reduce((a, b) => a + b, 0)
    avgResponses.value = postSeries.length ? Math.round((sum(postSeries) / postSeries.length) * 10) / 10 : 0
    peakResponses.value = postSeries.length ? Math.max(...postSeries) : 0
    avgPosts.value = avgResponses.value
    peakPosts.value = peakResponses.value

    // Build or update chart
    const labels = allDates
    const datasets = [
      {
        label: 'Logins (approx)',
        data: loginSeries,
        borderColor: '#10b981',
        backgroundColor: 'rgba(16,185,129,0.15)',
        tension: 0.3,
        fill: true,
        pointRadius: 3
      },
      {
        label: 'Posts',
        data: postSeries,
        borderColor: themeStore.isAdminDark() ? '#6366f1' : '#4f46e5',
        backgroundColor: themeStore.isAdminDark() ? 'rgba(99,102,241,0.15)' : 'rgba(79,70,229,0.15)',
        tension: 0.3,
        fill: true,
        pointRadius: 3
      },
      {
        label: 'Comments (pending backend)',
        data: commentSeries,
        borderColor: '#d97706',
        backgroundColor: 'rgba(217,119,6,0.08)',
        tension: 0.3,
        fill: false,
        pointRadius: 2,
        borderDash: [4,4]
      }
    ]

    if (chartInstance) {
      chartInstance.data.labels = labels
      chartInstance.data.datasets = datasets
      chartInstance.update()
    } else {
      chartInstance = new Chart(chartEl.value.getContext('2d'), {
        type: 'line',
        data: { labels, datasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: 'index', intersect: false },
          plugins: {
            legend: {
              labels: {
                color: themeStore.isAdminDark() ? '#f3f4f6' : '#374151',
                font: { size: 11 }
              }
            },
            tooltip: {
              backgroundColor: themeStore.isAdminDark() ? '#1f2937' : '#fff',
              titleColor: themeStore.isAdminDark() ? '#fff' : '#111',
              bodyColor: themeStore.isAdminDark() ? '#e5e7eb' : '#111',
              borderColor: themeStore.isAdminDark() ? '#374151' : '#e5e7eb',
              borderWidth: 1
            }
          },
          scales: {
            x: {
              ticks: {
                color: themeStore.isAdminDark() ? '#9ca3af' : '#6b7280',
                maxRotation: 45,
                minRotation: 45
              },
              grid: { display: false }
            },
            y: {
              ticks: {
                color: themeStore.isAdminDark() ? '#9ca3af' : '#6b7280'
              },
              grid: {
                color: themeStore.isAdminDark() ? 'rgba(55,65,81,0.4)' : 'rgba(209,213,219,0.4)'
              },
              beginAtZero: true
            }
          }
        }
      })
    }
  } catch (e) {
    console.error('Failed to load engagement data', e)
  } finally {
    loading.value = false
  }
}

// Auto refresh
const startAutoRefresh = () => {
  if (refreshTimer) clearInterval(refreshTimer)
  refreshTimer = setInterval(fetchAndRender, props.autoRefreshMs)
}

const stopAutoRefresh = () => {
  if (refreshTimer) clearInterval(refreshTimer)
  refreshTimer = null
}

watch(() => themeStore.isAdminDark(), () => {
  // Rebuild chart for theme change
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
    fetchAndRender()
  }
})

onMounted(() => {
  fetchAndRender()
  startAutoRefresh()
})

onBeforeUnmount(() => {
  stopAutoRefresh()
  if (chartInstance) chartInstance.destroy()
})
</script>
