import { ref, onMounted, onUnmounted, computed } from 'vue'
import { adminService } from '@/services/adminService'

/**
 * Admin Analytics Composable
 * Manages analytics data and dashboard state following COPILOT_INSTRUCTIONS
 */
export function useAdminAnalytics() {
  // Reactive data
  const loading = ref(false)
  const error = ref(null)
  const lastUpdated = ref(null)
  const refreshInterval = ref(null)

  // Analytics data
  const analytics = ref({
    totalUsers: 0,
    activeUsers: 0,
    pendingApprovals: 0,
    recentRegistrations: 0,
    onlineUsers: 0,
    totalPosts: 0,
    pendingPosts: 0,
    reportedPosts: 0,
    declinedPosts: 0,
    weeklyPosts: 0,
    userEngagement: 0,
    pendingActions: 0
  })

  // Computed properties
  const activityRate = computed(() => {
    if (analytics.value.totalUsers === 0) return '0.0'
    return ((analytics.value.activeUsers / analytics.value.totalUsers) * 100).toFixed(1)
  })

  const approvalRate = computed(() => {
    // Prefer backend-provided approvalRate when present
    if (analytics.value.approvalRate !== undefined && analytics.value.approvalRate !== null) {
      // Ensure it's a number or numeric string
      const val = parseFloat(analytics.value.approvalRate)
      if (!isNaN(val)) return val.toFixed(1)
    }

    const total = (analytics.value.approvedPosts || 0) + (analytics.value.declinedPosts || 0)
    if (total === 0) return '0.0'
    return ((analytics.value.approvedPosts / total) * 100).toFixed(1)
  })

  // Methods
  const fetchAnalytics = async () => {
    loading.value = true
    error.value = null
    
    try {
      console.log('Dashboard Debug: Fetching analytics...')
      const rawData = await adminService.getAnalytics()
      console.log('Dashboard Debug: Raw analytics data:', rawData)

      // If backend returns already formatted analytics object, use it; otherwise transform
      const formatted = adminService.formatAnalyticsData(rawData)
      analytics.value = Object.assign({}, analytics.value, formatted)
      console.log('Dashboard Debug: Formatted analytics:', analytics.value)

      // Prefer backend-provided timestamp when available
      if (formatted.lastUpdated) {
        try {
          lastUpdated.value = new Date(formatted.lastUpdated)
        } catch {
          lastUpdated.value = new Date()
        }
      } else if (rawData.last_updated) {
        try { lastUpdated.value = new Date(rawData.last_updated) } catch { lastUpdated.value = new Date() }
      } else {
        lastUpdated.value = new Date()
      }

      // If backend analytics are missing sensible post totals, fetch raw posts as fallback
      try {
        const weekAgo = new Date()
        weekAgo.setDate(weekAgo.getDate() - 7)

        // If posts total looks missing or zero, fetch posts directly
        if (!analytics.value.totalPosts || analytics.value.totalPosts === 0) {
          const allPosts = await adminService.getRecentPosts(1000)
          analytics.value.totalPosts = Array.isArray(allPosts) ? allPosts.length : 0
          analytics.value.pendingPosts = Array.isArray(allPosts) ? allPosts.filter(p => p.status === 'pending').length : 0
          analytics.value.approvedPosts = Array.isArray(allPosts) ? allPosts.filter(p => p.status === 'approved').length : 0
          analytics.value.declinedPosts = Array.isArray(allPosts) ? allPosts.filter(p => p.status === 'declined').length : 0
          analytics.value.weeklyPosts = Array.isArray(allPosts) ? allPosts.filter(p => new Date(p.created_at) >= weekAgo).length : 0
        }

        // Ensure reportedPosts is numeric
        if (analytics.value.reportedPosts === undefined || analytics.value.reportedPosts === null) {
          const reports = await adminService.getPostReports()
          analytics.value.reportedPosts = Array.isArray(reports) ? reports.length : 0
        }

        // Only compute approved-alumni-based recent registrations if backend didn't provide a value
        if (analytics.value.recentRegistrations === null || analytics.value.recentRegistrations === undefined) {
          try {
            // Request a larger page so we get all recent users for the week (backend supports `limit` query param)
            const users = await adminService.getUsers({ limit: 1000 })
            if (Array.isArray(users)) {
              const approvedAlumni = users.filter(u => u.user_type === 3 && u.is_approved)
              // recent registrations (approved only, last 7 days)
              const weekAgoDate = new Date()
              weekAgoDate.setDate(weekAgoDate.getDate() - 7)
              analytics.value.recentRegistrations = approvedAlumni.filter(u => new Date(u.date_joined) >= weekAgoDate).length
              // Optionally expose totalApprovedUsers
              analytics.value.totalApprovedUsers = approvedAlumni.length
              // Also compute totalUsers as approved users if you prefer (do not overwrite unless empty)
              if (!analytics.value.totalUsers || analytics.value.totalUsers === 0) {
                analytics.value.totalUsers = approvedAlumni.length
              }
            }
          } catch (e) {
            console.warn('Failed to compute approved users fallback:', e)
          }
        }
      } catch (err) {
        console.warn('Fallback analytics fetch failed:', err)
      }
      
    } catch (err) {
      console.error('Dashboard Debug: Analytics fetch failed:', err)
      error.value = err.message || 'Failed to load analytics data'
      
      // Fallback to legacy method if main analytics fails
      await fetchAnalyticsLegacy()
      
    } finally {
      loading.value = false
    }
  }

  const fetchAnalyticsLegacy = async () => {
    try {
      console.log('Dashboard Debug: Using legacy analytics method')
      
      const [usersData, postsData, reportsData] = await Promise.allSettled([
        adminService.getUsers({ limit: 1000 }),
        adminService.getRecentPosts(1000), // Get all posts for counting
        adminService.getPostReports()
      ])

      // Process users data
      const users = usersData.status === 'fulfilled' ? usersData.value : []
      
      // Process posts data  
      const posts = postsData.status === 'fulfilled' ? postsData.value : []
        
      // Process reports data
      const reports = reportsData.status === 'fulfilled' ? reportsData.value : []

      // Calculate analytics from raw data
      const weekAgo = new Date()
      weekAgo.setDate(weekAgo.getDate() - 7)
      
      const fifteenMinutesAgo = new Date()
      fifteenMinutesAgo.setMinutes(fifteenMinutesAgo.getMinutes() - 15)

      analytics.value = {
        totalUsers: users.length,
        activeUsers: users.filter(user => user.is_active).length,
        pendingApprovals: users.filter(user => user.user_type === 3 && !user.is_approved).length,
        recentRegistrations: users.filter(user => {
          const joinDate = new Date(user.date_joined)
          return joinDate >= weekAgo
        }).length,
        onlineUsers: users.filter(user => {
          if (!user.last_login) return false
          const lastLogin = new Date(user.last_login)
          return lastLogin >= fifteenMinutesAgo
        }).length,
  totalPosts: posts.length,
  pendingPosts: posts.filter(post => post.status === 'pending').length,
  reportedPosts: Array.isArray(reports) ? reports.length : 0,
  approvedPosts: posts.filter(post => post.status === 'approved').length,
  declinedPosts: posts.filter(post => post.status === 'declined').length,
        weeklyPosts: posts.filter(post => {
          const postDate = new Date(post.created_at)
          return postDate >= weekAgo
        }).length,
        userEngagement: 0,
        pendingActions: 0
      }

      // Calculate derived metrics
      analytics.value.userEngagement = analytics.value.activeUsers > 0 ?
        Math.round((analytics.value.onlineUsers / analytics.value.activeUsers) * 100) : 0

      analytics.value.pendingActions = analytics.value.reportedPosts + analytics.value.pendingApprovals

      // Compute approval rate if not set
      if (!analytics.value.approvalRate) {
        const reviewed = analytics.value.approvedPosts + analytics.value.declinedPosts
        analytics.value.approvalRate = reviewed > 0 ? ((analytics.value.approvedPosts / reviewed) * 100).toFixed(1) : '0.0'
      }

      error.value = null
  lastUpdated.value = new Date()
      
    } catch (err) {
      console.error('Dashboard Debug: Legacy analytics failed:', err)
      error.value = 'Failed to load dashboard data. Please check your connection and try again.'
    }
  }

  const startAutoRefresh = (intervalMs = 30000) => {
    if (refreshInterval.value) {
      clearInterval(refreshInterval.value)
    }
    
    refreshInterval.value = setInterval(() => {
      fetchAnalytics()
    }, intervalMs)
  }

  const stopAutoRefresh = () => {
    if (refreshInterval.value) {
      clearInterval(refreshInterval.value)
      refreshInterval.value = null
    }
  }

  const refreshData = async () => {
    await fetchAnalytics()
  }

  // Cleanup
  onUnmounted(() => {
    stopAutoRefresh()
  })

  return {
    // State
    loading,
    error,
    lastUpdated,
    analytics,
    
    // Computed
    activityRate,
    approvalRate,
    
    // Methods
    fetchAnalytics,
    refreshData,
    startAutoRefresh,
    stopAutoRefresh
  }
}