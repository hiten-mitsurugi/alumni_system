import { ref, computed, onMounted } from 'vue'
import { adminService } from '@/services/adminService'

/**
 * Admin Dashboard Composable
 * Manages dashboard actions and state following COPILOT_INSTRUCTIONS
 */
export function useAdminDashboard() {
  // State management
  const loading = ref(false)
  const error = ref(null)
  const activeTab = ref('overview')
  
  // Recent data
  const recentPosts = ref([])
  const recentUsers = ref([])
  const pendingApprovals = ref([])
  const recentReports = ref([])

  // Computed properties
  const hasData = computed(() => 
    recentPosts.value.length > 0 || 
    recentUsers.value.length > 0 || 
    pendingApprovals.value.length > 0
  )

  const totalPendingActions = computed(() =>
    pendingApprovals.value.length + recentReports.value.length
  )

  // Recent data fetching methods
  const fetchRecentPosts = async (limit = 5) => {
    try {
      const response = await adminService.getRecentPosts(limit)
      recentPosts.value = Array.isArray(response) ? response : 
        (response.results || response.data || [])
    } catch (err) {
      console.error('Failed to fetch recent posts:', err)
      recentPosts.value = []
    }
  }

  const fetchRecentUsers = async (limit = 5) => {
    try {
      const response = await adminService.getUsers()
      let users = Array.isArray(response) ? response : 
        (response.results || response.data || [])
      
      // Sort by date joined and take most recent
      users = users
        .sort((a, b) => new Date(b.date_joined) - new Date(a.date_joined))
        .slice(0, limit)
      
      recentUsers.value = users
    } catch (err) {
      console.error('Failed to fetch recent users:', err)
      recentUsers.value = []
    }
  }

  const fetchPendingApprovals = async () => {
    try {
      const response = await adminService.getUsers()
      let users = Array.isArray(response) ? response : 
        (response.results || response.data || [])
      
      // Filter for pending alumni approvals
      pendingApprovals.value = users.filter(user => 
        user.user_type === 3 && !user.is_approved
      )
    } catch (err) {
      console.error('Failed to fetch pending approvals:', err)
      pendingApprovals.value = []
    }
  }

  const fetchRecentReports = async (limit = 5) => {
    try {
      const response = await adminService.getPostReports()
      let reports = Array.isArray(response) ? response : 
        (response.results || response.data || [])
      
      recentReports.value = reports.slice(0, limit)
    } catch (err) {
      console.error('Failed to fetch recent reports:', err)
      recentReports.value = []
    }
  }

  const fetchAllRecentData = async () => {
    loading.value = true
    error.value = null
    
    try {
      await Promise.all([
        fetchRecentPosts(),
        fetchRecentUsers(),
        fetchPendingApprovals(),
        fetchRecentReports()
      ])
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err)
      error.value = 'Failed to load dashboard data'
    } finally {
      loading.value = false
    }
  }

  // User action methods
  const approveUser = async (userId) => {
    try {
      // Use the admin service approve endpoint which performs approval and sends notifications
      await adminService.approveUser(userId)
      
      // Update local state
      const userIndex = pendingApprovals.value.findIndex(user => user.id === userId)
      if (userIndex !== -1) {
        pendingApprovals.value.splice(userIndex, 1)
      }
      
      // Refresh data to ensure consistency
      await fetchPendingApprovals()
      
      return { success: true }
    } catch (err) {
      console.error('Failed to approve user:', err)
      return { 
        success: false, 
        error: err.message || 'Failed to approve user'
      }
    }
  }

  const rejectUser = async (userId) => {
    try {
      // Use the admin service reject endpoint which deletes/rejects the pending user
      await adminService.rejectUser(userId)
      
      // Update local state
      const userIndex = pendingApprovals.value.findIndex(user => user.id === userId)
      if (userIndex !== -1) {
        pendingApprovals.value.splice(userIndex, 1)
      }
      
      return { success: true }
    } catch (err) {
      console.error('Failed to reject user:', err)
      return { 
        success: false, 
        error: err.message || 'Failed to reject user'
      }
    }
  }

  // Post action methods
  const approvePost = async (postId) => {
    try {
      const result = await adminService.approvePost(postId)
      
      // Update local state
      const postIndex = recentPosts.value.findIndex(post => post.id === postId)
      if (postIndex !== -1) {
        recentPosts.value[postIndex].status = 'approved'
      }
      
      return { success: true }
    } catch (err) {
      console.error('Failed to approve post:', err)
      return { 
        success: false, 
        error: err.message || 'Failed to approve post'
      }
    }
  }

  const rejectPost = async (postId) => {
    try {
      const result = await adminService.rejectPost(postId)
      
      // Update local state
      const postIndex = recentPosts.value.findIndex(post => post.id === postId)
      if (postIndex !== -1) {
        recentPosts.value[postIndex].status = 'declined'
      }
      
      return { success: true }
    } catch (err) {
      console.error('Failed to reject post:', err)
      return { 
        success: false, 
        error: err.message || 'Failed to reject post'
      }
    }
  }

  const deletePost = async (postId) => {
    try {
      await adminService.deletePost(postId)
      
      // Remove from local state
      const postIndex = recentPosts.value.findIndex(post => post.id === postId)
      if (postIndex !== -1) {
        recentPosts.value.splice(postIndex, 1)
      }
      
      return { success: true }
    } catch (err) {
      console.error('Failed to delete post:', err)
      return { 
        success: false, 
        error: err.message || 'Failed to delete post'
      }
    }
  }

  // Utility methods
  const refreshDashboard = async () => {
    await fetchAllRecentData()
  }

  const setActiveTab = (tab) => {
    activeTab.value = tab
  }

  // Format helpers
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    try {
      return new Date(dateString).toLocaleDateString()
    } catch {
      return 'Invalid Date'
    }
  }

  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A'
    try {
      return new Date(dateString).toLocaleString()
    } catch {
      return 'Invalid Date'
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'text-green-600'
      case 'pending': return 'text-yellow-600'
      case 'declined': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getUserTypeLabel = (userType) => {
    switch (userType) {
      case 1: return 'Admin'
      case 2: return 'Faculty'
      case 3: return 'Alumni'
      default: return 'Unknown'
    }
  }

  return {
    // State
    loading,
    error,
    activeTab,
    recentPosts,
    recentUsers,
    pendingApprovals,
    recentReports,

    // Computed
    hasData,
    totalPendingActions,

    // Methods
    fetchAllRecentData,
    fetchRecentPosts,
    fetchRecentUsers,
    fetchPendingApprovals,
    fetchRecentReports,
    refreshDashboard,
    
    // Actions
    approveUser,
    rejectUser,
    approvePost,
    rejectPost,
    deletePost,
    
    // Utilities
    setActiveTab,
    formatDate,
    formatDateTime,
    getStatusColor,
    getUserTypeLabel
  }
}