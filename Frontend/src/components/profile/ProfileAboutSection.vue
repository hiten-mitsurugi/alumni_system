<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-bold text-gray-900">About</h2>
      <button 
        v-if="isOwnProfile" 
        @click="$emit('edit')"
        class="text-green-600 hover:text-green-700 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
        </svg>
      </button>
    </div>
    
    <div v-if="profile?.summary" class="prose prose-gray max-w-none">
      <div 
        :class="{ 'line-clamp-4': !showFullSummary && profile.summary.length > 200 }"
        class="text-gray-700 whitespace-pre-wrap"
      >
        {{ profile.summary }}
      </div>
      
      <button 
        v-if="profile.summary.length > 200"
        @click="showFullSummary = !showFullSummary"
        class="text-green-600 hover:text-green-700 mt-2 font-medium"
      >
        {{ showFullSummary ? 'See less' : 'See more' }}
      </button>
    </div>
    
    <div v-else-if="isOwnProfile" class="text-gray-500 text-center py-8">
      <p class="mb-3">Add a summary to help people understand your background and interests.</p>
      <button 
        @click="$emit('edit')"
        class="text-green-600 hover:text-green-700 font-medium"
      >
        Add About Section
      </button>
    </div>
    
    <div v-else class="text-gray-500 text-center py-4">
      <p>No about information available.</p>
    </div>

    <!-- Contact Information Grid -->
    <div v-if="hasContactInfo" class="mt-6 pt-6 border-t border-gray-200">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Contact Information</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- LinkedIn -->
        <div v-if="profile?.linkedin_url" class="flex items-center space-x-3">
          <div class="flex-shrink-0">
            <svg class="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
              <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
            </svg>
          </div>
          <a 
            :href="profile.linkedin_url" 
            target="_blank" 
            class="text-blue-600 hover:text-blue-700 font-medium"
          >
            LinkedIn Profile
          </a>
        </div>

        <!-- Website -->
        <div v-if="profile?.website_url" class="flex items-center space-x-3">
          <div class="flex-shrink-0">
            <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0-9v9m0 9c-5 0-9-4-9-9s4-9 9-9"></path>
            </svg>
          </div>
          <a 
            :href="profile.website_url" 
            target="_blank" 
            class="text-blue-600 hover:text-blue-700 font-medium"
          >
            Website
          </a>
        </div>

        <!-- Facebook -->
        <div v-if="profile?.facebook_url" class="flex items-center space-x-3">
          <div class="flex-shrink-0">
            <svg class="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
              <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
            </svg>
          </div>
          <a 
            :href="profile.facebook_url" 
            target="_blank" 
            class="text-blue-600 hover:text-blue-700 font-medium"
          >
            Facebook Profile
          </a>
        </div>

        <!-- Twitter -->
        <div v-if="profile?.twitter_url" class="flex items-center space-x-3">
          <div class="flex-shrink-0">
            <svg class="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
            </svg>
          </div>
          <a 
            :href="profile.twitter_url" 
            target="_blank" 
            class="text-blue-600 hover:text-blue-700 font-medium"
          >
            Twitter Profile
          </a>
        </div>

        <!-- Instagram -->
        <div v-if="profile?.instagram_url" class="flex items-center space-x-3">
          <div class="flex-shrink-0">
            <svg class="w-5 h-5 text-pink-600" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 6.624 5.367 11.99 11.988 11.99s11.987-5.366 11.987-11.99C24.004 5.367 18.641.001 12.017.001zM8.449 16.988c-2.509 0-4.544-2.036-4.544-4.544s2.035-4.544 4.544-4.544 4.544 2.036 4.544 4.544-2.035 4.544-4.544 4.544zm7.081 0c-2.509 0-4.544-2.036-4.544-4.544s2.035-4.544 4.544-4.544 4.544 2.036 4.544 4.544-2.035 4.544-4.544 4.544z"/>
            </svg>
          </div>
          <a 
            :href="profile.instagram_url" 
            target="_blank" 
            class="text-blue-600 hover:text-blue-700 font-medium"
          >
            Instagram Profile
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  profile: Object,
  isOwnProfile: Boolean
})

const emit = defineEmits(['edit'])

const showFullSummary = ref(false)

const hasContactInfo = computed(() => {
  return props.profile?.linkedin_url || 
         props.profile?.website_url || 
         props.profile?.facebook_url || 
         props.profile?.twitter_url || 
         props.profile?.instagram_url
})
</script>

<style scoped>
.line-clamp-4 {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
