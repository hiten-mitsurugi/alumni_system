/**
 * Test the mention display conversion functionality
 */

// Test the convertMentionsForDisplay function directly
import { convertMentionsForDisplay } from '../Frontend/src/utils/mentionUtils.js'

// Mock test data
const testContent = "Hey @prince.antigo, how are you doing? Also @john.doe should see this!"

const testAvailableUsers = {
  'prince.antigo': {
    full_name: 'Prince Nino Antigo',
    name: 'Prince Nino Antigo'
  },
  'john.doe': {
    full_name: 'John Doe',
    name: 'John Doe'
  }
}

// Test conversion
console.log("🧪 Testing Mention Display Conversion:")
console.log("Original content:", testContent)
console.log("Available users:", testAvailableUsers)

const convertedContent = convertMentionsForDisplay(testContent, [], testAvailableUsers)
console.log("Converted content:", convertedContent)

console.log("\n✅ Expected: Hey @Prince Nino Antigo, how are you doing? Also @John Doe should see this!")
console.log("✅ Result matches:", convertedContent === "Hey @Prince Nino Antigo, how are you doing? Also @John Doe should see this!")

// Test with empty available users (should keep original)
const noConversion = convertMentionsForDisplay(testContent, [], {})
console.log("\n🔄 Test with no available users:")
console.log("Result:", noConversion)
console.log("✅ Should keep original:", noConversion === testContent)