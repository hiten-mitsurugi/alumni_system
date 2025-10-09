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
    
    // Note: posts_app.urls defines routes like 'posts/reports/' and this file is included under '/api/posts/',
    // so the full path is '/api/posts/posts/reports/' (yes, double 'posts').
    const response = await axios.get(`${BASE_URL}/api/posts/posts/reports/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
      params
    })
    
    return response.data
  },

  /**
   * Take action on a report (dismiss, warn, remove)
   * @param {number} reportId - Report ID
   * @param {Object} data - Action data
   * @returns {Promise<Object>} Action response
   */
  async takeAction(reportId, data) {
    const authStore = useAuthStore()
    
    const response = await axios.post(`${BASE_URL}/api/posts/posts/reports/${reportId}/action/`, data, {
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
    
    // Reporting a post route is defined as 'posts/<int:post_id>/report/' inside posts_app, so full path is '/api/posts/posts/<id>/report/'
    const response = await axios.post(`${BASE_URL}/api/posts/posts/${postId}/report/`, data, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    
    return response.data
  }
}