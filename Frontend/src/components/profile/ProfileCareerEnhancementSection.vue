<template>
  <div :class="[
    'rounded-lg shadow-lg p-6 transition-colors duration-200',
    themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white'
  ]">
    <SectionPrivacyControl 
      title="Career Enhancement"
      :is-own-profile="isOwnProfile"
      :section-visibility="sectionVisibility"
      @add="$emit('add')"
      @visibility-changed="handleVisibilityChange"
    />

    <div v-if="hasCareerEnhancementData" class="space-y-6">
      <!-- Certificates Section -->
      <div v-if="careerEnhancement.certificates && careerEnhancement.certificates.length > 0" class="space-y-4">
        <h4 :class="[
          'text-lg font-semibold border-b pb-2',
          themeStore.isDarkMode ? 'text-gray-200 border-gray-600' : 'text-gray-800 border-gray-200'
        ]">Professional Certificates</h4>
        
        <div class="space-y-3">
          <div 
            v-for="certificate in careerEnhancement.certificates" 
            :key="certificate.id"
            class="group border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all duration-200"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center space-x-3">
                  <div class="flex-shrink-0 w-3 h-3 bg-green-600 rounded-full"></div>
                  <h5 :class="[
                    'font-medium text-lg',
                    themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                  ]">{{ certificate.certificate_type }}</h5>
                  <span v-if="certificate.is_active === false" class="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    Expired
                  </span>
                  <span v-else-if="certificate.is_active" class="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Active
                  </span>
                </div>
                
                <div class="ml-6 mt-3 space-y-2 text-sm">
                  <!-- Issuing Body -->
                  <div v-if="certificate.issuing_body" class="flex items-center">
                    <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                    <span :class="[
                      'font-medium mr-2',
                      themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                    ]">Issued by:</span>
                    <span :class="[
                      themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                    ]">{{ certificate.issuing_body }}</span>
                  </div>
                  
                  <!-- Certificate Number -->
                  <div v-if="certificate.certificate_number" class="flex items-center">
                    <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                    </svg>
                    <span :class="[
                      'font-medium mr-2',
                      themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                    ]">Certificate #:</span>
                    <span :class="[
                      'px-2 py-1 rounded text-xs font-mono',
                      themeStore.isDarkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-gray-800'
                    ]">{{ certificate.certificate_number }}</span>
                  </div>
                  
                  <!-- Date Issued -->
                  <div v-if="certificate.date_issued" class="flex items-center">
                    <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span :class="[
                      'font-medium mr-2',
                      themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                    ]">Date Issued:</span>
                    <span :class="[
                      themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                    ]">{{ formatDate(certificate.date_issued) }}</span>
                  </div>
                  
                  <!-- Expiry Date -->
                  <div v-if="certificate.expiry_date" class="flex items-center">
                    <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span :class="[
                      'font-medium mr-2',
                      themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                    ]">Expires:</span>
                    <span :class="getExpiryClass(certificate.expiry_date)">
                      {{ formatDate(certificate.expiry_date) }}
                    </span>
                  </div>
                  
                  <!-- Certificate File -->
                  <div v-if="certificate.certificate_file" class="flex items-center">
                    <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    <span :class="[
                      'font-medium mr-2',
                      themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                    ]">Document:</span>
                    <a 
                      :href="certificate.certificate_file"
                      target="_blank"
                      class="text-blue-600 hover:text-blue-800 underline text-xs"
                    >View Certificate</a>
                  </div>
                </div>
              </div>
              
              <div v-if="isOwnProfile" class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button 
                  @click="$emit('edit-certificate', certificate)"
                  class="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                  title="Edit certificate"
                >
                  <PencilIcon class="w-4 h-4" />
                </button>
                <button 
                  @click="$emit('delete-certificate', certificate.id)"
                  class="p-2 text-gray-400 hover:text-red-600 transition-colors"
                  title="Delete certificate"
                >
                  <TrashIcon class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Civil Service Examination Section -->
      <div v-if="careerEnhancement.cse_status" class="space-y-4">
        <h4 :class="[
          'text-lg font-semibold border-b pb-2',
          themeStore.isDarkMode ? 'text-gray-200 border-gray-600' : 'text-gray-800 border-gray-200'
        ]">Civil Service Examination</h4>
        
        <div class="border border-gray-200 rounded-lg p-4">
          <div class="flex items-center space-x-3">
            <div :class="[
              'flex-shrink-0 w-3 h-3 rounded-full',
              careerEnhancement.cse_status.is_passer ? 'bg-green-600' : 'bg-red-600'
            ]"></div>
            <div class="flex-1">
              <div class="flex items-center space-x-4">
                <span :class="[
                  'font-medium text-lg',
                  themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                ]">
                  {{ careerEnhancement.cse_status.is_passer ? 'CSE Passer' : 'Not a CSE Passer' }}
                </span>
                <span :class="[
                  'px-3 py-1 rounded-full text-sm font-medium',
                  careerEnhancement.cse_status.is_passer 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                ]">
                  {{ careerEnhancement.cse_status.is_passer ? 'Passer' : 'Non-passer' }}
                </span>
              </div>
              
              <div v-if="careerEnhancement.cse_status.is_passer" class="mt-2 space-y-1 text-sm">
                <div v-if="careerEnhancement.cse_status.examination_type" class="flex items-center">
                  <span :class="[
                    'font-medium mr-2',
                    themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                  ]">Examination Type:</span>
                  <span :class="[
                    themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                  ]">{{ formatCSEType(careerEnhancement.cse_status.examination_type) }}</span>
                </div>
                
                <div v-if="careerEnhancement.cse_status.date_passed" class="flex items-center">
                  <span :class="[
                    'font-medium mr-2',
                    themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                  ]">Date Passed:</span>
                  <span :class="[
                    themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                  ]">{{ formatDate(careerEnhancement.cse_status.date_passed) }}</span>
                </div>
                
                <div v-if="careerEnhancement.cse_status.rating" class="flex items-center">
                  <span :class="[
                    'font-medium mr-2',
                    themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                  ]">Rating:</span>
                  <span :class="[
                    'px-2 py-1 rounded font-semibold text-sm',
                    getRatingClass(careerEnhancement.cse_status.rating)
                  ]">{{ careerEnhancement.cse_status.rating }}%</span>
                </div>
                
                <div v-if="careerEnhancement.cse_status.eligibility" class="flex items-center">
                  <span :class="[
                    'font-medium mr-2',
                    themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                  ]">Eligibility:</span>
                  <span :class="[
                    themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                  ]">{{ careerEnhancement.cse_status.eligibility }}</span>
                </div>
              </div>
            </div>
            
            <div v-if="isOwnProfile" class="flex items-center gap-2">
              <button 
                @click="$emit('edit-cse')"
                class="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                title="Edit CSE status"
              >
                <PencilIcon class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-8">
      <div class="mx-auto w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mb-4">
        <svg class="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      <p :class="[
        'text-lg font-medium',
        themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-900'
      ]">No career enhancement data</p>
      <p :class="[
        'text-sm mt-2',
        themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'
      ]">{{ isOwnProfile ? 'Add your certificates and CSE status to showcase your professional development' : 'This user hasn\'t added any career enhancement information yet' }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'
import SectionPrivacyControl from '@/components/profile/SectionPrivacyControl.vue'

const props = defineProps({
  careerEnhancement: {
    type: Object,
    default: () => ({})
  },
  isOwnProfile: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['add', 'edit-certificate', 'delete-certificate', 'edit-cse', 'visibility-changed'])

const themeStore = useThemeStore()
const sectionVisibility = ref('connections_only')

const hasCareerEnhancementData = computed(() => {
  return (props.careerEnhancement.certificates && props.careerEnhancement.certificates.length > 0) ||
         props.careerEnhancement.cse_status
})

const handleVisibilityChange = (visibility) => {
  sectionVisibility.value = visibility
  emit('visibility-changed', { section: 'career_enhancement', visibility })
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long',
    day: 'numeric'
  })
}

const formatCSEType = (type) => {
  const types = {
    'professional': 'Professional Level',
    'subprofessional': 'Sub-professional Level',
    'first_level': 'First Level',
    'second_level': 'Second Level'
  }
  return types[type] || type
}

const getExpiryClass = (expiryDate) => {
  if (!expiryDate) return themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
  
  const today = new Date()
  const expiry = new Date(expiryDate)
  const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
  
  if (daysUntilExpiry < 0) {
    return 'text-red-600 font-medium' // Expired
  } else if (daysUntilExpiry <= 30) {
    return 'text-yellow-600 font-medium' // Expiring soon
  } else {
    return themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
  }
}

const getRatingClass = (rating) => {
  const numRating = parseFloat(rating)
  if (numRating >= 90) {
    return 'bg-green-100 text-green-800'
  } else if (numRating >= 80) {
    return 'bg-blue-100 text-blue-800'
  } else if (numRating >= 75) {
    return 'bg-yellow-100 text-yellow-800'
  } else {
    return 'bg-red-100 text-red-800'
  }
}
</script>