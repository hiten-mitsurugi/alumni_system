<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { GraduationCap, FileText, TrendingUp, Users, ArrowRight, CheckCircle } from 'lucide-vue-next'

const router = useRouter()

const handleProceedHome = () => {
  // Mark as seen in localStorage
  localStorage.setItem('alumni_intro_seen', 'true')
  router.push('/alumni')
}

const handleProceedSurvey = () => {
  // Mark as seen in localStorage
  localStorage.setItem('alumni_intro_seen', 'true')
  router.push('/alumni/survey')
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-orange-50 via-white to-orange-50">
    <!-- Header Section with Orange Gradient -->
    <div class="bg-gradient-to-r from-orange-500 to-orange-600 py-16 px-4 text-white text-center">
      <div class="flex justify-center mb-6">
        <div class="bg-white/20 backdrop-blur-sm rounded-full p-6">
          <GraduationCap class="w-20 h-20" />
        </div>
      </div>
      <h1 class="text-5xl font-bold mb-3">Welcome to ATENDA</h1>
      <p class="text-orange-100 text-xl">Your Alumni Engagement Platform</p>
    </div>

    <!-- Content Section -->
    <div class="max-w-6xl mx-auto px-4 py-12 md:py-16">
      <!-- About Section -->
      <div class="mb-12 bg-white rounded-2xl p-8 shadow-lg">
        <h2 class="text-3xl font-bold text-gray-900 mb-4 flex items-center gap-3">
          <div class="w-1.5 h-10 bg-orange-500 rounded"></div>
          About ATENDA
        </h2>
        <p class="text-gray-700 text-lg leading-relaxed">
          ATENDA is Caraga State University Main Campus's dedicated platform designed to strengthen the bond between 
          the College of Computing and Information Sciences and its alumni community. We believe that staying connected with our graduates is 
          essential for continuous improvement and maintaining the excellence of our institution.
        </p>
      </div>

      <!-- Features Grid -->
      <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <div class="bg-white rounded-xl p-8 shadow-lg border-t-4 border-orange-500 hover:shadow-xl transition-shadow duration-300">
          <div class="bg-gradient-to-br from-orange-500 to-orange-600 w-16 h-16 rounded-xl flex items-center justify-center mb-6">
            <Users class="w-8 h-8 text-white" />
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-3">Network</h3>
          <p class="text-gray-600 leading-relaxed">Connect with fellow alumni, build professional relationships, and expand your network across industries.</p>
        </div>

        <div class="bg-white rounded-xl p-8 shadow-lg border-t-4 border-orange-500 hover:shadow-xl transition-shadow duration-300">
          <div class="bg-gradient-to-br from-orange-500 to-orange-600 w-16 h-16 rounded-xl flex items-center justify-center mb-6">
            <FileText class="w-8 h-8 text-white" />
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-3">Engage</h3>
          <p class="text-gray-600 leading-relaxed">Participate in events, forums, and discussions to stay engaged with the CCIS community and share experiences.</p>
        </div>

        <div class="bg-white rounded-xl p-8 shadow-lg border-t-4 border-orange-500 hover:shadow-xl transition-shadow duration-300">
          <div class="bg-gradient-to-br from-orange-500 to-orange-600 w-16 h-16 rounded-xl flex items-center justify-center mb-6">
            <TrendingUp class="w-8 h-8 text-white" />
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-3">Grow</h3>
          <p class="text-gray-600 leading-relaxed">Share knowledge, mentor others, and discover career development opportunities within our community.</p>
        </div>

        <div class="bg-white rounded-xl p-8 shadow-lg border-t-4 border-orange-500 hover:shadow-xl transition-shadow duration-300">
          <div class="bg-gradient-to-br from-orange-500 to-orange-600 w-16 h-16 rounded-xl flex items-center justify-center mb-6">
            <CheckCircle class="w-8 h-8 text-white" />
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-3">Drive Improvement</h3>
          <p class="text-gray-600 leading-relaxed">Contribute valuable insights that shape curriculum development, enhance educational quality, and drive continuous institutional excellence.</p>
        </div>
      </div>

      <!-- Survey Section -->
      <div class="bg-white rounded-2xl p-10 shadow-xl mb-12">
        <div class="flex items-start gap-4 mb-8">
          <div class="bg-orange-100 rounded-full p-4 flex-shrink-0">
            <CheckCircle class="w-10 h-10 text-orange-600" />
          </div>
          <div>
            <h2 class="text-3xl font-bold text-gray-900 mb-2">Help Us Improve Through Your Feedback</h2>
            <p class="text-gray-600 text-lg">Your input is invaluable to our continuous growth</p>
          </div>
        </div>

        <div class="bg-gradient-to-br from-orange-50 to-orange-100/50 rounded-xl p-8 border border-orange-200">
          <h3 class="font-bold text-2xl mb-6 text-gray-900 flex items-center gap-2">
            <div class="w-1 h-8 bg-orange-500 rounded"></div>
            Why Your Participation Matters
          </h3>
          <div class="grid md:grid-cols-2 gap-6">
            <div class="bg-white rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow border-l-4 border-orange-400">
              <div class="flex items-start gap-3">
                <div class="bg-orange-500 rounded-full p-1.5 mt-1 flex-shrink-0">
                  <div class="w-2 h-2 bg-white rounded-full"></div>
                </div>
                <div>
                  <h4 class="font-bold text-gray-900 mb-1">Curriculum Enhancement</h4>
                  <p class="text-gray-700 text-sm leading-relaxed">Your career experiences help us align our programs with industry needs and emerging trends</p>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow border-l-4 border-orange-400">
              <div class="flex items-start gap-3">
                <div class="bg-orange-500 rounded-full p-1.5 mt-1 flex-shrink-0">
                  <div class="w-2 h-2 bg-white rounded-full"></div>
                </div>
                <div>
                  <h4 class="font-bold text-gray-900 mb-1">Student Success</h4>
                  <p class="text-gray-700 text-sm leading-relaxed">Your feedback guides us in preparing current students for real-world challenges and opportunities</p>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow border-l-4 border-orange-400">
              <div class="flex items-start gap-3">
                <div class="bg-orange-500 rounded-full p-1.5 mt-1 flex-shrink-0">
                  <div class="w-2 h-2 bg-white rounded-full"></div>
                </div>
                <div>
                  <h4 class="font-bold text-gray-900 mb-1">Institutional Accreditation</h4>
                  <p class="text-gray-700 text-sm leading-relaxed">Alumni tracer studies are essential for maintaining and improving our college's accreditation status</p>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow border-l-4 border-orange-400">
              <div class="flex items-start gap-3">
                <div class="bg-orange-500 rounded-full p-1.5 mt-1 flex-shrink-0">
                  <div class="w-2 h-2 bg-white rounded-full"></div>
                </div>
                <div>
                  <h4 class="font-bold text-gray-900 mb-1">Quality Assurance</h4>
                  <p class="text-gray-700 text-sm leading-relaxed">Your responses help us measure the effectiveness of our educational programs and identify areas for improvement</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-8 bg-gradient-to-r from-orange-500/10 to-orange-600/10 rounded-xl p-6 border-2 border-orange-200">
          <div class="flex flex-wrap items-center justify-center gap-6 text-gray-700">
            <div class="flex items-center gap-2">
              <span class="text-2xl">📋</span>
              <div>
                <p class="font-semibold text-sm text-gray-900">Survey Completion Time</p>
                <p class="text-sm">Approximately 10-15 minutes</p>
              </div>
            </div>
            <div class="hidden md:block w-px h-12 bg-orange-300"></div>
            <div class="flex items-center gap-2">
              <span class="text-2xl">🔒</span>
              <div>
                <p class="font-semibold text-sm text-gray-900">Privacy Guarantee</p>
                <p class="text-sm">All responses are confidential</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Data Privacy Act Assurance -->
      <div class="bg-white rounded-2xl p-10 shadow-xl mb-12 border-2 border-blue-200">
        <div class="flex items-start gap-4 mb-6">
          <div class="bg-blue-100 rounded-full p-4 flex-shrink-0">
            <svg class="w-10 h-10 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <div>
            <h2 class="text-3xl font-bold text-gray-900 mb-2">Your Privacy is Protected</h2>
            <p class="text-gray-600 text-lg">Data Privacy Act of 2012 (R.A. 10173) Compliance</p>
          </div>
        </div>

        <div class="bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-xl p-8 border border-blue-200">
          <p class="text-gray-700 leading-relaxed mb-6">
            We are committed to protecting your personal information in accordance with the <span class="font-semibold">Philippine Data Privacy Act of 2012 (Republic Act No. 10173)</span>. 
            Your data privacy rights are our priority, and we implement comprehensive measures to ensure your information is secure.
          </p>
          
          <div class="grid md:grid-cols-2 gap-4">
            <div class="bg-white rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow">
              <div class="flex items-start gap-3">
                <div class="bg-blue-500 rounded-full p-2 mt-1 flex-shrink-0">
                  <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-bold text-gray-900 mb-1">Your Rights Protected</h4>
                  <p class="text-gray-700 text-sm leading-relaxed">Right to be informed, access, rectify, erase, object to processing, and file complaints</p>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow">
              <div class="flex items-start gap-3">
                <div class="bg-blue-500 rounded-full p-2 mt-1 flex-shrink-0">
                  <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-bold text-gray-900 mb-1">Secure Data Handling</h4>
                  <p class="text-gray-700 text-sm leading-relaxed">Organizational, physical, and technical security measures protect your personal information</p>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow">
              <div class="flex items-start gap-3">
                <div class="bg-blue-500 rounded-full p-2 mt-1 flex-shrink-0">
                  <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-bold text-gray-900 mb-1">Lawful Processing</h4>
                  <p class="text-gray-700 text-sm leading-relaxed">Data collected only for legitimate educational purposes with transparency and proportionality</p>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow">
              <div class="flex items-start gap-3">
                <div class="bg-blue-500 rounded-full p-2 mt-1 flex-shrink-0">
                  <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-bold text-gray-900 mb-1">Voluntary Consent</h4>
                  <p class="text-gray-700 text-sm leading-relaxed">Your participation is entirely voluntary with informed and specific consent for data processing</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex justify-center mb-12">
        <button
          @click="handleProceedSurvey"
          class="group bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white px-16 py-5 rounded-xl font-bold text-xl shadow-2xl hover:shadow-orange-500/50 transform hover:scale-105 transition-all duration-200 flex items-center justify-center gap-3"
        >
          <FileText class="w-6 h-6" />
          Proceed
          <ArrowRight class="w-6 h-6 group-hover:translate-x-1 transition-transform" />
        </button>
      </div>

      <!-- Footer Note -->
      <div class="text-center text-gray-600 pb-8">
        <p class="text-sm">
          © 2025 Caraga State University Main Campus - College of Computing and Information Sciences | Building Stronger Alumni Connections
        </p>
      </div>
    </div>
  </div>
</template>
