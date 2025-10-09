<script setup>
import { ref, reactive, computed, watch, defineProps, defineEmits, nextTick } from 'vue';
import { useAuthStore } from '@/stores/auth';
import axios from 'axios';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  alumni: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['close', 'saved']);

const authStore = useAuthStore();
const BASE_URL = 'http://127.0.0.1:8000';

// State
const loading = ref(false);
const errors = ref({});

// Programs list
const programs = [
  'BA in Sociology',
  'Bachelor of Agricultural Technology',
  'Bachelor of Elementary Education',
  'Bachelor of Secondary Education Major in English',
  'Bachelor of Secondary Education Major in Filipino',
  'Bachelor of Secondary Education Major in Mathematics',
  'Bachelor of Secondary Education Major in Science',
  'BS in Agroforestry',
  'BS in Agricultural and Biosystems Engineering',
  'BS in Agriculture',
  'BS in Agriculture, Major in Agribusiness Management',
  'BS in Agriculture, Major in Agricultural Economics',
  'BS in Agriculture, Major in Agronomy',
  'BS in Agriculture, Major in Animal Science',
  'BS in Agriculture, Major in Crop Protection',
  'BS in Agriculture, Major in Horticulture',
  'BS in Agriculture, Major in Soil Science',
  'BS in Applied Mathematics',
  'BS in Biology',
  'BS in Chemistry',
  'BS in Civil Engineering',
  'BS in Computer Science',
  'BS in Electronics Engineering',
  'BS in Environmental Science',
  'BS in Forestry',
  'BS in Geodetic Engineering',
  'BS in Geology',
  'BS in Information Systems',
  'BS in Information Technology',
  'BS in Mathematics',
  'BS in Mining Engineering',
  'BS in Physics',
  'BS in Psychology',
  'BS in Social Work'
];

const sexOptions = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' }
];

// Form data
const form = reactive({
  first_name: '',
  middle_name: '',
  last_name: '',
  birth_date: '',
  program: '',
  year_graduated: '',
  sex: ''
});

// Computed
const isEditMode = computed(() => !!props.alumni);
const modalTitle = computed(() => isEditMode.value ? 'Edit Alumni' : 'Create New Alumni');

const currentYear = computed(() => new Date().getFullYear());
const minYear = computed(() => currentYear.value - 50);
const maxYear = computed(() => currentYear.value + 5);

// Methods
const resetForm = () => {
  Object.assign(form, {
    first_name: '',
    middle_name: '',
    last_name: '',
    birth_date: '',
    program: '',
    year_graduated: '',
    sex: ''
  });
  errors.value = {};
};

const populateForm = (alumniData) => {
  if (alumniData) {
    Object.assign(form, {
      first_name: alumniData.first_name || '',
      middle_name: alumniData.middle_name || '',
      last_name: alumniData.last_name || '',
      birth_date: alumniData.birth_date || '',
      program: alumniData.program || '',
      year_graduated: alumniData.year_graduated?.toString() || '',
    sex: alumniData.sex || ''
    });
  }
};

const validateForm = () => {
  errors.value = {};
  
  if (!form.first_name.trim()) {
    errors.value.first_name = 'First name is required';
  }
  
  if (!form.last_name.trim()) {
    errors.value.last_name = 'Last name is required';
  }
  
  if (!form.program) {
    errors.value.program = 'Program is required';
  }
  
  if (!form.birth_date) {
    errors.value.birth_date = 'Birth date is required';
  }
  
  if (!form.year_graduated) {
    errors.value.year_graduated = 'Year graduated is required';
  } else {
    const year = parseInt(form.year_graduated);
    if (isNaN(year) || year < minYear.value || year > maxYear.value) {
      errors.value.year_graduated = `Year must be between ${minYear.value} and ${maxYear.value}`;
    }
  }
  
  if (!form.sex) {
    errors.value.sex = 'Sex is required';
  }
  
  return Object.keys(errors.value).length === 0;
};

const handleSubmit = async (event) => {
  event.preventDefault();
  console.log('🎯 Form submitted');
  
  if (!validateForm()) {
    console.log('🎯 Form validation failed');
    return;
  }
  
  loading.value = true;
  
  try {
    const payload = {
  ...form,
  year_graduated: parseInt(form.year_graduated),
  middle_name: form.middle_name || null
    };
    
    if (isEditMode.value) {
      await axios.put(`${BASE_URL}/api/auth/alumni-directory/${props.alumni.id}/`, payload, {
        headers: { Authorization: `Bearer ${authStore.token}` }
      });
      console.log('✅ Alumni updated successfully');
    } else {
      await axios.post(`${BASE_URL}/api/auth/alumni-directory/`, payload, {
        headers: { Authorization: `Bearer ${authStore.token}` }
      });
      console.log('✅ Alumni created successfully');
    }
    
    emit('saved');
  } catch (error) {
    console.error('❌ Failed to save alumni:', error);
    
    if (error.response?.data) {
      const backendErrors = error.response.data;
      if (typeof backendErrors === 'object') {
        errors.value = { ...errors.value, ...backendErrors };
      } else {
        errors.value.general = 'Failed to save alumni. Please try again.';
      }
    } else {
      errors.value.general = 'Failed to save alumni. Please check your connection and try again.';
    }
  } finally {
    loading.value = false;
  }
};

const closeModal = () => {
  console.log('🎯 Close modal called');
  emit('close');
};

const handleBackdropClick = (event) => {
  console.log('🎯 Backdrop clicked');
  if (event.target === event.currentTarget) {
    closeModal();
  }
};

// Watchers
watch(() => props.show, (newValue) => {
  console.log('🎯 Modal show prop changed to:', newValue);
  if (newValue) {
    nextTick(() => {
      if (props.alumni) {
        populateForm(props.alumni);
        console.log('🎯 Form populated for edit');
      } else {
        resetForm();
        console.log('🎯 Form reset for create');
      }
    });
  }
});
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" @click="handleBackdropClick">
  <div class="alumni-directory-modal bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto modal-scrollable" @click.stop>
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <div>
          <h2 class="text-2xl font-semibold" style="color: #16a34a;">{{ modalTitle }}</h2>
          <p class="text-gray-600 mt-1">{{ isEditMode ? 'Update alumni information' : 'Add a new alumni to the directory' }}</p>
        </div>
        <button
          @click="closeModal"
          type="button"
          class="text-gray-400 hover:text-gray-600 p-2 rounded-lg hover:bg-gray-100"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Form -->
      <form @submit="handleSubmit" class="p-6 space-y-6">
        <!-- Error Message -->
        <div v-if="errors.general" class="bg-red-50 border border-red-200 rounded-lg p-4">
          <div class="flex">
            <svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div class="ml-3">
              <p class="text-sm text-red-800">{{ errors.general }}</p>
            </div>
          </div>
        </div>

        <!-- Name Fields -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              First Name <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.first_name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              :class="{ 'border-red-500': errors.first_name }"
              placeholder="Enter first name"
            />
            <p v-if="errors.first_name" class="text-red-500 text-sm mt-1">{{ errors.first_name }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Middle Name</label>
            <input
              v-model="form.middle_name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter middle name (optional)"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Last Name <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.last_name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              :class="{ 'border-red-500': errors.last_name }"
              placeholder="Enter last name"
            />
            <p v-if="errors.last_name" class="text-red-500 text-sm mt-1">{{ errors.last_name }}</p>
          </div>
        </div>

        <!-- Program -->
        <div class="grid grid-cols-1 md:grid-cols-1 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Program <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.program"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              :class="{ 'border-red-500': errors.program }"
            >
              <option value="">Select Program</option>
              <option v-for="program in programs" :key="program" :value="program">{{ program }}</option>
            </select>
            <p v-if="errors.program" class="text-red-500 text-sm mt-1">{{ errors.program }}</p>
          </div>
        </div>

        <!-- Other Fields -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Birth Date <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.birth_date"
              type="date"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              :class="{ 'border-red-500': errors.birth_date }"
            />
            <p v-if="errors.birth_date" class="text-red-500 text-sm mt-1">{{ errors.birth_date }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Year Graduated <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.year_graduated"
              type="number"
              :min="minYear"
              :max="maxYear"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              :class="{ 'border-red-500': errors.year_graduated }"
              placeholder="YYYY"
            />
            <p v-if="errors.year_graduated" class="text-red-500 text-sm mt-1">{{ errors.year_graduated }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Sex <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.sex"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              :class="{ 'border-red-500': errors.sex }"
            >
              <option value="">Select Sex</option>
              <option v-for="option in sexOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
            <p v-if="errors.sex" class="text-red-500 text-sm mt-1">{{ errors.sex }}</p>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex items-center justify-end space-x-4 pt-6 border-t border-gray-200">
          <button
            type="button"
            @click="closeModal"
            class="px-6 py-3 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="loading"
            class="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center space-x-2 font-bold"
          >
            <div v-if="loading" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            <span>{{ loading ? 'Saving...' : (isEditMode ? 'Update Alumni' : 'Create Alumni') }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

/* =================================================================
   PROFESSIONAL ALUMNI DIRECTORY MODAL STYLING
   ================================================================= */

.alumni-directory-modal {
  font-family: 'Poppins', sans-serif !important;
  background: #ffffff;
  color: #065f46;
}

.alumni-directory-modal * {
  font-family: 'Poppins', sans-serif !important;
}

/* Header styling */
.alumni-directory-modal h1,
.alumni-directory-modal h2,
.alumni-directory-modal h3,
.alumni-directory-modal h4 {
  font-family: 'Poppins', sans-serif !important;
  font-weight: 700;
  color: #059669 !important;
}

.alumni-directory-modal .text-gray-900 {
  color: #059669 !important;
}

.alumni-directory-modal .text-gray-600,
.alumni-directory-modal .text-gray-700 {
  color: #065f46 !important;
  font-weight: 400;
}

/* Form styling */
.alumni-directory-modal label {
  font-family: 'Poppins', sans-serif !important;
  font-weight: 600;
  color: #065f46 !important;
  margin-bottom: 8px;
}

.alumni-directory-modal input,
.alumni-directory-modal select {
  font-family: 'Poppins', sans-serif !important;
  border: 2px solid #e5e7eb !important;
  border-radius: 10px !important;
  background: #ffffff !important;
  color: #065f46 !important;
  padding: 12px 16px !important;
  font-weight: 400;
  transition: all 0.3s ease;
}

.alumni-directory-modal input:focus,
.alumni-directory-modal select:focus {
  outline: none !important;
  border-color: #059669 !important;
  box-shadow: 0 0 0 4px rgba(5, 150, 105, 0.1) !important;
  background: #f8fafc !important;
}

.alumni-directory-modal input::placeholder {
  color: #6b7280 !important;
  font-weight: 400;
}

/* Button styling */
.alumni-directory-modal button {
  font-family: 'Poppins', sans-serif !important;
  font-weight: 600;
  border-radius: 12px !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: none !important;
  cursor: pointer;
}

/* Primary submit button */
.alumni-directory-modal .bg-blue-600 {
  background: #059669 !important;
  color: #ffffff !important;
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
}

.alumni-directory-modal .bg-blue-600:hover,
.alumni-directory-modal .hover\:bg-blue-700:hover {
  background: #047857 !important;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(5, 150, 105, 0.4);
}

/* Cancel button */
.alumni-directory-modal .bg-gray-100 {
  background: #f8fafc !important;
  color: #065f46 !important;
  border: 2px solid #e2e8f0 !important;
}

.alumni-directory-modal .bg-gray-100:hover,
.alumni-directory-modal .hover\:bg-gray-200:hover {
  background: #ecfdf5 !important;
  color: #059669 !important;
  border: 2px solid #059669 !important;
}

/* Error styling */
.alumni-directory-modal .border-red-500 {
  border-color: #ef4444 !important;
}

.alumni-directory-modal .text-red-500,
.alumni-directory-modal .text-red-800 {
  color: #dc2626 !important;
}

.alumni-directory-modal .bg-red-50 {
  background: #fef2f2 !important;
}

/* Animations */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.alumni-directory-modal .animate-spin {
  animation: spin 1s linear infinite;
}

/* Disabled state */
.alumni-directory-modal button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

/* Smooth transitions */
.alumni-directory-modal .transition-colors {
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}
</style>

/* Ensure modal content is always scrollable if too tall */
.modal-scrollable {
  max-height: 90vh;
  overflow-y: auto;
}
