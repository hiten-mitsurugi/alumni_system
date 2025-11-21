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
  <div class="min-h-screen bg-gradient-to-br from-orange-50 via-white to-orange-50 flex items-center justify-center p-4">
    <div class="max-w-4xl w-full">
      <!-- Main Card -->
      <div class="bg-white rounded-2xl shadow-2xl overflow-hidden">
        <!-- Header Section with Orange Gradient -->
        <div class="bg-gradient-to-r from-orange-500 to-orange-600 p-8 text-white text-center">
          <div class="flex justify-center mb-4">
            <div class="bg-white/20 backdrop-blur-sm rounded-full p-4">
              <GraduationCap class="w-16 h-16" />
            </div>
          </div>
          <h1 class="text-4xl font-bold mb-2">Welcome to A-Connect</h1>
          <p class="text-orange-100 text-lg">Your Alumni Engagement Platform</p>
        </div>

        <!-- Content Section -->
        <div class="p-8 md:p-12">
          <!-- About Section -->
          <div class="mb-10">
            <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <div class="w-1 h-8 bg-orange-500 rounded"></div>
              About A-Connect
            </h2>
            <p class="text-gray-700 text-lg leading-relaxed">
              A-Connect is Caraga State University Main Campus's dedicated platform designed to strengthen the bond between 
              the College of Computing and Information Sciences and its alumni community. We believe that staying connected with our graduates is 
              essential for continuous improvement and maintaining the excellence of our institution.
            </p>
          </div>

          <!-- Features Grid -->
          <div class="grid md:grid-cols-3 gap-6 mb-10">
            <div class="bg-orange-50 rounded-lg p-6 border border-orange-100">
              <div class="bg-orange-500 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Users class="w-6 h-6 text-white" />
              </div>
              <h3 class="font-semibold text-gray-900 mb-2">Stay Connected</h3>
              <p class="text-gray-600 text-sm">Engage with fellow alumni and university updates</p>
            </div>

            <div class="bg-orange-50 rounded-lg p-6 border border-orange-100">
              <div class="bg-orange-500 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <FileText class="w-6 h-6 text-white" />
              </div>
              <h3 class="font-semibold text-gray-900 mb-2">Share Your Journey</h3>
              <p class="text-gray-600 text-sm">Update your career progress and achievements</p>
            </div>

            <div class="bg-orange-50 rounded-lg p-6 border border-orange-100">
              <div class="bg-orange-500 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <TrendingUp class="w-6 h-6 text-white" />
              </div>
              <h3 class="font-semibold text-gray-900 mb-2">Drive Improvement</h3>
              <p class="text-gray-600 text-sm">Help shape the future of CSU education</p>
            </div>
          </div>

          <!-- Survey Section -->
          <div class="bg-gradient-to-r from-orange-500 to-orange-600 rounded-xl p-8 text-white mb-8">
            <div class="flex items-start gap-4 mb-6">
              <div class="bg-white/20 backdrop-blur-sm rounded-full p-3 flex-shrink-0">
                <CheckCircle class="w-8 h-8" />
              </div>
              <div>
                <h2 class="text-2xl font-bold mb-2">Help Us Improve Through Your Feedback</h2>
                <p class="text-orange-100 text-lg">Your input is invaluable to our continuous growth</p>
              </div>
            </div>

            <div class="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
              <h3 class="font-semibold text-xl mb-3">Why Your Participation Matters:</h3>
              <ul class="space-y-3">
                <li class="flex items-start gap-3">
                  <div class="bg-white/20 rounded-full p-1 mt-0.5 flex-shrink-0">
                    <div class="w-2 h-2 bg-white rounded-full"></div>
                  </div>
                  <span><strong>Curriculum Enhancement:</strong> Your career experiences help us align our programs with industry needs and emerging trends</span>
                </li>
                <li class="flex items-start gap-3">
                  <div class="bg-white/20 rounded-full p-1 mt-0.5 flex-shrink-0">
                    <div class="w-2 h-2 bg-white rounded-full"></div>
                  </div>
                  <span><strong>Student Success:</strong> Your feedback guides us in preparing current students for real-world challenges and opportunities</span>
                </li>
                <li class="flex items-start gap-3">
                  <div class="bg-white/20 rounded-full p-1 mt-0.5 flex-shrink-0">
                    <div class="w-2 h-2 bg-white rounded-full"></div>
                  </div>
                  <span><strong>Institutional Accreditation:</strong> Alumni tracer studies are essential for maintaining and improving our college's accreditation status</span>
                </li>
                <li class="flex items-start gap-3">
                  <div class="bg-white/20 rounded-full p-1 mt-0.5 flex-shrink-0">
                    <div class="w-2 h-2 bg-white rounded-full"></div>
                  </div>
                  <span><strong>Quality Assurance:</strong> Your responses help us measure the effectiveness of our educational programs and identify areas for improvement</span>
                </li>
              </ul>
            </div>

            <div class="mt-6 bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
              <p class="text-sm text-orange-50">
                <strong>📋 Survey Completion Time:</strong> Approximately 10-15 minutes | 
                <strong class="ml-3">🔒 Privacy:</strong> All responses are confidential and used solely for institutional improvement
              </p>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex justify-center">
            <button
              @click="handleProceedSurvey"
              class="group bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white px-12 py-4 rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center justify-center gap-2"
            >
              <FileText class="w-5 h-5" />
              Proceed
              <ArrowRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>

         
        </div>
      </div>

      <!-- Footer Note -->
      <div class="text-center mt-6 text-gray-600">
        <p class="text-sm">
          © 2025 Caraga State University Main Campus - College of Computing and Information Sciences | Building Stronger Alumni Connections
        </p>
      </div>
    </div>
  </div>
</template>
