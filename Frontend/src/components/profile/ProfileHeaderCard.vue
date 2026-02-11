<template>
  <div :class="[
    'rounded-lg shadow-lg overflow-hidden mb-6 transition-colors duration-200',
    isDarkMode ? 'bg-gray-800' : 'bg-white'
  ]">
    <!-- Cover Photo -->
    <div class="relative h-48 bg-gradient-to-r from-green-400 to-blue-500">
      <img
        v-if="profile?.cover_photo"
        :src="profile.cover_photo"
        alt="Cover Photo"
        class="object-cover w-full h-full"
      />
      <div
        v-if="isOwnProfile"
        :class="[
          'absolute top-4 right-4 rounded-full p-2 cursor-pointer transition-colors',
          isDarkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-white hover:bg-gray-100'
        ]"
        @click="$emit('edit-cover-photo')"
      >
        <svg :class="['w-5 h-5', isDarkMode ? 'text-gray-300' : 'text-gray-600']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path>
        </svg>
      </div>
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
              isDarkMode ? 'border-gray-800' : 'border-white'
            ]"
          />
          <div
            v-if="isOwnProfile"
            class="absolute p-2 transition-colors bg-orange-500 rounded-full cursor-pointer bottom-2 right-2 hover:bg-orange-600"
            @click="$emit('edit-profile-picture')"
          >
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
          </div>
        </div>
      </div>

      <!-- Name and Basic Info -->
      <div class="pt-20">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h1 :class="['text-3xl font-bold', isDarkMode ? 'text-white' : 'text-gray-900']">
              {{ user?.first_name }} {{ user?.middle_name }} {{ user?.last_name }}
            </h1>
            <p :class="['text-lg mt-1', isDarkMode ? 'text-gray-300' : 'text-gray-600']">
              {{ displayHeadline }}
            </p>

            <div v-if="displayEducationInfo" :class="['flex items-center mt-2', isDarkMode ? 'text-gray-400' : 'text-gray-500']">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
            </svg>
              {{ displayEducationInfo }}
            </div>

            <div :class="['flex items-center mt-2', isDarkMode ? 'text-gray-400' : 'text-gray-500']">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
              {{ profile?.location || profile?.present_address || 'Location not specified' }}
            </div>

            <div :class="['flex items-center mt-1', isDarkMode ? 'text-gray-400' : 'text-gray-500']">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
              </svg>
              {{ connectionsCount }} connections
            </div>
          </div>

          <!-- Action Buttons -->
          <div v-if="!isOwnProfile" class="flex mt-4 space-x-3 lg:mt-0">
            <button
              @click="$emit('toggle-follow')"
              :disabled="followLoading"
              :class="[
                'px-6 py-2 rounded-lg font-medium transition-colors',
                isFollowing
                  ? isDarkMode 
                    ? 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  : 'bg-orange-500 text-white hover:bg-orange-600'
              ]"
            >
              <span v-if="followLoading" class="mr-2 animate-spin">⟳</span>
              {{ isFollowing ? 'Following' : 'Follow' }}
            </button>
            <button
              @click="$emit('open-message')"
              class="px-6 py-2 font-medium text-white transition-colors bg-orange-600 rounded-lg hover:bg-orange-700"
            >
              Message
            </button>
          </div>

          <div v-else class="flex gap-3 mt-4 lg:mt-0">
            <button
              @click="$emit('export-cv')"
              class="px-6 py-2 font-medium text-white transition-colors bg-blue-600 rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              Export CV
            </button>
            <button
              @click="$emit('edit-profile')"
              class="px-6 py-2 font-medium text-white transition-colors bg-orange-500 rounded-lg hover:bg-orange-600"
            >
              Edit Profile
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  user: Object,
  profile: Object,
  education: Array,
  workHistories: Array,
  profilePictureUrl: String,
  connectionsCount: Number,
  isFollowing: Boolean,
  followLoading: Boolean,
  isOwnProfile: Boolean,
  isDarkMode: Boolean
})

defineEmits([
  'edit-cover-photo',
  'edit-profile-picture',
  'toggle-follow',
  'open-message',
  'export-cv',
  'edit-profile'
])

const currentEducation = computed(() => {
  if (!props.education || props.education.length === 0) return null
  return props.education.find(edu => edu.is_current) || props.education[0]
})

const displayHeadline = computed(() => {
  return props.profile?.headline || props.profile?.present_occupation || 'Alumni'
})

const displayEducationInfo = computed(() => {
  if (!currentEducation.value) return null
  const parts = []
  if (currentEducation.value.degree) parts.push(currentEducation.value.degree)
  if (currentEducation.value.institution) parts.push(currentEducation.value.institution)
  return parts.join(' at ')
})
</script>
