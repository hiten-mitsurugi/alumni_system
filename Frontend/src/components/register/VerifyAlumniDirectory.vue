a<script setup>
import { defineProps, defineEmits, reactive, ref } from 'vue';
import api from '../../services/api';

const props = defineProps(['form']);
const emit = defineEmits(['verified', 'update:form']);

const localForm = reactive({ ...props.form });
const error = ref('');

const validateName = (name) => /^[A-Za-z]+(?: [A-Za-z]+)*(?: (Sr|Jr)\.?)?$/.test(name.trim());
const validateSchoolId = (id) => /^\d{3}-\d{5}$/.test(id);
const validateYear = (year) => /^\d{4}$/.test(year);

const validateFields = () => {
  if (
    !validateName(localForm.first_name) ||
    !validateName(localForm.last_name) ||
    (localForm.middle_name && !validateName(localForm.middle_name)) ||
    !validateSchoolId(localForm.school_id) ||
    !localForm.program ||
    !localForm.birth_date ||
    !validateYear(localForm.year_graduated) ||
    !localForm.gender
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
    const response = await api.post('/check-alumni-directory/', {
      first_name: localForm.first_name,
      middle_name: localForm.middle_name,
      last_name: localForm.last_name,
      school_id: localForm.school_id,
      program: localForm.program,
      birth_date: localForm.birth_date,
      year_graduated: localForm.year_graduated,
      gender: localForm.gender,
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
        <input
          v-model="localForm.first_name"
          type="text"
          class="mt-1 block w-full border border-gray-300 rounded-md p-2"
          @input="emit('update:form', localForm)"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700">Middle Name (Optional)</label>
        <input
          v-model="localForm.middle_name"
          type="text"
          class="mt-1 block w-full border border-gray-300 rounded-md p-2"
          @input="emit('update:form', localForm)"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700">Last Name</label>
        <input
          v-model="localForm.last_name"
          type="text"
          class="mt-1 block w-full border border-gray-300 rounded-md p-2"
          @input="emit('update:form', localForm)"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700">School ID</label>
        <input
          v-model="localForm.school_id"
          type="text"
          class="mt-1 block w-full border border-gray-300 rounded-md p-2"
          @input="emit('update:form', localForm)"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700">Program</label>
        <select
          v-model="localForm.program"
          class="mt-1 block w-full border border-gray-300 rounded-md p-2"
          @change="emit('update:form', localForm)"
        >
          <option value="">Select Program</option>
          <option value="BA in Sociology">BA in Sociology</option>
          <option value="Bachelor of Agricultural Technology">Bachelor of Agricultural Technology</option>
          <option value="Bachelor of Elementary Education">Bachelor of Elementary Education</option>
          <option value="Bachelor of Secondary Education Major in English">Bachelor of Secondary Education Major in English</option>
          <option value="Bachelor of Secondary Education Major in Filipino">Bachelor of Secondary Education Major in Filipino</option>
          <option value="Bachelor of Secondary Education Major in Mathematics">Bachelor of Secondary Education Major in Mathematics</option>
          <option value="Bachelor of Secondary Education Major in Science">Bachelor of Secondary Education Major in Science</option>
          <option value="BS in Agroforestry">BS in Agroforestry</option>
          <option value="BS in Agricultural and Biosystems Engineering">BS in Agricultural and Biosystems Engineering</option>
          <option value="BS in Agriculture">BS in Agriculture</option>
          <option value="BS in Agriculture, Major in Agribusiness Management">BS in Agriculture, Major in Agribusiness Management</option>
          <option value="BS in Agriculture, Major in Agricultural Economics">BS in Agriculture, Major in Agricultural Economics</option>
          <option value="BS in Agriculture, Major in Agronomy">BS in Agriculture, Major in Agronomy</option>
          <option value="BS in Agriculture, Major in Animal Science">BS in Agriculture, Major in Animal Science</option>
          <option value="BS in Agriculture, Major in Crop Protection">BS in Agriculture, Major in Crop Protection</option>
          <option value="BS in Agriculture, Major in Horticulture">BS in Agriculture, Major in Horticulture</option>
          <option value="BS in Agriculture, Major in Soil Science">BS in Agriculture, Major in Soil Science</option>
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
        <label class="block text-sm font-medium text-gray-700">Birth Date</label>
        <input
          v-model="localForm.birth_date"
          type="date"
          class="mt-1 block w-full border border-gray-300 rounded-md p-2"
          @input="emit('update:form', localForm)"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700">Year Graduated</label>
        <input
          v-model="localForm.year_graduated"
          type="text"
          class="mt-1 block w-full border border-gray-300 rounded-md p-2"
          @input="emit('update:form', localForm)"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700">Gender</label>
        <select
          v-model="localForm.gender"
          class="mt-1 block w-full border border-gray-300 rounded-md p-2"
          @change="emit('update:form', localForm)"
        >
          <option value="">Select Gender</option>
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
  </div>
</template>