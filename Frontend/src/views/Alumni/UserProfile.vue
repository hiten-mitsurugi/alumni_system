<template>
  <div :class="[
    'min-h-screen transition-colors duration-200',
    themeStore.isDarkMode ? 'bg-gray-900' : 'bg-white'
  ]">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center h-64">
      <div class="w-12 h-12 border-b-2 border-green-600 rounded-full animate-spin"></div>
    </div>

    <!-- Main Profile Content -->
    <div v-else class="max-w-6xl p-4 mx-auto">
      <!-- Profile Header Section -->
      <div :class="[
        'rounded-lg shadow-lg overflow-hidden mb-6 transition-colors duration-200',
        themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white'
      ]">
        <!-- Cover Photo -->
        <div class="relative h-48 bg-gradient-to-r from-green-400 to-blue-500">
          <img
            v-if="coverPhotoUrl"
            :src="coverPhotoUrl"
            alt="Cover Photo"
            class="object-cover w-full h-full"
          />
        </div>

        <!-- Profile Info -->
        <div class="relative px-6 pb-6">
          <!-- Profile Picture -->
          <div class="absolute -top-16 left-6">
            <div class="relative">
              <img
                :src="profilePictureUrl"
                alt="Profile Picture"
                :class="[
                  'w-32 h-32 rounded-full border-4 shadow-lg object-cover',
                  themeStore.isDarkMode ? 'border-gray-800' : 'border-white'
                ]"
              />
            </div>
          </div>

          <!-- Name and Basic Info -->
          <div class="pt-20">
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between">
              <div>
                <h1 :class="[
                  'text-3xl font-bold',
                  themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                ]">
                  {{ user?.first_name }} {{ user?.middle_name }} {{ user?.last_name }}
                </h1>
                <p :class="[
                  'text-lg mt-1',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">
                  {{ displayHeadline }}
                </p>

                <!-- Education Info -->
                <div v-if="displayEducationInfo" :class="[
                  'flex items-center mt-2',
                  themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
                ]">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                  </svg>
                  {{ displayEducationInfo }}
                </div>

                <!-- Location -->
                <div :class="[
                  'flex items-center mt-2',
                  themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
                ]">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  </svg>
                  {{ profile?.location || profile?.present_address || 'Location not specified' }}
                </div>

                <!-- Connections -->
                <div :class="[
                  'flex items-center mt-1',
                  themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'
                ]">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                  </svg>
                  {{ connections }} connections
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="flex mt-4 space-x-3 lg:mt-0">
                <button
                  @click="connectUser"
                  :disabled="isConnecting"
                  :class="[
                    'px-6 py-2 rounded-lg font-medium transition-colors',
                    isFollowing
                      ? themeStore.isDarkMode
                        ? 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      : 'bg-orange-500 text-white hover:bg-orange-600'
                  ]"
                >
                  <span v-if="isConnecting" class="mr-2 animate-spin">⟳</span>
                  {{ isFollowing ? 'Following' : 'Connect' }}
                </button>
                <button
                  @click="sendMessage"
                  class="px-6 py-2 font-medium text-white transition-colors bg-orange-600 rounded-lg hover:bg-orange-700"
                >
                  Message
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab Navigation -->
      <div :class="[
        'border-b shadow-sm transition-colors duration-200',
        themeStore.isDarkMode
          ? 'bg-gray-800 border-gray-700'
          : 'bg-white border-gray-200'
      ]">
        <div class="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
          <nav class="flex space-x-8">
            <button
              @click="activeTab = 'about'"
              :class="[
                'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                activeTab === 'about'
                  ? 'border-orange-500 ' + (themeStore.isDarkMode ? 'text-orange-400' : 'text-orange-600')
                  : 'border-transparent ' + (themeStore.isDarkMode
                      ? 'text-gray-400 hover:text-gray-200 hover:border-gray-600'
                      : 'text-gray-500 hover:text-gray-700 hover:border-gray-300')
              ]"
            >
              About
            </button>
            <button
              @click="activeTab = 'posts'"
              :class="[
                'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                activeTab === 'posts'
                  ? 'border-orange-500 ' + (themeStore.isDarkMode ? 'text-orange-400' : 'text-orange-600')
                  : 'border-transparent ' + (themeStore.isDarkMode
                      ? 'text-gray-400 hover:text-gray-200 hover:border-gray-600'
                      : 'text-gray-500 hover:text-gray-700 hover:border-gray-300')
              ]"
            >
              Posts
            </button>
          </nav>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <!-- Left Column - Profile Sections -->
        <div class="space-y-6 lg:col-span-2">

          <!-- About Tab Content -->
          <div v-show="activeTab === 'about'" class="space-y-6">
            <!-- Empty Profile Privacy Notice -->
            <div 
              v-if="isProfileFilteredByPrivacy" 
              :class="[
                'rounded-lg p-8 text-center',
                themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white shadow-md'
              ]"
            >
              <div class="mx-auto w-16 h-16 mb-4">
                <svg 
                  class="w-full h-full text-gray-400" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    stroke-linecap="round" 
                    stroke-linejoin="round" 
                    stroke-width="2" 
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                  />
                </svg>
              </div>
              <h3 :class="[
                'text-xl font-semibold mb-2',
                themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
              ]">
                Profile Information Not Available
              </h3>
              <p :class="[
                'mb-4',
                themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
              ]">
                <template v-if="!isFollowing">
                  Connect with {{ user?.first_name }} to view their profile information.
                </template>
                <template v-else>
                  {{ user?.first_name }} hasn't added profile information yet, or their privacy settings restrict visibility.
                </template>
              </p>
              <button
                v-if="!isFollowing"
                @click="connectUser"
                :disabled="isConnecting"
                :class="[
                  'px-6 py-2 rounded-lg font-medium transition-colors',
                  isConnecting
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-orange-600 hover:bg-orange-700 text-white'
                ]"
              >
                {{ isConnecting ? 'Sending Request...' : 'Send Connection Request' }}
              </button>
            </div>

            <!-- About Section -->
            <ProfileAboutSection
              :profile="profile"
              :is-own-profile="false"
              :user-id="user?.id"
              @profile-updated="fetchUserProfile"
            />

            <!-- Contact Information Section -->
            <ProfileContactSection
              :profile="profile"
              :is-own-profile="false"
              :user-id="user?.id"
              @profile-updated="fetchUserProfile"
            />

            <!-- Education Section -->
            <ProfileEducationSection
              :education="education"
              :profile="profile"
              :user="user"
              :is-own-profile="false"
              @add="() => {}"
              @edit="() => {}"
              @edit-profile="() => {}"
              @delete="() => {}"
            />

            <!-- Work History Section -->
            <ProfileExperienceSection
              :workHistories="workHistories"
              :is-own-profile="false"
              @add="() => {}"
              @edit="() => {}"
              @delete="() => {}"
            />

            <!-- Skills Section -->
            <ProfileSkillsSection
              :skills="skills"
              :is-own-profile="false"
              @add="() => {}"
              @edit="() => {}"
              @delete="() => {}"
            />

            <!-- Achievements Section -->
            <ProfileAchievementsSection
              :achievements="achievements"
              :is-own-profile="false"
              @add="() => {}"
              @edit="() => {}"
              @delete="() => {}"
            />

            <!-- Memberships Section -->
            <ProfileMembershipsSection
              :memberships="memberships"
              :is-own-profile="false"
              @add="() => {}"
              @edit="() => {}"
              @delete="() => {}"
              @visibility-changed="() => {}"
            />

            <!-- Non-Academic Recognitions Section -->
            <ProfileRecognitionsSection
              :recognitions="recognitions"
              :is-own-profile="false"
              @add="() => {}"
              @edit="() => {}"
              @delete="() => {}"
              @visibility-changed="() => {}"
            />

            <!-- Trainings Section -->
            <ProfileTrainingsSection
              :trainings="trainings"
              :is-own-profile="false"
              @add="() => {}"
              @edit="() => {}"
              @delete="() => {}"
              @visibility-changed="() => {}"
            />

            <!-- Publications Section -->
            <ProfilePublicationsSection
              :publications="publications"
              :is-own-profile="false"
              @add="() => {}"
              @edit="() => {}"
              @delete="() => {}"
              @visibility-changed="() => {}"
            />

            <!-- Career Enhancement Section -->
            <ProfileCareerEnhancementSection
              :career-enhancement="careerEnhancement"
              :is-own-profile="false"
              @add="() => {}"
              @edit-certificate="() => {}"
              @delete-certificate="() => {}"
              @edit-cse="() => {}"
              @visibility-changed="() => {}"
            />
          </div>

          <!-- Posts Tab Content -->
          <div v-show="activeTab === 'posts'">
            <PostsTab :user-id="user?.id" />
          </div>

        </div>

        <!-- Right Column - Sidebar -->
        <div class="space-y-6">
          <!-- People You May Know -->
          <SuggestedConnectionsWidget @connect="handleConnect" />

          <!-- Recent Activity Widget (optional for user profile) -->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import api from '@/services/api'
import { getProfilePictureUrl, getCoverPhotoUrl } from '@/utils/imageUrl'

// Components
import ProfileAboutSection from '@/components/profile/ProfileAboutSection.vue'
import ProfileContactSection from '@/components/profile/ProfileContactSection.vue'
import ProfileEducationSection from '@/components/profile/ProfileEducationSection.vue'
import ProfileExperienceSection from '@/components/profile/ProfileExperienceSection.vue'
import ProfileSkillsSection from '@/components/profile/ProfileSkillsSection.vue'
import ProfileAchievementsSection from '@/components/profile/ProfileAchievementsSection.vue'
import ProfileMembershipsSection from '@/components/profile/ProfileMembershipsSection.vue'
import ProfileRecognitionsSection from '@/components/profile/ProfileRecognitionsSection.vue'
import ProfileTrainingsSection from '@/components/profile/ProfileTrainingsSection.vue'
import ProfilePublicationsSection from '@/components/profile/ProfilePublicationsSection.vue'
import ProfileCareerEnhancementSection from '@/components/profile/ProfileCareerEnhancementSection.vue'
import SuggestedConnectionsWidget from '@/components/profile/SuggestedConnectionsWidget.vue'
import PostsTab from '@/components/profile/tabs/PostsTab.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

// State
const loading = ref(true)
const user = ref(null)
const profile = ref(null)
const education = ref([])
const workHistories = ref([])
const skills = ref([])
const achievements = ref([])
const memberships = ref([])
const recognitions = ref([])
const trainings = ref([])
const publications = ref([])
const careerEnhancement = ref({})
const connections = ref(0)
const isFollowing = ref(false)
const isConnecting = ref(false)

// Tab state
const activeTab = ref('about')

// Get user identifier from route
const userIdentifier = computed(() => route.params.userIdentifier)

// Computed properties to derive profile info (like MyProfile)
const currentEducation = computed(() => {
  if (!education.value || education.value.length === 0) return null

  // Find current education (is_current = true) or most recent one
  const current = education.value.find(edu => edu.is_current)
  if (current) return current

  // If no current, get the most recent one by end_date or start_date
  const sorted = [...education.value].sort((a, b) => {
    const dateA = new Date(a.end_date || a.start_date || '1900-01-01')
    const dateB = new Date(b.end_date || b.start_date || '1900-01-01')
    return dateB - dateA
  })

  return sorted[0]
})

const currentJob = computed(() => {
  if (!workHistories.value || workHistories.value.length === 0) return null

  // Find current job (job_type = 'current_job') or most recent one
  const current = workHistories.value.find(work => work.job_type === 'current_job')
  if (current) return current

  // If no current job, get the most recent one by end_date or start_date
  const sorted = [...workHistories.value].sort((a, b) => {
    const dateA = new Date(a.end_date || a.start_date || '1900-01-01')
    const dateB = new Date(b.end_date || b.start_date || '1900-01-01')
    return dateB - dateA
  })

  return sorted[0]
})

// Profile picture URL with fallback
const profilePictureUrl = computed(() => {
  return getProfilePictureUrl(user.value?.profile_picture)
})

// Cover photo URL with fallback
const coverPhotoUrl = computed(() => {
  return getCoverPhotoUrl(profile.value?.cover_photo)
})

// Compute total visible items to detect empty profile
const totalVisibleItems = computed(() => {
  return (
    education.value.length +
    workHistories.value.length +
    skills.value.length +
    achievements.value.length +
    memberships.value.length +
    recognitions.value.length +
    trainings.value.length +
    publications.value.length +
    (careerEnhancement.value.certificates?.length || 0)
  )
})

// Check if profile appears empty due to privacy
const isProfileFilteredByPrivacy = computed(() => {
  return totalVisibleItems.value === 0 && !loading.value && user.value
})

const displayHeadline = computed(() => {
  // Priority: Profile headline > Current job title > Current education > Default
  if (profile.value?.headline) {
    return profile.value.headline
  }

  if (currentJob.value) {
    return `${currentJob.value.occupation} at ${currentJob.value.employing_agency}`
  }

  if (currentEducation.value) {
    const degree = currentEducation.value.degree_type?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Student'
    const field = currentEducation.value.field_of_study ? ` in ${currentEducation.value.field_of_study}` : ''
    return `${degree}${field}`
  }

  return 'Alumni'
})

const displayEducationInfo = computed(() => {
  if (currentEducation.value) {
    const degree = currentEducation.value.degree_type?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || ''
    const field = currentEducation.value.field_of_study || ''
    const institution = currentEducation.value.institution || ''

    if (degree && field && institution) {
      return `${degree} in ${field} from ${institution}`
    } else if (degree && institution) {
      return `${degree} from ${institution}`
    } else if (institution) {
      return institution
    }
  }

  // Fallback to user basic info if available
  if (user.value?.program && user.value?.year_graduated) {
    return `${user.value.program} (Class of ${user.value.year_graduated})`
  }

  return null
})

// Add refresh function for privacy changes
const refreshProfileData = async () => {
  console.log('🔄 Refreshing UserProfile data...')
  await fetchUserProfile()
}

// Expose refresh function globally for debugging
window.refreshUserProfile = refreshProfileData

// Privacy filtering function
const applyPrivacyFiltering = async (data) => {
  try {
    // Get current user info
    const currentUserResponse = await api.get('/auth/user/')
    const currentUser = currentUserResponse.data
    
    console.log('🔐 Privacy filtering - Current user:', currentUser.id, 'Viewing user:', data.id)
    console.log('🔐 Connection status (isFollowing):', isFollowing.value)
    console.log('🔐 Raw data from backend:', {
      education: data.education?.length || 0,
      work_histories: data.work_histories?.length || 0,
      achievements: data.achievements?.length || 0,
      memberships: data.memberships?.length || 0,
      recognitions: data.recognitions?.length || 0,
      trainings: data.trainings?.length || 0,
      publications: data.publications?.length || 0,
      certificates: data.certificates?.length || 0,
      user_skills: data.user_skills?.length || 0
    })
    
    // If viewing own profile, use all backend data directly
    if (currentUser.id === data.id) {
      console.log('🔓 Own profile - using all backend data without filtering')
      education.value = data.education || []
      workHistories.value = data.work_histories || []
      achievements.value = data.achievements || []
      memberships.value = data.memberships || []
      recognitions.value = data.recognitions || []
      trainings.value = data.trainings || []
      publications.value = data.publications || []
      careerEnhancement.value = {
        certificates: data.certificates || [],
        cseStatus: data.cse_status || null
      }
      console.log('✅ Own profile data loaded:', {
        education: education.value.length,
        workHistories: workHistories.value.length,
        achievements: achievements.value.length
      })
      return
    }
    
    // For other users: Backend EnhancedUserDetailSerializer already applies privacy filtering
    // Trust the backend filtering and use the data as-is
    console.log('🔒 Other user profile - using backend-filtered data')
    
    education.value = data.education || []
    workHistories.value = data.work_histories || []
    achievements.value = data.achievements || []
    memberships.value = data.memberships || []
    recognitions.value = data.recognitions || []
    trainings.value = data.trainings || []
    publications.value = data.publications || []
    
    
    // Career enhancement data - map backend fields to expected structure (same as MyProfile)
    careerEnhancement.value = {
      certificates: data.certificates || [],
      cseStatus: data.cse_status || null
    }
    
    console.log('✅ Backend-filtered data applied:', {
      education: education.value.length,
      workHistories: workHistories.value.length,
      achievements: achievements.value.length,
      memberships: memberships.value.length,
      recognitions: recognitions.value.length,
      trainings: trainings.value.length,
      publications: publications.value.length,
      certificates: careerEnhancement.value.certificates.length,
      cseStatus: careerEnhancement.value.cseStatus ? 'Yes' : 'No'
    })
    
    // Log if everything is empty (might indicate privacy settings issue)
    const totalItems = education.value.length + workHistories.value.length + 
                      achievements.value.length + memberships.value.length + 
                      recognitions.value.length + trainings.value.length + 
                      publications.value.length + careerEnhancement.value.certificates.length
    
    if (totalItems === 0 && !isFollowing.value) {
      console.log('⚠️ No items visible - User might have all privacy set to "connections_only" and you are not connected')
      console.log('💡 To see this user\'s profile, try connecting with them first')
    } else if (totalItems === 0 && isFollowing.value) {
      console.log('⚠️ No items visible despite being connected - Check backend privacy filtering or user might not have added any information')
    }
    
  } catch (error) {
    console.error('❌ Error applying privacy filtering:', error)
    // Fallback: use backend data directly (backend already applies privacy filtering)
    education.value = data.education || []
    workHistories.value = data.work_histories || []
    achievements.value = data.achievements || []
    memberships.value = data.memberships || []
    recognitions.value = data.recognitions || []
    trainings.value = data.trainings || []
    publications.value = data.publications || []
    careerEnhancement.value = {
      certificates: data.certificates || [],
      cseStatus: data.cse_status || null
    }
    console.log('⚠️ Using backend-filtered data as fallback')
  }
}

// Fetch user profile data
const fetchUserProfile = async () => {
  try {
    loading.value = true
    
    if (!userIdentifier.value) {
      router.push({ name: 'AlumniHome' })
      return
    }

    // Fetch user profile by username using enhanced-profile endpoint
    const response = await api.get(`/auth/enhanced-profile/username/${userIdentifier.value}/`)
    
    // Debug: Log the API response structure
    console.log('UserProfile API response:', response.data)
    console.log('Available fields in response:', Object.keys(response.data))
    console.log('Skills data in response:', response.data.user_skills)
    console.log('Skills data type:', typeof response.data.user_skills)
    console.log('Skills data length:', response.data.user_skills?.length)
    
    // The API returns the user data directly, with profile nested inside
    const data = response.data
    user.value = data
    profile.value = data.profile
    connections.value = data.connections_count || 0
    
    // Check if already following FIRST (needed for privacy filtering)
    await checkFollowingStatus()
    
    // Apply privacy filtering to the data AFTER connection status is known
    await applyPrivacyFiltering(data)
    
    // Load user skills separately (like MyProfile does)
    await loadUserSkills()
    
    // Debug: Log the extracted data
    console.log('UserProfile extracted data:', {
      user: {
        name: user.value?.first_name + ' ' + user.value?.last_name,
        email: user.value?.email,
        fields: user.value ? Object.keys(user.value) : []
      },
      profile: {
        bio: profile.value?.bio,
        headline: profile.value?.headline,
        fields: profile.value ? Object.keys(profile.value) : []
      },
      education: education.value.length,
      workHistories: workHistories.value.length,
      achievements: achievements.value.length,
      skills: skills.value.length
    })
    
  } catch (error) {
    console.error('Error fetching user profile:', error)
    if (error.response?.status === 404) {
      router.push({ name: 'AlumniHome' })
    }
  } finally {
    loading.value = false
  }
}

// Load user skills using the same approach as MyProfile
const loadUserSkills = async () => {
  try {
    if (!user.value) return
    
    // Check if we're viewing our own profile
    const currentUserResponse = await api.get('/auth/user/')
    const currentUser = currentUserResponse.data
    
    if (currentUser.id === user.value.id) {
      // If viewing own profile, use the user-skills endpoint (like MyProfile does)
      const response = await api.get('/auth/user-skills/')
      skills.value = response.data || []
      console.log('🔐 Own profile - loaded skills from /user-skills/:', skills.value.length)
    } else {
      // For other users' profiles, use user_skills from the enhanced-profile response
      // The backend EnhancedUserDetailSerializer already applies privacy filtering
      skills.value = user.value.user_skills || []
      console.log('🔐 Other user profile - using user_skills from response:', skills.value.length)
    }
  } catch (error) {
    console.error('Error loading user skills:', error)
    // Fallback to user_skills from response
    skills.value = user.value?.user_skills || []
  }
}

// Check if current user is following this user
const checkFollowingStatus = async () => {
  try {
    if (!user.value) return
    
    const response = await api.get('/auth/connections/')
    const following = response.data.following || []
    isFollowing.value = following.some(f => f.id === user.value.id)
  } catch (error) {
    console.error('Error checking following status:', error)
  }
}

// Connect/Follow user
const connectUser = async () => {
  try {
    if (!user.value) return
    
    isConnecting.value = true
    
    if (isFollowing.value) {
      // Unfollow logic would go here
      console.log('Unfollow functionality not implemented yet')
    } else {
      await api.post(`/auth/follow/${user.value.id}/`)
      isFollowing.value = true
      connections.value += 1
    }
    
  } catch (error) {
    console.error('Error connecting user:', error)
  } finally {
    isConnecting.value = false
  }
}

// Send message to user
const sendMessage = () => {
  if (!user.value) return
  
  router.push({
    name: 'AlumniMessaging',
    query: { user: user.value.id }
  })
}

// Handle profile updates
const handleProfileUpdate = () => {
  fetchUserProfile()
}

// Handle connection from suggestions widget
const handleConnect = (userId) => {
  console.log('Connected to user:', userId)
  // Optionally refresh connections or show notification
}

// Watch for route changes
watch(userIdentifier, () => {
  if (userIdentifier.value) {
    fetchUserProfile()
  }
})

// Auto-refresh privacy data periodically (every 30 seconds)
let refreshInterval = null

onMounted(() => {
  fetchUserProfile()
  
  // Set up auto-refresh for privacy changes
  refreshInterval = setInterval(() => {
    if (user.value && !loading.value) {
      console.log('🔄 Auto-refreshing UserProfile for privacy changes...')
      refreshProfileData()
    }
  }, 30000) // Refresh every 30 seconds
})

// Cleanup interval on unmount
onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>