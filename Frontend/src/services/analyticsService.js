import api from './api'

class AnalyticsService {
  
  // ============= ANALYTICS DATA ENDPOINTS =============
  
  async getAnalyticsData(filters = {}) {
    try {
      // Get data from all analytics endpoints in parallel
      const [
        overviewResponse,
        employabilityResponse,
        skillsResponse,
        curriculumResponse,
        studiesResponse,
        competitivenessResponse,
        programComparisonResponse,
        demographicsResponse
      ] = await Promise.all([
        api.post('/survey/admin/analytics/overview/', { filters }),
        api.post('/survey/admin/analytics/employability/', { filters }),
        api.post('/survey/admin/analytics/skills/', { filters }),
        api.post('/survey/admin/analytics/curriculum/', { filters }),
        api.post('/survey/admin/analytics/studies/', { filters }),
        api.post('/survey/admin/analytics/competitiveness/', { filters }),
        api.post('/survey/admin/analytics/program-comparison/', { filters }),
        api.post('/survey/admin/analytics/demographics/', { filters })
      ])
      
      return this.processAnalyticsData({
        overview: overviewResponse.data.overview,
        employability: employabilityResponse.data.employability,
        skills: skillsResponse.data.skills,
        curriculum: curriculumResponse.data.curriculum,
        studies: studiesResponse.data.studies,
        competitiveness: competitivenessResponse.data.competitiveness,
        program_comparison: programComparisonResponse.data.program_comparison,
        demographics: demographicsResponse.data.demographics,
        metadata: {
          generated_at: new Date().toISOString(),
          filters_applied: filters
        }
      })
    } catch (error) {
      console.error('Failed to fetch analytics data:', error)
      throw error
    }
  }

  async getOverviewData(filters = {}) {
    try {
      const response = await api.post('/survey/admin/analytics/overview/', { filters })
      return response.data
    } catch (error) {
      console.error('Failed to fetch overview data:', error)
      throw error
    }
  }

  async getEmployabilityData(filters = {}) {
    try {
      const response = await api.post('/survey/admin/analytics/employability/', { filters })
      return response.data
    } catch (error) {
      console.error('Failed to fetch employability data:', error)
      throw error
    }
  }

  async getSkillsData(filters = {}) {
    try {
      const response = await api.post('/survey/admin/analytics/skills/', { filters })
      return response.data
    } catch (error) {
      console.error('Failed to fetch skills data:', error)
      throw error
    }
  }

  async getCurriculumData(filters = {}) {
    try {
      const response = await api.post('/survey/admin/analytics/curriculum/', { filters })
      return response.data
    } catch (error) {
      console.error('Failed to fetch curriculum data:', error)
      throw error
    }
  }

  async getStudiesData(filters = {}) {
    try {
      const response = await api.post('/survey/admin/analytics/studies/', { filters })
      return response.data
    } catch (error) {
      console.error('Failed to fetch studies data:', error)
      throw error
    }
  }

  async getCompetitivenessData(filters = {}) {
    try {
      const response = await api.post('/survey/admin/analytics/competitiveness/', { filters })
      return response.data
    } catch (error) {
      console.error('Failed to fetch competitiveness data:', error)
      throw error
    }
  }

  async getProgramComparisonData(filters = {}) {
    try {
      const response = await api.post('/survey/admin/analytics/program-comparison/', { filters })
      return response.data
    } catch (error) {
      console.error('Failed to fetch program comparison data:', error)
      throw error
    }
  }

  async getDemographicsData(filters = {}) {
    try {
      const response = await api.post('/survey/admin/analytics/demographics/', { filters })
      return response.data
    } catch (error) {
      console.error('Failed to fetch demographics data:', error)
      throw error
    }
  }

  // ============= FILTER OPTIONS =============
  
  async getFilterOptions() {
    try {
      const response = await api.get('/survey/admin/analytics/filter-options/')
      return response.data
    } catch (error) {
      console.error('Failed to fetch filter options:', error)
      throw error
    }
  }

  // ============= EXPORT FUNCTIONALITY =============
  
  async exportReport(reportType, format = 'xlsx', filters = {}) {
    try {
      const response = await api.post('/survey/admin/analytics/export/', {
        report_type: reportType,
        format,
        filters
      }, {
        responseType: 'blob'
      })

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      
      const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
      const extension = format === 'pdf' ? 'pdf' : format === 'csv' ? 'csv' : 'xlsx'
      link.setAttribute('download', `analytics-${reportType}-${timestamp}.${extension}`)
      
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      return true
    } catch (error) {
      console.error('Failed to export report:', error)
      throw error
    }
  }

  async exportFullReport(format = 'pdf', filters = {}) {
    try {
      const response = await api.post('/survey/admin/analytics/export-full/', {
        format,
        filters
      }, {
        responseType: 'blob'
      })

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      
      const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
      const extension = format === 'pdf' ? 'pdf' : 'xlsx'
      link.setAttribute('download', `csu-analytics-full-report-${timestamp}.${extension}`)
      
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      return true
    } catch (error) {
      console.error('Failed to export full report:', error)
      throw error
    }
  }

  // ============= DATA PROCESSING UTILITIES =============
  
  processAnalyticsData(rawData) {
    return {
      overview: this.processOverviewData(rawData.overview || {}),
      employability: this.processEmployabilityData(rawData.employability || {}),
      skills: this.processSkillsData(rawData.skills || {}),
      curriculum: this.processCurriculumData(rawData.curriculum || {}),
      studies: this.processStudiesData(rawData.studies || {}),
      competitiveness: this.processCompetitivenessData(rawData.competitiveness || {}),
      programComparison: this.processProgramComparisonData(rawData.program_comparison || {}),
      demographics: this.processDemographicsData(rawData.demographics || {}),
      metadata: rawData.metadata || {}
    }
  }

  processOverviewData(data) {
    return {
      totalRespondents: data.total_respondents || 0,
      employmentRate: this.calculatePercentage(data.employed_count, data.total_respondents),
      averageIncome: data.average_income || 0,
      internationalRate: this.calculatePercentage(data.international_count, data.employed_count),
      furtherStudiesRate: this.calculatePercentage(data.studies_count, data.total_respondents),
      competitivenessScore: data.average_competitiveness || 0,
      topProgram: data.top_performing_program || null,
      topSkill: data.most_valued_skill || null,
      quickInsights: data.quick_insights || [],
      kpiCards: this.generateKPICards(data)
    }
  }

  processEmployabilityData(data) {
    return {
      overallStats: {
        employmentRate: this.calculatePercentage(data.employed_count, data.total_respondents),
        unemploymentRate: this.calculatePercentage(data.unemployed_count, data.total_respondents),
        selfEmployedRate: this.calculatePercentage(data.self_employed_count, data.total_respondents),
        averageIncome: data.average_income || 0,
        localEmploymentRate: this.calculatePercentage(data.local_employed, data.employed_count),
        internationalRate: this.calculatePercentage(data.international_employed, data.employed_count)
      },
      programAnalysis: data.program_analysis || [],
      incomeAnalysis: data.income_analysis || {},
      jobRelevance: data.job_relevance || {},
      employmentSectors: data.employment_sectors || {},
      topPerformers: data.top_performers || []
    }
  }

  processSkillsData(data) {
    const skillsAverages = data.skills_averages || {}
    const rankedSkills = Object.entries(skillsAverages)
      .map(([skill, avg]) => ({ skill, average: avg }))
      .sort((a, b) => b.average - a.average)

    return {
      overallAverages: skillsAverages,
      rankedSkills: rankedSkills,
      topSkills: rankedSkills.slice(0, 5),
      programMatrix: data.program_matrix || {},
      skillsGaps: data.skills_gaps || [],
      correlationAnalysis: data.correlation_analysis || {},
      recommendations: data.recommendations || []
    }
  }

  processCurriculumData(data) {
    const componentAverages = data.component_averages || {}
    const rankedComponents = Object.entries(componentAverages)
      .map(([component, avg]) => ({ component, average: avg }))
      .sort((a, b) => b.average - a.average)

    return {
      componentRatings: componentAverages,
      rankedComponents: rankedComponents,
      topComponents: rankedComponents.slice(0, 5),
      programAnalysis: data.program_analysis || {},
      theoreticalVsPractical: data.theoretical_vs_practical || {},
      lowPerformance: data.low_performance || [],
      employmentCorrelation: data.employment_correlation || {},
      recommendations: data.recommendations || []
    }
  }

  processStudiesData(data) {
    return {
      overview: {
        participationRate: this.calculatePercentage(data.pursuing_studies, data.total_respondents),
        totalPursuing: data.pursuing_studies || 0
      },
      studyLevels: data.study_levels || {},
      studyModes: data.study_modes || {},
      motivations: data.motivations || {},
      programBreakdown: data.program_breakdown || {},
      impactAnalysis: data.impact_analysis || {},
      institutionalPartnerships: data.partnerships || []
    }
  }

  processCompetitivenessData(data) {
    return {
      overallScore: data.overall_score || 0,
      distribution: data.distribution || {},
      programRankings: data.program_rankings || [],
      factorsAnalysis: data.factors_analysis || {},
      employmentCorrelation: data.employment_correlation || {},
      internationalComparison: data.international_comparison || {},
      recommendations: data.recommendations || []
    }
  }

  processProgramComparisonData(data) {
    return {
      performanceMatrix: data.performance_matrix || [],
      overallRankings: data.overall_rankings || [],
      strengths: data.strengths || {},
      weaknesses: data.weaknesses || {},
      bestPractices: data.best_practices || [],
      underperforming: data.underperforming || [],
      trendAnalysis: data.trend_analysis || {},
      benchmarks: data.benchmarks || {}
    }
  }

  processDemographicsData(data) {
    return {
      overview: {
        totalRespondents: data.total_respondents || 0,
        genderDistribution: data.gender_distribution || {},
        civilStatusDistribution: data.civil_status_distribution || {},
        locationDistribution: data.location_distribution || {}
      },
      responseRates: data.response_rates || {},
      programDemographics: data.program_demographics || {},
      impactAnalysis: data.impact_analysis || {},
      geographicMobility: data.geographic_mobility || {},
      diversityMetrics: data.diversity_metrics || {}
    }
  }

  // ============= UTILITY METHODS =============
  
  calculatePercentage(numerator, denominator) {
    if (!denominator || denominator === 0) return 0
    return parseFloat(((numerator / denominator) * 100).toFixed(2))
  }

  generateKPICards(data) {
    return [
      {
        title: 'Total Respondents',
        value: data.total_respondents || 0,
        format: 'number',
        trend: data.respondents_trend || 0,
        icon: '👥'
      },
      {
        title: 'Employment Rate',
        value: this.calculatePercentage(data.employed_count, data.total_respondents),
        format: 'percentage',
        trend: data.employment_trend || 0,
        icon: '💼'
      },
      {
        title: 'Average Income',
        value: data.average_income || 0,
        format: 'currency',
        trend: data.income_trend || 0,
        icon: '💰'
      },
      {
        title: 'Further Studies',
        value: this.calculatePercentage(data.studies_count, data.total_respondents),
        format: 'percentage',
        trend: data.studies_trend || 0,
        icon: '🎓'
      },
      {
        title: 'Competitiveness',
        value: data.average_competitiveness || 0,
        format: 'rating',
        trend: data.competitiveness_trend || 0,
        icon: '🏆'
      },
      {
        title: 'International Rate',
        value: this.calculatePercentage(data.international_count, data.employed_count),
        format: 'percentage',
        trend: data.international_trend || 0,
        icon: '🌍'
      }
    ]
  }

  formatValue(value, format) {
    switch (format) {
      case 'number':
        return parseInt(value).toLocaleString()
      case 'percentage':
        return `${value}%`
      case 'currency':
        return `₱${parseInt(value).toLocaleString()}`
      case 'rating':
        return `${parseFloat(value).toFixed(1)}/5.0`
      default:
        return value.toString()
    }
  }

  // ============= VALIDATION HELPERS =============
  
  validateFilters(filters) {
    const validatedFilters = {}
    
    if (filters.programs && Array.isArray(filters.programs) && filters.programs.length > 0) {
      validatedFilters.programs = filters.programs
    }
    
    if (filters.graduationYears && Array.isArray(filters.graduationYears) && filters.graduationYears.length > 0) {
      validatedFilters.graduation_years = filters.graduationYears
    }
    
    if (filters.employmentStatus && Array.isArray(filters.employmentStatus) && filters.employmentStatus.length > 0) {
      validatedFilters.employment_status = filters.employmentStatus
    }
    
    if (filters.location && Array.isArray(filters.location) && filters.location.length > 0) {
      validatedFilters.location = filters.location
    }
    
    if (filters.gender && Array.isArray(filters.gender) && filters.gender.length > 0) {
      validatedFilters.gender = filters.gender
    }
    
    if (filters.civilStatus && Array.isArray(filters.civilStatus) && filters.civilStatus.length > 0) {
      validatedFilters.civil_status = filters.civilStatus
    }
    
    if (filters.incomeRange && Array.isArray(filters.incomeRange) && filters.incomeRange.length === 2) {
      validatedFilters.income_min = filters.incomeRange[0]
      validatedFilters.income_max = filters.incomeRange[1]
    }
    
    if (filters.skillsRatingRange && Array.isArray(filters.skillsRatingRange) && filters.skillsRatingRange.length === 2) {
      validatedFilters.skills_rating_min = filters.skillsRatingRange[0]
      validatedFilters.skills_rating_max = filters.skillsRatingRange[1]
    }
    
    if (filters.dateRange && filters.dateRange.start && filters.dateRange.end) {
      validatedFilters.date_from = filters.dateRange.start
      validatedFilters.date_to = filters.dateRange.end
    }
    
    return validatedFilters
  }
}

export const analyticsService = new AnalyticsService()
export default analyticsService