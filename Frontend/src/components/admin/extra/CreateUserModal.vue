<script setup>
import { ref, reactive } from 'vue';
import api from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const emit = defineEmits(['created', 'close']);

const loading = ref(false);
const errors = reactive({
  first_name: '',
  middle_name: '',
  last_name: '',
  email: '',
  password: '',
  government_id: '',
  program: '',
  address: '',
  birth_date: '',
  year_graduated: '',
  employment_status: '',
  civil_status: '',
  sex: '',
  profile_picture: '',
  contact_number: '',
  server: '',
  general: ''
});

const form = reactive({
  first_name: '',
  middle_name: '',
  last_name: '',
  email: '',
  password: '',
  government_id: null,
  program: '',
  address: '',
  birth_date: '',
  year_graduated: '',
  employment_status: '',
  civil_status: '',
  sex: '',
  profile_picture: null,
  user_type: 3,
  is_approved: false,
  contact_number: ''
});

const validateName = (name) => /^[A-Za-z\s]+$/.test(name);
const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
const validatePassword = (password) =>
  /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/.test(password);
const validatePhoneNumber = (num) => /^\d{11}$/.test(num);

const clearErrors = () => {
  Object.keys(errors).forEach((key) => {
    errors[key] = '';
  });
};

const handleSubmit = async () => {
  loading.value = true;
  clearErrors();

  let hasError = false;
const requiredFields = [
  'first_name', 'last_name', 'email', 'password', 
  'program', 'address', 'birth_date', 'year_graduated', 
  'employment_status', 'civil_status', 'sex', 'contact_number'
];  for (const field of requiredFields) {
    if (!form[field]) {
      errors[field] = 'This field is required.';
      hasError = true;
    }
  }

  if (form.middle_name && !validateName(form.middle_name)) {
    errors.middle_name = 'Middle name must contain only letters and spaces.';
    hasError = true;
  }
  if (form.first_name && !validateName(form.first_name)) {
    errors.first_name = 'First name must contain only letters and spaces.';
    hasError = true;
  }
  if (form.last_name && !validateName(form.last_name)) {
    errors.last_name = 'Last name must contain only letters and spaces.';
    hasError = true;
  }
  if (form.email && !validateEmail(form.email)) {
    errors.email = 'Invalid email format.';
    hasError = true;
  }
  if (form.contact_number && !validatePhoneNumber(form.contact_number)) {
    errors.contact_number = 'Contact number must be 11 digits.';
    hasError = true;
  }
  if (form.password && !validatePassword(form.password)) {
    errors.password = 'Password must have 8+ characters, 1 uppercase, 1 lowercase, 1 number, and 1 special character.';
    hasError = true;
  }
  if (form.government_id && !['image/jpeg', 'image/jpg', 'image/png'].includes(form.government_id.type)) {
    errors.government_id = 'Upload valid Government ID (JPEG, JPG, PNG).';
    hasError = true;
  }
  if (form.profile_picture && !['image/jpeg', 'image/jpg', 'image/png'].includes(form.profile_picture.type)) {
    errors.profile_picture = 'Upload valid Profile Picture (JPEG, JPG, PNG).';
    hasError = true;
  }

  if (hasError) {
    loading.value = false;
    return;
  }

  const refreshed = await auth.tryRefreshToken();
  if (!refreshed && !auth.token) {
    errors.server = 'Session expired. Please log in again.';
    loading.value = false;
    return;
  }

  try {
    const formData = new FormData();
    for (const key in form) {
      if (form[key] !== null && form[key] !== '') {
        formData.append(key, form[key]);
      }
    }

    await api.post('/create-user/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    emit('created');
    emit('close');
  } catch (err) {
    if (err.response?.data) {
      errors.server = err.response.data.detail || err.response.data.message || 'Something went wrong.';
    } else {
      errors.server = 'Network error or server not responding.';
    }
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-4xl p-8 relative max-h-[90vh] overflow-y-auto">
      <button @click="$emit('close')" class="absolute top-4 right-4 text-gray-400 hover:text-gray-700 text-xl font-bold">&times;</button>
      <h2 class="text-xl font-semibold mb-6 text-gray-800">Create User</h2>

      <form @submit.prevent="handleSubmit" class="grid grid-cols-1 sm:grid-cols-2 gap-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">First Name</label>
          <input v-model="form.first_name" type="text" class="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300" />
          <p v-if="errors.first_name" class="text-red-600 text-sm mt-1">{{ errors.first_name }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Middle Name (Optional)</label>
          <input v-model="form.middle_name" type="text" class="w-full border rounded-lg px-4 py-2" />
          <p v-if="errors.middle_name" class="text-red-600 text-sm mt-1">{{ errors.middle_name }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
          <input v-model="form.last_name" type="text" class="w-full border rounded-lg px-4 py-2" />
          <p v-if="errors.last_name" class="text-red-600 text-sm mt-1">{{ errors.last_name }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input v-model="form.email" type="email" class="w-full border rounded-lg px-4 py-2" />
          <p v-if="errors.email" class="text-red-600 text-sm mt-1">{{ errors.email }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input v-model="form.password" type="password" class="w-full border rounded-lg px-4 py-2" />
          <p v-if="errors.password" class="text-red-600 text-sm mt-1">{{ errors.password }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Government ID</label>
          <input type="file" @change="e => form.government_id = e.target.files[0]" class="w-full border rounded-lg px-4 py-2" />
          <p v-if="errors.government_id" class="text-red-600 text-sm mt-1">{{ errors.government_id }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Program</label>
          <select v-model="form.program" class="w-full border rounded-lg px-4 py-2">
            <option value="" disabled>Select Program</option>
            <option value="BA in Sociology">BA in Sociology</option>
            <option value="Bachelor of Agricultural Technology">Bachelor of Agricultural Technology</option>
            <option value="Bachelor of Elementary Education">Bachelor of Elementary Education</option>
            <option value="Bachelor of Secondary Education Major in English">Bachelor of Secondary Education Major in English</option>
            <option value="Bachelor of Secondary Education Major in Filipino">Bachelor of Secondary Education Major in Filipino</option>
            <option value="Bachelor of Secondary Education Major in Mathematics">Bachelor of Secondary Education Major in Mathematics</option>
            <option value="Bachelor of Secondary Education Major in Science">Bachelor of Secondary Education Major in Science</option>
            <option value="BS in Computer Science">BS in Computer Science</option>
            <option value="BS in Information Systems">BS in Information Systems</option>
            <option value="BS in Information Technology">BS in Information Technology</option>
          </select>
          <p v-if="errors.program" class="text-red-600 text-sm mt-1">{{ errors.program }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Address</label>
          <input v-model="form.address" type="text" class="w-full border rounded-lg px-4 py-2" />
          <p v-if="errors.address" class="text-red-600 text-sm mt-1">{{ errors.address }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Birth Date</label>
          <input v-model="form.birth_date" type="date" class="w-full border rounded-lg px-4 py-2" />
          <p v-if="errors.birth_date" class="text-red-600 text-sm mt-1">{{ errors.birth_date }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Year Graduated</label>
          <input v-model="form.year_graduated" type="number" min="1990" max="2030" class="w-full border rounded-lg px-4 py-2" />
          <p v-if="errors.year_graduated" class="text-red-600 text-sm mt-1">{{ errors.year_graduated }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Employment Status</label>
          <select v-model="form.employment_status" class="w-full border rounded-lg px-4 py-2">
            <option value="" disabled>Select Status</option>
            <option value="employed_locally">Employed Locally</option>
            <option value="employed_abroad">Employed Abroad</option>
            <option value="self_employed">Self-Employed</option>
            <option value="unemployed">Unemployed</option>
            <option value="student">Student</option>
            <option value="retired">Retired</option>
          </select>
          <p v-if="errors.employment_status" class="text-red-600 text-sm mt-1">{{ errors.employment_status }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Civil Status</label>
          <select v-model="form.civil_status" class="w-full border rounded-lg px-4 py-2">
            <option value="" disabled>Select Civil Status</option>
            <option value="single">Single</option>
            <option value="married">Married</option>
            <option value="divorced">Divorced</option>
            <option value="widowed">Widowed</option>
            <option value="separated">Separated</option>
          </select>
          <p v-if="errors.civil_status" class="text-red-600 text-sm mt-1">{{ errors.civil_status }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Sex</label>
          <select v-model="form.sex" class="w-full border rounded-lg px-4 py-2">
            <option value="" disabled>Select Sex</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="prefer_not_to_say">Prefer not to say</option>
          </select>
          <p v-if="errors.sex" class="text-red-600 text-sm mt-1">{{ errors.sex }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Profile Picture</label>
          <input type="file" @change="e => form.profile_picture = e.target.files[0]" class="w-full border rounded-lg px-4 py-2" />
          <p v-if="errors.profile_picture" class="text-red-600 text-sm mt-1">{{ errors.profile_picture }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">User Type</label>
          <select v-model="form.user_type" class="w-full border rounded-lg px-4 py-2">
            <option :value="2">Admin</option>
            <option :value="3">Alumni</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Contact Number</label>
          <input v-model="form.contact_number" type="text" class="w-full border rounded-lg px-4 py-2" />
          <p v-if="errors.contact_number" class="text-red-600 text-sm mt-1">{{ errors.contact_number }}</p>
        </div>

        <div class="sm:col-span-2">
          <p v-if="errors.general" class="text-red-600 text-sm">{{ errors.general }}</p>
          <p v-if="errors.server" class="text-red-600 text-sm">{{ errors.server }}</p>
        </div>

        <div class="sm:col-span-2 flex justify-end mt-6">
          <button type="submit" :disabled="loading"
            class="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white font-semibold py-2 px-6 rounded-lg shadow-md disabled:opacity-50 transition-all duration-200">
            {{ loading ? 'Creating...' : 'Create User' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
