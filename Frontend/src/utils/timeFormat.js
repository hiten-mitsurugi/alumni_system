/**
 * Format a date string into a relative time format
 * @param {string} dateString - ISO date string
 * @returns {string} - Formatted relative time (e.g., "3 minutes ago", "2 hours ago")
 */
export function formatRelativeTime(dateString) {
  if (!dateString) return 'Never';
  
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now - date) / 1000);
  
  if (diffInSeconds < 0) {
    return 'Just now';
  }
  
  if (diffInSeconds < 60) {
    return diffInSeconds === 0 ? 'Just now' : `${diffInSeconds} second${diffInSeconds !== 1 ? 's' : ''} ago`;
  }
  
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes} minute${diffInMinutes !== 1 ? 's' : ''} ago`;
  }
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours} hour${diffInHours !== 1 ? 's' : ''} ago`;
  }
  
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) {
    return `${diffInDays} day${diffInDays !== 1 ? 's' : ''} ago`;
  }
  
  const diffInWeeks = Math.floor(diffInDays / 7);
  if (diffInWeeks < 4) {
    return `${diffInWeeks} week${diffInWeeks !== 1 ? 's' : ''} ago`;
  }
  
  const diffInMonths = Math.floor(diffInDays / 30);
  if (diffInMonths < 12) {
    return `${diffInMonths} month${diffInMonths !== 1 ? 's' : ''} ago`;
  }
  
  const diffInYears = Math.floor(diffInDays / 365);
  return `${diffInYears} year${diffInYears !== 1 ? 's' : ''} ago`;
}

/**
 * Format last login with status consideration
 * @param {string} lastLogin - Last login date string
 * @param {object} realTimeStatus - Real-time status object
 * @returns {string} - Formatted last login or status
 */
export function formatLastLogin(lastLogin, realTimeStatus) {
  // If user is currently online, show "Online now"
  if (realTimeStatus && realTimeStatus.is_online) {
    return 'Online now';
  }
  
  // Use last_seen from real_time_status if available, otherwise fall back to last_login
  const dateToUse = realTimeStatus && realTimeStatus.last_seen 
    ? realTimeStatus.last_seen 
    : lastLogin;
    
  return formatRelativeTime(dateToUse);
}

/**
 * Get online status indicator class
 * @param {object} realTimeStatus - Real-time status object
 * @returns {string} - CSS class for status indicator
 */
export function getOnlineStatusClass(realTimeStatus) {
  if (!realTimeStatus) return 'bg-gray-400';
  return realTimeStatus.is_online ? 'bg-green-500' : 'bg-gray-400';
}

/**
 * Get online status text class
 * @param {object} realTimeStatus - Real-time status object
 * @returns {string} - CSS class for status text
 */
export function getOnlineStatusTextClass(realTimeStatus) {
  if (!realTimeStatus) return 'text-gray-600';
  return realTimeStatus.is_online ? 'text-green-600 font-medium' : 'text-gray-600';
}

/**
 * Get online status text
 * @param {object} realTimeStatus - Real-time status object
 * @returns {string} - Status text
 */
export function getOnlineStatusText(realTimeStatus) {
  if (!realTimeStatus) return 'Unknown';
  return realTimeStatus.is_online ? 'Online' : 'Offline';
}
