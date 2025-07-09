<script setup>
import { defineProps, defineEmits, reactive, watch } from 'vue';

const props = defineProps(['form']);
const emit = defineEmits(['update:form']);

const defaultForm = {
  current_job: {
    job_type: 'current_job',
    employment_status: '',
    classification: '',
    occupation: '',
    agency_name: '',
    agency_address: '',
    employing_agency: '',
    how_got_job: '',
    monthly_income: '',
    is_breadwinner: false,
    length_of_service: '',
    college_education_relevant: '',
  },
  is_first_job_different: false,
  first_job: {
    job_type: 'first_job',
    employment_status: '',
    classification: '',
    occupation: '',
    agency_name: '',
    agency_address: '',
    employing_agency: '',
    how_got_job: '',
    monthly_income: '',
    is_breadwinner: false,
    length_of_service: '',
    college_education_relevant: '',
  },
};

// Initialize localForm with default values to prevent undefined errors
const localForm = reactive(JSON.parse(JSON.stringify(defaultForm)));

watch(
  () => props.form,
  (newVal) => {
    // Reset localForm to default
    Object.assign(localForm, JSON.parse(JSON.stringify(defaultForm)));

    if (newVal) {
      // If form comes as current_job and first_job structure
      if (newVal.current_job) {
        Object.assign(localForm.current_job, newVal.current_job);
        const [cName = '', cAddress = ''] = (newVal.current_job.employing_agency || '').split(' - ');
        localForm.current_job.agency_name = cName;
        localForm.current_job.agency_address = cAddress;
      }
      localForm.is_first_job_different = newVal.is_first_job_different || false;
      if (newVal.first_job) {
        Object.assign(localForm.first_job, newVal.first_job);
        const [fName = '', fAddress = ''] = (newVal.first_job.employing_agency || '').split(' - ');
        localForm.first_job.agency_name = fName;
        localForm.first_job.agency_address = fAddress;
      }
    }
  },
  { deep: true, immediate: true } // Run immediately to initialize
);

watch(
  localForm,
  (newVal) => {
    const currentJob = { ...newVal.current_job };
    currentJob.employing_agency = `${currentJob.agency_name || ''}${currentJob.agency_address ? ' - ' + currentJob.agency_address : ''}`;
    // Remove unnecessary fields
    delete currentJob.agency_name;
    delete currentJob.agency_address;

    const firstJob = { ...newVal.first_job };
    firstJob.employing_agency = `${firstJob.agency_name || ''}${firstJob.agency_address ? ' - ' + firstJob.agency_address : ''}`;
    // Remove unnecessary fields
    delete firstJob.agency_name;
    delete firstJob.agency_address;

    emit('update:form', {
      current_job: currentJob,
      is_first_job_different: newVal.is_first_job_different,
      first_job: newVal.is_first_job_different ? firstJob : null
    });
  },
  { deep: true }
);

</script>

<template>
  <div>
    <h4 class="text-lg font-semibold mb-4">Present Employment</h4>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Current Job Inputs -->
      <div>
        <label class="block text-sm text-gray-600 mb-1">Employment Status</label>
        <select v-model="localForm.current_job.employment_status" class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="" disabled>Select Status</option>
          <option value="employed_locally">Employed Locally</option>
          <option value="employed_internationally">Employed Internationally</option>
          <option value="unemployed">Unemployed</option>
          <option value="retired">Retired</option>
        </select>
      </div>

      <div>
        <label class="block text-sm text-gray-600 mb-1">Classification</label>
        <select v-model="localForm.current_job.classification" class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="" disabled>Select Classification</option>
          <option value="government">Government</option>
          <option value="private">Private</option>
          <option value="ngo">NGO</option>
          <option value="freelance">Freelance</option>
        </select>
      </div>

      <div>
        <label class="block text-sm text-gray-600 mb-1">Occupation</label>
        <input v-model="localForm.current_job.occupation" placeholder="Occupation" class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>

      <div>
        <label class="block text-sm text-gray-600 mb-1">Agency Name</label>
        <input v-model="localForm.current_job.agency_name" placeholder="Agency Name" class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div>
        <label class="block text-sm text-gray-600 mb-1">Agency Address</label>
        <input v-model="localForm.current_job.agency_address" placeholder="Agency Address" class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>

      <div>
        <label class="block text-sm text-gray-600 mb-1">How Did You Get This Job?</label>
        <select v-model="localForm.current_job.how_got_job" class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="" disabled>Select one</option>
          <option value="online">Online (JobStreet, LinkedIn, etc.)</option>
          <option value="referral">Referred by a friend or family</option>
          <option value="teacher_recommendation">Recommended by a teacher/professor</option>
          <option value="school_fair">School/job fair</option>
          <option value="walk_in">Walk-in application</option>
          <option value="internship">From internship</option>
          <option value="direct_company">Hired directly by company</option>
          <option value="social_media">Social media (Facebook, etc.)</option>
          <option value="government_program">Government program (PESO, etc.)</option>
          <option value="freelance">Freelance or own business</option>
          <option value="family_business">Family business</option>
          <option value="others">Others</option>
        </select>
      </div>

      <div>
        <label class="block text-sm text-gray-600 mb-1">Monthly Income</label>
        <select v-model="localForm.current_job.monthly_income" class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="" disabled>Select Income</option>
          <option value="less_than_15000">Less than P 15,000</option>
          <option value="15000_to_29999">P 15,000 - P29,999</option>
          <option value="30000_to_49999">P30,000 - P49,999</option>
          <option value="50000_or_more">P50,000 or more</option>
          <option value="prefer_not_to_say">Prefer not to say</option>
        </select>
      </div>

      <div>
        <label class="block text-sm text-gray-600 mb-1">Are You the Breadwinner?</label>
        <div class="flex gap-4">
          <label><input type="radio" v-model="localForm.current_job.is_breadwinner" :value="true" /> Yes</label>
          <label><input type="radio" v-model="localForm.current_job.is_breadwinner" :value="false" /> No</label>
        </div>
      </div>

      <div>
        <label class="block text-sm text-gray-600 mb-1">Length of Service</label>
        <input v-model="localForm.current_job.length_of_service" placeholder="e.g., 2 years" class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>

      <div>
        <label class="block text-sm text-gray-600 mb-1">Is your college education relevant?</label>
        <select v-model="localForm.current_job.college_education_relevant" class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="" disabled>Select Relevance</option>
          <option value="yes">Yes</option>
          <option value="no">No</option>
          <option value="somewhat">Somewhat</option>
        </select>
      </div>
    </div>

    <!-- First Job Section -->
    <div class="mt-4">
      <label class="block text-sm text-gray-600 mb-1">Is your current job your first job?</label>
      <input type="checkbox" v-model="localForm.is_first_job_different" /> No, it’s different
    </div>

    <div v-if="localForm.is_first_job_different" class="mt-6">
      <h4 class="text-lg font-semibold mb-4">First Job</h4>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm text-gray-600 mb-1">Employment Status</label>
          <select v-model="localForm.first_job.employment_status" class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="" disabled>Select Status</option>
            <option value="employed_locally">Employed Locally</option>
            <option value="employed_internationally">Employed Internationally</option>
            <option value="unemployed">Unemployed</option>
            <option value="retired">Retired</option>
          </select>
        </div>

        <div>
          <label class="block text-sm text-gray-600 mb-1">Classification</label>
          <select v-model="localForm.first_job.classification" class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="" disabled>Select Classification</option>
            <option value="government">Government</option>
            <option value="private">Private</option>
            <option value="ngo">NGO</option>
            <option value="freelance">Freelance</option>
          </select>
        </div>

        <div>
          <label class="block text-sm text-gray-600 mb-1">Occupation</label>
          <input v-model="localForm.first_job.occupation" placeholder="Occupation" class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>

        <div>
          <label class="block text-sm text-gray-600 mb-1">Agency Name</label>
          <input v-model="localForm.first_job.agency_name" placeholder="Agency Name" class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">Agency Address</label>
          <input v-model="localForm.first_job.agency_address" placeholder="Agency Address" class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>

        <div>
          <label class="block text-sm text-gray-600 mb-1">How Did You Get This Job?</label>
          <select v-model="localForm.first_job.how_got_job" class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="" disabled>Select one</option>
            <option value="online">Online (JobStreet, LinkedIn, etc.)</option>
            <option value="referral">Referred by a friend or family</option>
            <option value="teacher_recommendation">Recommended by a teacher/professor</option>
            <option value="school_fair">School/job fair</option>
            <option value="walk_in">Walk-in application</option>
            <option value="internship">From internship</option>
            <option value="direct_company">Hired directly by company</option>
            <option value="social_media">Social media (Facebook, etc.)</option>
            <option value="government_program">Government program (PESO, etc.)</option>
            <option value="freelance">Freelance or own business</option>
            <option value="family_business">Family business</option>
            <option value="others">Others</option>
          </select>
        </div>

        <div>
          <label class="block text-sm text-gray-600 mb-1">Monthly Income</label>
          <select v-model="localForm.first_job.monthly_income" class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="" disabled>Select Income</option>
            <option value="less_than_15000">Less than P 15,000</option>
            <option value="15000_to_29999">P 15,000 - P29,999</option>
            <option value="30000_to_49999">P30,000 - P49,999</option>
            <option value="50000_or_more">P50,000 or more</option>
            <option value="prefer_not_to_say">Prefer not to say</option>
          </select>
        </div>

        <div>
          <label class="block text-sm text-gray-600 mb-1">Are You the Breadwinner?</label>
          <div class="flex gap-4">
            <label><input type="radio" v-model="localForm.first_job.is_breadwinner" :value="true" /> Yes</label>
            <label><input type="radio" v-model="localForm.first_job.is_breadwinner" :value="false" /> No</label>
          </div>
        </div>

        <div>
          <label class="block text-sm text-gray-600 mb-1">Length of Service</label>
          <input v-model="localForm.first_job.length_of_service" placeholder="e.g., 2 years" class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>

        <div>
          <label class="block text-sm text-gray-600 mb-1">Is your college education relevant?</label>
          <select v-model="localForm.first_job.college_education_relevant" class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="" disabled>Select Relevance</option>
            <option value="yes">Yes</option>
            <option value="no">No</option>
            <option value="somewhat">Somewhat</option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>