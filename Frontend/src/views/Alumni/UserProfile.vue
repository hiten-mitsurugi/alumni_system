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
            v-if="profile?.cover_photo"
            :src="profile.cover_photo"
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
                :src="user?.profile_picture || '/default-avatar.png'"
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

            <!-- Experience Section -->
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

// Components
import ProfileAboutSection from '@/components/profile/ProfileAboutSection.vue'
import ProfileContactSection from '@/components/profile/ProfileContactSection.vue'
import ProfileEducationSection from '@/components/profile/ProfileEducationSection.vue'
import ProfileExperienceSection from '@/components/profile/ProfileExperienceSection.vue'
import ProfileSkillsSection from '@/components/profile/ProfileSkillsSection.vue'
import ProfileAchievementsSection from '@/components/profile/ProfileAchievementsSection.vue'
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
    
    // If viewing own profile, show everything
    if (currentUser.id === data.id) {
      education.value = data.education || []
      workHistories.value = data.work_histories || []
      achievements.value = data.achievements || []
      return
    }
    
    // For other users, get their privacy settings (with timestamp to avoid cache)
    const privacyResponse = await api.get(`/auth/profile/field-update/`, {
      params: { 
        user_id: data.id,
        _t: Date.now() // Prevent caching
      }
    })
    
    const privacySettings = {}
    privacyResponse.data.forEach(setting => {
      privacySettings[setting.field_name] = setting.visibility
    })
    
    console.log('🔐 Privacy settings for user:', privacySettings)
    console.log('🔐 Connection status (isFollowing):', isFollowing.value)
    
    // Filter education based on privacy
    education.value = (data.education || []).filter(edu => {
      const privacy = privacySettings[`education_${edu.id}`] || 'connections_only'
      const isVisible = privacy === 'everyone' || (privacy === 'connections_only' && isFollowing.value)
      console.log(`🔐 Education ${edu.id}: privacy="${privacy}", visible=${isVisible}`)
      return isVisible
    })
    
    // Filter work histories based on privacy
    workHistories.value = (data.work_histories || []).filter(work => {
      const privacy = privacySettings[`experience_${work.id}`] || 'connections_only'
      const isVisible = privacy === 'everyone' || (privacy === 'connections_only' && isFollowing.value)
      console.log(`🔐 Experience ${work.id}: privacy="${privacy}", visible=${isVisible}`)
      return isVisible
    })
    
    // Filter achievements based on privacy
    achievements.value = (data.achievements || []).filter(achievement => {
      const privacy = privacySettings[`achievement_${achievement.id}`] || 'connections_only'
      const isVisible = privacy === 'everyone' || (privacy === 'connections_only' && isFollowing.value)
      console.log(`🔐 Achievement ${achievement.id}: privacy="${privacy}", visible=${isVisible}`)
      return isVisible
    })
    
    console.log('🔐 After privacy filtering:', {
      education: education.value.length,
      workHistories: workHistories.value.length, 
      achievements: achievements.value.length
    })
    
  } catch (error) {
    console.error('❌ Error applying privacy filtering:', error)
    // Fallback: show everything if privacy check fails
    education.value = data.education || []
    workHistories.value = data.work_histories || []
    achievements.value = data.achievements || []
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
    
    // For UserProfile, we're viewing another user's profile, but the /auth/user-skills/ endpoint
    // only returns skills for the authenticated user. Since we can't get other users' skills directly,
    // we'll need to check if this is our own profile or implement a different approach.
    
    // Check if we're viewing our own profile
    const currentUserResponse = await api.get('/auth/user/')
    const currentUser = currentUserResponse.data
    
    if (currentUser.id === user.value.id) {
      // If viewing own profile, use the user-skills endpoint
      const response = await api.get('/auth/user-skills/')
      skills.value = response.data || []
    } else {
      // For other users' profiles, apply privacy filtering to skills
      const allSkills = user.value.user_skills || []
      
      try {
        // Get privacy settings for skills
        const privacyResponse = await api.get(`/auth/profile/field-update/`, {
          params: { user_id: user.value.id }
        })
        
        const privacySettings = {}
        privacyResponse.data.forEach(setting => {
          privacySettings[setting.field_name] = setting.visibility
        })
        
        // Filter skills based on privacy
        skills.value = allSkills.filter(skill => {
          const privacy = privacySettings[`skill_${skill.id}`] || 'connections_only'
          return privacy === 'everyone' || (privacy === 'connections_only' && isFollowing.value)
        })
        
        console.log('🔐 Skills after privacy filtering:', skills.value.length, 'of', allSkills.length)
        
      } catch (error) {
        console.error('❌ Error filtering skills privacy:', error)
        // Fallback: show all skills if privacy check fails
        skills.value = allSkills
      }
    }
  } catch (error) {
    console.error('Error loading user skills:', error)
    skills.value = []
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