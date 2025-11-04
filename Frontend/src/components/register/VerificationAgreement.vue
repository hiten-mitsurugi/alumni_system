<script setup>
import { defineProps, defineEmits, ref } from 'vue'
import { CheckCircle, AlertCircle, ChevronDown, ChevronUp } from 'lucide-vue-next'

const props = defineProps({
  form: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['proceed', 'go-back', 'skip-register'])

const agreed = ref(false)
const showDetails = ref(false)

const getEmploymentStatus = (status) => {
  const statusMap = {
    'employed': 'Employed',
    'self_employed': 'Self-Employed',
    'unemployed': 'Unemployed',
    'retired': 'Retired',
    'student': 'Student'
  }
  return statusMap[status] || status
}

const formatAddress = (address) => {
  if (typeof address === 'string') return address
  if (typeof address === 'object') {
    const parts = [
      address.street_address,
      address.barangay,
      address.city_name,
      address.province_name,
      address.postal_code
    ].filter(Boolean)
    return parts.join(', ')
  }
  return 'Not specified'
}
</script>

<template>
  <div class="space-y-6 max-w-3xl mx-auto">
    <!-- Header -->
    <div class="text-center mb-8">
      <div class="flex justify-center mb-4">
        <CheckCircle class="w-16 h-16 text-green-500" />
      </div>
      <h2 class="text-3xl font-bold text-gray-800 mb-2">Verify Your Information</h2>
      <p class="text-gray-600">Please review the information you provided. If everything is correct, click proceed to continue registration.</p>
    </div>

    <!-- Verification Card -->
    <div class="bg-white rounded-xl border-2 border-orange-200 shadow-lg overflow-hidden">
      <!-- Card Header -->
      <div class="bg-gradient-to-r from-orange-50 to-orange-100 px-6 py-4 border-b border-orange-200">
        <h3 class="font-bold text-gray-800 flex items-center gap-2">
          <CheckCircle class="w-5 h-5 text-green-500" />
          Personal Information Summary
        </h3>
      </div>

      <!-- Card Body -->
      <div class="px-6 py-6 space-y-6">
        <!-- Contact Info Section -->
        <div>
          <h4 class="font-semibold text-gray-800 mb-3 text-sm uppercase tracking-wider">Contact Information</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-gray-50 p-4 rounded-lg">
              <p class="text-xs text-gray-600 mb-1">Email</p>
              <p class="font-medium text-gray-800">{{ form.email || 'Not provided' }}</p>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
              <p class="text-xs text-gray-600 mb-1">Contact Number</p>
              <p class="font-medium text-gray-800">{{ form.contact_number || 'Not provided' }}</p>
            </div>
          </div>
        </div>

        <!-- Address Info Section -->
        <div>
          <h4 class="font-semibold text-gray-800 mb-3 text-sm uppercase tracking-wider">Address</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-gray-50 p-4 rounded-lg">
              <p class="text-xs text-gray-600 mb-1">Present Address</p>
              <p class="font-medium text-gray-800 text-sm">{{ formatAddress(form.present_address_data || form.present_address) }}</p>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
              <p class="text-xs text-gray-600 mb-1">Permanent Address</p>
              <p class="font-medium text-gray-800 text-sm">{{ formatAddress(form.permanent_address_data || form.permanent_address) }}</p>
            </div>
          </div>
        </div>

        <!-- Personal Details Section -->
        <div>
          <h4 class="font-semibold text-gray-800 mb-3 text-sm uppercase tracking-wider">Personal Details</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-gray-50 p-4 rounded-lg">
              <p class="text-xs text-gray-600 mb-1">Civil Status</p>
              <p class="font-medium text-gray-800">{{ form.civil_status || 'Not provided' }}</p>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
              <p class="text-xs text-gray-600 mb-1">Gender</p>
              <p class="font-medium text-gray-800">{{ form.gender || 'Not provided' }}</p>
            </div>
          </div>
        </div>

        <!-- Family Info Section -->
        <div>
          <h4 class="font-semibold text-gray-800 mb-3 text-sm uppercase tracking-wider">Family Information</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-gray-50 p-4 rounded-lg">
              <p class="text-xs text-gray-600 mb-1">Mother's Name</p>
              <p class="font-medium text-gray-800 text-sm">{{ form.mothers_name || 'Not provided' }}</p>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
              <p class="text-xs text-gray-600 mb-1">Mother's Occupation</p>
              <p class="font-medium text-gray-800 text-sm">{{ form.mothers_occupation || 'Not provided' }}</p>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
              <p class="text-xs text-gray-600 mb-1">Father's Name</p>
              <p class="font-medium text-gray-800 text-sm">{{ form.fathers_name || 'Not provided' }}</p>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
              <p class="text-xs text-gray-600 mb-1">Father's Occupation</p>
              <p class="font-medium text-gray-800 text-sm">{{ form.fathers_occupation || 'Not provided' }}</p>
            </div>
          </div>
        </div>

        <!-- Employment Status -->
        <div>
          <h4 class="font-semibold text-gray-800 mb-3 text-sm uppercase tracking-wider">Employment</h4>
          <div class="bg-gray-50 p-4 rounded-lg">
            <p class="text-xs text-gray-600 mb-1">Employment Status</p>
            <p class="font-medium text-gray-800">{{ getEmploymentStatus(form.employment_status) || 'Not provided' }}</p>
          </div>
        </div>

        <!-- Expandable Details -->
        <div class="border-t border-gray-200 pt-4">
          <button
            @click="showDetails = !showDetails"
            class="flex items-center gap-2 text-orange-600 hover:text-orange-700 font-medium text-sm transition-colors"
          >
            {{ showDetails ? 'Hide' : 'Show' }} Additional Details
            <ChevronDown v-if="!showDetails" class="w-4 h-4" />
            <ChevronUp v-else class="w-4 h-4" />
          </button>

          <div v-if="showDetails" class="mt-4 pt-4 border-t border-gray-200 space-y-3">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <p class="text-gray-600">Government ID</p>
                <p class="font-medium text-gray-800">{{ form.government_id ? '✓ Uploaded' : '✗ Not uploaded' }}</p>
              </div>
              <div>
                <p class="text-gray-600">Profile Picture</p>
                <p class="font-medium text-gray-800">{{ form.profile_picture ? '✓ Uploaded' : '✗ Not uploaded' }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Agreement Checkbox -->
    <div class="bg-blue-50 border border-blue-200 rounded-xl p-6">
      <label class="flex items-start gap-3 cursor-pointer">
        <input
          v-model="agreed"
          type="checkbox"
          class="w-5 h-5 text-orange-500 border-gray-300 rounded mt-1 cursor-pointer"
        />
        <span class="text-gray-800">
          <span class="font-medium">I confirm that all the information provided above is accurate and correct.</span>
          <p class="text-sm text-gray-600 mt-1">
            I understand that providing false information may result in account suspension or termination.
          </p>
        </span>
      </label>
    </div>

    <!-- Action Buttons -->
    <div class="flex flex-col sm:flex-row gap-3 justify-center pt-6">
      <button
        @click="$emit('go-back')"
        class="px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:border-gray-400 hover:bg-gray-50 font-medium transition-colors cursor-pointer"
      >
        ← Go Back
      </button>
      <button
        @click="$emit('proceed')"
        :disabled="!agreed"
        class="px-6 py-3 bg-gradient-to-r from-orange-600 to-orange-500 text-white rounded-lg hover:from-orange-500 hover:to-orange-600 font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all cursor-pointer"
      >
        ✓ Proceed →
      </button>
    </div>

    <!-- Alternative Option -->
    <div class="text-center pt-4 border-t border-gray-200">
      <p class="text-sm text-gray-600 mb-3">Want to complete registration later?</p>
      <button
        @click="$emit('skip-register')"
        class="text-orange-600 hover:text-orange-700 font-medium text-sm underline transition-colors"
      >
        Skip & Register with Current Info
      </button>
    </div>
  </div>
</template>
