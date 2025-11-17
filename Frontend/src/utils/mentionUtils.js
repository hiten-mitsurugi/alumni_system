// mentionUtils.js
// Utility functions for handling mentions in text content

/**
 * Parse text content and convert @mentions to bold styled text
 * Only highlights mentions that we're confident about
 * @param {string} content - The raw text content with @mentions
 * @returns {string} - HTML string with bold mentions
 */
export function parseMentions(content) {
  if (!content) return ''
  
  // Only highlight mentions that follow these strict patterns:
  // 1. Full names with proper capitalization: "@John Doe", "@Mary Jane Smith"
  // 2. Valid usernames: "@username", "@user.name", "@user_name" (lowercase/numbers/dots/underscores)
  
  // Pattern 1: Full names (2-4 capitalized words)
  // Matches: "@John Doe", "@Mary Jane Smith", "@Prince Nino Antigo"
  let result = content.replace(/@([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})(?=\s|$|[^\w])/g, (match) => {
    return `<span class="mention-text">${match}</span>`
  })
  
  // Pattern 2: Usernames (lowercase with dots, underscores, numbers)
  // Matches: "@prince.nino", "@john_doe", "@user123"
  // Excludes: random "@" symbols, "@", "@A" (single letters), already processed full names
  result = result.replace(/@([a-z][a-z0-9._-]*[a-z0-9])(?=\s|$|[^\w.-])/g, (match) => {
    // Don't process if it's already been highlighted as a full name
    if (result.includes(`<span class="mention-text">${match}</span>`)) {
      return match
    }
    return `<span class="mention-text">${match}</span>`
  })
  
  return result
}

/**
 * Extract mentions from text content for backend processing
 * @param {string} content - The text content
 * @param {Array} mentionedUsers - Array of user objects that were mentioned
 * @returns {Array} - Array of mention data for backend
 */
export function extractMentionsForBackend(content, mentionedUsers = []) {
  const mentions = []
  
  mentionedUsers.forEach(user => {
    const mentionPattern = `@${user.full_name}`
    if (content.includes(mentionPattern)) {
      mentions.push({
        user_id: user.id,
        username: user.username,
        full_name: user.full_name
      })
    }
  })
  
  return mentions
}

/**
 * Replace full name mentions with username mentions for backend storage
 * @param {string} content - Content with @[Full Name] mentions
 * @param {Array} mentionedUsers - Array of user objects
 * @returns {string} - Content with @username format for backend
 */
export function convertMentionsForStorage(content, mentionedUsers = []) {
  let convertedContent = content
  
  mentionedUsers.forEach(user => {
    const fullNameMention = `@${user.full_name}`
    const usernameMention = `@${user.username}`
    convertedContent = convertedContent.replace(
      new RegExp(escapeRegExp(fullNameMention), 'g'), 
      usernameMention
    )
  })
  
  return convertedContent
}

/**
 * Escape special regex characters in a string
 * @param {string} string - String to escape
 * @returns {string} - Escaped string
 */
function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

/**
 * Convert backend mentions (with usernames) back to full name display
 * @param {string} content - Content from backend with @username mentions
 * @param {Array} mentions - Mention data from backend with user info
 * @param {Object} availableUsers - Additional user data for conversion (optional)
 * @returns {string} - Content with @[Full Name] for display
 */
export function convertMentionsForDisplay(content, mentions = [], availableUsers = {}) {
  let displayContent = content
  
  // First, try to convert using the mentions array (if available)
  mentions.forEach(mention => {
    if (mention.username && mention.full_name) {
      const usernameMention = `@${mention.username}`
      const fullNameMention = `@${mention.full_name}`
      displayContent = displayContent.replace(
        new RegExp(escapeRegExp(usernameMention), 'g'),
        fullNameMention
      )
    }
  })
  
  // If we still have @username patterns, try to convert using available user data
  // This handles cases where mention data isn't properly stored in backend
  const remainingUsernamePattern = /@([\w.-]+)/g
  displayContent = displayContent.replace(remainingUsernamePattern, (match, username) => {
    // Check if we have user data for this username
    if (availableUsers[username]) {
      return `@${availableUsers[username].full_name || availableUsers[username].name || username}`
    }
    
    // If no user data available, keep the original username mention
    return match
  })
  
  return displayContent
}