<template>
  <div :class="[
    'rounded-lg shadow-lg p-6 transition-colors duration-200',
    themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white'
  ]">
    <SectionPrivacyControl 
      title="Membership in Organizations"
      :is-own-profile="isOwnProfile"
      :section-visibility="sectionVisibility"
      @add="$emit('add')"
      @visibility-changed="handleVisibilityChange"
    />

    <div v-if="memberships && memberships.length > 0" class="space-y-4">
      <div 
        v-for="membership in memberships" 
        :key="membership.id"
        class="group border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all duration-200"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0 w-3 h-3 bg-blue-600 rounded-full"></div>
              <h3 :class="[
                'text-lg font-semibold',
                themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
              ]">{{ membership.organization_name }}</h3>
            </div>
            
            <div class="ml-6 mt-2 space-y-2">
              <div v-if="membership.position" class="flex items-center text-sm">
                <span :class="[
                  'font-medium mr-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Position:</span>
                <span :class="[
                  themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                ]">{{ membership.position }}</span>
              </div>
              
              <div v-if="membership.membership_type" class="flex items-center text-sm">
                <span :class="[
                  'font-medium mr-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Type:</span>
                <span :class="[
                  'px-2 py-1 rounded-full text-xs',
                  getMembershipTypeClass(membership.membership_type)
                ]">{{ formatMembershipType(membership.membership_type) }}</span>
              </div>
              
              <div v-if="membership.date_joined" class="flex items-center text-sm">
                <span :class="[
                  'font-medium mr-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Joined:</span>
                <span :class="[
                  themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                ]">{{ formatDate(membership.date_joined) }}</span>
              </div>
              
              <div v-if="membership.date_ended" class="flex items-center text-sm">
                <span :class="[
                  'font-medium mr-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Ended:</span>
                <span :class="[
                  themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                ]">{{ formatDate(membership.date_ended) }}</span>
              </div>
              
              <div v-if="membership.description" class="text-sm">
                <span :class="[
                  'font-medium',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Description:</span>
                <p :class="[
                  'mt-1',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
                ]">{{ membership.description }}</p>
              </div>
            </div>
          </div>
          
          <!-- Edit/Delete buttons for own profile -->
          <div v-if="isOwnProfile" class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button 
              @click="$emit('edit', membership)"
              class="p-2 text-gray-400 hover:text-blue-600 transition-colors"
              title="Edit membership"
            >
              <PencilIcon class="w-4 h-4" />
            </button>
            <button 
              @click="$emit('delete', membership.id)"
              class="p-2 text-gray-400 hover:text-red-600 transition-colors"
              title="Delete membership"
            >
              <TrashIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-8">
      <div class="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
        <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      </div>
      <p :class="[
        'text-lg font-medium',
        themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-900'
      ]">No organization memberships</p>
      <p :class="[
        'text-sm mt-2',
        themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'
      ]">{{ isOwnProfile ? 'Add your organization memberships to showcase your professional involvement' : 'This user hasn\'t added any organization memberships yet' }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'
import SectionPrivacyControl from '@/components/profile/SectionPrivacyControl.vue'

defineProps({
  memberships: {
    type: Array,
    default: () => []
  },
  isOwnProfile: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['add', 'edit', 'delete', 'visibility-changed'])

const themeStore = useThemeStore()
const sectionVisibility = ref('connections_only')

const handleVisibilityChange = (visibility) => {
  sectionVisibility.value = visibility
  emit('visibility-changed', { section: 'memberships', visibility })
}

const getMembershipTypeClass = (type) => {
  const classes = {
    'active': 'bg-green-100 text-green-800',
    'inactive': 'bg-gray-100 text-gray-800',
    'honorary': 'bg-purple-100 text-purple-800',
    'lifetime': 'bg-blue-100 text-blue-800'
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

const formatMembershipType = (type) => {
  const types = {
    'active': 'Active Member',
    'inactive': 'Inactive Member',
    'honorary': 'Honorary Member',
    'lifetime': 'Lifetime Member'
  }
  return types[type] || type
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long'
  })
}
</script>