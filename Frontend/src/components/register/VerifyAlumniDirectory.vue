a
<script setup>
import { defineProps, defineEmits, reactive, ref, computed } from 'vue';
import api from '../../services/api';

const props = defineProps(['form']);
const emit = defineEmits(['verified', 'update:form']);

const localForm = reactive({ ...props.form });
const error = ref('');

// Calculate current year for the year graduated input
const currentYear = computed(() => new Date().getFullYear());

const validateName = (name) => /^[A-Za-z]+(?: [A-Za-z]+)*(?: (Sr|Jr)\.?)?$/.test(name.trim());
const validateYear = (year) => /^\d{4}$/.test(year);

const validateFields = () => {
  if (
    !validateName(localForm.first_name) ||
    !validateName(localForm.last_name) ||
    (localForm.middle_name && !validateName(localForm.middle_name)) ||
    !localForm.program ||
    !localForm.birth_date ||
    !validateYear(localForm.year_graduated) ||
    !localForm.sex
  ) {
    return false;
  }
  return true;
};

const checkDirectory = async () => {
  error.value = '';
  if (!validateFields()) {
    error.value = '❌ Please fill all required fields correctly.';
    return;
  }
  try {
    const response = await api.post('/auth/check-alumni-directory/', {
      first_name: localForm.first_name,
      middle_name: localForm.middle_name,
      last_name: localForm.last_name,
      program: localForm.program,
      birth_date: localForm.birth_date,
      year_graduated: localForm.year_graduated,
      sex: localForm.sex,
    });
    if (response.data.exists) {
      emit('verified');
    } else {
      error.value = 'Alumni record not found. Please check your details.';
    }
  } catch {
    error.value = 'Verification failed. Please try again later.';
  }
};
</script>

<template>
  <div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700">First Name</label>
        <input v-model="localForm.first_name" type="text"
          class="mt-1 block w-full border border-gray-300 rounded-md p-2" @input="emit('update:form', localForm)" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700">Middle Name (Optional)</label>
        <input v-model="localForm.middle_name" type="text"
          class="mt-1 block w-full border border-gray-300 rounded-md p-2" @input="emit('update:form', localForm)" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700">Last Name</label>
        <input v-model="localForm.last_name" type="text" class="mt-1 block w-full border border-gray-300 rounded-md p-2"
          @input="emit('update:form', localForm)" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700">Program</label>
        <select v-model="localForm.program" class="mt-1 block w-full border border-gray-300 rounded-md p-2"
          @change="emit('update:form', localForm)">
          <option value="">Select Program</option>
          
          <option value="BS in Computer Science">BS in Computer Science</option>
          <option value="BS in Information Systems">BS in Information Systems</option>
          <option value="BS in Information Technology">BS in Information Technology</option>
        </select>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700">Birth Date</label>
        <input v-model="localForm.birth_date" type="date"
          class="mt-1 block w-full border border-gray-300 rounded-md p-2" @input="emit('update:form', localForm)" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700">Year Graduated</label>
        <input v-model="localForm.year_graduated" type="number" :min="currentYear - 50" :max="currentYear + 50"
          class="mt-1 block w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
          placeholder="Enter year (YYYY)" @input="emit('update:form', localForm)" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700">Sex</label>
        <select v-model="localForm.sex" class="mt-1 block w-full border border-gray-300 rounded-md p-2"
          @change="emit('update:form', localForm)">
          <option value="">Select Sex</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
        </select>
      </div>
    </div>
    <button @click="checkDirectory"
      class="w-full mt-6 bg-orange-500 text-white py-2 rounded hover:bg-orange-600 font-semibold">
      Verify
    </button>
    <p v-if="error" class="text-red-500 text-sm text-center mt-2">{{ error }}</p>
  </div>
</template>