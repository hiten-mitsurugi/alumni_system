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
              class="px-3 py-2 text-sm bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors"
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
                    class="p-1 text-orange-600 hover:bg-orange-100 rounded"
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
            class="px-4 py-2 text-sm font-medium bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors"
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
  certificates: []
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
      certificates: newCareerEnhancement.certificates || []
    }
  } else {
    // Reset form for new career enhancement
    formData.value = {
      certificates: []
    }
  }
}, { immediate: true })

const handleSubmit = () => {
  emit('save', formData.value)
}
</script>