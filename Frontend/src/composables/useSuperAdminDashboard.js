import { ref } from 'vue'
import { surveyService } from '@/services/surveyService'
import { adminService } from '@/services/adminService'
import { postsService } from '@/services/postsService'

/**
 * SuperAdmin Dashboard Composable
 * Manages dashboard data and operations
 */
export function useSuperAdminDashboard() {
  // Reactive data
  const loading = ref(false)
  const error = ref(null)
  
  const pendingApprovals = ref([])
  const recentActivity = ref([])
  const upcomingClosures = ref([])
  const systemStatus = ref({
    database: true,
    server: true,
    api: true
  })
  const systemUptime = ref(0)
  const systemLogs = ref([])

  // Methods
  const fetchPendingApprovals = async (limit = 5) => {
    try {
      const users = await adminService.getUsers({ limit: 100 })
      
      pendingApprovals.value = users
        .filter(user => user.user_type === 3 && !user.is_approved)
        .slice(0, limit)
        .map(user => ({
          id: user.id,
          name: `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username || 'Unknown',
          email: user.email,
          program: user.program || 'N/A',
          yearGraduated: user.year_graduated || 'N/A',
          submittedAt: user.date_joined,
          status: 'Pending'
        }))
    } catch (err) {
      console.error('Failed to fetch pending approvals:', err)
      pendingApprovals.value = []
    }
  }

  const fetchRecentActivity = async (limit = 5) => {
    try {
      // Get recent forms/surveys activity
      const formsResponse = await surveyService.getForms()
      const forms = formsResponse.data?.results || formsResponse.data || []
      
      // Sort by created/updated date
      const sortedForms = [...forms].sort((a, b) => {
        const dateA = new Date(a.updated_at || a.created_at)
        const dateB = new Date(b.updated_at || b.created_at)
        return dateB - dateA
      })

      recentActivity.value = sortedForms.slice(0, limit).map(form => {
        let action = 'Created'
        if (form.is_active) {
          action = 'Published'
        } else if (form.end_date && new Date(form.end_date) < new Date()) {
          action = 'Closed'
        }

        return {
          id: form.id,
          type: 'survey',
          action: action,
          title: form.title || form.name || 'Untitled Survey',
          user: 'System', // Could be enhanced to track who created it
          timestamp: form.updated_at || form.created_at
        }
      })
    } catch (err) {
      console.error('Failed to fetch recent activity:', err)
      recentActivity.value = []
    }
  }

  const fetchUpcomingClosures = async (days = 7) => {
    try {
      const formsResponse = await surveyService.getForms()
      const forms = formsResponse.data?.results || formsResponse.data || []
      
      const now = new Date()
      const futureDate = new Date()
      futureDate.setDate(futureDate.getDate() + days)

      upcomingClosures.value = forms
        .filter(form => {
          if (!form.end_date || !form.is_active) return false
          const endDate = new Date(form.end_date)
          return endDate >= now && endDate <= futureDate
        })
        .map(form => ({
          id: form.id,
          title: form.title || form.name || 'Untitled Survey',
          endDate: form.end_date,
          daysRemaining: Math.ceil((new Date(form.end_date) - now) / (1000 * 60 * 60 * 24))
        }))
        .sort((a, b) => a.daysRemaining - b.daysRemaining)
    } catch (err) {
      console.error('Failed to fetch upcoming closures:', err)
      upcomingClosures.value = []
    }
  }

  const fetchSystemStatus = async () => {
    try {
      // Check system health by making test API calls
      const startTime = Date.now()
      
      try {
        // Test database/API connectivity
        await adminService.getUsers({ limit: 1 })
        systemStatus.value.database = true
        systemStatus.value.api = true
        systemStatus.value.server = true
      } catch (err) {
        console.error('System health check failed:', err)
        systemStatus.value.database = false
        systemStatus.value.api = false
      }

      // Calculate uptime (mock - in production this would come from backend)
      const currentUptime = Math.floor((Date.now() - startTime) / 1000)
      systemUptime.value = currentUptime + 86400 * 7 // Mock 7 days uptime
    } catch (err) {
      console.error('Failed to fetch system status:', err)
    }
  }

  const fetchSystemLogs = async (limit = 10) => {
    try {
      // Fetch comprehensive system activity from all sources
      const [usersResponse, formsResponse, postsResponse] = await Promise.allSettled([
        adminService.getUsers({ limit: 30 }),
        surveyService.getForms(),
        postsService.getPosts({ limit: 30 })
      ])

      const users = usersResponse.status === 'fulfilled' ? usersResponse.value : []
      const forms = formsResponse.status === 'fulfilled' ? (formsResponse.value.data?.results || formsResponse.value.data || []) : []
      const posts = postsResponse.status === 'fulfilled' ? (Array.isArray(postsResponse.value) ? postsResponse.value : postsResponse.value.results || []) : []

      const logs = []

      // 1. USER ACTIVITY LOGS (Alumni & Admin registrations, approvals)
      const recentUsers = users
        .filter(u => u.date_joined)
        .slice(0, 10)
        .map(u => {
          let action = 'User Registered'
          let level = 'info'
          let message = `New user ${u.first_name || ''} ${u.last_name || ''} registered`

          if (u.user_type === 3 && u.is_approved) {
            action = 'Alumni Approved'
            level = 'success'
            message = `Alumni ${u.first_name || ''} ${u.last_name || ''} was approved and activated`
          } else if (u.user_type === 3 && !u.is_approved) {
            action = 'Alumni Pending'
            level = 'warning'
            message = `Alumni ${u.first_name || ''} ${u.last_name || ''} registered, awaiting approval`
          } else if (u.user_type === 2) {
            action = 'Admin Registered'
            level = 'success'
            message = `Admin ${u.first_name || ''} ${u.last_name || ''} registered`
          } else if (u.user_type === 1) {
            action = 'SuperAdmin Created'
            level = 'success'
            message = `SuperAdmin ${u.first_name || ''} ${u.last_name || ''} created`
          }

          return {
            id: `user-${u.id}-${u.date_joined}`,
            level: level,
            action: action,
            message: message.trim(),
            user: u.username || 'System',
            timestamp: u.date_joined,
            category: 'user'
          }
        })

      // 2. SURVEY ACTIVITY LOGS
      const recentSurveys = forms.slice(0, 10).map(f => {
        let action = 'Survey Created'
        let level = 'info'
        let message = `Survey "${f.title || f.name || 'Untitled'}" was created`
        
        if (f.is_active) {
          action = 'Survey Published'
          level = 'success'
          message = `Survey "${f.title || f.name || 'Untitled'}" published and now active`
        } else if (f.end_date && new Date(f.end_date) < new Date()) {
          action = 'Survey Closed'
          level = 'warning'
          message = `Survey "${f.title || f.name || 'Untitled'}" has been closed`
        }

        return {
          id: `survey-${f.id}-${f.updated_at || f.created_at}`,
          level: level,
          action: action,
          message: message,
          user: 'SuperAdmin',
          timestamp: f.updated_at || f.created_at,
          category: 'survey'
        }
      })

      // 3. ALUMNI POST ACTIVITY LOGS (content creation)
      const recentPosts = posts.slice(0, 10).map(p => {
        let action = 'Post Created'
        let level = 'info'
        let message = `New post created by ${p.author?.first_name || ''} ${p.author?.last_name || ''}`

        // Check for different post types and statuses
        if (p.shared_post) {
          action = 'Post Shared'
          message = `Post shared by ${p.author?.first_name || ''} ${p.author?.last_name || ''}`
        } else if (p.is_pinned) {
          action = 'Post Pinned'
          level = 'success'
          message = `Post pinned by ${p.author?.first_name || ''} ${p.author?.last_name || ''}`
        }

        // Check reactions count for engagement tracking
        const totalReactions = (p.likes_count || 0) + (p.loves_count || 0) + (p.hahas_count || 0) + (p.wows_count || 0) + (p.sads_count || 0) + (p.angrys_count || 0)
        if (totalReactions > 10) {
          level = 'success'
          message += ` (${totalReactions} reactions)`
        }

        return {
          id: `post-${p.id}-${p.created_at}`,
          level: level,
          action: action,
          message: message.trim(),
          user: p.author?.username || 'Alumni',
          timestamp: p.created_at,
          category: 'post'
        }
      })

      // 4. ADMIN ACTIONS LOGS (post approvals, deletions, etc.)
      // These would come from admin actions - we can detect deleted/moderated posts
      const moderationLogs = posts
        .filter(p => p.status && p.status !== 'active')
        .slice(0, 5)
        .map(p => ({
          id: `moderation-${p.id}`,
          level: p.status === 'approved' ? 'success' : 'warning',
          action: p.status === 'approved' ? 'Post Approved' : 'Post Moderated',
          message: `Post by ${p.author?.first_name || ''} ${p.author?.last_name || ''} was ${p.status}`,
          user: 'Admin',
          timestamp: p.updated_at || p.created_at,
          category: 'moderation'
        }))

      // Combine all logs and sort by timestamp (most recent first)
      logs.push(...recentUsers, ...recentSurveys, ...recentPosts, ...moderationLogs)
      logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))

      systemLogs.value = logs.slice(0, limit)
    } catch (err) {
      console.error('Failed to fetch system logs:', err)
      systemLogs.value = []
    }
  }

  const fetchAllData = async () => {
    loading.value = true
    error.value = null

    try {
      await Promise.all([
        fetchPendingApprovals(),
        fetchRecentActivity(),
        fetchUpcomingClosures(),
        fetchSystemStatus(),
        fetchSystemLogs()
      ])
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err)
      error.value = 'Failed to load dashboard data'
    } finally {
      loading.value = false
    }
  }

  const approveUser = async (userId) => {
    try {
      await adminService.approveUser(userId)
      
      // Remove from pending list
      const index = pendingApprovals.value.findIndex(user => user.id === userId)
      if (index !== -1) {
        pendingApprovals.value.splice(index, 1)
      }
      
      return { success: true }
    } catch (err) {
      console.error('Failed to approve user:', err)
      return { success: false, error: err.message || 'Failed to approve user' }
    }
  }

  const rejectUser = async (userId) => {
    try {
      await adminService.rejectUser(userId)
      
      // Remove from pending list
      const index = pendingApprovals.value.findIndex(user => user.id === userId)
      if (index !== -1) {
        pendingApprovals.value.splice(index, 1)
      }
      
      return { success: true }
    } catch (err) {
      console.error('Failed to reject user:', err)
      return { success: false, error: err.message || 'Failed to reject user' }
    }
  }

  const refreshDashboard = async () => {
    await fetchAllData()
  }

  return {
    // State
    loading,
    error,
    pendingApprovals,
    recentActivity,
    upcomingClosures,
    systemStatus,
    systemUptime,
    systemLogs,
    
    // Methods
    fetchAllData,
    fetchPendingApprovals,
    fetchRecentActivity,
    fetchUpcomingClosures,
    fetchSystemStatus,
    fetchSystemLogs,
    approveUser,
    rejectUser,
    refreshDashboard
  }
}
