/**
 * Utilities for parsing and formatting @mentions in messages
 */

/**
 * Parse @mentions from text content
 * @param {string} content - The message content
 * @returns {Array} Array of mention objects with position and username
 */
export function parseMentions(content) {
  // Updated regex to handle FirstName_LastName format (allowing underscores and longer names)
  const mentionRegex = /@([a-zA-Z0-9._-]+(?:_[a-zA-Z0-9._-]+)*)/g
  const mentions = []
  let match
  
  while ((match = mentionRegex.exec(content)) !== null) {
    mentions.push({
      username: match[1], // This will be FirstName_LastName or regular username
      start: match.index,
      end: match.index + match[0].length,
      fullMatch: match[0]
    })
  }
  
  return mentions
}

/**
 * Replace @mentions in content with formatted HTML
 * @param {string} content - The message content
 * @param {Array} groupMembers - Array of group members to validate mentions against
 * @returns {string} HTML content with styled mentions
 */
export function formatMentionsToHtml(content, groupMembers = []) {
  const mentions = parseMentions(content)
  if (mentions.length === 0) return content
  
  // Create maps for both username and FirstName_LastName format lookup
  const memberMap = {}
  groupMembers.forEach(member => {
    // Support both formats: username and FirstName_LastName
    memberMap[member.username.toLowerCase()] = member
    const fullNameKey = `${member.first_name}_${member.last_name}`.toLowerCase()
    memberMap[fullNameKey] = member
  })
  
  let formattedContent = content
  let offset = 0
  
  mentions.forEach(mention => {
    const member = memberMap[mention.username.toLowerCase()]
    if (member) {
      // Create a styled mention span
      const mentionSpan = `<span class="mention" data-user-id="${member.id}" data-username="${member.username}" data-full-name="${member.first_name} ${member.last_name}">${mention.fullMatch}</span>`
      
      // Replace the mention in the content
      const start = mention.start + offset
      const end = mention.end + offset
      
      formattedContent = formattedContent.substring(0, start) + 
                       mentionSpan + 
                       formattedContent.substring(end)
      
      // Update offset for next replacements
      offset += mentionSpan.length - mention.fullMatch.length
    }
  })
  
  return formattedContent
}

/**
 * Extract mentioned user IDs from content
 * @param {string} content - The message content
 * @param {Array} groupMembers - Array of group members to validate mentions against
 * @returns {Array} Array of user IDs that were mentioned
 */
export function extractMentionedUserIds(content, groupMembers = []) {
  const mentions = parseMentions(content)
  if (mentions.length === 0) return []
  
  // Create maps for both username and FirstName_LastName format lookup
  const memberMap = {}
  groupMembers.forEach(member => {
    // Support both formats: username and FirstName_LastName
    memberMap[member.username.toLowerCase()] = member
    const fullNameKey = `${member.first_name}_${member.last_name}`.toLowerCase()
    memberMap[fullNameKey] = member
  })
  
  const mentionedUserIds = []
  mentions.forEach(mention => {
    const member = memberMap[mention.username.toLowerCase()]
    if (member && !mentionedUserIds.includes(member.id)) {
      mentionedUserIds.push(member.id)
    }
  })
  
  return mentionedUserIds
}

/**
 * Insert mention at cursor position in a textarea
 * @param {HTMLTextAreaElement} textarea - The textarea element
 * @param {Object} member - The member object to mention
 * @param {string} queryToReplace - The query text to replace (including @)
 * @returns {string} The new content with the mention inserted
 */
export function insertMentionInTextarea(textarea, member, queryToReplace = '') {
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const currentContent = textarea.value
  
  // Find the start of the query to replace
  let replaceStart = start
  if (queryToReplace) {
    replaceStart = start - queryToReplace.length
  }
  
  // Create the mention text using first_name and last_name
  // Format: @FirstName_LastName (underscore separated to avoid space issues)
  const mentionText = `@${member.first_name}_${member.last_name}`
  
  // Replace the query with the mention
  const newContent = currentContent.substring(0, replaceStart) + 
                    mentionText + ' ' + 
                    currentContent.substring(end)
  
  // Set the new content
  textarea.value = newContent
  
  // Position cursor after the mention and space
  const newCursorPos = replaceStart + mentionText.length + 1
  textarea.setSelectionRange(newCursorPos, newCursorPos)
  
  return newContent
}

/**
 * Detect @mention typing in real-time
 * @param {string} content - Current textarea content
 * @param {number} cursorPosition - Current cursor position
 * @returns {Object|null} Object with query and position info, or null if no mention being typed
 */
export function detectMentionTyping(content, cursorPosition) {
  // Look backwards from cursor to find @ symbol
  let searchStart = cursorPosition - 1
  let mentionStart = -1
  
  // Find the @ symbol, but stop at whitespace or beginning
  while (searchStart >= 0) {
    const char = content[searchStart]
    if (char === '@') {
      mentionStart = searchStart
      break
    } else if (char === ' ' || char === '\n' || char === '\t') {
      // Found whitespace before @, so not a mention
      break
    }
    searchStart--
  }
  
  if (mentionStart === -1) return null
  
  // Extract the query from @ to cursor
  const query = content.substring(mentionStart + 1, cursorPosition)
  
  // Only consider it a mention if:
  // 1. @ is at start or preceded by whitespace
  // 2. Query contains only valid characters (including underscore for FirstName_LastName)
  // 3. Query is reasonable length
  const isValidMention = (mentionStart === 0 || /\s/.test(content[mentionStart - 1])) &&
                        /^[a-zA-Z0-9._-]*$/.test(query) &&
                        query.length <= 50 // Increased length to accommodate full names
  
  if (!isValidMention) return null
  
  return {
    query,
    start: mentionStart,
    end: cursorPosition,
    fullQuery: '@' + query
  }
}

/**
 * Highlight mentions in display text (for MessageBubble)
 * @param {string} content - The message content
 * @param {Array} groupMembers - Array of group members for validation
 * @returns {string} Content with mentions wrapped in spans for styling
 */
export function highlightMentions(content, groupMembers = []) {
  const mentions = parseMentions(content)
  if (mentions.length === 0) return content
  
  // Create maps for both username and FirstName_LastName format lookup
  const memberMap = {}
  groupMembers.forEach(member => {
    // Support both formats: username and FirstName_LastName
    memberMap[member.username.toLowerCase()] = member
    const fullNameKey = `${member.first_name}_${member.last_name}`.toLowerCase()
    memberMap[fullNameKey] = member
  })
  
  let highlightedContent = content
  let offset = 0
  
  mentions.forEach(mention => {
    const member = memberMap[mention.username.toLowerCase()]
    if (member) {
      // Create a clickable mention span with full name in tooltip
      const mentionSpan = `<span class="mention-highlight cursor-pointer" data-user-id="${member.id}" data-username="${member.username}" title="${member.first_name} ${member.last_name}">${mention.fullMatch}</span>`
      
      const start = mention.start + offset
      const end = mention.end + offset
      
      highlightedContent = highlightedContent.substring(0, start) + 
                          mentionSpan + 
                          highlightedContent.substring(end)
      
      offset += mentionSpan.length - mention.fullMatch.length
    }
  })
  
  return highlightedContent
}
