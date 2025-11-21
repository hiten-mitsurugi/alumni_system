import api from './api'

class SurveyService {
  // ============= ADMIN ENDPOINTS =============
  
  // Categories (Admin Management)
  async getCategories() {
    return api.get('/survey/admin/categories/')
  }

  async getCategory(id) {
    return api.get(`/survey/admin/categories/${id}/`)
  }

  async createCategory(data) {
    return api.post('/survey/admin/categories/', data)
  }

  async updateCategory(id, data) {
    return api.put(`/survey/admin/categories/${id}/`, data)
  }

  async deleteCategory(id) {
    return api.delete(`/survey/admin/categories/${id}/`)
  }

  // Questions (Admin Management)
  async getQuestions(categoryId = null) {
    const params = categoryId ? { category: categoryId } : {}
    return api.get('/survey/admin/questions/', { params })
  }

  async getQuestion(id) {
    return api.get(`/survey/admin/questions/${id}/`)
  }

  async createQuestion(data) {
    return api.post('/survey/admin/questions/', data)
  }

  async updateQuestion(id, data) {
    return api.put(`/survey/admin/questions/${id}/`, data)
  }

  async deleteQuestion(id) {
    return api.delete(`/survey/admin/questions/${id}/`)
  }

  // Analytics (Admin Only)
  async getAnalytics() {
    return api.get('/survey/admin/analytics/')
  }

  async getCategoryAnalytics(categoryId, filters = {}) {
    const params = { category_id: categoryId }
    
    // Add optional filters
    if (filters.programs && filters.programs.length > 0) {
      params.programs = filters.programs.join(',')
    }
    if (filters.graduation_years && filters.graduation_years.length > 0) {
      params.graduation_years = filters.graduation_years.join(',')
    }
    if (filters.response_years && filters.response_years.length > 0) {
      params.response_years = filters.response_years.join(',')
    }
    
    return api.get('/survey/admin/analytics/category/', { params })
  }

  async exportCategoryPDF(categoryId) {
    return api.post('/survey/admin/analytics/category/pdf/', {
      category_id: categoryId
    }, {
      responseType: 'blob'
    })
  }

  async exportFormPDF(categoryIds, filters = {}) {
    const requestData = {
      category_ids: categoryIds
    }
    
    // Add optional filters
    if (filters.programs && filters.programs.length > 0) {
      requestData.programs = filters.programs
    }
    if (filters.graduation_years && filters.graduation_years.length > 0) {
      requestData.graduation_years = filters.graduation_years
    }
    if (filters.response_years && filters.response_years.length > 0) {
      requestData.response_years = filters.response_years
    }
    
    return api.post('/survey/admin/analytics/form/pdf/', requestData, {
      responseType: 'blob'
    })
  }

  async getResponses(filters = {}) {
    return api.get('/survey/admin/responses/', { params: filters })
  }

  async exportResponses(exportData = {}) {
    const {
      format = 'xlsx',
      category_id = null,
      category_ids = [],
      date_from = null,
      date_to = null,
      programs = [],
      graduation_years = [],
      response_years = [],  // NEW: Response years filter
      include_profile_fields = [
        'first_name', 'last_name', 'email', 'program', 
        'year_graduated', 'student_id', 'birth_date', 'user_type'
      ]
    } = exportData

    return api.post('/survey/admin/export/', {
      format,
      category_id,
      category_ids,
      date_from,
      date_to,
      programs,
      graduation_years,
      response_years,  // NEW: Include response years
      include_profile_fields
    }, {
      responseType: format === 'xlsx' ? 'blob' : 'json'
    })
  }

  async clearCache() {
    return api.post('/survey/admin/clear-cache/')
  }

  // Forms (SurveyTemplate) as top-level forms
  async getForms() {
    return api.get('/survey/admin/forms/')
  }

  async getForm(id) {
    return api.get(`/survey/admin/forms/${id}/`)
  }

  async createForm(data) {
    return api.post('/survey/admin/forms/', data)
  }

  async updateForm(id, data) {
    return api.patch(`/survey/admin/forms/${id}/`, data)
  }

  async deleteForm(id) {
    return api.delete(`/survey/admin/forms/${id}/`)
  }

  async publishForm(id, data) {
    return api.post(`/survey/admin/forms/${id}/publish/`, data)
  }

  // ============= PUBLIC SURVEY ACCESS =============
  
  /**
   * Get public survey details by slug (NO AUTHENTICATION REQUIRED)
   * This is used when alumni click on shared survey links
   * @param {string} slug - The public slug of the survey
   * @returns {Promise} Survey data with sections and questions
   */
  async getPublicSurvey(slug) {
    return api.get(`/survey/public/${slug}/`)
  }

  // ============= MONITORING ENDPOINTS (Problem 2) =============
  
  /**
   * Get response statistics for all surveys
   * @returns {Promise} All surveys statistics
   */
  async getAllSurveysStatistics() {
    return api.get('/survey/statistics/all/')
  }

  /**
   * Get response statistics for a specific survey
   * @param {number} surveyId - Survey ID
   * @returns {Promise} Survey statistics
   */
  async getSurveyStatistics(surveyId) {
    return api.get(`/survey/${surveyId}/statistics/`)
  }

  /**
   * Get list of non-respondents for a survey
   * @param {number} surveyId - Survey ID
   * @param {Object} filters - Optional filters (program, year_graduated, etc.)
   * @returns {Promise} Non-respondents list with statistics
   */
  async getSurveyNonRespondents(surveyId, filters = {}) {
    return api.get(`/survey/${surveyId}/non-respondents/`, { params: filters })
  }

  /**
   * Export non-respondents to CSV
   * @param {number} surveyId - Survey ID
   * @param {Object} filters - Optional filters
   * @returns {Promise<Blob>} CSV file blob
   */
  async exportNonRespondentsCSV(surveyId, filters = {}) {
    try {
      const params = { ...filters, export: 'csv' }
      const response = await api.get(`/survey/${surveyId}/non-respondents/`, {
        params,
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      console.error('Export failed:', error)
      throw error
    }
  }

  /**
   * Download non-respondents CSV file
   * @param {number} surveyId - Survey ID
   * @param {string} surveyName - Survey name for filename
   * @param {Object} filters - Optional filters
   */
  async downloadNonRespondentsCSV(surveyId, surveyName, filters = {}) {
    try {
      const blob = await this.exportNonRespondentsCSV(surveyId, filters)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `non_respondents_${surveyName.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      return true
    } catch (error) {
      console.error('Download failed:', error)
      return false
    }
  }

  // ============= ALUMNI/USER ENDPOINTS =============
  
  // Get survey questions for alumni to answer
  async getActiveSurveyQuestions() {
    return api.get('/survey/active-questions/')
  }

  // Get survey questions for registration process (public endpoint)
  async getRegistrationSurveyQuestions() {
    return api.get('/survey/registration-questions/')
  }

  // Submit survey responses (alumni)
  async submitSurveyResponse(data) {
    return api.post('/survey/responses/', data)
  }

  // Get user's own responses
  async getMyResponses() {
    return api.get('/survey/my-responses/')
  }

  // Get user's survey progress
  async getSurveyProgress() {
    return api.get('/survey/progress/')
  }

  // ============= UTILITY METHODS =============

  // Question type definitions
  getQuestionTypes() {
    return [
      { value: 'text', label: 'Short Text', icon: '📝', hasOptions: false },
      { value: 'textarea', label: 'Long Text', icon: '📄', hasOptions: false },
      { value: 'number', label: 'Number', icon: '🔢', hasOptions: false },
      { value: 'email', label: 'Email', icon: '📧', hasOptions: false },
      { value: 'date', label: 'Date', icon: '📅', hasOptions: false },
      { value: 'radio', label: 'Single Choice', icon: '🔘', hasOptions: true },
      { value: 'checkbox', label: 'Multiple Choice', icon: '☑️', hasOptions: true },
      { value: 'select', label: 'Dropdown', icon: '📋', hasOptions: true },
      { value: 'rating', label: 'Rating Scale', icon: '⭐', hasOptions: false },
      { value: 'yes_no', label: 'Yes/No', icon: '✅', hasOptions: false },
      { value: 'file', label: 'File Upload', icon: '📎', hasOptions: false }
    ]
  }

  // Validate question data before saving
  validateQuestionData(data) {
    const errors = {}

    // Required fields
    if (!data.question_text?.trim()) {
      errors.question_text = 'Question text is required'
    }

    if (!data.question_type) {
      errors.question_type = 'Question type is required'
    }

    if (!data.category) {
      errors.category = 'Category is required'
    }

    // Type-specific validation
    if (data.question_type === 'rating') {
      if (!data.min_value || !data.max_value) {
        errors.rating = 'Rating scale requires min and max values'
      } else if (parseInt(data.min_value) >= parseInt(data.max_value)) {
        errors.rating = 'Min value must be less than max value'
      }
    }

    if (['radio', 'checkbox', 'select'].includes(data.question_type)) {
      if (!data.options || data.options.length < 2) {
        errors.options = 'At least 2 options are required for choice questions'
      }
    }

    if (data.question_type === 'number') {
      if (data.min_value && data.max_value && parseInt(data.min_value) >= parseInt(data.max_value)) {
        errors.number_range = 'Min value must be less than max value'
      }
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    }
  }

  // Format question type display
  formatQuestionType(type) {
    const types = this.getQuestionTypes()
    const found = types.find(t => t.value === type)
    return found ? found.label : type
  }

  // Format response value for display
  formatResponseValue(question, value) {
    if (value === null || value === undefined) return 'No response'
    
    switch (question.question_type) {
      case 'yes_no':
        return value ? 'Yes' : 'No'
      case 'rating':
        return `${value} / ${question.max_value || 5}`
      case 'checkbox':
        return Array.isArray(value) ? value.join(', ') : value
      case 'date':
        return new Date(value).toLocaleDateString()
      case 'file':
        return typeof value === 'string' ? value.split('/').pop() : 'File uploaded'
      default:
        return value.toString()
    }
  }

  // ============= DATA PROCESSING UTILITIES =============

  // Process analytics data
  processAnalyticsData(responses, questions) {
    const analytics = {
      totalResponses: responses.length,
      completionRate: 0,
      questionStats: {}
    }

    questions.forEach(question => {
      const questionResponses = responses.filter(r => 
        r.responses && r.responses[question.id] !== undefined
      )

      analytics.questionStats[question.id] = {
        question: question.question_text,
        type: question.question_type,
        responseCount: questionResponses.length,
        responseRate: responses.length > 0 ? (questionResponses.length / responses.length * 100) : 0,
        values: questionResponses.map(r => r.responses[question.id])
      }

      // Type-specific analytics
      if (question.question_type === 'rating') {
        const values = questionResponses.map(r => parseFloat(r.responses[question.id])).filter(v => !isNaN(v))
        if (values.length > 0) {
          analytics.questionStats[question.id].average = values.reduce((a, b) => a + b, 0) / values.length
          analytics.questionStats[question.id].distribution = this.calculateRatingDistribution(values, question.min_value, question.max_value)
        }
      } else if (['radio', 'select'].includes(question.question_type)) {
        analytics.questionStats[question.id].distribution = this.calculateChoiceDistribution(
          questionResponses.map(r => r.responses[question.id])
        )
      } else if (question.question_type === 'checkbox') {
        analytics.questionStats[question.id].distribution = this.calculateMultiChoiceDistribution(
          questionResponses.map(r => r.responses[question.id])
        )
      }
    })

    return analytics
  }

  calculateRatingDistribution(values, min = 1, max = 5) {
    const distribution = {}
    for (let i = min; i <= max; i++) {
      distribution[i] = values.filter(v => v === i).length
    }
    return distribution
  }

  calculateChoiceDistribution(values) {
    const distribution = {}
    values.forEach(value => {
      distribution[value] = (distribution[value] || 0) + 1
    })
    return distribution
  }

  calculateMultiChoiceDistribution(values) {
    const distribution = {}
    values.forEach(valueArray => {
      if (Array.isArray(valueArray)) {
        valueArray.forEach(value => {
          distribution[value] = (distribution[value] || 0) + 1
        })
      }
    })
    return distribution
  }

  // ============= SURVEY MANAGEMENT HELPERS =============

  // Get survey completion statistics
  async getSurveyStats() {
    try {
      const [categoriesResponse, questionsResponse, analyticsResponse] = await Promise.all([
        this.getCategories(),
        this.getQuestions(),
        this.getAnalytics()
      ])

      return {
        totalCategories: categoriesResponse.data.length,
        activeCategories: categoriesResponse.data.filter(c => c.is_active).length,
        totalQuestions: questionsResponse.data.length,
        activeQuestions: questionsResponse.data.filter(q => q.is_active).length,
        analytics: analyticsResponse.data
      }
    } catch (error) {
      console.error('Error getting survey stats:', error)
      throw error
    }
  }

  // Bulk operations
  async bulkUpdateQuestions(questionIds, updates) {
    const promises = questionIds.map(id => this.updateQuestion(id, updates))
    return Promise.all(promises)
  }

  async bulkDeleteQuestions(questionIds) {
    const promises = questionIds.map(id => this.deleteQuestion(id))
    return Promise.all(promises)
  }

  // Survey response helpers
  async getUserResponsesCount(userId) {
    try {
      const response = await this.getResponses({ user_id: userId })
      return response.data.length
    } catch (error) {
      console.error('Error getting user responses count:', error)
      return 0
    }
  }

  // Check if survey system is properly configured
  async validateSurveySystem() {
    try {
      const categories = await this.getCategories()
      const questions = await this.getQuestions()
      
      const validation = {
        hasCategories: categories.data.length > 0,
        hasActiveCategories: categories.data.some(c => c.is_active),
        hasQuestions: questions.data.length > 0,
        hasActiveQuestions: questions.data.some(q => q.is_active),
        categoriesWithoutQuestions: categories.data.filter(c => 
          !questions.data.some(q => q.category?.id === c.id)
        )
      }

      validation.isValid = validation.hasCategories && 
                          validation.hasActiveCategories && 
                          validation.hasQuestions && 
                          validation.hasActiveQuestions

      return validation
    } catch (error) {
      console.error('Error validating survey system:', error)
      return { isValid: false, error: error.message }
    }
  }
}

export const surveyService = new SurveyService()
export default surveyService
