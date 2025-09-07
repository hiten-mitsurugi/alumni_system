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
  // Check if user is actually online using same logic as messaging components
  const isOnline = isUserActuallyOnline(realTimeStatus);
  
  if (isOnline) {
    return 'Online now';
  }
  
  // Use last_seen from real_time_status if available, otherwise fall back to last_login
  const dateToUse = realTimeStatus && realTimeStatus.last_seen 
    ? realTimeStatus.last_seen 
    : lastLogin;
    
  return formatRelativeTime(dateToUse);
}

/**
 * Check if user is actually online using same logic as messaging components
 * @param {object} realTimeStatus - Real-time status object
 * @returns {boolean} - True if user is actually online
 */
function isUserActuallyOnline(realTimeStatus) {
  if (!realTimeStatus) return false;
  
  // If backend status is explicitly offline, user is offline
  if (realTimeStatus.status === 'offline') {
    return false;
  }
  
  // If backend status is online, check if last_seen is reasonable
  if (realTimeStatus.status === 'online') {
    if (!realTimeStatus.last_seen) {
      return true; // Trust backend status
    }
    
    const lastSeen = new Date(realTimeStatus.last_seen);
    const now = new Date();
    const diffMinutes = (now - lastSeen) / (1000 * 60);
    
    // If backend says online but last seen is over 10 minutes ago, something's wrong
    if (diffMinutes > 10) {
      return false;
    }
    
    return true;
  }
  
  // Fallback to legacy is_online field if status field is not available
  return realTimeStatus.is_online === true;
}

/**
 * Get online status indicator class
 * @param {object} realTimeStatus - Real-time status object
 * @returns {string} - CSS class for status indicator
 */
export function getOnlineStatusClass(realTimeStatus) {
  const isOnline = isUserActuallyOnline(realTimeStatus);
  return isOnline ? 'bg-green-500' : 'bg-gray-400';
}

/**
 * Get online status text class
 * @param {object} realTimeStatus - Real-time status object
 * @returns {string} - CSS class for status text
 */
export function getOnlineStatusTextClass(realTimeStatus) {
  const isOnline = isUserActuallyOnline(realTimeStatus);
  return isOnline ? 'text-green-600 font-medium' : 'text-gray-600';
}

/**
 * Get online status text
 * @param {object} realTimeStatus - Real-time status object
 * @returns {string} - Status text
 */
export function getOnlineStatusText(realTimeStatus) {
  const isOnline = isUserActuallyOnline(realTimeStatus);
  return isOnline ? 'Online' : 'Offline';
}
