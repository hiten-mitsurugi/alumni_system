import apiClient from './api'

/**
 * Admin Service
 * Handles all admin-related API calls following COPILOT_INSTRUCTIONS modular structure
 */
class AdminService {
  constructor() {
    // Using absolute API paths now
  }

  // Analytics endpoints
  async getAnalytics() {
    try {
      // Backend exposes admin analytics at /auth/admin/analytics/ (apiClient prefixes /api)
      const response = await apiClient.get('/auth/admin/analytics/')
      return response.data
    } catch (error) {
      console.error('Failed to fetch analytics:', error)
      throw this.handleError(error)
    }
  }

  // Posts management endpoints  
  async getRecentPosts(limit = 10) {
    try {
      const response = await apiClient.get(`/posts/posts/?ordering=-created_at&limit=${limit}`)
      // Normalize paginated or direct array responses
      const data = response.data
      return Array.isArray(data) ? data : (data.results || data.items || [])
    } catch (error) {
      console.error('Failed to fetch recent posts:', error)
      throw this.handleError(error)
    }
  }

  async approvePost(postId) {
    try {
      const response = await apiClient.post(`/posts/posts/${postId}/approve/`)
      return response.data
    } catch (error) {
      console.error('Failed to approve post:', error)
      throw this.handleError(error)
    }
  }

  async rejectPost(postId) {
    try {
      const response = await apiClient.patch(`/posts/posts/${postId}/`, { status: 'declined' })
      return response.data
    } catch (error) {
      console.error('Failed to reject post:', error)
      throw this.handleError(error)
    }
  }

  async deletePost(postId) {
    try {
      const response = await apiClient.delete(`/posts/posts/${postId}/`)
      return response.data
    } catch (error) {
      console.error('Failed to delete post:', error)
      throw this.handleError(error)
    }
  }

  // User management endpoints
  async getUsers(params = {}) {
    try {
      const response = await apiClient.get('/auth/users/', { params })
      const data = response.data
      return Array.isArray(data) ? data : (data.results || data.items || [])
    } catch (error) {
      console.error('Failed to fetch users:', error)
      throw this.handleError(error)
    }
  }

  async getAlumniDirectory(params = {}) {
    try {
      const response = await apiClient.get('/auth/alumni-directory/', { params })
      const data = response.data
      return Array.isArray(data) ? data : (data.results || data.items || [])
    } catch (error) {
      console.error('Failed to fetch alumni directory:', error)
      throw this.handleError(error)
    }
  }

  async getPendingUsers() {
    try {
      const response = await apiClient.get('/auth/pending-alumni/')
      return response.data
    } catch (error) {
      console.error('Failed to fetch pending users:', error)
      throw this.handleError(error)
    }
  }

  async approveUser(userId) {
    try {
      // Backend expects a POST to approve the pending user
      const response = await apiClient.post(`/auth/approve-user/${userId}/`)
      return response.data
    } catch (error) {
      console.error('Failed to approve user:', error)
      throw this.handleError(error)
    }
  }

  async rejectUser(userId) {
    try {
      // Backend expects a POST to reject the pending user
      const response = await apiClient.post(`/auth/reject-user/${userId}/`)
      return response.data
    } catch (error) {
      console.error('Failed to reject user:', error)
      throw this.handleError(error)
    }
  }

  // Reports management endpoints
  async getPostReports(status = 'pending') {
    try {
      const response = await apiClient.get('/posts/posts/reports/')
      const data = response.data
      return Array.isArray(data) ? data : (data.results || data.items || [])
    } catch (error) {
      console.error('Failed to fetch post reports:', error)
      // Return empty result if reports API is not available
      return []
    }
  }

  // Error handling helper
  handleError(error) {
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.message || 
                        error.response?.data?.error ||
                        error.message || 
                        'An unexpected error occurred'

    const errorCode = error.response?.status || 'UNKNOWN'
    
    return {
      message: errorMessage,
      code: errorCode,
      details: error.response?.data || {},
      originalError: error
    }
  }

  // Utility methods
  formatAnalyticsData(rawData) {
    // Transform API response to match dashboard expectations
    if (!rawData) return {}
    return {
      // Users
      totalUsers: rawData.users?.total || rawData.total_users || rawData.summary?.total_users || 0,
      activeUsers: rawData.users?.active || rawData.active_users || 0,
      pendingApprovals: rawData.users?.pending_approvals || rawData.pending_approvals || 0,
  // Keep null when backend doesn't provide a value so frontend can decide to fallback
  recentRegistrations: (rawData.users && rawData.users.recent_registrations !== undefined) ? rawData.users.recent_registrations : (rawData.recent_registrations !== undefined ? rawData.recent_registrations : null),
      onlineUsers: rawData.users?.online_now || rawData.online_now || 0,
      // Posts (try several possible keys)
      totalPosts: rawData.posts?.total || rawData.total_posts || rawData.summary?.total_content || 0,
      pendingPosts: rawData.posts?.pending || rawData.pending_posts || 0,
      reportedPosts: (() => {
        const reported = rawData.posts?.reported || rawData.reports?.pending || rawData.reports?.total || 0;
        console.log('Debug reportedPosts calculation:', {
          'rawData.posts?.reported': rawData.posts?.reported,
          'rawData.reports?.pending': rawData.reports?.pending,
          'rawData.reports?.total': rawData.reports?.total,
          'final reported value': reported
        });
        return reported;
      })(),
      approvedPosts: rawData.posts?.approved || rawData.approved_posts || 0,
      declinedPosts: rawData.posts?.declined || rawData.declined_posts || 0,
      weeklyPosts: rawData.posts?.weekly_posts || rawData.weekly_posts || 0,
      // Approval rate: prefer posts.approval_rate, then summary value
      approvalRate: (rawData.posts && rawData.posts.approval_rate !== undefined) ? rawData.posts.approval_rate : (rawData.approval_rate || rawData.summary?.approval_rate || 0),
      userEngagement: rawData.summary?.user_engagement || rawData.user_engagement || 0,
      pendingActions: rawData.summary?.pending_actions || rawData.pending_actions || 0,
      lastUpdated: rawData.last_updated || rawData.summary?.last_updated || null
    }
  }
}

// Create singleton instance
const adminService = new AdminService()
export { adminService }