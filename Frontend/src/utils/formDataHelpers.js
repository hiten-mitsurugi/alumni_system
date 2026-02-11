/**
 * Creates FormData for achievement submission
 * @param {Object} achievement - Achievement data
 * @param {File|null} file - Achievement file (optional)
 * @returns {FormData}
 */
export function createAchievementFormData(achievement, file = null) {
  const formData = new FormData()
  
  // Add basic fields
  if (achievement.title) formData.append('title', achievement.title)
  if (achievement.issuing_organization) formData.append('issuing_organization', achievement.issuing_organization)
  if (achievement.issue_date) formData.append('issue_date', achievement.issue_date)
  if (achievement.description) formData.append('description', achievement.description)
  if (achievement.url) formData.append('url', achievement.url)
  
  // Add visibility
  if (achievement.visibility !== undefined) {
    formData.append('visibility', achievement.visibility)
  }
  
  // Add file if provided
  if (file) {
    formData.append('achievement_file', file)
  }
  
  return formData
}

/**
 * Creates FormData for career enhancement submission
 * @param {Object} careerData - Career enhancement data
 * @param {Array} certificateFiles - Array of certificate files
 * @returns {FormData}
 */
export function createCareerEnhancementFormData(careerData, certificateFiles = []) {
  const formData = new FormData()
  
  // Add basic fields
  if (careerData.current_position) formData.append('current_position', careerData.current_position)
  if (careerData.organization) formData.append('organization', careerData.organization)
  if (careerData.start_date) formData.append('start_date', careerData.start_date)
  if (careerData.end_date) formData.append('end_date', careerData.end_date)
  if (careerData.is_current !== undefined) formData.append('is_current', careerData.is_current)
  
  // Employment details
  if (careerData.employment_status) formData.append('employment_status', careerData.employment_status)
  if (careerData.job_search_status) formData.append('job_search_status', careerData.job_search_status)
  if (careerData.open_to_opportunities !== undefined) {
    formData.append('open_to_opportunities', careerData.open_to_opportunities)
  }
  
  // Professional development
  if (careerData.professional_certifications) {
    formData.append('professional_certifications', careerData.professional_certifications)
  }
  if (careerData.skills_expertise) formData.append('skills_expertise', careerData.skills_expertise)
  if (careerData.languages) formData.append('languages', careerData.languages)
  
  // Goals and interests
  if (careerData.career_goals) formData.append('career_goals', careerData.career_goals)
  if (careerData.industry_interests) formData.append('industry_interests', careerData.industry_interests)
  if (careerData.mentorship_interest !== undefined) {
    formData.append('mentorship_interest', careerData.mentorship_interest)
  }
  if (careerData.volunteer_activities) formData.append('volunteer_activities', careerData.volunteer_activities)
  
  // Networking
  if (careerData.networking_preferences) formData.append('networking_preferences', careerData.networking_preferences)
  if (careerData.preferred_contact_method) formData.append('preferred_contact_method', careerData.preferred_contact_method)
  if (careerData.linkedin_profile) formData.append('linkedin_profile', careerData.linkedin_profile)
  if (careerData.personal_website) formData.append('personal_website', careerData.personal_website)
  
  // Notes
  if (careerData.additional_notes) formData.append('additional_notes', careerData.additional_notes)
  
  // Visibility
  if (careerData.visibility !== undefined) {
    formData.append('visibility', careerData.visibility)
  }
  
  // Add certificate files
  if (certificateFiles && certificateFiles.length > 0) {
    certificateFiles.forEach((file, index) => {
      if (file instanceof File) {
        formData.append(`certificate_${index}`, file)
      }
    })
  }
  
  return formData
}

/**
 * Validates achievement data
 * @param {Object} achievement - Achievement to validate
 * @returns {Object} { valid: boolean, errors: Array }
 */
export function validateAchievement(achievement) {
  const errors = []
  
  if (!achievement.title || achievement.title.trim() === '') {
    errors.push('Title is required')
  }
  
  if (!achievement.issuing_organization || achievement.issuing_organization.trim() === '') {
    errors.push('Issuing organization is required')
  }
  
  if (!achievement.issue_date) {
    errors.push('Issue date is required')
  }
  
  return {
    valid: errors.length === 0,
    errors
  }
}

/**
 * Validates career enhancement data
 * @param {Object} careerData - Career data to validate
 * @returns {Object} { valid: boolean, errors: Array }
 */
export function validateCareerEnhancement(careerData) {
  const errors = []
  
  if (careerData.current_position && careerData.current_position.trim() === '') {
    errors.push('Current position cannot be empty if provided')
  }
  
  if (careerData.organization && careerData.organization.trim() === '') {
    errors.push('Organization cannot be empty if provided')
  }
  
  if (careerData.start_date && careerData.end_date) {
    const startDate = new Date(careerData.start_date)
    const endDate = new Date(careerData.end_date)
    if (startDate > endDate) {
      errors.push('Start date cannot be after end date')
    }
  }
  
  return {
    valid: errors.length === 0,
    errors
  }
}
