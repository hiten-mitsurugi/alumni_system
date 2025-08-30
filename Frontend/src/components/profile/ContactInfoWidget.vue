<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">Contact Info</h3>
    
    <div class="space-y-4">
      <!-- Email -->
      <div v-if="user?.email" class="flex items-center space-x-3">
        <div class="flex-shrink-0">
          <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 7.89a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
          </svg>
        </div>
        <div>
          <p class="text-sm font-medium text-gray-900">Email</p>
          <a 
            :href="`mailto:${user.email}`"
            class="text-sm text-blue-600 hover:text-blue-700"
          >
            {{ user.email }}
          </a>
        </div>
      </div>

      <!-- Phone -->
      <div v-if="profile?.phone_number" class="flex items-center space-x-3">
        <div class="flex-shrink-0">
          <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
          </svg>
        </div>
        <div>
          <p class="text-sm font-medium text-gray-900">Phone</p>
          <a 
            :href="`tel:${profile.phone_number}`"
            class="text-sm text-blue-600 hover:text-blue-700"
          >
            {{ profile.phone_number }}
          </a>
        </div>
      </div>

      <!-- Birthday -->
      <div v-if="profile?.birth_date" class="flex items-center space-x-3">
        <div class="flex-shrink-0">
          <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
          </svg>
        </div>
        <div>
          <p class="text-sm font-medium text-gray-900">Birthday</p>
          <p class="text-sm text-gray-600">
            {{ formatBirthday(profile.birth_date) }}
          </p>
        </div>
      </div>

      <!-- Address -->
      <div v-if="profile?.present_address" class="flex items-center space-x-3">
        <div class="flex-shrink-0">
          <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
          </svg>
        </div>
        <div>
          <p class="text-sm font-medium text-gray-900">Address</p>
          <p class="text-sm text-gray-600">
            {{ profile.present_address }}
          </p>
        </div>
      </div>

      <!-- Graduation Year -->
      <div v-if="profile?.graduation_year" class="flex items-center space-x-3">
        <div class="flex-shrink-0">
          <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"></path>
          </svg>
        </div>
        <div>
          <p class="text-sm font-medium text-gray-900">Graduation Year</p>
          <p class="text-sm text-gray-600">
            {{ profile.graduation_year }}
          </p>
        </div>
      </div>

      <!-- Program -->
      <div v-if="profile?.program_graduated" class="flex items-center space-x-3">
        <div class="flex-shrink-0">
          <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
          </svg>
        </div>
        <div>
          <p class="text-sm font-medium text-gray-900">Program</p>
          <p class="text-sm text-gray-600">
            {{ formatProgram(profile.program_graduated) }}
          </p>
        </div>
      </div>

      <!-- Current Occupation -->
      <div v-if="profile?.present_occupation" class="flex items-center space-x-3">
        <div class="flex-shrink-0">
          <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V8a2 2 0 012-2V6"></path>
          </svg>
        </div>
        <div>
          <p class="text-sm font-medium text-gray-900">Current Role</p>
          <p class="text-sm text-gray-600">
            {{ profile.present_occupation }}
          </p>
        </div>
      </div>

      <!-- Company -->
      <div v-if="profile?.present_employer" class="flex items-center space-x-3">
        <div class="flex-shrink-0">
          <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
          </svg>
        </div>
        <div>
          <p class="text-sm font-medium text-gray-900">Company</p>
          <p class="text-sm text-gray-600">
            {{ profile.present_employer }}
          </p>
        </div>
      </div>
    </div>

    <!-- Social Links (if any) -->
    <div v-if="hasSocialLinks" class="mt-6 pt-4 border-t border-gray-200">
      <h4 class="text-sm font-medium text-gray-900 mb-3">Social Media</h4>
      <div class="flex space-x-3">
        <!-- LinkedIn -->
        <a 
          v-if="profile?.linkedin_url" 
          :href="profile.linkedin_url" 
          target="_blank"
          class="text-blue-600 hover:text-blue-700 transition-colors"
        >
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
          </svg>
        </a>

        <!-- Facebook -->
        <a 
          v-if="profile?.facebook_url" 
          :href="profile.facebook_url" 
          target="_blank"
          class="text-blue-600 hover:text-blue-700 transition-colors"
        >
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
          </svg>
        </a>

        <!-- Twitter -->
        <a 
          v-if="profile?.twitter_url" 
          :href="profile.twitter_url" 
          target="_blank"
          class="text-blue-400 hover:text-blue-500 transition-colors"
        >
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
          </svg>
        </a>

        <!-- Instagram -->
        <a 
          v-if="profile?.instagram_url" 
          :href="profile.instagram_url" 
          target="_blank"
          class="text-pink-600 hover:text-pink-700 transition-colors"
        >
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 6.624 5.367 11.99 11.988 11.99s11.987-5.366 11.987-11.99C24.004 5.367 18.641.001 12.017.001zM8.449 16.988c-2.509 0-4.544-2.036-4.544-4.544s2.035-4.544 4.544-4.544 4.544 2.036 4.544 4.544-2.035 4.544-4.544 4.544zm7.081 0c-2.509 0-4.544-2.036-4.544-4.544s2.035-4.544 4.544-4.544 4.544 2.036 4.544 4.544-2.035 4.544-4.544 4.544z"/>
          </svg>
        </a>

        <!-- Website -->
        <a 
          v-if="profile?.website_url" 
          :href="profile.website_url" 
          target="_blank"
          class="text-gray-600 hover:text-gray-700 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0-9v9m0 9c-5 0-9-4-9-9s4-9 9-9"></path>
          </svg>
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  profile: Object,
  user: Object
})

const formatBirthday = (date) => {
  return new Date(date).toLocaleDateString('en-US', { 
    month: 'long', 
    day: 'numeric' 
  })
}

const formatProgram = (program) => {
  const programMap = {
    'BSIT': 'Bachelor of Science in Information Technology',
    'BSCS': 'Bachelor of Science in Computer Science',
    'BSIS': 'Bachelor of Science in Information Systems',
    'BSECE': 'Bachelor of Science in Electronics and Communications Engineering',
    'BSEE': 'Bachelor of Science in Electrical Engineering',
    'BSME': 'Bachelor of Science in Mechanical Engineering',
    'BSCE': 'Bachelor of Science in Civil Engineering',
    'BSIE': 'Bachelor of Science in Industrial Engineering',
    'BSBA': 'Bachelor of Science in Business Administration',
    'AB': 'Bachelor of Arts',
    'BSA': 'Bachelor of Science in Accountancy',
    'BSED': 'Bachelor of Science in Education',
    'BEED': 'Bachelor of Elementary Education',
    'BSN': 'Bachelor of Science in Nursing',
    'BSPSYCH': 'Bachelor of Science in Psychology'
  }
  return programMap[program] || program
}

const hasSocialLinks = computed(() => {
  return props.profile?.linkedin_url || 
         props.profile?.facebook_url || 
         props.profile?.twitter_url || 
         props.profile?.instagram_url || 
         props.profile?.website_url
})
</script>
