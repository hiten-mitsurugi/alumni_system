<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-900">About</h2>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
      <span class="ml-3 text-gray-600">Loading profile data...</span>
    </div>

    <!-- Waiting for Props State -->
    <div v-else-if="!loading && !user && !props.user" class="flex items-center justify-center py-8">
      <div class="text-center">
        <div class="text-gray-400 mb-2">
          <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
          </svg>
        </div>
        <p class="text-gray-500">Waiting for profile data...</p>
      </div>
    </div>

    <!-- Profile Fields -->
    <div v-else class="space-y-6">
      <!-- Full Name Section - Featured -->
      <div class="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
        <div class="flex items-center mb-3">
          <div class="bg-blue-100 p-2 rounded-full mr-3">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
            </svg>
          </div>
          <span class="font-semibold text-blue-800">Full Name</span>
        </div>
        <div class="text-2xl font-bold text-gray-900 tracking-wide">
          {{ fullName }}
        </div>
        <div v-if="profileData?.headline" class="text-lg text-blue-700 mt-2 font-medium">
          {{ profileData.headline }}
        </div>
      </div>

      <!-- Personal Information -->
      <div class="bg-gray-50 rounded-lg p-6 border border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <div class="bg-green-100 p-2 rounded-full mr-3">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          Personal Information
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <InfoCard 
            v-if="user?.email" 
            icon="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
            label="Email Address" 
            :value="user.email" 
            iconColor="text-blue-600"
          />
          <InfoCard 
            v-if="user?.contact_number" 
            icon="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
            label="Contact Number" 
            :value="user.contact_number" 
            iconColor="text-green-600"
          />
          <InfoCard 
            v-if="user?.birth_date" 
            icon="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            label="Birth Date" 
            :value="formatDate(user.birth_date)" 
            iconColor="text-purple-600"
          />
          <InfoCard 
            v-if="user?.gender" 
            icon="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
            label="Gender" 
            :value="formatEnum(user.gender)" 
            iconColor="text-pink-600"
          />
          <InfoCard 
            v-if="user?.civil_status" 
            icon="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
            label="Civil Status" 
            :value="formatEnum(user.civil_status)" 
            iconColor="text-red-600"
          />
          <InfoCard 
            v-if="profileData?.location" 
            icon="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z M15 11a3 3 0 11-6 0 3 3 0 016 0z"
            label="Location" 
            :value="profileData.location" 
            iconColor="text-orange-600"
          />
        </div>
      </div>

      <!-- Academic Information -->
      <div v-if="user?.program || user?.year_graduated" class="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <div class="bg-purple-100 p-2 rounded-full mr-3">
            <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5z M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"></path>
            </svg>
          </div>
          Academic Background
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <InfoCard 
            v-if="user?.program" 
            icon="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
            label="Program" 
            :value="user.program" 
            iconColor="text-purple-600"
          />
          <InfoCard 
            v-if="user?.year_graduated" 
            icon="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"
            label="Year Graduated" 
            :value="`Class of ${user.year_graduated}`" 
            iconColor="text-indigo-600"
          />
        </div>
      </div>

      <!-- Professional Information -->
      <div v-if="hasWorkInfo" class="bg-gradient-to-r from-green-50 to-teal-50 border border-green-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <div class="bg-green-100 p-2 rounded-full mr-3">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H8a2 2 0 01-2-2V8a2 2 0 012-2V6"></path>
            </svg>
          </div>
          Professional Information
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <InfoCard 
            v-if="profileData?.present_occupation" 
            icon="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H8a2 2 0 01-2-2V8a2 2 0 012-2V6"
            label="Current Occupation" 
            :value="profileData.present_occupation" 
            iconColor="text-green-600"
          />
          <InfoCard 
            v-if="profileData?.employing_agency" 
            icon="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
            label="Employing Agency" 
            :value="profileData.employing_agency" 
            iconColor="text-blue-600"
          />
          <InfoCard 
            v-if="profileData?.present_employment_status" 
            icon="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
            label="Employment Status" 
            :value="formatEnum(profileData.present_employment_status)" 
            iconColor="text-teal-600"
          />
          <InfoCard 
            v-if="profileData?.employment_classification" 
            icon="M9 5H7a2 2 0 00-2 2v6a2 2 0 002 2h2m0 0h6m-6 0v1a2 2 0 01-2 2H5m14-8h-2m-1 5v1a2 2 0 01-2 2h-2m6-4V7a2 2 0 00-2-2h-2"
            label="Employment Classification" 
            :value="formatEnum(profileData.employment_classification)" 
            iconColor="text-indigo-600"
          />
        </div>
      </div>


      <!-- Address Information -->
      <div v-if="addresses.length > 0" class="bg-gradient-to-r from-teal-50 to-blue-50 border border-teal-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <div class="bg-teal-100 p-2 rounded-full mr-3">
            <svg class="w-5 h-5 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
          </div>
          Address Information
        </h3>
        <div class="space-y-4">
          <div v-for="address in addresses" :key="address.id" class="bg-white rounded-lg p-4 border border-gray-200">
            <div class="flex items-center mb-2">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-teal-100 text-teal-800 mr-2">
                {{ formatEnum(address.address_category) }} Address
              </span>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {{ formatEnum(address.address_type) }}
              </span>
            </div>
            <p class="text-gray-900 leading-relaxed">{{ address.formatted_address }}</p>
          </div>
        </div>
      </div>

      <!-- Social Media Links -->
      <div v-if="hasSocialLinks" class="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <div class="bg-indigo-100 p-2 rounded-full mr-3">
            <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
            </svg>
          </div>
          Social Media & Links
        </h3>
        <div class="flex flex-wrap gap-3">
          <SocialLink 
            v-if="profileData?.linkedin_url" 
            :url="profileData.linkedin_url" 
            platform="LinkedIn" 
            color="bg-blue-600 hover:bg-blue-700"
          />
          <SocialLink 
            v-if="profileData?.facebook_url" 
            :url="profileData.facebook_url" 
            platform="Facebook" 
            color="bg-blue-500 hover:bg-blue-600"
          />
          <SocialLink 
            v-if="profileData?.twitter_url" 
            :url="profileData.twitter_url" 
            platform="Twitter" 
            color="bg-sky-500 hover:bg-sky-600"
          />
          <SocialLink 
            v-if="profileData?.instagram_url" 
            :url="profileData.instagram_url" 
            platform="Instagram" 
            color="bg-pink-500 hover:bg-pink-600"
          />
          <SocialLink 
            v-if="profileData?.website_url" 
            :url="profileData.website_url" 
            platform="Website" 
            color="bg-gray-600 hover:bg-gray-700"
          />
        </div>
      </div>

      <!-- Bio/Summary Section -->
      <div v-if="profileData?.bio || profileData?.summary" class="bg-gradient-to-r from-gray-50 to-slate-50 border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <div class="bg-gray-100 p-2 rounded-full mr-3">
            <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
          </div>
          {{ profileData?.bio ? 'About Me' : 'Summary' }}
        </h3>
        <div class="prose prose-gray max-w-none">
          <p class="text-gray-900 leading-relaxed text-base">
            {{ profileData?.bio || profileData?.summary }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api'
import InfoCard from './InfoCard.vue'
import SocialLink from './SocialLink.vue'

const route = useRoute()
const loading = ref(true)
const user = ref(null)
const profileData = ref(null)
const addresses = ref([])

// Define props for when data is passed from parent
const props = defineProps({
  user: {
    type: Object,
    default: null
  },
  profile: {
    type: Object,
    default: null
  }
})

const fullName = computed(() => {
  const userData = user.value || props.user
  if (!userData) return 'Loading...'
  const parts = []
  if (userData.first_name) parts.push(userData.first_name)
  if (userData.middle_name) parts.push(userData.middle_name)
  if (userData.last_name) parts.push(userData.last_name)
  const name = parts.join(' ') || 'No name available'
  console.log('UserAboutSection: Computing full name:', { userData, name })
  return name
})

const hasWorkInfo = computed(() => {
  const profile = profileData.value || props.profile
  return profile && (
    profile.present_occupation ||
    profile.employing_agency ||
    profile.present_employment_status ||
    profile.employment_classification
  )
})

const hasFamilyInfo = computed(() => {
  const userData = user.value || props.user
  return userData && (
    userData.mothers_name ||
    userData.mothers_occupation ||
    userData.fathers_name ||
    userData.fathers_occupation
  )
})

const hasSocialLinks = computed(() => {
  const profile = profileData.value || props.profile
  return profile && (
    profile.linkedin_url ||
    profile.facebook_url ||
    profile.twitter_url ||
    profile.instagram_url ||
    profile.website_url
  )
})

// Utility functions for formatting
const formatEnum = (value) => {
  if (!value) return ''
  return value.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  } catch {
    return dateString
  }
}

// API functions removed since component now works entirely with props data
// These can be re-added later when proper backend endpoints are implemented

const formatAddress = (address) => {
  const parts = []
  
  if (address.address_type === 'philippines') {
    // Philippine address format
    if (address.street_address) parts.push(address.street_address)
    if (address.barangay) parts.push(`Brgy. ${address.barangay}`)
    if (address.city_municipality) parts.push(address.city_municipality)
    if (address.province) parts.push(address.province)
    if (address.region) parts.push(address.region)
    if (address.postal_code) parts.push(address.postal_code)
  } else {
    // International address format
    if (address.street_address) parts.push(address.street_address)
    if (address.city) parts.push(address.city)
    if (address.state_province) parts.push(address.state_province)
    if (address.country) parts.push(address.country)
    if (address.postal_code) parts.push(address.postal_code)
  }
  
  return parts.filter(Boolean).join(', ')
}

onMounted(async () => {
  // Debug: Log what props we're receiving
  console.log('UserAboutSection onMounted - Props received:', {
    user: props.user,
    profile: props.profile,
    hasUser: !!props.user,
    hasProfile: !!props.profile
  })
  
  // Since this component is designed to work with props from UserProfile.vue,
  // we just set loading to false and let the watcher handle data updates
  // when props are provided by the parent component
  loading.value = false
  
  // If props are already available on mount, use them
  if (props.user && props.profile) {
    user.value = props.user
    profileData.value = props.profile
    
    console.log('UserAboutSection: Setting data from props', {
      userName: props.user.first_name + ' ' + props.user.last_name,
      userFields: Object.keys(props.user),
      profileFields: Object.keys(props.profile)
    })
    
    // For now, addresses are not available through the current API
    // This could be enhanced later when address endpoints are implemented
    addresses.value = []
  } else {
    console.log('UserAboutSection: No props data available on mount, waiting for watcher...')
  }
})

// Watch for prop changes
watch([() => props.user, () => props.profile], ([newUser, newProfile]) => {
  console.log('UserAboutSection watcher triggered:', {
    newUser: !!newUser,
    newProfile: !!newProfile,
    userFields: newUser ? Object.keys(newUser) : [],
    profileFields: newProfile ? Object.keys(newProfile) : []
  })
  
  if (newUser && newProfile) {
    user.value = newUser
    profileData.value = newProfile
    
    // For now, addresses are not available through the current API
    // This could be enhanced later when address endpoints are implemented
    addresses.value = []
    
    console.log('UserAboutSection: Updated with props data', { 
      userName: (newUser.first_name || '') + ' ' + (newUser.last_name || ''),
      email: newUser.email,
      hasProfile: !!newProfile,
      profileBio: newProfile.bio
    })
  } else {
    console.log('UserAboutSection: Props are null/undefined')
  }
}, { deep: true })
</script>