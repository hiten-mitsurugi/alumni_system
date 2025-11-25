<script setup>
import { defineProps, defineEmits } from 'vue'
import { X } from 'lucide-vue-next'

defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

defineEmits(['close'])
</script>

<template>
  <!-- Modal Backdrop -->
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="isOpen"
        class="fixed inset-0 bg-black/50 z-40"
        @click="$emit('close')"
      />
    </Transition>

    <!-- Modal Content -->
    <Transition name="scale">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <div class="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
          <!-- Header -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-orange-600 to-orange-500">
            <h2 class="text-xl font-bold text-white">Terms and Conditions</h2>
            <button
              @click="$emit('close')"
              class="text-white hover:text-orange-100 transition-colors"
            >
              <X class="w-6 h-6" />
            </button>
          </div>

          <!-- Content -->
          <div class="overflow-y-auto flex-1 px-6 py-6 space-y-6 text-gray-700 text-sm leading-relaxed">
            <section>
              <h3 class="font-bold text-lg text-gray-900 mb-2">1. Acceptance of Terms</h3>
              <p>
                By registering and using the ATENDA platform, you acknowledge that you have read, understood, and agree to be bound by these Terms and Conditions. If you do not agree to any part of these terms, please do not proceed with registration.
              </p>
            </section>

            <section>
              <h3 class="font-bold text-lg text-gray-900 mb-2">2. User Accounts</h3>
              <p>
                You are responsible for maintaining the confidentiality of your account login credentials and password. You agree to accept responsibility for all activities that occur under your account. You must notify us immediately of any unauthorized use of your account.
              </p>
            </section>

            <section>
              <h3 class="font-bold text-lg text-gray-900 mb-2">3. User Data and Privacy</h3>
              <p>
                The information you provide during registration will be used to create your alumni profile. You consent to the collection, use, and storage of your personal data in accordance with our Privacy Policy. Your data will be kept secure and will not be shared with third parties without your consent.
              </p>
            </section>

            <section>
              <h3 class="font-bold text-lg text-gray-900 mb-2">4. Data Privacy Act Compliance (Republic Act No. 10173)</h3>
              <p class="mb-3">
                In compliance with the <span class="font-semibold">Data Privacy Act of 2012 (Republic Act No. 10173)</span>, we are committed to protecting your personal information and ensuring your privacy rights. By using this platform, you acknowledge and agree to the following:
              </p>
              <ul class="list-disc pl-6 space-y-2">
                <li><span class="font-semibold">Lawful Processing:</span> Your personal data will be collected, processed, and stored in accordance with the principles of transparency, legitimate purpose, and proportionality as mandated by the DPA.</li>
                <li><span class="font-semibold">Your Rights:</span> You have the right to be informed, object to processing, access your data, rectify inaccuracies, erase or block your data, claim damages, and file complaints with the National Privacy Commission.</li>
                <li><span class="font-semibold">Data Security:</span> We implement appropriate organizational, physical, and technical security measures to protect your personal data against unauthorized access, disclosure, alteration, or destruction.</li>
                <li><span class="font-semibold">Consent:</span> By registering and using this platform, you provide your voluntary, informed, and specific consent to the collection and processing of your personal information for legitimate educational and institutional purposes.</li>
                <li><span class="font-semibold">Data Retention:</span> Your data will be retained only for as long as necessary to fulfill the purposes for which it was collected or as required by applicable laws and regulations.</li>
              </ul>
            </section>

            <section>
              <h3 class="font-bold text-lg text-gray-900 mb-2">5. Accurate Information</h3>
              <p>
                You agree to provide accurate, current, and complete information during registration. You will promptly update your account information to maintain its accuracy. We reserve the right to suspend or terminate accounts with false or misleading information.
              </p>
            </section>

            <section>
              <h3 class="font-bold text-lg text-gray-900 mb-2">6. Acceptable Use</h3>
              <p>
                You agree not to use the platform for any unlawful or prohibited activities. You will not upload, share, or transmit any content that is offensive, defamatory, or violates intellectual property rights. This includes harassment, discrimination, or inappropriate conduct toward other users.
              </p>
            </section>

            <section>
              <h3 class="font-bold text-lg text-gray-900 mb-2">7. Intellectual Property</h3>
              <p>
                All content, features, and functionality of the ATENDA platform are owned by the institution, its content suppliers, or other providers of such material and are protected by international copyright, trademark, and other intellectual property laws.
              </p>
            </section>

            <section>
              <h3 class="font-bold text-lg text-gray-900 mb-2">8. Survey Participation</h3>
              <p>
                Your participation in surveys is voluntary. The survey responses you provide will be used for institutional research and improvement purposes. Your responses will be kept confidential, and individual responses will not be disclosed to unauthorized parties.
              </p>
            </section>

            <section>
              <h3 class="font-bold text-lg text-gray-900 mb-2">9. Limitation of Liability</h3>
              <p>
                The platform is provided "as is" without warranties of any kind, either express or implied. We are not liable for any direct, indirect, incidental, special, or consequential damages arising from your use of or inability to use the platform.
              </p>
            </section>

            <section>
              <h3 class="font-bold text-lg text-gray-900 mb-2">10. Termination</h3>
              <p>
                We reserve the right to suspend or terminate your account at any time for violations of these terms or for any other reason we deem appropriate. Upon termination, you must cease using the platform immediately.
              </p>
            </section>

            <section>
              <h3 class="font-bold text-lg text-gray-900 mb-2">11. Changes to Terms</h3>
              <p>
                We reserve the right to modify these Terms and Conditions at any time. Changes will be effective immediately upon posting. Your continued use of the platform following the posting of modified terms means you accept and agree to the changes.
              </p>
            </section>

            <section>
              <h3 class="font-bold text-lg text-gray-900 mb-2">12. Governing Law</h3>
              <p>
                These Terms and Conditions are governed by and construed in accordance with the laws of the Philippines, and you irrevocably submit to the exclusive jurisdiction of the courts located therein.
              </p>
            </section>

            <section>
              <h3 class="font-bold text-lg text-gray-900 mb-2">13. Contact Information</h3>
              <p>
                If you have any questions regarding these Terms and Conditions, please contact us at the provided institutional email address.
              </p>
            </section>
          </div>

          <!-- Footer -->
          <div class="border-t border-gray-200 px-6 py-4 bg-gray-50 flex gap-3">
            <button
              @click="$emit('close')"
              class="flex-1 px-4 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 font-medium transition-colors cursor-pointer"
            >
              Close
            </button>
            <button
              @click="$emit('close')"
              class="flex-1 px-4 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 font-medium transition-colors cursor-pointer"
            >
              I Accept & Agree
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.scale-enter-active,
.scale-leave-active {
  transition: all 0.3s ease;
}

.scale-enter-from,
.scale-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
