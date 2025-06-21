<!-- eslint-disable vue/multi-word-component-names -->
<script setup>
import { ref } from 'vue';
import api from '../services/api';
import Navbar from '@/components/Navbar.vue';
import backgroundImage from '@/assets/Background.png';

const stepTwo = ref(false);
const error = ref('');
const success = ref('');

const form = ref({
  first_name: '',
  middle_name: '',
  last_name: '',
  email: '',
  contact_number: '',
  password: '',
  confirm_password: '',
  school_id: '',
  government_id: null,
  program: '',
  address: '',
  birth_date: '',
  year_graduated: '',
  employment_status: '',
  profile_picture: null,
  civil_status: '',
  gender: '',
  alumni_exists: false,
});

// Validators
const validateName = (name) => /^[A-Za-z]+(?: [A-Za-z]+)*(?: (Sr|Jr)\.?)?$/.test(name.trim());
const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
const validatePassword = (password) =>
  /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/.test(password);
const validateSchoolId = (id) => /^\d{3}-\d{5}$/.test(id);
const validatePhoneNumber = (num) => /^\d{11}$/.test(num);
const validateYear = (year) => /^\d{4}$/.test(year);

const checkDirectory = async () => {
  error.value = '';
  success.value = '';

  if (
    !validateName(form.value.first_name) ||
    !validateName(form.value.last_name) ||
    (form.value.middle_name && !validateName(form.value.middle_name)) ||
    !validateSchoolId(form.value.school_id) ||
    !form.value.program ||
    !form.value.birth_date ||
    !validateYear(form.value.year_graduated) ||
    !form.value.gender
  ) {
    error.value = 'Please fill all required fields correctly.';
    return;
  }

  try {
    await api.post('/check-alumni-directory/', {
      first_name: form.value.first_name,
      middle_name: form.value.middle_name,
      last_name: form.value.last_name,
      school_id: form.value.school_id,
      program: form.value.program,
      birth_date: form.value.birth_date,
      year_graduated: form.value.year_graduated,
      gender: form.value.gender,
    });
    error.value = '';
    form.value.alumni_exists = true;
    success.value = 'Alumni record found. Please complete registration.';
    stepTwo.value = true;
  } catch (err) {
    error.value = err.response?.data?.non_field_errors?.[0] || 'Verification failed. Please try again.';
    success.value = '';
    stepTwo.value = false;
  }
};

const register = async () => {
  error.value = '';
  success.value = '';

  const govIdType = form.value.government_id?.type || '';
  const profilePicType = form.value.profile_picture?.type || '';

  if (
    !validateName(form.value.first_name) ||
    !validateName(form.value.last_name) ||
    (form.value.middle_name && !validateName(form.value.middle_name)) ||
    !validateEmail(form.value.email) ||
    !validatePhoneNumber(form.value.contact_number) ||
    !validatePassword(form.value.password) ||
    form.value.password !== form.value.confirm_password ||
    !validateSchoolId(form.value.school_id) ||
    !form.value.government_id ||
    !govIdType.match(/image\/(jpeg|jpg|png)/) ||
    !form.value.profile_picture ||
    !profilePicType.match(/image\/(jpeg|jpg|png)/) ||
    !form.value.program ||
    !form.value.address ||
    !form.value.birth_date ||
    !validateYear(form.value.year_graduated) ||
    !form.value.employment_status ||
    !form.value.civil_status ||
    !form.value.gender
  ) {
    error.value = 'Please fill all required fields correctly.';
    return;
  }

  const formData = new FormData();
  Object.keys(form.value).forEach((key) => {
    if (form.value[key] && key !== 'government_id' && key !== 'profile_picture') {
      formData.append(key, form.value[key]);
    }
  });
  formData.append('government_id', form.value.government_id);
  formData.append('profile_picture', form.value.profile_picture);

  try {
    await api.post('/register/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    success.value = 'Registration successful! Please wait for approval from the Alumni Relations Office.';
    error.value = '';

    // ✅ Alert and refresh
    alert(success.value);
    window.location.reload();

  } catch (err) {
    error.value = err.response?.data?.non_field_errors?.[0] || 'Registration failed. Please try again.';
    success.value = '';
  }
};

const handleFileUpload = (event, type) => {
  const file = event.target.files[0];
  if (type === 'governmentId') form.value.government_id = file;
  else if (type === 'profilePicture') form.value.profile_picture = file;
};
</script>



<template>
  <div class="min-h-screen bg-cover bg-center flex flex-col" :style="{ backgroundImage: `url(${backgroundImage})` }">
    <div class="fixed top-0 left-0 right-0 z-50">
      <Navbar />
    </div>

    <div class="h-20"></div> <!-- Spacer -->

    <div class="flex items-center justify-center px-4 md:px-20 py-12">
      <div class="bg-white bg-opacity-90 backdrop-blur-md shadow-xl rounded-xl p-10 w-full max-w-3xl">
        <h2 class="text-3xl font-bold text-center text-gray-800 mb-8">Register (Alumni Only)</h2>

        <!-- Step 1: Verify Alumni Directory -->
        <div v-if="!stepTwo">
          <h3 class="text-xl font-semibold text-center mb-6">Step 1: Verify Alumni Directory</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm text-gray-600 mb-1">First Name</label>
              <input
                v-model="form.first_name"
                placeholder="First Name"
                class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">Middle Name (Optional)</label>
              <input
                v-model="form.middle_name"
                placeholder="Middle Name"
                class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">Last Name</label>
              <input
                v-model="form.last_name"
                placeholder="Last Name"
                class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">School ID (e.g., 221-00000)</label>
              <input
                v-model="form.school_id"
                placeholder="School ID"
                class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">Program</label>
              <select
                v-model="form.program"
                class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="" disabled>Select Program</option>
                <option value="BA in Sociology">BA in Sociology</option>
                <option value="Bachelor of Agricultural Technology">Bachelor of Agricultural Technology</option>
                <option value="Bachelor of Elementary Education">Bachelor of Elementary Education</option>
                <option value="Bachelor of Secondary Education Major in English">
                  Bachelor of Secondary Education Major in English
                </option>
                <option value="Bachelor of Secondary Education Major in Filipino">
                  Bachelor of Secondary Education Major in Filipino
                </option>
                <option value="Bachelor of Secondary Education Major in Mathematics">
                  Bachelor of Secondary Education Major in Mathematics
                </option>
                <option value="Bachelor of Secondary Education Major in Science">
                  Bachelor of Secondary Education Major in Science
                </option>
                <!-- cSpell:disable-next-line -->
                <option value="BS in Agroforestry">BS in Agroforestry</option>
                <!-- cSpell:disable-next-line -->
                <option value="BS in Agricultural and Biosystems Engineering">
                  <!-- cSpell:disable-next-line -->
                  BS in Agricultural and Biosystems Engineering
                </option>
                <option value="BS in Agriculture">BS in Agriculture</option>
                <option value="BS in Agriculture, Major in Agribusiness Management">
                  BS in Agriculture, Major in Agribusiness Management
                </option>
                <option value="BS in Agriculture, Major in Agricultural Economics">
                  BS in Agriculture, Major in Agricultural Economics
                </option>
                <option value="BS in Agriculture, Major in Agronomy">BS in Agriculture, Major in Agronomy</option>
                <option value="BS in Agriculture, Major in Animal Science">
                  BS in Agriculture, Major in Animal Science
                </option>
                <option value="BS in Agriculture, Major in Crop Protection">
                  BS in Agriculture, Major in Crop Protection
                </option>
                <option value="BS in Agriculture, Major in Horticulture">
                  BS in Agriculture, Major in Horticulture
                </option>
                <option value="BS in Agriculture, Major in Soil Science">
                  BS in Agriculture, Major in Soil Science
                </option>
                <option value="BS in Applied Mathematics">BS in Applied Mathematics</option>
                <option value="BS in Biology">BS in Biology</option>
                <option value="BS in Chemistry">BS in Chemistry</option>
                <option value="BS in Civil Engineering">BS in Civil Engineering</option>
                <option value="BS in Computer Science">BS in Computer Science</option>
                <option value="BS in Electronics Engineering">BS in Electronics Engineering</option>
                <option value="BS in Environmental Science">BS in Environmental Science</option>
                <option value="BS in Forestry">BS in Forestry</option>
                <option value="BS in Geodetic Engineering">BS in Geodetic Engineering</option>
                <option value="BS in Geology">BS in Geology</option>
                <option value="BS in Information System">BS in Information System</option>
                <option value="BS in Information Systems">BS in Information Systems</option>
                <option value="BS in Information Technology">BS in Information Technology</option>
                <option value="BS in Mathematics">BS in Mathematics</option>
                <option value="BS in Mining Engineering">BS in Mining Engineering</option>
                <option value="BS in Physics">BS in Physics</option>
                <option value="BS in Psychology">BS in Psychology</option>
                <option value="BS in Social Work">BS in Social Work</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">Birth Date</label>
              <input
                v-model="form.birth_date"
                type="date"
                class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">Year Graduated</label>
              <input
                v-model="form.year_graduated"
                placeholder="Year Graduated"
                class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">Gender</label>
              <select
                v-model="form.gender"
                class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="" disabled>Select Gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="prefer_not_to_say">Prefer not to say</option>
              </select>
            </div>
          </div>
          <button
            @click="checkDirectory"
            class="w-full mt-6 bg-green-700 text-white py-2 rounded hover:bg-green-800 font-semibold"
          >
            Verify
          </button>
          <p v-if="error" class="text-red-500 text-sm text-center mt-2">{{ error }}</p>
          <p v-if="success" class="text-green-500 text-sm text-center mt-2">{{ success }}</p>
        </div>

        <!-- Step 2: Complete Registration -->
        <div v-else>
          <h3 class="text-xl font-semibold text-center mb-6">Step 2: Complete Registration</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm text-gray-600 mb-1">Email</label>
              <input
                v-model="form.email"
                type="email"
                placeholder="Email"
                class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">Contact Number (11 digits)</label>
              <input
                v-model="form.contact_number"
                type="text"
                placeholder="Contact Number"
                class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">Password</label>
              <input
                v-model="form.password"
                type="password"
                placeholder="Password"
                class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">Confirm Password</label>
              <input
                v-model="form.confirm_password"
                type="password"
                placeholder="Confirm Password"
                class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">Address</label>
              <input
                v-model="form.address"
                placeholder="Address"
                class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">Employment Status</label>
              <select
                v-model="form.employment_status"
                class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="" disabled>Select Employment Status</option>
                <option value="employed_locally">Employed Locally</option>
                <option value="employed_internationally">Employed Internationally</option>
                <option value="self_employed">Self-Employed</option>
                <option value="unemployed">Unemployed</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">Civil Status</label>
              <select
                v-model="form.civil_status"
                class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="" disabled>Select Civil Status</option>
                <option value="single">Single</option>
                <option value="married">Married</option>
                <option value="widow">Widow</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">Government ID (JPEG, JPG, PNG)</label>
              <input
                type="file"
                @change="handleFileUpload($event, 'governmentId')"
                accept=".jpeg,.jpg,.png"
                class="w-full p-2 border rounded"
              />
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">Profile Picture (JPEG, JPG, PNG)</label>
              <input
                type="file"
                @change="handleFileUpload($event, 'profilePicture')"
                accept=".jpeg,.jpg,.png"
                class="w-full p-2 border rounded"
              />
            </div>
          </div>
          <button
            @click="register"
            class="w-full mt-6 bg-green-700 text-white py-2 rounded hover:bg-green-800 font-semibold"
          >
            Register
          </button>
          <p v-if="error" class="text-red-500 text-sm text-center mt-2">{{ error }}</p>
          <p v-if="success" class="text-green-500 text-sm text-center mt-2">{{ success }}</p>
        </div>

        <p class="text-center text-sm mt-4">
          Already have an account?
          <router-link to="/login" class="text-blue-600 hover:underline">Login</router-link>
        </p>
      </div>
    </div>
  </div>
</template>