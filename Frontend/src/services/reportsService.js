import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const reportsService = {
  /**
   * Get reports list with filters and pagination
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} Reports response
   */
  async getReports(params = {}) {
    const authStore = useAuthStore()
    
    console.log('🔑 Auth token exists:', !!authStore.token)
    console.log('👤 Current user:', authStore.user?.username, 'Type:', authStore.user?.user_type)
    
    try {
      // posts_app.urls defines routes like 'reports/' and this file is included under '/api/posts/',
      // so the full path is '/api/posts/reports/'.
      const response = await axios.get(`${BASE_URL}/api/posts/reports/`, {
        headers: { Authorization: `Bearer ${authStore.token}` },
        params
      })
      
      console.log('✅ Reports API success:', response.status)
      return response.data
    } catch (error) {
      console.error('❌ Reports API error:', error.response?.status, error.response?.data)
      throw error
    }
  },

  /**
   * Take action on a report (dismiss, warn, remove)
   * @param {number} reportId - Report ID
   * @param {Object} data - Action data
   * @returns {Promise<Object>} Action response
   */
  async takeAction(reportId, data) {
    const authStore = useAuthStore()
    
    const response = await axios.post(`${BASE_URL}/api/posts/reports/${reportId}/action/`, data, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    
    return response.data
  },

  /**
   * Report a post
   * @param {number} postId - Post ID
   * @param {Object} data - Report data
   * @returns {Promise<Object>} Report response
   */
  async reportPost(postId, data) {
    const authStore = useAuthStore()
    
    // Reporting a post route is defined as '<int:post_id>/report/' inside posts_app, so full path is '/api/posts/<id>/report/'
    const response = await axios.post(`${BASE_URL}/api/posts/${postId}/report/`, data, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    
    return response.data
  }
}