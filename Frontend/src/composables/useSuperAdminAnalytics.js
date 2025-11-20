import { ref, computed, onUnmounted } from 'vue'
import { surveyService } from '@/services/surveyService'
import { adminService } from '@/services/adminService'

/**
 * SuperAdmin Analytics Composable
 * Manages survey-focused analytics for SuperAdmin dashboard
 */
export function useSuperAdminAnalytics() {
  // Reactive data
  const loading = ref(false)
  const error = ref(null)
  const lastUpdated = ref(null)
  const refreshInterval = ref(null)

  // Analytics data
  const analytics = ref({
    totalAlumni: 0,
    registeredAlumni: 0,
    registrationRate: 0,
    activeSurveys: 0,
    responsesToday: 0,
    pendingApprovals: 0,
    totalResponses: 0,
    respondents: 0,
    nonRespondents: 0,
    responseRate: 0,
    closedSurveys: 0,
    avgCompletionRate: 0,
    onlineUsers: 0,
    userEngagement: 0,
    activeUsers: 0
  })

  // Computed properties
  const completionRateFormatted = computed(() => {
    return `${analytics.value.avgCompletionRate.toFixed(1)}%`
  })

  const responseGrowth = computed(() => {
    // Could calculate day-over-day growth if we have historical data
    return '+12%' // Placeholder
  })

  // Methods
  const fetchAnalytics = async () => {
    loading.value = true
    error.value = null
    
    try {
      console.log('SuperAdmin Debug: Fetching survey analytics...')
      
      // Add cache buster to force fresh data
      const cacheBuster = `?_t=${Date.now()}`
      
      // Fetch data in parallel - now including AlumniDirectory
      const [formsData, responsesData, usersData, alumniDirectoryData] = await Promise.allSettled([
        surveyService.getForms(),
        surveyService.getResponses(),
        adminService.getUsers({ limit: 1000, _t: Date.now() }),
        adminService.getAlumniDirectory({ _t: Date.now() })
      ])

      // Process forms
      const forms = formsData.status === 'fulfilled' ? (formsData.value.data?.results || formsData.value.data || []) : []
      
      // Process responses
      const responses = responsesData.status === 'fulfilled' ? (responsesData.value.data?.results || responsesData.value.data || []) : []
      
      // Process registered users
      const users = usersData.status === 'fulfilled' ? usersData.value : []

      // Process alumni directory (all graduates, registered or not)
      const alumniDirectory = alumniDirectoryData.status === 'fulfilled' ? alumniDirectoryData.value : []

      console.log('SuperAdmin Debug: Raw users data:', users)
      console.log('SuperAdmin Debug: Total users fetched:', users.length)
      console.log('SuperAdmin Debug: Alumni directory data:', alumniDirectory)
      console.log('SuperAdmin Debug: Total alumni in directory:', alumniDirectory.length)

      // Calculate survey metrics
      const today = new Date()
      today.setHours(0, 0, 0, 0)

      const fifteenMinutesAgo = new Date()
      fifteenMinutesAgo.setMinutes(fifteenMinutesAgo.getMinutes() - 15)

      // Alumni calculations
      // Total Alumni = count from AlumniDirectory (all graduates)
      const totalAlumniCount = alumniDirectory.length
      
      // Registered Alumni = users with user_type=3 and is_approved=true
      const registeredUsers = users.filter(u => u.user_type === 3)
      const registeredAlumni = registeredUsers.filter(u => u.is_approved)
      const registeredCount = registeredAlumni.length
      
      console.log('SuperAdmin Debug: Total alumni in directory:', totalAlumniCount)
      console.log('SuperAdmin Debug: Registered alumni users (user_type=3, is_approved=true):', registeredCount)
      console.log('SuperAdmin Debug: Registered alumni details:', registeredAlumni.map(u => ({ 
        id: u.id, 
        name: `${u.first_name} ${u.last_name}`, 
        user_type: u.user_type, 
        is_approved: u.is_approved 
      })))
      
      // Calculate registration rate
      const registrationRate = totalAlumniCount > 0 
        ? (registeredCount / totalAlumniCount) * 100 
        : 0

      // Active and online users
      const activeUsers = registeredAlumni.filter(u => u.is_active).length
      const onlineUsers = registeredAlumni.filter(u => {
        if (!u.last_login) return false
        const lastLogin = new Date(u.last_login)
        return lastLogin >= fifteenMinutesAgo
      }).length

      // User engagement calculation
      const userEngagement = activeUsers > 0
        ? Math.round((onlineUsers / activeUsers) * 100)
        : 0

      // Survey response participation tracking
      // Get unique respondents (registered alumni who have submitted at least one response)
      const uniqueRespondentIds = new Set(
        responses
          .filter(r => r.user && r.user.id)
          .map(r => r.user.id)
      )
      const respondentsCount = uniqueRespondentIds.size
      const nonRespondentsCount = registeredCount - respondentsCount
      const responseRate = registeredCount > 0
        ? (respondentsCount / registeredCount) * 100
        : 0

      // Pending approvals - users who registered but not yet approved
      const allRegisteredUsers = users.filter(u => u.user_type === 3)
      const pendingApprovalsCount = allRegisteredUsers.filter(u => !u.is_approved).length

      analytics.value = {
        totalAlumni: totalAlumniCount,  // From AlumniDirectory
        registeredAlumni: registeredCount,  // From CustomUser where user_type=3 and is_approved=true
        registrationRate: registrationRate,
        activeSurveys: forms.filter(f => f.is_active).length,
        responsesToday: responses.filter(r => {
          const responseDate = new Date(r.created_at)
          responseDate.setHours(0, 0, 0, 0)
          return responseDate.getTime() === today.getTime()
        }).length,
        pendingApprovals: pendingApprovalsCount,
        totalResponses: responses.length,
        respondents: respondentsCount,
        nonRespondents: nonRespondentsCount,
        responseRate: responseRate,
        closedSurveys: forms.filter(f => {
          if (!f.end_date) return false
          return new Date(f.end_date) < new Date()
        }).length,
        avgCompletionRate: calculateCompletionRate(forms, responses),
        onlineUsers: onlineUsers,
        userEngagement: userEngagement,
        activeUsers: activeUsers
      }

      lastUpdated.value = new Date()
      console.log('SuperAdmin Debug: Analytics updated:', analytics.value)
      
    } catch (err) {
      console.error('SuperAdmin Debug: Analytics fetch failed:', err)
      error.value = err.message || 'Failed to load analytics data'
    } finally {
      loading.value = false
    }
  }

  const calculateCompletionRate = (forms, responses) => {
    if (!forms.length || !responses.length) return 0

    // Simple calculation: completed responses / total responses
    const completedResponses = responses.filter(r => r.is_complete || r.status === 'completed').length
    
    if (responses.length === 0) return 0
    return (completedResponses / responses.length) * 100
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
    completionRateFormatted,
    responseGrowth,
    
    // Methods
    fetchAnalytics,
    refreshData,
    startAutoRefresh,
    stopAutoRefresh
  }
}
