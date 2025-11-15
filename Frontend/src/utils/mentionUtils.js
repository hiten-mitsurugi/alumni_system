// mentionUtils.js
// Utility functions for handling mentions in text content

/**
 * Parse text content and convert @mentions to bold styled text
 * @param {string} content - The raw text content with @mentions
 * @returns {string} - HTML string with bold mentions
 */
export function parseMentions(content) {
  if (!content) return ''
  
  // Create a regex pattern that matches both:
  // 1. @[Full Name] format: "@John Doe", "@Mary Jane Smith" 
  // 2. @[username] format: "@prince.nino", "@john_doe", "@user123"
  // This handles: letters, numbers, dots, underscores, hyphens, and spaces in names
  const mentionRegex = /@[\w.-]+(?:\s+[\w.-]+)*(?=\s|$|[^\w\s.-])/g
  
  return content.replace(mentionRegex, (match) => {
    // Make the mention bold and add a slight blue color like Facebook
    return `<span class="mention-text font-bold text-blue-600 dark:text-blue-400">${match}</span>`
  })
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
 * @returns {string} - Content with @[Full Name] for display
 */
export function convertMentionsForDisplay(content, mentions = []) {
  let displayContent = content
  
  mentions.forEach(mention => {
    const usernameMention = `@${mention.username}`
    const fullNameMention = `@${mention.full_name}`
    displayContent = displayContent.replace(
      new RegExp(escapeRegExp(usernameMention), 'g'),
      fullNameMention
    )
  })
  
  return displayContent
}