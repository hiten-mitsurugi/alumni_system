<template>
  <div :class="[
    'rounded-lg shadow-lg p-6',
    themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white'
  ]">
    <h3 :class="[
      'text-lg font-semibold mb-4',
      themeStore.isDarkMode ? 'text-gray-100' : 'text-gray-900'
    ]">Recent Activity</h3>
    
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="animate-pulse">
        <div class="flex items-start space-x-3">
          <div :class="[
            'w-8 h-8 rounded-full',
            themeStore.isDarkMode ? 'bg-gray-600' : 'bg-gray-300'
          ]"></div>
          <div class="flex-1">
            <div :class="[
              'h-3 rounded w-full mb-2',
              themeStore.isDarkMode ? 'bg-gray-600' : 'bg-gray-300'
            ]"></div>
            <div :class="[
              'h-3 rounded w-2/3',
              themeStore.isDarkMode ? 'bg-gray-600' : 'bg-gray-300'
            ]"></div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="activities.length > 0" class="space-y-4">
      <div 
        v-for="activity in activities" 
        :key="activity.id"
        :class="[
          'flex items-start space-x-3 pb-3 border-b last:border-b-0',
          themeStore.isDarkMode ? 'border-gray-600' : 'border-gray-100'
        ]"
      >
        <!-- Activity Icon -->
        <div class="flex-shrink-0">
          <div 
            class="w-8 h-8 rounded-full flex items-center justify-center"
            :class="getActivityColor(activity.type)"
          >
            <component :is="getActivityIcon(activity.type)" class="w-4 h-4" />
          </div>
        </div>
        
        <!-- Activity Content -->
        <div class="flex-1 min-w-0">
          <p :class="[
            'text-sm',
            themeStore.isDarkMode ? 'text-gray-100' : 'text-gray-900'
          ]">
            {{ getActivityText(activity) }}
          </p>
          <p :class="[
            'text-xs mt-1',
            themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
          ]">
            {{ formatTime(activity.created_at) }}
          </p>
        </div>
      </div>
      
      <!-- View All Activity -->
      <div :class="[
        'pt-3 border-t',
        themeStore.isDarkMode ? 'border-gray-600' : 'border-gray-200'
      ]">
        <button 
          @click="showAllActivity"
          class="text-sm text-green-600 hover:text-green-700 font-medium"
        >
          View all activity
        </button>
      </div>
    </div>

    <div v-else class="text-center py-6">
      <svg :class="[
        'w-12 h-12 mx-auto mb-3',
        themeStore.isDarkMode ? 'text-gray-500' : 'text-gray-400'
      ]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
      </svg>
      <p :class="[
        'text-sm',
        themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
      ]">No recent activity</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, h } from 'vue'
import { useThemeStore } from '@/stores/theme'
import api from '@/services/api'

const themeStore = useThemeStore()

const loading = ref(true)
const activities = ref([])

const fetchActivity = async () => {
  try {
    loading.value = true
    // Mock activity data for now - replace with actual API call
    activities.value = [
      {
        id: 1,
        type: 'profile_update',
        description: 'Updated profile information',
        created_at: new Date(Date.now() - 2 * 60 * 60 * 1000) // 2 hours ago
      },
      {
        id: 2,
        type: 'new_connection',
        description: 'Connected with John Doe',
        created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000) // 1 day ago
      },
      {
        id: 3,
        type: 'achievement_added',
        description: 'Added new achievement: Excellence Award',
        created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000) // 3 days ago
      }
    ]
  } catch (error) {
    console.error('Error fetching activity:', error)
    activities.value = []
  } finally {
    loading.value = false
  }
}

const getActivityColor = (type) => {
  const lightColors = {
    'profile_update': 'bg-blue-100 text-blue-600',
    'new_connection': 'bg-green-100 text-green-600',
    'achievement_added': 'bg-yellow-100 text-yellow-600',
    'work_added': 'bg-purple-100 text-purple-600',
    'education_added': 'bg-indigo-100 text-indigo-600',
    'post_created': 'bg-pink-100 text-pink-600'
  }
  
  const darkColors = {
    'profile_update': 'bg-blue-900/30 text-blue-400',
    'new_connection': 'bg-green-900/30 text-green-400',
    'achievement_added': 'bg-yellow-900/30 text-yellow-400',
    'work_added': 'bg-purple-900/30 text-purple-400',
    'education_added': 'bg-indigo-900/30 text-indigo-400',
    'post_created': 'bg-pink-900/30 text-pink-400'
  }
  
  const colors = themeStore.isDarkMode ? darkColors : lightColors
  return colors[type] || (themeStore.isDarkMode ? 'bg-gray-700 text-gray-400' : 'bg-gray-100 text-gray-600')
}

const getActivityIcon = (type) => {
  const iconMap = {
    'profile_update': () => h('svg', { 
      fill: 'none', 
      stroke: 'currentColor', 
      viewBox: '0 0 24 24' 
    }, [
      h('path', { 
        'stroke-linecap': 'round', 
        'stroke-linejoin': 'round', 
        'stroke-width': '2', 
        d: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' 
      })
    ]),
    'new_connection': () => h('svg', { 
      fill: 'none', 
      stroke: 'currentColor', 
      viewBox: '0 0 24 24' 
    }, [
      h('path', { 
        'stroke-linecap': 'round', 
        'stroke-linejoin': 'round', 
        'stroke-width': '2', 
        d: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z' 
      })
    ]),
    'achievement_added': () => h('svg', { 
      fill: 'currentColor', 
      viewBox: '0 0 24 24' 
    }, [
      h('path', { d: 'M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z' })
    ])
  }
  
  return iconMap[type] || iconMap['profile_update']
}

const getActivityText = (activity) => {
  return activity.description
}

const formatTime = (date) => {
  const now = new Date()
  const activityDate = new Date(date)
  const diffInSeconds = Math.floor((now - activityDate) / 1000)
  
  if (diffInSeconds < 60) {
    return 'Just now'
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60)
    return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600)
    return `${hours} hour${hours !== 1 ? 's' : ''} ago`
  } else if (diffInSeconds < 604800) {
    const days = Math.floor(diffInSeconds / 86400)
    return `${days} day${days !== 1 ? 's' : ''} ago`
  } else {
    return activityDate.toLocaleDateString()
  }
}

const showAllActivity = () => {
  // Navigate to full activity page or show modal
  console.log('Show all activity')
}

onMounted(() => {
  fetchActivity()
})
</script>
