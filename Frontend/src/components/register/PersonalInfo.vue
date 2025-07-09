<script setup>
import { defineProps, defineEmits, reactive, watch } from 'vue';

// Define props and emits
const props = defineProps(['form']);
const emit = defineEmits(['update:form']);

// Initialize localForm with all expected fields to prevent undefined errors
const localForm = reactive({
  email: props.form?.email || '',
  contact_number: props.form?.contact_number || '',
  password: props.form?.password || '',
  confirm_password: props.form?.confirm_password || '',
  present_address: props.form?.present_address || '',
  permanent_address: props.form?.permanent_address || '',
  civil_status: props.form?.civil_status || '',
  employment_status: props.form?.employment_status || '',
  government_id: props.form?.government_id || null,
  profile_picture: props.form?.profile_picture || null,
  mothers_name: props.form?.mothers_name || '',
  mothers_occupation: props.form?.mothers_occupation || '',
  fathers_name: props.form?.fathers_name || '',
  fathers_occupation: props.form?.fathers_occupation || '',
});

// Handle file input
const handleFileChange = (event, field) => {
  localForm[field] = event.target.files[0];
  emit('update:form', { ...localForm });
};

// Sync updates to parent
watch(
  localForm,
  (newVal) => {
    emit('update:form', { ...newVal });
  },
  { deep: true }
);
</script>

<template>
  <div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Contact Info -->
      <div>
        <label class="block text-sm font-medium text-gray-700">Email</label>
        <input v-model="localForm.email" type="email" class="mt-1 w-full border rounded-md p-2" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">Contact Number</label>
        <input v-model="localForm.contact_number" type="text" class="mt-1 w-full border rounded-md p-2" />
      </div>

      <!-- Passwords -->
      <div>
        <label class="block text-sm font-medium text-gray-700">Password</label>
        <input v-model="localForm.password" type="password" class="mt-1 w-full border rounded-md p-2" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">Confirm Password</label>
        <input v-model="localForm.confirm_password" type="password" class="mt-1 w-full border rounded-md p-2" />
      </div>

      <!-- Address -->
      <div>
        <label class="block text-sm font-medium text-gray-700">Present Address</label>
        <input v-model="localForm.present_address" type="text" class="mt-1 w-full border rounded-md p-2" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">Permanent Address</label>
        <input v-model="localForm.permanent_address" type="text" class="mt-1 w-full border rounded-md p-2" />
      </div>

      <!-- Civil Status -->
      <div>
        <label class="block text-sm font-medium text-gray-700">Civil Status</label>
        <select v-model="localForm.civil_status" class="mt-1 w-full border rounded-md p-2">
          <option value="">Select Status</option>
          <option value="single">Single</option>
          <option value="married">Married</option>
          <option value="separated">Separated</option>
          <option value="widowed">Widowed</option>
        </select>
      </div>

      <!-- Employment Status -->
      <div>
        <label class="block text-sm font-medium text-gray-700">Employment Status</label>
        <select v-model="localForm.employment_status" class="mt-1 w-full border rounded-md p-2">
          <option value="">Select Employment Status</option>
          <option value="employed_locally">Employed Locally</option>
          <option value="employed_internationally">Employed Internationally</option>
          <option value="self_employed">Self-Employed</option>
          <option value="unemployed">Unemployed</option>
          <option value="retired">Retired</option>
        </select>
      </div>

      <!-- Uploads -->
      <div>
        <label class="block text-sm font-medium text-gray-700">Government ID</label>
        <input type="file" @change="handleFileChange($event, 'government_id')" class="mt-1 w-full border rounded-md p-2" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">Profile Picture</label>
        <input type="file" @change="handleFileChange($event, 'profile_picture')" class="mt-1 w-full border rounded-md p-2" />
      </div>

      <!-- Parents Info -->
      <div>
        <label class="block text-sm font-medium text-gray-700">Mother's Name</label>
        <input v-model="localForm.mothers_name" type="text" class="mt-1 w-full border rounded-md p-2" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">Mother's Occupation</label>
        <input v-model="localForm.mothers_occupation" type="text" class="mt-1 w-full border rounded-md p-2" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">Father's Name</label>
        <input v-model="localForm.fathers_name" type="text" class="mt-1 w-full border rounded-md p-2" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">Father's Occupation</label>
        <input v-model="localForm.fathers_occupation" type="text" class="mt-1 w-full border rounded-md p-2" />
      </div>
    </div>
  </div>
</template>