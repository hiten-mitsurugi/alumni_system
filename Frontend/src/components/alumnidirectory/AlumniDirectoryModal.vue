<script setup>
import { ref, reactive, computed, watch, defineProps, defineEmits } from 'vue';
import { useAuthStore } from '@/stores/auth';
import axios from 'axios';

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
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

// Programs list based on the user's requirements
const programs = [
  'BS in Computer Science',
  'BS in Information Systems',
  'BS in Information Technology'
];

const genderOptions = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'prefer_not_to_say', label: 'Prefer not to say' }
];

// Form data
const form = reactive({
  first_name: '',
  middle_name: '',
  last_name: '',
  birth_date: '',
  school_id: '',
  program: '',
  year_graduated: '',
  sex: ''
});

// Computed
const isEditMode = computed(() => !!props.alumni);
const modalTitle = computed(() => isEditMode.value ? 'Edit Alumni' : 'Create New Alumni');

const currentYear = computed(() => new Date().getFullYear());
const minYear = computed(() => currentYear.value - 50); // 50 years back
const maxYear = computed(() => currentYear.value + 5); // 5 years forward

// Validation
const validateForm = () => {
  errors.value = {};
  
  if (!form.first_name.trim()) {
    errors.value.first_name = 'First name is required';
  }
  
  if (!form.last_name.trim()) {
    errors.value.last_name = 'Last name is required';
  }
  
  if (!form.school_id.trim()) {
    errors.value.school_id = 'School ID is required';
  } else if (!/^\d{3}-\d{5}$/.test(form.school_id)) {
    errors.value.school_id = 'School ID must be in format XXX-XXXXX (e.g., 221-01926)';
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

// Methods
const resetForm = () => {
  Object.assign(form, {
    first_name: '',
    middle_name: '',
    last_name: '',
    birth_date: '',
    school_id: '',
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
      school_id: alumniData.school_id || '',
      program: alumniData.program || '',
      year_graduated: alumniData.year_graduated?.toString() || '',
      sex: alumniData.sex || ''
    });
  }
};

const handleSubmit = async (event) => {
  event.preventDefault(); // Prevent default form submission
  event.stopPropagation(); // Stop event bubbling
  
  if (!validateForm()) {
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
      // Update existing alumni
      await axios.put(`${BASE_URL}/api/alumni-directory/${props.alumni.id}/`, payload, {
        headers: { Authorization: `Bearer ${authStore.token}` }
      });
      console.log('✅ Alumni updated successfully');
    } else {
      // Create new alumni
      await axios.post(`${BASE_URL}/api/alumni-directory/`, payload, {
        headers: { Authorization: `Bearer ${authStore.token}` }
      });
      console.log('✅ Alumni created successfully');
    }
    
    emit('saved');
  } catch (error) {
    console.error('❌ Failed to save alumni:', error);
    
    if (error.response?.data) {
      // Handle validation errors from backend
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

const handleClose = (event) => {
  console.log('🎯 Modal handleClose called');
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }
  if (!loading.value) {
    console.log('🎯 Emitting close event...');
    // Add a small delay to prevent immediate closing
    setTimeout(() => {
      emit('close');
    }, 100);
  }
};

const handleOverlayClick = (event) => {
  // Only close if clicking directly on the overlay, not on child elements
  if (event.target === event.currentTarget) {
    handleClose(event);
  }
};

const handleModalContentClick = (event) => {
  // Prevent any clicks inside the modal from bubbling up
  event.stopPropagation();
};

// Watchers
watch(() => props.isOpen, (newValue) => {
  console.log('🎯 Modal isOpen changed to:', newValue);
  if (newValue) {
    if (props.alumni) {
      populateForm(props.alumni);
      console.log('🎯 Populated form for edit mode');
    } else {
      resetForm();
      console.log('🎯 Reset form for create mode');
    }
  }
}, { immediate: true });

watch(() => props.alumni, (newValue) => {
  console.log('🎯 Modal alumni prop changed:', newValue);
  if (props.isOpen) {
    if (newValue) {
      populateForm(newValue);
    } else {
      resetForm();
    }
  }
}, { immediate: true });
</script>

<template>
  <!-- Modal Overlay -->
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto" @click="handleOverlayClick">
    <div class="flex min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" aria-hidden="true"></div>

      <!-- Center modal -->
      <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

      <!-- Modal content -->
      <div 
        @click="handleModalContentClick"
        class="inline-block w-full max-w-2xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg sm:align-middle"
      >
        <!-- Header -->
        <div class="flex items-center justify-between mb-6">
          <div>
            <h3 class="text-2xl font-bold text-gray-900">{{ modalTitle }}</h3>
            <p class="text-gray-600 mt-1">{{ isEditMode ? 'Update alumni information' : 'Add a new alumni to the directory' }}</p>
          </div>
          <button
            @click.stop="handleClose"
            :disabled="loading"
            class="text-gray-400 hover:text-gray-600 p-2 rounded-lg hover:bg-gray-100 transition-colors duration-200 disabled:opacity-50"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Form -->
        <form @submit="handleSubmit" @click="handleModalContentClick" class="space-y-6">
          <!-- General Error -->
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
            <!-- First Name -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                First Name <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.first_name"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                :class="{ 'border-red-500 focus:ring-red-500 focus:border-red-500': errors.first_name }"
                placeholder="Enter first name"
                :disabled="loading"
              />
              <p v-if="errors.first_name" class="text-red-500 text-sm mt-1">{{ errors.first_name }}</p>
            </div>

            <!-- Middle Name -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Middle Name
              </label>
              <input
                v-model="form.middle_name"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter middle name (optional)"
                :disabled="loading"
              />
            </div>

            <!-- Last Name -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Last Name <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.last_name"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                :class="{ 'border-red-500 focus:ring-red-500 focus:border-red-500': errors.last_name }"
                placeholder="Enter last name"
                :disabled="loading"
              />
              <p v-if="errors.last_name" class="text-red-500 text-sm mt-1">{{ errors.last_name }}</p>
            </div>
          </div>

          <!-- School ID and Program -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- School ID -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                School ID <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.school_id"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                :class="{ 'border-red-500 focus:ring-red-500 focus:border-red-500': errors.school_id }"
                placeholder="XXX-XXXXX (e.g., 221-01926)"
                :disabled="loading"
              />
              <p v-if="errors.school_id" class="text-red-500 text-sm mt-1">{{ errors.school_id }}</p>
            </div>

            <!-- Program -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Program <span class="text-red-500">*</span>
              </label>
              <select
                v-model="form.program"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                :class="{ 'border-red-500 focus:ring-red-500 focus:border-red-500': errors.program }"
                :disabled="loading"
              >
                <option value="">Select Program</option>
                <option v-for="program in programs" :key="program" :value="program">{{ program }}</option>
              </select>
              <p v-if="errors.program" class="text-red-500 text-sm mt-1">{{ errors.program }}</p>
            </div>
          </div>

          <!-- Birth Date, Year Graduated, and Sex -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Birth Date -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Birth Date <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.birth_date"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                :class="{ 'border-red-500 focus:ring-red-500 focus:border-red-500': errors.birth_date }"
                :disabled="loading"
              />
              <p v-if="errors.birth_date" class="text-red-500 text-sm mt-1">{{ errors.birth_date }}</p>
            </div>

            <!-- Year Graduated -->
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
                :class="{ 'border-red-500 focus:ring-red-500 focus:border-red-500': errors.year_graduated }"
                placeholder="YYYY"
                :disabled="loading"
              />
              <p v-if="errors.year_graduated" class="text-red-500 text-sm mt-1">{{ errors.year_graduated }}</p>
            </div>

            <!-- Sex -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Sex <span class="text-red-500">*</span>
              </label>
              <select
                v-model="form.sex"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                :class="{ 'border-red-500 focus:ring-red-500 focus:border-red-500': errors.sex }"
                :disabled="loading"
              >
                <option value="">Select Sex</option>
                <option v-for="option in genderOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
              <p v-if="errors.sex" class="text-red-500 text-sm mt-1">{{ errors.sex }}</p>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="flex items-center justify-end space-x-4 pt-6 border-t border-gray-200">
            <button
              type="button"
              @click.stop="handleClose"
              :disabled="loading"
              class="px-6 py-3 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors duration-200 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 disabled:opacity-50 flex items-center space-x-2"
              @click.stop
            >
              <div v-if="loading" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>{{ loading ? 'Saving...' : (isEditMode ? 'Update Alumni' : 'Create Alumni') }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Modal animation */
@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.inline-block {
  animation: modalSlideIn 0.3s ease-out;
}

/* Form field focus effects */
input:focus,
select:focus {
  outline: none;
}

/* Loading spinner */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Error state styling */
.border-red-500 {
  border-color: #ef4444;
}

/* Disabled state */
input:disabled,
select:disabled,
button:disabled {
  cursor: not-allowed;
}

/* Smooth transitions */
.transition-colors {
  transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

/* Button hover effects */
button:hover:not(:disabled) {
  transform: translateY(-1px);
}
</style>
