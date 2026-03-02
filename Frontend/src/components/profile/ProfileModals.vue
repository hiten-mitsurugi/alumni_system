<template>
  <div>
    <!-- Edit Profile Modal -->
    <EditProfileModal
    v-if="modals.showEditModal"
    :profile="profile"
    @close="modals.showEditModal = false"
    @save="$emit('update-profile', $event)"
  />

  <!-- Cover Photo Upload Modal -->
  <CoverPhotoModal
    v-if="modals.showCoverModal"
    @close="modals.showCoverModal = false"
    @save="$emit('update-cover-photo', $event)"
  />

  <!-- Profile Picture Upload Modal -->
  <ProfilePictureModal
    v-if="modals.showProfilePictureModal"
    @close="modals.showProfilePictureModal = false"
    @save="$emit('update-profile-picture', $event)"
  />

  <!-- Education Modal -->
  <EducationModal
    v-if="modals.showEducationModal"
    :education="selectedItems.education"
    @close="handlers.closeEducationModal"
    @save="handlers.saveEducation"
  />

  <!-- Work History Modal -->
  <WorkHistoryModal
    v-if="modals.showExperienceModal"
    :experience="selectedItems.experience"
    @close="handlers.closeExperienceModal"
    @save="handlers.saveExperience"
  />

  <!-- Skill Modal -->
  <SkillModal
    v-if="modals.showSkillModal"
    :skill="selectedItems.skill"
    @close="handlers.closeSkillModal"
    @save="handlers.saveSkill"
  />

  <!-- Achievement Modal -->
  <AchievementModal
    v-if="modals.showAchievementModal"
    :achievement="selectedItems.achievement"
    @close="handlers.closeAchievementModal"
    @save="handlers.saveAchievement"
  />

  <!-- Membership Modal -->
  <MembershipModal
    v-if="modals.showMembershipModal"
    :membership="selectedItems.membership"
    @close="handlers.closeMembershipModal"
    @save="handlers.saveMembership"
  />

  <!-- Recognition Modal -->
  <RecognitionModal
    v-if="modals.showRecognitionModal"
    :recognition="selectedItems.recognition"
    @close="handlers.closeRecognitionModal"
    @save="handlers.saveRecognition"
  />

  <!-- Training Modal -->
  <TrainingModal
    v-if="modals.showTrainingModal"
    :training="selectedItems.training"
    @close="handlers.closeTrainingModal"
    @save="handlers.saveTraining"
  />

  <!-- Publication Modal -->
  <PublicationModal
    v-if="modals.showPublicationModal"
    :publication="selectedItems.publication"
    @close="handlers.closePublicationModal"
    @save="handlers.savePublication"
  />

  <!-- Career Enhancement Modal -->
  <CareerEnhancementModal
    v-if="modals.showCareerEnhancementModal"
    :career-enhancement="selectedItems.careerEnhancement"
    @close="handlers.closeCareerEnhancementModal"
    @save="handlers.saveCareerEnhancement"
  />

    <!-- Export CV Modal -->
    <ExportCvModal
      :is-open="modals.showExportCvModal"
      @close="modals.showExportCvModal = false"
      @success="$emit('cv-export-success', $event)"
    />
  </div>
</template>

<script setup>
import EditProfileModal from '@/components/profile/EditProfileModal.vue'
import CoverPhotoModal from '@/components/profile/CoverPhotoModal.vue'
import ProfilePictureModal from '@/components/profile/ProfilePictureModal.vue'
import EducationModal from '@/components/profile/EducationModal.vue'
import WorkHistoryModal from '@/components/profile/WorkHistoryModal.vue'
import SkillModal from '@/components/profile/SkillModal.vue'
import AchievementModal from '@/components/profile/AchievementModal.vue'
import MembershipModal from '@/components/profile/MembershipModal.vue'
import RecognitionModal from '@/components/profile/RecognitionModal.vue'
import TrainingModal from '@/components/profile/TrainingModal.vue'
import PublicationModal from '@/components/profile/PublicationModal.vue'
import CareerEnhancementModal from '@/components/profile/CareerEnhancementModal.vue'
import ExportCvModal from '@/components/profile/ExportCvModal.vue'

defineProps({
  modals: { type: Object, required: true },
  selectedItems: { type: Object, required: true },
  handlers: { type: Object, required: true },
  profile: { type: Object, default: () => ({}) }
})

defineEmits(['update-profile', 'update-cover-photo', 'update-profile-picture', 'cv-export-success'])
</script>
