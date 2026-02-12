import { ref, computed } from 'vue'
import api from '@/services/api'

export function useProfileData(route, authStore) {
  const loading = ref(false)
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
  const isFollowing = ref(false)
  const connectionsCount = ref(0)
  const resolvedUserId = ref(null)
  const privacySettings = ref({})

  const isOwnProfile = computed(() => {
    const userIdentifier = route.params.userIdentifier
    if (!userIdentifier) return true
    if (authStore.user && userIdentifier === authStore.user.username) return true
    return false
  })

  const profileUserId = computed(() => {
    return route.params.userIdentifier || authStore.user?.id
  })

  const loadPrivacySettings = async () => {
    try {
      const response = await api.get('/auth/profile/field-update/')
      privacySettings.value = {}
      response.data.forEach(setting => {
        privacySettings.value[setting.field_name] = setting.visibility
      })
    } catch (error) {
      console.error('Failed to load privacy settings:', error)
      privacySettings.value = {}
    }
  }

  const getItemPrivacy = (itemType, itemId) => {
    const fieldName = `${itemType}_${itemId}`
    return privacySettings.value[fieldName] || 'connections_only'
  }

  const loadUserSkills = async () => {
    try {
      const endpoint = isOwnProfile.value ? '/user-skills/' : `/user-skills/user/${profileUserId.value}/`
      const response = await api.get(`/auth${endpoint}`)
      skills.value = (response.data || []).map(skill => ({
        ...skill,
        visibility: getItemPrivacy('skill', skill.id) || 'connections_only'
      }))
    } catch (error) {
      console.error('Error loading user skills:', error)
      skills.value = []
    }
  }

  // Debounce timer to prevent rapid repeated calls
  let fetchProfileTimer = null
  
  const fetchProfile = async (force = false) => {
    // Debounce: prevent too many rapid calls
    if (!force && fetchProfileTimer) {
      clearTimeout(fetchProfileTimer)
      return new Promise(resolve => {
        fetchProfileTimer = setTimeout(async () => {
          await fetchProfile(true)
          resolve()
        }, 300)
      })
    }
    
    try {
      loading.value = true
      let userIdentifier = route.params.userIdentifier
      let userId = null

      if (!userIdentifier) {
        userId = authStore.user?.id
      } else if (!isNaN(userIdentifier)) {
        userId = parseInt(userIdentifier)
      } else {
        try {
          const response = await api.get(`/auth/alumni/by-name/${userIdentifier}/`)
          userId = response.data.id
        } catch (error) {
          try {
            const usersResponse = await api.get('/auth/users/')
            const foundUser = usersResponse.data.find(u => u.username === userIdentifier)
            userId = foundUser ? foundUser.id : authStore.user?.id
          } catch (fallbackError) {
            userId = authStore.user?.id
          }
        }
      }

      resolvedUserId.value = userId

      const endpoint = (userId === authStore.user?.id)
        ? '/enhanced-profile/'
        : `/enhanced-profile/${userId}/`

      const response = await api.get(`/auth${endpoint}`)
      const data = response.data

      console.log('🔍 useProfileData: Fetched profile data', {
        hasWorkHistories: !!data.work_histories,
        workHistoriesLength: data.work_histories?.length || 0,
        workHistoriesData: data.work_histories
      })

      // Only update values on successful fetch (don't set to null on error)
      user.value = data
      profile.value = data.profile || {}

      await loadPrivacySettings()

      education.value = (data.education || []).map(edu => ({
        ...edu,
        visibility: getItemPrivacy('education', edu.id) || 'connections_only'
      }))

      workHistories.value = (data.work_histories || []).map(work => ({
        ...work,
        visibility: getItemPrivacy('experience', work.id) || 'connections_only'
      }))
      
      console.log('✅ useProfileData: Updated workHistories ref', {
        length: workHistories.value.length,
        items: workHistories.value
      })

      achievements.value = (data.achievements || []).map(achievement => ({
        ...achievement,
        visibility: getItemPrivacy('achievement', achievement.id) || 'connections_only'
      }))

      memberships.value = (data.memberships || []).map(membership => ({
        ...membership,
        visibility: getItemPrivacy('membership', membership.id) || 'connections_only'
      }))

      recognitions.value = (data.recognitions || []).map(recognition => ({
        ...recognition,
        visibility: getItemPrivacy('recognition', recognition.id) || 'connections_only'
      }))

      trainings.value = (data.trainings || []).map(training => ({
        ...training,
        visibility: getItemPrivacy('training', training.id) || 'connections_only'
      }))

      publications.value = (data.publications || []).map(publication => ({
        ...publication,
        visibility: getItemPrivacy('publication', publication.id) || 'connections_only'
      }))

      careerEnhancement.value = {
        certificates: data.certificates || [],
        cseStatus: data.cse_status || null
      }

      await loadUserSkills()

      if (profile.value) {
        connectionsCount.value = profile.value.connections_count || 0
        isFollowing.value = profile.value.is_following || false
      }
    } catch (error) {
      console.error('Error fetching profile:', error)
      // Don't set values to null on error; keep previous values or set safe defaults
      if (!user.value) {
        user.value = { id: authStore.user?.id }
      }
      if (!profile.value) {
        profile.value = {}
      }
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    user,
    profile,
    education,
    workHistories,
    skills,
    achievements,
    memberships,
    recognitions,
    trainings,
    publications,
    careerEnhancement,
    isFollowing,
    connectionsCount,
    resolvedUserId,
    privacySettings,
    isOwnProfile,
    profileUserId,
    fetchProfile,
    loadUserSkills,
    loadPrivacySettings,
    getItemPrivacy
  }
}
