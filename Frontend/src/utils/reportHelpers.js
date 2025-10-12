// Report reason labels and badges
export const getReasonLabel = (reason) => {
  const labels = {
    spam: 'Spam',
    harassment: 'Harassment and Bullying',
    inappropriate: 'Inappropriate Content',
    false_information: 'False Information',
    violence: 'Violence or Threats',
    copyright: 'Copyright Infringement',
    other: 'Other'
  }
  return labels[reason] || 'Unknown'
}

export const getReasonBadgeClass = (reason) => {
  const classes = {
    spam: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
    harassment: 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400',
    inappropriate: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
    false_information: 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400',
    violence: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
    copyright: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
    other: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
  }
  return classes[reason] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
}

export const getReasonColor = (reason) => {
  const colors = {
    spam: 'text-red-600 dark:text-red-400',
    harassment: 'text-orange-600 dark:text-orange-400',
    inappropriate: 'text-yellow-600 dark:text-yellow-400',
    false_information: 'text-purple-600 dark:text-purple-400',
    violence: 'text-red-600 dark:text-red-400',
    copyright: 'text-blue-600 dark:text-blue-400',
    other: 'text-gray-600 dark:text-gray-400'
  }
  return colors[reason] || 'text-gray-600 dark:text-gray-400'
}

// Date formatting
export const formatDate = (dateString) => {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export const formatTimeAgo = (dateString) => {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  const now = new Date()
  const diffInMs = now - date
  const diffInMinutes = Math.floor(diffInMs / (1000 * 60))
  const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60))
  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24))

  if (diffInMinutes < 1) {
    return 'Just now'
  } else if (diffInMinutes < 60) {
    return `${diffInMinutes}m ago`
  } else if (diffInHours < 24) {
    return `${diffInHours}h ago`
  } else if (diffInDays < 7) {
    return `${diffInDays}d ago`
  } else {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }
}

// Category labels
export const getCategoryLabel = (category) => {
  const labels = {
    general: 'General',
    career: 'Career',
    networking: 'Networking',
    events: 'Events',
    news: 'News',
    achievements: 'Achievements'
  }
  return labels[category] || 'General'
}

// Status colors
export const getStatusColor = (status) => {
  const colors = {
    pending: 'text-yellow-600 dark:text-yellow-400',
    resolved: 'text-green-600 dark:text-green-400',
    dismissed: 'text-gray-600 dark:text-gray-400'
  }
  return colors[status] || 'text-gray-600 dark:text-gray-400'
}

// Priority levels based on reason
export const getReportPriority = (reason) => {
  const priorities = {
    violence: 'high',
    harassment: 'high',
    inappropriate: 'medium',
    spam: 'medium',
    false_information: 'medium',
    copyright: 'low',
    other: 'low'
  }
  return priorities[reason] || 'low'
}

export const getPriorityColor = (priority) => {
  const colors = {
    high: 'text-red-600 dark:text-red-400',
    medium: 'text-yellow-600 dark:text-yellow-400',
    low: 'text-green-600 dark:text-green-400'
  }
  return colors[priority] || 'text-gray-600 dark:text-gray-400'
}