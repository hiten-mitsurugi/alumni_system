<script setup>
import { defineProps, defineEmits } from 'vue';
import { CheckCircle, XCircle } from 'lucide-vue-next';

defineProps({
  form: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['accept', 'decline']);
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-4">
    <div class="max-w-4xl w-full">
      <!-- Header Section -->
      <div class="text-center mb-12">
        <div class="flex justify-center mb-6">
          <div class="w-16 h-16 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        <h1 class="text-4xl font-bold text-gray-800 mb-3">We Value Your Insights</h1>
        <p class="text-lg text-gray-600">Help us understand your career journey and experiences</p>
      </div>

      <!-- Main Content Card -->
      <div class="bg-white rounded-xl shadow-lg overflow-hidden mb-8">
        <!-- Invitation Section -->
        <div class="p-8 bg-gradient-to-r from-orange-50 to-yellow-50 border-b-2 border-orange-100">
          <div class="flex items-start gap-4 mb-6">
            <div class="flex-shrink-0">
              <CheckCircle class="w-8 h-8 text-orange-600" />
            </div>
            <div>
              <h2 class="text-2xl font-semibold text-gray-800 mb-2">Survey Invitation & Consent</h2>
              <p class="text-gray-700 leading-relaxed">
                Dear Alumnus/Alumna,
              </p>
            </div>
          </div>
          
          <p class="text-gray-700 leading-relaxed mb-4 text-justify">
            We would like to cordially invite you to participate in our <span class="font-semibold">Alumni Tracer Survey</span>. 
            Your participation is entirely voluntary, and your responses will be kept strictly confidential and used solely for 
            academic and institutional research purposes.
          </p>
        </div>

        <!-- Purpose Section -->
        <div class="p-8 border-b border-gray-200">
          <h3 class="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Purpose of This Survey
          </h3>
          <div class="space-y-3 ml-8 text-gray-700">
            <div class="flex gap-3">
              <span class="text-orange-600 font-bold mt-1">•</span>
              <p>
                <span class="font-semibold">Career Development:</span> Track your professional growth and career 
                progression since graduation
              </p>
            </div>
            <div class="flex gap-3">
              <span class="text-orange-600 font-bold mt-1">•</span>
              <p>
                <span class="font-semibold">Educational Impact:</span> Assess the relevance and effectiveness of 
                our academic programs
              </p>
            </div>
            <div class="flex gap-3">
              <span class="text-orange-600 font-bold mt-1">•</span>
              <p>
                <span class="font-semibold">Institutional Improvement:</span> Identify areas for curriculum 
                enhancement and skill development
              </p>
            </div>
            <div class="flex gap-3">
              <span class="text-orange-600 font-bold mt-1">•</span>
              <p>
                <span class="font-semibold">Alumni Network:</span> Strengthen ATENDA and opportunities 
                within our alumni community
              </p>
            </div>
          </div>
        </div>

        <!-- How It Helps Section -->
        <div class="p-8 border-b border-gray-200">
          <h3 class="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            How Your Responses Help Us
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 ml-8">
            <div class="bg-orange-50 rounded-lg p-4 border-l-4 border-orange-600">
              <p class="font-semibold text-gray-800 mb-2">Curriculum Development</p>
              <p class="text-sm text-gray-600">
                Your feedback helps us align our programs with industry demands and skill requirements
              </p>
            </div>
            <div class="bg-orange-50 rounded-lg p-4 border-l-4 border-orange-600">
              <p class="font-semibold text-gray-800 mb-2">Student Preparation</p>
              <p class="text-sm text-gray-600">
                We use your experiences to better prepare current students for career success
              </p>
            </div>
            <div class="bg-orange-50 rounded-lg p-4 border-l-4 border-orange-600">
              <p class="font-semibold text-gray-800 mb-2">Strategic Planning</p>
              <p class="text-sm text-gray-600">
                Your insights inform institutional strategies and educational initiatives
              </p>
            </div>
            <div class="bg-orange-50 rounded-lg p-4 border-l-4 border-orange-600">
              <p class="font-semibold text-gray-800 mb-2">Networking Opportunities</p>
              <p class="text-sm text-gray-600">
                Participating engages you with fellow alumni through ATENDA and institutional programs
              </p>
            </div>
          </div>
        </div>

        <!-- Survey Details Section -->
        <div class="p-8 border-b border-gray-200 bg-blue-50">
          <h3 class="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Survey Information
          </h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 ml-8">
            <div class="bg-white rounded-lg p-4 shadow-sm">
              <p class="text-xs text-gray-500 font-semibold">ESTIMATED TIME</p>
              <p class="text-lg font-bold text-blue-600">10-15 min</p>
            </div>
            <div class="bg-white rounded-lg p-4 shadow-sm">
              <p class="text-xs text-gray-500 font-semibold">QUESTIONS</p>
              <p class="text-lg font-bold text-blue-600">15-25</p>
            </div>
            <div class="bg-white rounded-lg p-4 shadow-sm">
              <p class="text-xs text-gray-500 font-semibold">CONFIDENTIALITY</p>
              <p class="text-lg font-bold text-blue-600">Protected</p>
            </div>
            <div class="bg-white rounded-lg p-4 shadow-sm">
              <p class="text-xs text-gray-500 font-semibold">PARTICIPATION</p>
              <p class="text-lg font-bold text-blue-600">Optional</p>
            </div>
          </div>
        </div>

        <!-- Data Privacy Act Compliance -->
        <div class="p-8 border-b border-gray-200 bg-blue-50">
          <h3 class="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            Data Privacy Act Compliance (R.A. 10173)
          </h3>
          <p class="text-gray-700 leading-relaxed mb-4 ml-8">
            In compliance with the <span class="font-semibold">Philippine Data Privacy Act of 2012 (Republic Act No. 10173)</span>, 
            we assure you that your personal information is protected and will be processed with the highest standards of data privacy and security.
          </p>
          <ul class="space-y-2 ml-8 text-gray-700">
            <li class="flex gap-3">
              <span class="text-blue-600 font-bold">🔒</span>
              <p><span class="font-semibold">Your Rights:</span> You have the right to be informed, access your data, correct inaccuracies, object to processing, and file complaints with the National Privacy Commission.</p>
            </li>
            <li class="flex gap-3">
              <span class="text-blue-600 font-bold">🛡️</span>
              <p><span class="font-semibold">Data Security:</span> We implement organizational, physical, and technical security measures to protect your information from unauthorized access or disclosure.</p>
            </li>
            <li class="flex gap-3">
              <span class="text-blue-600 font-bold">⚖️</span>
              <p><span class="font-semibold">Lawful Processing:</span> Your data will be collected and processed only for legitimate educational purposes in accordance with principles of transparency and proportionality.</p>
            </li>
            <li class="flex gap-3">
              <span class="text-blue-600 font-bold">✅</span>
              <p><span class="font-semibold">Your Consent:</span> By participating, you provide voluntary and informed consent to the collection and processing of your personal information for institutional research and development.</p>
            </li>
          </ul>
        </div>

        <!-- Confidentiality Statement -->
        <div class="p-8 border-b border-gray-200">
          <h3 class="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            Data Protection & Confidentiality
          </h3>
          <ul class="space-y-2 ml-8 text-gray-700">
            <li class="flex gap-3">
              <span class="text-green-600 font-bold">✓</span>
              <p>All personal information will be kept confidential and secure</p>
            </li>
            <li class="flex gap-3">
              <span class="text-green-600 font-bold">✓</span>
              <p>Your responses will be used for statistical analysis only, not for individual identification</p>
            </li>
            <li class="flex gap-3">
              <span class="text-green-600 font-bold">✓</span>
              <p>Data will be stored securely and accessible only to authorized research personnel</p>
            </li>
            <li class="flex gap-3">
              <span class="text-green-600 font-bold">✓</span>
              <p>You may withdraw from the survey at any time without penalties or consequences</p>
            </li>
          </ul>
        </div>

        <!-- Consent Statement -->
        <div class="p-8 bg-gradient-to-r from-green-50 to-emerald-50 border-t-2 border-green-100">
          <div class="flex items-start gap-4">
            <div class="flex-shrink-0 mt-1">
              <CheckCircle class="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p class="text-gray-800 leading-relaxed">
                <span class="font-semibold">By proceeding to the survey,</span> you consent to participate in this 
                tracer study and acknowledge that you have read and understood the information provided above. 
                Your participation will greatly contribute to our institutional development and the success of future alumni.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <!-- Decline Button -->
        <button
          @click="emit('decline')"
          class="group relative px-8 py-4 bg-gradient-to-r from-gray-100 to-gray-200 hover:from-gray-200 hover:to-gray-300 text-gray-800 font-bold rounded-xl transition-all duration-300 transform hover:scale-105 flex items-center justify-center gap-2 shadow-md hover:shadow-lg border-2 border-gray-300"
        >
          <XCircle class="w-6 h-6 text-gray-600 group-hover:text-gray-800" />
          <span>Decline & Submit Registration</span>
        </button>

        <!-- Accept Button -->
        <button
          @click="emit('accept')"
          class="group relative px-8 py-4 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-bold rounded-xl transition-all duration-300 transform hover:scale-105 flex items-center justify-center gap-2 shadow-lg hover:shadow-xl"
        >
          <CheckCircle class="w-6 h-6 text-white group-hover:text-yellow-100" />
          <span>Accept & Proceed to Survey</span>
        </button>
      </div>

      <!-- Footer Info -->
      <div class="text-center text-sm text-gray-600">
        <p class="mb-2">
          For questions or concerns about this survey, please contact our Alumni Relations Office
        </p>
        <p>
          <span class="font-semibold">Email:</span> alumni@institution.edu | 
          <span class="font-semibold">Phone:</span> +63 (0) XXXX-XXXX
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Smooth transitions for all interactive elements */
button {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Responsive text sizing */
@media (max-width: 768px) {
  .text-4xl {
    font-size: 1.875rem;
  }
  
  .text-2xl {
    font-size: 1.5rem;
  }
}
</style>
