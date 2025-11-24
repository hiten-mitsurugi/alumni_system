<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="$emit('close')">
    <div :class="[
      'w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-lg shadow-lg',
      themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white'
    ]">
      <div :class="[
        'p-6 border-b',
        themeStore.isDarkMode ? 'border-gray-700' : 'border-gray-200'
      ]">
        <h2 :class="[
          'text-xl font-semibold',
          themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
        ]">
          {{ careerEnhancement ? 'Edit Career Enhancement' : 'Add Career Enhancement' }}
        </h2>
        <p :class="[
          'text-sm mt-1',
          themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'
        ]">
          Manage your professional certificates and civil service examination status
        </p>
      </div>

      <div class="p-6 space-y-6">
        <!-- Certificates Section -->
        <div>
          <div class="flex items-center justify-between mb-4">
            <h3 :class="[
              'text-lg font-medium',
              themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
            ]">
              Professional Certificates
            </h3>
            <button
              @click="addCertificate"
              type="button"
              class="px-3 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Add Certificate
            </button>
          </div>

          <!-- Certificate List -->
          <div v-if="formData.certificates && formData.certificates.length > 0" class="space-y-3">
            <div 
              v-for="(cert, index) in formData.certificates" 
              :key="index"
              :class="[
                'p-4 border rounded-lg',
                themeStore.isDarkMode ? 'border-gray-600 bg-gray-700' : 'border-gray-200 bg-gray-50'
              ]"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <h4 :class="[
                    'font-medium',
                    themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                  ]">
                    {{ cert.certificate_type }}
                  </h4>
                  <p :class="[
                    'text-sm',
                    themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                  ]">
                    Issued by {{ cert.issuing_body }}
                  </p>
                  <div class="flex items-center space-x-4 text-xs text-gray-500 mt-1">
                    <span v-if="cert.date_issued">Issued: {{ formatDate(cert.date_issued) }}</span>
                    <span v-if="cert.expiry_date">Expires: {{ formatDate(cert.expiry_date) }}</span>
                  </div>
                </div>
                <div class="flex space-x-2">
                  <button
                    @click="editCertificate(index)"
                    type="button"
                    class="p-1 text-blue-600 hover:bg-blue-100 rounded"
                  >
                    <PencilIcon class="w-4 h-4" />
                  </button>
                  <button
                    @click="removeCertificate(index)"
                    type="button"
                    class="p-1 text-red-600 hover:bg-red-100 rounded"
                  >
                    <TrashIcon class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty certificates state -->
          <div v-else :class="[
            'p-6 text-center border-2 border-dashed rounded-lg',
            themeStore.isDarkMode ? 'border-gray-600' : 'border-gray-300'
          ]">
            <p :class="[
              'text-sm',
              themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'
            ]">
              No certificates added yet. Click "Add Certificate" to get started.
            </p>
          </div>
        </div>

        <!-- Current Employment Status Section -->
        <div :class="[
          'border-t pt-6',
          themeStore.isDarkMode ? 'border-gray-700' : 'border-gray-200'
        ]">
          <h3 :class="[
            'text-lg font-medium mb-4',
            themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
          ]">
            Current Employment Status
          </h3>

          <!-- Employment Status -->
          <div class="space-y-4">
            <div>
              <label :class="[
                'block text-sm font-medium mb-2',
                themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
              ]">
                Status
              </label>
              <select
                v-model="formData.cse_status.status"
                :class="[
                  'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                  themeStore.isDarkMode 
                    ? 'bg-gray-700 border-gray-600 text-white' 
                    : 'bg-white border-gray-300 text-gray-900'
                ]"
              >
                <option value="employed">Employed</option>
                <option value="unemployed">Unemployed</option>
                <option value="self_employed">Self-Employed</option>
                <option value="student">Student</option>
                <option value="retired">Retired</option>
              </select>
            </div>

            <!-- Employment Details (shown only if employed or self_employed) -->
            <div v-if="formData.cse_status.status === 'employed' || formData.cse_status.status === 'self_employed'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label :class="[
                  'block text-sm font-medium mb-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
                ]">
                  Current Position
                </label>
                <input
                  v-model="formData.cse_status.current_position"
                  type="text"
                  :class="[
                    'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                    themeStore.isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white' 
                      : 'bg-white border-gray-300 text-gray-900'
                  ]"
                  placeholder="e.g., Software Engineer"
                />
              </div>

              <div>
                <label :class="[
                  'block text-sm font-medium mb-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
                ]">
                  Current Company
                </label>
                <input
                  v-model="formData.cse_status.current_company"
                  type="text"
                  :class="[
                    'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                    themeStore.isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white' 
                      : 'bg-white border-gray-300 text-gray-900'
                  ]"
                  placeholder="e.g., Tech Company Inc."
                />
              </div>

              <div>
                <label :class="[
                  'block text-sm font-medium mb-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
                ]">
                  Industry
                </label>
                <input
                  v-model="formData.cse_status.industry"
                  type="text"
                  :class="[
                    'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                    themeStore.isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white' 
                      : 'bg-white border-gray-300 text-gray-900'
                  ]"
                  placeholder="e.g., Information Technology"
                />
              </div>

              <div>
                <label :class="[
                  'block text-sm font-medium mb-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
                ]">
                  Start Date
                </label>
                <input
                  v-model="formData.cse_status.start_date"
                  type="date"
                  :class="[
                    'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                    themeStore.isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white' 
                      : 'bg-white border-gray-300 text-gray-900'
                  ]"
                />
              </div>

              <div>
                <label class="flex items-center space-x-3">
                  <input
                    v-model="formData.cse_status.is_current"
                    type="checkbox"
                    class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span :class="[
                    'font-medium',
                    themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                  ]">
                    I currently work here
                  </span>
                </label>
              </div>

              <div v-if="!formData.cse_status.is_current">
                <label :class="[
                  'block text-sm font-medium mb-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
                ]">
                  End Date
                </label>
                <input
                  v-model="formData.cse_status.end_date"
                  type="date"
                  :class="[
                    'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                    themeStore.isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white' 
                      : 'bg-white border-gray-300 text-gray-900'
                  ]"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Privacy Setting -->
        <div :class="[
          'border-t pt-6',
          themeStore.isDarkMode ? 'border-gray-700' : 'border-gray-200'
        ]">
          <label :class="[
            'block text-sm font-medium mb-2',
            themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
          ]">
            Visibility
          </label>
          <select
            v-model="formData.visibility"
            :class="[
              'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
              themeStore.isDarkMode 
                ? 'bg-gray-700 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-900'
            ]"
          >
            <option value="public">Public</option>
            <option value="connections_only">Connections Only</option>
            <option value="private">Private</option>
          </select>
        </div>

        <!-- Form Actions -->
        <div :class="[
          'flex justify-end space-x-3 pt-4 border-t',
          themeStore.isDarkMode ? 'border-gray-700' : 'border-gray-200'
        ]">
          <button
            type="button"
            @click="$emit('close')"
            :class="[
              'px-4 py-2 text-sm font-medium rounded-md transition-colors',
              themeStore.isDarkMode
                ? 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
            ]"
          >
            Cancel
          </button>
          <button
            type="button"
            @click="handleSubmit"
            class="px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            {{ careerEnhancement ? 'Update' : 'Save' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Certificate Modal -->
    <CertificateModal
      v-if="showCertificateModal"
      :certificate="selectedCertificate"
      @close="closeCertificateModal"
      @save="saveCertificate"
    />
  </div>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'
import CertificateModal from './CertificateModal.vue'

const props = defineProps({
  careerEnhancement: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

const themeStore = useThemeStore()

// Modal states
const showCertificateModal = ref(false)
const selectedCertificate = ref(null)
const selectedCertificateIndex = ref(-1)

// Form data
const formData = ref({
  certificates: [],
  cse_status: {
    status: 'unemployed',
    current_position: '',
    current_company: '',
    industry: '',
    start_date: '',
    end_date: '',
    is_current: true
  },
  visibility: 'connections_only'
})

// Certificate management
const addCertificate = () => {
  selectedCertificate.value = null
  selectedCertificateIndex.value = -1
  showCertificateModal.value = true
}

const editCertificate = (index) => {
  selectedCertificate.value = { ...formData.value.certificates[index] }
  selectedCertificateIndex.value = index
  showCertificateModal.value = true
}

const removeCertificate = (index) => {
  if (confirm('Are you sure you want to remove this certificate?')) {
    formData.value.certificates.splice(index, 1)
  }
}

const closeCertificateModal = () => {
  showCertificateModal.value = false
  selectedCertificate.value = null
  selectedCertificateIndex.value = -1
}

const saveCertificate = (certificateData) => {
  if (selectedCertificateIndex.value >= 0) {
    // Edit existing certificate
    formData.value.certificates[selectedCertificateIndex.value] = certificateData
  } else {
    // Add new certificate
    formData.value.certificates.push(certificateData)
  }
  closeCertificateModal()
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short',
    day: 'numeric'
  })
}

// Watch for changes in careerEnhancement prop to populate form
watch(() => props.careerEnhancement, (newCareerEnhancement) => {
  if (newCareerEnhancement) {
    formData.value = {
      certificates: newCareerEnhancement.certificates || [],
      cse_status: {
        status: newCareerEnhancement.cse_status?.status || 'unemployed',
        current_position: newCareerEnhancement.cse_status?.current_position || '',
        current_company: newCareerEnhancement.cse_status?.current_company || '',
        industry: newCareerEnhancement.cse_status?.industry || '',
        start_date: newCareerEnhancement.cse_status?.start_date || '',
        end_date: newCareerEnhancement.cse_status?.end_date || '',
        is_current: newCareerEnhancement.cse_status?.is_current ?? true
      },
      visibility: newCareerEnhancement.visibility || 'connections_only'
    }
  } else {
    // Reset form for new career enhancement
    formData.value = {
      certificates: [],
      cse_status: {
        status: 'unemployed',
        current_position: '',
        current_company: '',
        industry: '',
        start_date: '',
        end_date: '',
        is_current: true
      },
      visibility: 'connections_only'
    }
  }
}, { immediate: true })

const handleSubmit = () => {
  // Clean up form data
  const cleanedData = { ...formData.value }
  
  // Remove empty strings for CSE fields
  Object.keys(cleanedData.cse_status).forEach(key => {
    if (cleanedData.cse_status[key] === '') {
      cleanedData.cse_status[key] = null
    }
  })

  emit('save', cleanedData)
}
</script>