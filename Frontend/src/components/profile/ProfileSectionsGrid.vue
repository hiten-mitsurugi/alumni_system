<template>
  <div class="space-y-6">
    <!-- About Section -->
    <ProfileAboutSection
      :profile="profile"
      :is-own-profile="isOwnProfile"
      @profile-updated="$emit('fetch-profile')"
    />

    <!-- Contact Information Section -->
    <ProfileContactSection
      :profile="profile"
      :is-own-profile="isOwnProfile"
      @profile-updated="$emit('fetch-profile')"
    />

    <!-- Education Section -->
    <ProfileEducationSection
      :education="education"
      :profile="profile"
      :user="user"
      :is-own-profile="isOwnProfile"
      @add="$emit('add-education')"
      @edit="$emit('edit-education', $event)"
      @edit-profile="$emit('edit-profile')"
      @delete="$emit('delete-education', $event)"
      @education-visibility-changed="$emit('education-visibility-changed', $event)"
    />

    <!-- Experience Section -->
    <ProfileExperienceSection
      :workHistories="workHistories"
      :is-own-profile="isOwnProfile"
      @add="$emit('add-experience')"
      @edit="$emit('edit-experience', $event)"
      @delete="$emit('delete-experience', $event)"
      @experience-visibility-changed="$emit('experience-visibility-changed', $event)"
    />

    <!-- Skills Section -->
    <ProfileSkillsSection
      :skills="skills"
      :is-own-profile="isOwnProfile"
      @add="$emit('add-skill')"
      @edit="$emit('edit-skill', $event)"
      @delete="$emit('delete-skill', $event)"
      @skill-visibility-changed="$emit('skill-visibility-changed', $event)"
    />

    <!-- Achievements Section -->
    <ProfileAchievementsSection
      :achievements="achievements"
      :is-own-profile="isOwnProfile"
      @add="$emit('add-achievement')"
      @edit="$emit('edit-achievement', $event)"
      @delete="$emit('delete-achievement', $event)"
      @toggle-visibility="$emit('achievement-visibility-changed', $event)"
    />

    <!-- Memberships Section -->
    <ProfileMembershipsSection
      :memberships="memberships"
      :is-own-profile="isOwnProfile"
      @add="$emit('add-membership')"
      @edit="$emit('edit-membership', $event)"
      @delete="$emit('delete-membership', $event)"
      @visibility-changed="$emit('membership-visibility-changed', $event)"
    />

    <!-- Non-Academic Recognitions Section -->
    <ProfileRecognitionsSection
      :recognitions="recognitions"
      :is-own-profile="isOwnProfile"
      @add="$emit('add-recognition')"
      @edit="$emit('edit-recognition', $event)"
      @delete="$emit('delete-recognition', $event)"
      @visibility-changed="$emit('recognition-visibility-changed', $event)"
    />

    <!-- Trainings Section -->
    <ProfileTrainingsSection
      :trainings="trainings"
      :is-own-profile="isOwnProfile"
      @add="$emit('add-training')"
      @edit="$emit('edit-training', $event)"
      @delete="$emit('delete-training', $event)"
      @visibility-changed="$emit('training-visibility-changed', $event)"
    />

    <!-- Publications Section -->
    <ProfilePublicationsSection
      :publications="publications"
      :is-own-profile="isOwnProfile"
      @add="$emit('add-publication')"
      @edit="$emit('edit-publication', $event)"
      @delete="$emit('delete-publication', $event)"
      @visibility-changed="$emit('publication-visibility-changed', $event)"
    />

    <!-- Career Enhancement Section -->
    <ProfileCareerEnhancementSection
      :career-enhancement="careerEnhancement"
      :is-own-profile="isOwnProfile"
      @add="$emit('add-career-enhancement')"
      @edit-certificate="$emit('edit-certificate', $event)"
      @delete-certificate="$emit('delete-certificate', $event)"
      @edit-cse="$emit('edit-cse')"
      @visibility-changed="$emit('career-enhancement-visibility-changed', $event)"
    />
  </div>
</template>

<script setup>
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

defineProps({
  profile: { type: Object, default: () => ({}) },
  user: { type: Object, default: () => ({}) },
  education: { type: Array, default: () => [] },
  workHistories: { type: Array, default: () => [] },
  skills: { type: Array, default: () => [] },
  achievements: { type: Array, default: () => [] },
  memberships: { type: Array, default: () => [] },
  recognitions: { type: Array, default: () => [] },
  trainings: { type: Array, default: () => [] },
  publications: { type: Array, default: () => [] },
  careerEnhancement: { type: Object, default: () => ({}) },
  isOwnProfile: { type: Boolean, default: false }
})

defineEmits([
  'fetch-profile',
  'edit-profile',
  'add-education', 'edit-education', 'delete-education', 'education-visibility-changed',
  'add-experience', 'edit-experience', 'delete-experience', 'experience-visibility-changed',
  'add-skill', 'edit-skill', 'delete-skill', 'skill-visibility-changed',
  'add-achievement', 'edit-achievement', 'delete-achievement', 'achievement-visibility-changed',
  'add-membership', 'edit-membership', 'delete-membership', 'membership-visibility-changed',
  'add-recognition', 'edit-recognition', 'delete-recognition', 'recognition-visibility-changed',
  'add-training', 'edit-training', 'delete-training', 'training-visibility-changed',
  'add-publication', 'edit-publication', 'delete-publication', 'publication-visibility-changed',
  'add-career-enhancement', 'edit-certificate', 'delete-certificate', 'edit-cse', 'career-enhancement-visibility-changed'
])
</script>
