<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import api from '@/services/api'
import { getProfilePictureUrl, getCoverPhotoUrl } from '@/utils/imageUrl'
// Component imports
import ProfileHeaderCard from '@/components/profile/ProfileHeaderCard.vue'
import ProfileTabs from '@/components/profile/ProfileTabs.vue'
import SuggestedConnectionsWidget from '@/components/profile/SuggestedConnectionsWidget.vue'
import ProfileModals from '@/components/profile/ProfileModals.vue'
import ProfileSectionsGrid from '@/components/profile/ProfileSectionsGrid.vue'
// Tab components
import PostsTab from '@/components/profile/tabs/PostsTab.vue'
import { useEntityCrud } from '@/composables/useEntityCrud'
import { usePrivacy } from '@/composables/usePrivacy'
import { useProfileData } from '@/composables/useProfileData'
import { useModals } from '@/composables/useModals'
import { useProfileCrud } from '@/composables/useProfileCrud'
import { createAchievementFormData, createCareerEnhancementFormData, validateAchievement, validateCareerEnhancement } from '@/utils/formDataHelpers'
// Initialize entity CRUD helpers
const { create: createEducation, update: updateEducation, remove: deleteEducationApi } = useEntityCrud('education')
const { create: createExperience, update: updateExperience, remove: deleteExperienceApi } = useEntityCrud('work-history')
const { create: createSkill, update: updateSkill, remove: deleteSkillApi } = useEntityCrud('user-skills')
const { create: createAchievement, update: updateAchievement, remove: deleteAchievementApi } = useEntityCrud('achievements')
const { create: createMembership, update: updateMembership, remove: deleteMembershipApi } = useEntityCrud('memberships')
const { create: createRecognition, update: updateRecognition, remove: deleteRecognitionApi } = useEntityCrud('recognitions')
const { create: createTraining, update: updateTraining, remove: deleteTrainingApi } = useEntityCrud('trainings')
const { create: createPublication, update: updatePublication, remove: deletePublicationApi } = useEntityCrud('publications')
const { create: createCertificate, update: updateCertificate, remove: deleteCertificateApi } = useEntityCrud('certificates')
// Initialize privacy composable
const { updateFieldPrivacy } = usePrivacy()
// Reactive data
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()
// Initialize profile data composable
const {
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
} = useProfileData(route, authStore)

const followLoading = ref(false)
// Initialize modals composable
const { modals, selectedItems, openModal, closeModal, openEditModal, openAddModal } = useModals()
// Alias modal states for backward compatibility
const showEditModal = computed(() => modals.profile)
const showCoverModal = computed(() => modals.coverPhoto)
const showProfilePictureModal = computed(() => modals.profilePicture)
const showEducationModal = computed(() => modals.education)
const showExperienceModal = computed(() => modals.workHistory)
const showSkillModal = computed(() => modals.skills)
const showAchievementModal = computed(() => modals.achievements)
const showMembershipModal = computed(() => modals.memberships)
const showRecognitionModal = computed(() => modals.recognitions)
const showTrainingModal = computed(() => modals.trainings)
const showPublicationModal = computed(() => modals.publications)
const showCareerEnhancementModal = computed(() => modals.careerEnhancement)
const showExportCvModal = ref(false)
// Alias selected items for backward compatibility
const selectedEducation = computed(() => selectedItems.education)
const selectedExperience = computed(() => selectedItems.workHistory)
const selectedSkill = computed(() => selectedItems.skills)
const selectedAchievement = computed(() => selectedItems.achievements)
const selectedMembership = computed(() => selectedItems.memberships)
const selectedRecognition = computed(() => selectedItems.recognitions)
const selectedTraining = computed(() => selectedItems.trainings)
const selectedPublication = computed(() => selectedItems.publications)
const selectedCareerEnhancement = computed(() => selectedItems.careerEnhancement)
// Tab state
const activeTab = ref('about')
// Profile picture URL with fallback (same logic as AlumniNavbar)
const profilePictureUrl = computed(() => {
  return getProfilePictureUrl(user.value?.profile_picture)
})

// Cover photo URL with fallback
const coverPhotoUrl = computed(() => {
  return getCoverPhotoUrl(profile.value?.cover_photo)
})
// Keep profile page in sync with global auth store (e.g. sidebar uploads)
watch(() => authStore.user, (newAuthUser) => {
  try {
    if (!newAuthUser || !user.value) return

    // If viewing own profile or the resolved profile matches the auth user,
    // update the local profile_picture to reflect immediate changes made via sidebars
    if (isOwnProfile.value || resolvedUserId.value === newAuthUser.id || (!resolvedUserId.value && authStore.user?.id === newAuthUser.id)) {
      // ensure reactive update
      user.value.profile_picture = newAuthUser.profile_picture
      if (profile.value) profile.value.profile_picture = newAuthUser.profile_picture
    }
  } catch (e) {
    console.error('Error syncing profile with auth store:', e)
  }
}, { deep: true })
const toggleFollow = async () => {
  try {
    followLoading.value = true
    await api[isFollowing.value ? 'delete' : 'post'](`/auth/follow/${profileUserId.value}/`)
    isFollowing.value = !isFollowing.value
    await fetchProfile()
  } catch (error) {
    console.error('Error toggling follow:', error)
  } finally {
    followLoading.value = false
  }
}
const openMessage = () => router.push({ name: 'AlumniMessaging', query: { userId: profileUserId.value } })
const editProfile = () => openModal('profile')
const editCoverPhoto = () => openModal('coverPhoto')
const editProfilePicture = () => openModal('profilePicture')
const handleCvExportSuccess = () => { showExportCvModal.value = false }

const updateProfile = async (profileData) => {
  try {
    await api.patch('/auth/enhanced-profile/', profileData)
    await fetchProfile()
    closeModal('profile')
  } catch (error) {
    console.error('Error updating profile:', error)
  }
}
const updateCoverPhoto = async (file) => {
  try {
    const formData = new FormData()
    formData.append('cover_photo', file)

    await api.patch('/auth/enhanced-profile/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    await fetchProfile()
    closeModal('coverPhoto')
  } catch (error) {
    console.error('Error updating cover photo:', error)
  }
}

const updateProfilePicture = async (file) => {
  try {
    const formData = new FormData()
    formData.append('profile_picture', file)

    await api.patch('/auth/enhanced-profile/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    await fetchProfile()
    closeModal('profilePicture')
  } catch (error) {
    console.error('Error updating profile picture:', error)
  }
}
// Education CRUD handlers
const educationCrud = useProfileCrud({
  fetchProfile,
  loadUserSkills,
  createApi: createEducation,
  updateApi: updateEducation,
  deleteApi: deleteEducationApi,
  selectedItem: selectedEducation,
  showModal: showEducationModal,
  closeModalFn: () => closeModal('education'),
  entityName: 'education record'
})
const { add: addEducation, edit: editEducation, remove: deleteEducation, save: saveEducation, close: closeEducationModal } = educationCrud
// Experience CRUD handlers
const experienceCrud = useProfileCrud({
  fetchProfile,
  loadUserSkills,
  createApi: createExperience,
  updateApi: updateExperience,
  deleteApi: deleteExperienceApi,
  selectedItem: selectedExperience,
  showModal: showExperienceModal,
  closeModalFn: () => closeModal('workHistory'),
  entityName: 'work experience'
})
const { add: addExperience, edit: editExperience, remove: deleteExperience, save: saveExperience, close: closeExperienceModal } = experienceCrud
// Skill CRUD handlers
const skillCrud = useProfileCrud({
  fetchProfile,
  loadUserSkills,
  createApi: createSkill,
  updateApi: updateSkill,
  deleteApi: deleteSkillApi,
  selectedItem: selectedSkill,
  showModal: showSkillModal,
  closeModalFn: () => closeModal('skills'),
  entityName: 'skill',
  isSkill: true,
  onSuccess: (action) => action === 'deleted' ? alert('Skill removed successfully!') : alert('Skill saved successfully!')
})
const { add: addSkill, edit: editSkill, remove: deleteSkill, save: saveSkill, close: closeSkillModal } = skillCrud
// Achievement CRUD handlers - custom save due to FormData
const achievementCrud = useProfileCrud({
  fetchProfile,
  loadUserSkills,
  createApi: createAchievement,
  updateApi: updateAchievement,
  deleteApi: deleteAchievementApi,
  selectedItem: selectedAchievement,
  showModal: showAchievementModal,
  closeModalFn: () => closeModal('achievements'),
  entityName: 'achievement'
})
const { add: addAchievement, edit: editAchievement, remove: deleteAchievement, close: closeAchievementModal } = achievementCrud

// Custom save for achievement (needs FormData transformation)
const saveAchievement = async (achievementData) => {
  try {
    const file = achievementData.attachment instanceof File ? achievementData.attachment : null
    const formData = createAchievementFormData(achievementData, file)

    if (selectedAchievement.value) {
      await updateAchievement(selectedAchievement.value.id, formData)
    } else {
      await createAchievement(formData)
    }

    closeAchievementModal()
    await fetchProfile()
  } catch (error) {
    console.error('Error saving achievement:', error)
    if (error.response?.status === 400) {
      alert('Please check all fields and try again. Make sure required fields are filled.')
    } else if (error.response?.status === 413) {
      alert('File size too large. Please upload a smaller file.')
    } else {
      alert('Failed to save achievement. Please try again.')
    }
  }
}
// Generic privacy handler for all item types
const handleItemVisibilityChange = async (itemType, itemId, newVisibility) => {
  try {
    const fieldName = `${itemType}_${itemId}`
    await updateFieldPrivacy(fieldName, newVisibility)  
    // Update local state based on item type
    const updateLocalState = (items, id, visibility) => {
      const item = items.value.find(i => i.id === id)
      if (item) item.visibility = visibility
    }
    switch(itemType) {
      case 'education': updateLocalState(education, itemId, newVisibility); break
      case 'experience': updateLocalState(workHistories, itemId, newVisibility); break
      case 'skill': updateLocalState(skills, itemId, newVisibility); break
      case 'achievement': updateLocalState(achievements, itemId, newVisibility); break
      case 'membership': updateLocalState(memberships, itemId, newVisibility); break
      case 'recognition': updateLocalState(recognitions, itemId, newVisibility); break
      case 'training': updateLocalState(trainings, itemId, newVisibility); break
      case 'publication': updateLocalState(publications, itemId, newVisibility); break
    }
    privacySettings.value[fieldName] = newVisibility
  } catch (error) {
    console.error(`❌ Failed to update ${itemType} privacy:`, error)
    alert('Failed to update privacy setting. Please try again.')
  }
}

// Visibility change handlers for template event bindings
const handleEducationVisibilityChange = (itemId, newVisibility) => handleItemVisibilityChange('education', itemId, newVisibility)
const handleExperienceVisibilityChange = (itemId, newVisibility) => handleItemVisibilityChange('experience', itemId, newVisibility)
const handleSkillVisibilityChange = (itemId, newVisibility) => handleItemVisibilityChange('skill', itemId, newVisibility)
const handleAchievementVisibilityChange = (itemId, newVisibility) => handleItemVisibilityChange('achievement', itemId, newVisibility)
const handleMembershipVisibilityChange = (itemId, newVisibility) => handleItemVisibilityChange('membership', itemId, newVisibility)
const handleRecognitionVisibilityChange = (itemId, newVisibility) => handleItemVisibilityChange('recognition', itemId, newVisibility)
const handleTrainingVisibilityChange = (itemId, newVisibility) => handleItemVisibilityChange('training', itemId, newVisibility)
const handlePublicationVisibilityChange = (itemId, newVisibility) => handleItemVisibilityChange('publication', itemId, newVisibility)
const handleCareerEnhancementVisibilityChange = (itemId, newVisibility) => handleItemVisibilityChange('career_enhancement', itemId, newVisibility)

const handleConnect = () => {
  // Handle connection from suggested connections
}
// Membership CRUD handlers
const membershipCrud = useProfileCrud({
  fetchProfile,
  loadUserSkills,
  createApi: createMembership,
  updateApi: updateMembership,
  deleteApi: deleteMembershipApi,
  selectedItem: selectedMembership,
  showModal: showMembershipModal,
  closeModalFn: () => closeModal('memberships'),
  entityName: 'membership'
})
const { add: addMembership, edit: editMembership, remove: deleteMembership, save: saveMembership, close: closeMembershipModal } = membershipCrud
// Recognition CRUD handlers
const recognitionCrud = useProfileCrud({
  fetchProfile,
  loadUserSkills,
  createApi: createRecognition,
  updateApi: updateRecognition,
  deleteApi: deleteRecognitionApi,
  selectedItem: selectedRecognition,
  showModal: showRecognitionModal,
  closeModalFn: () => closeModal('recognitions'),
  entityName: 'recognition'
})
const { add: addRecognition, edit: editRecognition, remove: deleteRecognition, save: saveRecognition, close: closeRecognitionModal } = recognitionCrud
// Training CRUD handlers
const trainingCrud = useProfileCrud({
  fetchProfile,
  loadUserSkills,
  createApi: createTraining,
  updateApi: updateTraining,
  deleteApi: deleteTrainingApi,
  selectedItem: selectedTraining,
  showModal: showTrainingModal,
  closeModalFn: () => closeModal('trainings'),
  entityName: 'training'
})
const { add: addTraining, edit: editTraining, remove: deleteTraining, save: saveTraining, close: closeTrainingModal } = trainingCrud
// Publication CRUD handlers  
const publicationCrud = useProfileCrud({
  fetchProfile,
  loadUserSkills,
  createApi: createPublication,
  updateApi: updatePublication,
  deleteApi: deletePublicationApi,
  selectedItem: selectedPublication,
  showModal: showPublicationModal,
  closeModalFn: () => closeModal('publications'),
  entityName: 'publication'
})
const { add: addPublication, edit: editPublication, remove: deletePublication, close: closePublicationModal } = publicationCrud
// Custom save for publication (needs data transformation)
const savePublication = async (publicationData) => {
  try {
    // Transform frontend data to match backend PublicationSerializer
    const backendData = {
      title: publicationData.title,
      publication_type: publicationData.publication_type || 'journal',
      authors: publicationData.co_authors && publicationData.co_authors.length > 0
        ? publicationData.co_authors.join(', ')
        : 'Unknown',
      date_published: publicationData.year_published 
        ? `${publicationData.year_published}-01-01`
        : new Date().toISOString().split('T')[0],
      publisher: publicationData.place_of_publication || null,
      url: publicationData.url || null,
      doi: publicationData.doi || null
    }
    let response
    if (selectedPublication.value) {
      response = await updatePublication(selectedPublication.value.id, backendData)
      const index = publications.value.findIndex(p => p.id === selectedPublication.value.id)
      if (index !== -1) {
        publications.value[index] = response
      }
    } else {
      response = await createPublication(backendData)
      publications.value.push(response)
    }    
    closePublicationModal()
  } catch (error) {
    console.error('Error saving publication:', error)
    const errorData = error.response?.data
    let errorMessage = 'Failed to save publication'
    if (errorData && typeof errorData === 'object') {
      const errors = Object.entries(errorData).map(([field, msg]) => `${field}: ${Array.isArray(msg) ? msg.join(', ') : msg}`).join('\\n')
      errorMessage += ':\\n' + errors
    } else if (errorData) {
      errorMessage += ': ' + errorData
    }
    alert(errorMessage)
  }
}
// Career Enhancement handlers
const addCareerEnhancement = () => {
  openAddModal('careerEnhancement')
}
const editCertificate = (certificate) => {
  // For editing certificates, we open the career enhancement modal with the full data
  openEditModal('careerEnhancement', careerEnhancement.value)
}
const deleteCertificate = async (certificateId) => {
  if (!confirm('Are you sure you want to delete this certificate?')) {
    return
  }
  try {
    await deleteCertificateApi(certificateId)
    if (careerEnhancement.value.certificates) {
      careerEnhancement.value.certificates = careerEnhancement.value.certificates.filter(c => c.id !== certificateId)
    }
  } catch (error) {
    console.error('Error deleting certificate:', error)
    alert('Failed to delete certificate')
  }
}
const editCSE = () => {
  openEditModal('careerEnhancement', careerEnhancement.value)
}
const closeCareerEnhancementModal = () => {
  closeModal('careerEnhancement')
}
const saveCareerEnhancement = async (careerEnhancementData) => {
  try {
    // Handle certificates
    if (careerEnhancementData.certificates) {
      const certs = Array.isArray(careerEnhancementData.certificates) ? careerEnhancementData.certificates : [careerEnhancementData.certificates]
      
      for (const cert of certs) {
        const fd = new FormData()
        Object.entries(cert).forEach(([key, val]) => {
          if (val && key !== 'id') fd.append(key, val instanceof File ? val : String(val))
        })
        
        await (cert.id ? updateCertificate(cert.id, fd) : createCertificate(fd))
      }
    }
    // Handle CSE status
    if (careerEnhancementData.cseStatus) {
      const res = await api.put('/auth/cse-status/', careerEnhancementData.cseStatus)
      careerEnhancement.value.cseStatus = res.data
    }
    closeCareerEnhancementModal()
    await fetchProfile()
  } catch (error) {
    console.error('Error saving career enhancement:', error)
    alert('Failed to save career enhancement')
  }
}
// Lifecycle
onMounted(() => {
  fetchProfile()
})
// Watch for route changes to update profile
watch(() => route.params.userIdentifier, () => {
  // Reset resolved user ID when route changes
  resolvedUserId.value = null
  fetchProfile()
}, { immediate: false })
</script>

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
      <!-- Profile Header Card Component -->
      <ProfileHeaderCard
        :user="user"
        :profile="profile"
        :education="education"
        :work-histories="workHistories"
        :profile-picture-url="profilePictureUrl"
        :cover-photo-url="coverPhotoUrl"
        :connections-count="connectionsCount"
        :is-following="isFollowing"
        :follow-loading="followLoading"
        :is-own-profile="isOwnProfile"
        :is-dark-mode="themeStore.isDarkMode"
        @edit-cover-photo="editCoverPhoto"
        @edit-profile-picture="editProfilePicture"
        @toggle-follow="toggleFollow"
        @open-message="openMessage"
        @export-cv="showExportCvModal = true"
        @edit-profile="editProfile"
      />

      <!-- Tab Navigation -->
      <ProfileTabs
        :active-tab="activeTab"
        :is-dark-mode="themeStore.isDarkMode"
        @update:active-tab="activeTab = $event"
      />

      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <!-- Left Column - Profile Sections -->
        <div class="space-y-6 lg:col-span-2">

          <!-- About Tab Content -->
          <div v-show="activeTab === 'about'">
            <ProfileSectionsGrid
              :profile="profile"
              :user="user"
              :education="education"
              :work-histories="workHistories"
              :skills="skills"
              :achievements="achievements"
              :memberships="memberships"
              :recognitions="recognitions"
              :trainings="trainings"
              :publications="publications"
              :career-enhancement="careerEnhancement"
              :is-own-profile="isOwnProfile"
              @fetch-profile="fetchProfile"
              @edit-profile="editProfile"
              @add-education="addEducation"
              @edit-education="editEducation"
              @delete-education="deleteEducation"
              @education-visibility-changed="handleEducationVisibilityChange"
              @add-experience="addExperience"
              @edit-experience="editExperience"
              @delete-experience="deleteExperience"
              @experience-visibility-changed="handleExperienceVisibilityChange"
              @add-skill="addSkill"
              @edit-skill="editSkill"
              @delete-skill="deleteSkill"
              @skill-visibility-changed="handleSkillVisibilityChange"
              @add-achievement="addAchievement"
              @edit-achievement="editAchievement"
              @delete-achievement="deleteAchievement"
              @achievement-visibility-changed="handleAchievementVisibilityChange"
              @add-membership="addMembership"
              @edit-membership="editMembership"
              @delete-membership="deleteMembership"
              @membership-visibility-changed="handleMembershipVisibilityChange"
              @add-recognition="addRecognition"
              @edit-recognition="editRecognition"
              @delete-recognition="deleteRecognition"
              @recognition-visibility-changed="handleRecognitionVisibilityChange"
              @add-training="addTraining"
              @edit-training="editTraining"
              @delete-training="deleteTraining"
              @training-visibility-changed="handleTrainingVisibilityChange"
              @add-publication="addPublication"
              @edit-publication="editPublication"
              @delete-publication="deletePublication"
              @publication-visibility-changed="handlePublicationVisibilityChange"
              @add-career-enhancement="addCareerEnhancement"
              @edit-certificate="editCertificate"
              @delete-certificate="deleteCertificate"
              @edit-cse="editCSE"
              @career-enhancement-visibility-changed="handleCareerEnhancementVisibilityChange"
            />
          </div>

          <!-- Posts Tab Content -->
          <div v-show="activeTab === 'posts'">
            <PostsTab :user-id="resolvedUserId" />
          </div>

        </div>

        <!-- Right Column - Sidebar -->
        <div class="space-y-6">
          <!-- People You May Know -->
          <SuggestedConnectionsWidget @connect="handleConnect" />
        </div>
      </div>
    </div>

    <!-- All Modals -->
    <ProfileModals
      :modals="{
        showEditModal,
        showCoverModal,
        showProfilePictureModal,
        showEducationModal,
        showExperienceModal,
        showSkillModal,
        showAchievementModal,
        showMembershipModal,
        showRecognitionModal,
        showTrainingModal,
        showPublicationModal,
        showCareerEnhancementModal,
        showExportCvModal
      }"
      :selected-items="{
        education: selectedEducation,
        experience: selectedExperience,
        skill: selectedSkill,
        achievement: selectedAchievement,
        membership: selectedMembership,
        recognition: selectedRecognition,
        training: selectedTraining,
        publication: selectedPublication,
        careerEnhancement: selectedCareerEnhancement
      }"
      :handlers="{
        closeEducationModal,
        saveEducation,
        closeExperienceModal,
        saveExperience,
        closeSkillModal,
        saveSkill,
        closeAchievementModal,
        saveAchievement,
        closeMembershipModal,
        saveMembership,
        closeRecognitionModal,
        saveRecognition,
        closeTrainingModal,
        saveTraining,
        closePublicationModal,
        savePublication,
        closeCareerEnhancementModal,
        saveCareerEnhancement
      }"
      :profile="profile"
      @update-profile="updateProfile"
      @update-cover-photo="updateCoverPhoto"
      @update-profile-picture="updateProfilePicture"
      @cv-export-success="handleCvExportSuccess"
    />
  </div>
</template>
<style scoped>
/* Custom styles if needed */
</style>
