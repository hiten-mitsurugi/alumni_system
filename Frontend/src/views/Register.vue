<script setup>
defineOptions({ name: 'AlumniRegister' });
import { ref } from 'vue';
import api from '../services/api';
import Navbar from '@/components/Navbar.vue';
import VerifyAlumniDirectory from '@/components/register/VerifyAlumniDirectory.vue';
import PersonalInfo from '@/components/register/PersonalInfo.vue';
import WorkHistory from '@/components/register/WorkHistory.vue';
import SkillsRelevance from '@/components/register/SkillRelevance.vue';
import CurriculumRelevance from '@/components/register/CurriculumRelevance.vue';
import PerceptionFurtherStudies from '@/components/register/PerceptionFurtherStudies.vue';
import FeedbackRecommendations from '@/components/register/FeedbackRecommendations.vue';
import backgroundImage from '@/assets/Background.png';

const currentStep = ref(1);
const totalSteps = 7;
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
  present_address: '',
  permanent_address: '',
  birth_date: '',
  year_graduated: '',
  employment_status: '',
  profile_picture: null,
  civil_status: '',
  mothers_name: '',
  mothers_occupation: '',
  fathers_name: '',
  fathers_occupation: '',
  alumni_exists: false,
  current_job: {
    employment_status: '',
    classification: '',
    occupation: '',
    employing_agency: '',
    how_got_job: '',
    monthly_income: '',
    is_breadwinner: false,
    length_of_service: '',
    college_education_relevant: '',
  },
  is_first_job_different: false,
  first_job: {
    employment_status: '',
    classification: '',
    occupation: '',
    employing_agency: '',
    how_got_job: '',
    monthly_income: '',
    is_breadwinner: false,
    length_of_service: '',
    college_education_relevant: '',
  },
  skills_relevance: {
    critical_thinking: null,
    communication: null,
    innovation: null,
    collaboration: null,
    leadership: null,
    productivity_accountability: null,
    entrepreneurship: null,
    global_citizenship: null,
    adaptability: null,
    accessing_analyzing_synthesizing_info: null,
  },
  curriculum_relevance: {
    general_education: null,
    core_major: null,
    special_professional: null,
    electives: null,
    internship_ojt: null,
    co_curricular_activities: null,
    extra_curricular_activities: null,
  },
  perception_further_studies: {
    competitiveness: null,
    pursued_further_studies: false,
    mode_of_study: '',
    level_of_study: '',
    field_of_study: '',
    specialization: '',
    related_to_undergrad: null,
    reasons_for_further_study: '',
  },
  feedback_recommendations: {
    recommendations: '',
  },
});

// Validation functions
const validateName = (name) => /^([A-Za-z]+|[A-Za-z]\.)(?: ([A-Za-z]+|[A-Za-z]\.))*(?: (Sr|Jr)\.?)?$/.test(name.trim());
const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
const validatePassword = (password) =>
  /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/.test(password);
const validatePhoneNumber = (num) => /^\d{11}$/.test(num);

const validateStep = (step) => {
  error.value = '';
  if (step === 1) {
    if (!form.value.alumni_exists) {
      error.value = '❌ Please verify your alumni status.';
      return false;
    }
    return true;
  } else if (step === 2) {
    console.log('Validating Step 2, employment_status:', form.value.employment_status); // Debugging
    const checks = {
      email: validateEmail(form.value.email) || 'Invalid email format.',
      contact_number: validatePhoneNumber(form.value.contact_number) || 'Contact number must be 11 digits.',
      password: validatePassword(form.value.password) || 'Password must be at least 8 characters with uppercase, lowercase, number, and special character.',
      confirm_password: form.value.password === form.value.confirm_password || 'Passwords do not match.',
      present_address: !!form.value.present_address || 'Present address is required.',
      permanent_address: !!form.value.permanent_address || 'Permanent address is required.',
      civil_status: !!form.value.civil_status || 'Civil status is required.',
      government_id: form.value.government_id instanceof File || 'Government ID upload is required.',
      profile_picture: form.value.profile_picture instanceof File || 'Profile picture upload is required.',
      mothers_name: validateName(form.value.mothers_name) || 'Invalid mother\'s name format.',
      mothers_occupation: !!form.value.mothers_occupation || 'Mother\'s occupation is required.',
      fathers_name: validateName(form.value.fathers_name) || 'Invalid father\'s name format.',
      fathers_occupation: !!form.value.fathers_occupation || 'Father\'s occupation is required.',
      employment_status: !!form.value.employment_status || 'Employment status is required.',
    };
    const failed = Object.entries(checks).find(([, val]) => typeof val === 'string');
    if (failed) {
      error.value = `❌ ${failed[1]}`;
      console.log(`Validation failed for ${failed[0]}: ${failed[1]}`);
      return false;
    }
    return true;
  } else if (step === 3) {
    const job = form.value.current_job;
    const checks = {
      employment_status: !!job.employment_status || 'Employment status is required.',
      classification: !!job.classification || 'Classification is required.',
      occupation: !!job.occupation || 'Occupation is required.',
      employing_agency: !!job.employing_agency || 'Employing agency is required.',
      how_got_job: !!job.how_got_job || 'How you got the job is required.',
      monthly_income: !!job.monthly_income || 'Monthly income is required.',
      is_breadwinner: job.is_breadwinner !== null || 'Breadwinner status is required.',
      length_of_service: !!job.length_of_service || 'Length of service is required.',
      college_education_relevant: !!job.college_education_relevant || 'Relevance of college education is required.',
    };
    let failed = Object.entries(checks).find(([, val]) => typeof val === 'string');
    if (failed) {
      error.value = `❌ Present Job: ${failed[1]}`;
      console.log(`Validation failed for current_job.${failed[0]}: ${failed[1]}`);
      return false;
    }
    if (form.value.is_first_job_different) {
      const first = form.value.first_job;
      const firstChecks = {
        employment_status: !!first.employment_status || 'Employment status is required.',
        classification: !!first.classification || 'Classification is required.',
        occupation: !!first.occupation || 'Occupation is required.',
        employing_agency: !!first.employing_agency || 'Employing agency is required.',
        how_got_job: !!first.how_got_job || 'How you got the job is required.',
        monthly_income: !!first.monthly_income || 'Monthly income is required.',
        is_breadwinner: first.is_breadwinner !== null || 'Breadwinner status is required.',
        length_of_service: !!first.length_of_service || 'Length_of_service is required.',
        college_education_relevant: !!first.college_education_relevant || 'Relevance of college education is required.',
      };
      failed = Object.entries(firstChecks).find(([, val]) => typeof val === 'string');
      if (failed) {
        error.value = `❌ First Job: ${failed[1]}`;
        console.log(`Validation failed for first_job.${failed[0]}: ${failed[1]}`);
        return false;
      }
    }
    return true;
  } else if (step === 4) {
    const skills = form.value.skills_relevance;
    const skillKeys = [
      'critical_thinking',
      'communication',
      'innovation',
      'collaboration',
      'leadership',
      'productivity_accountability',
      'entrepreneurship',
      'global_citizenship',
      'adaptability',
      'accessing_analyzing_synthesizing_info',
    ];
    const failedSkill = skillKeys.find(key => !skills[key]);
    if (failedSkill) {
      error.value = `❌ Please rate the skill: ${failedSkill.replace('_', ' ')}`;
      console.log(`Validation failed for skills_relevance.${failedSkill}: not rated`);
      return false;
    }
    return true;
  } else if (step === 5) {
    const curr = form.value.curriculum_relevance;
    const currKeys = [
      'general_education',
      'core_major',
      'special_professional',
      'electives',
      'internship_ojt',
      'co_curricular_activities',
      'extra_curricular_activities',
    ];
    const failedCurr = currKeys.find(key => !curr[key]);
    if (failedCurr) {
      error.value = `❌ Please rate the curriculum item: ${failedCurr.replace('_', ' ')}`;
      console.log(`Validation failed for curriculum_relevance.${failedCurr}: not rated`);
      return false;
    }
    return true;
  } else if (step === 6) {
    const perc = form.value.perception_further_studies;
    if (!perc.competitiveness) {
      error.value = '❌ Please rate the competitiveness of graduates.';
      console.log('Validation failed for perception_further_studies.competitiveness: not rated');
      return false;
    }
    if (perc.pursued_further_studies) {
      const checks = {
        mode_of_study: !!perc.mode_of_study || 'Mode of study is required.',
        level_of_study: !!perc.level_of_study || 'Level of study is required.',
        field_of_study: !!perc.field_of_study || 'Field of study is required.',
        specialization: !!perc.specialization || 'Specialization is required.',
        related_to_undergrad: perc.related_to_undergrad !== null || 'Relation to undergrad is required.',
      };
      const failed = Object.entries(checks).find(([, val]) => typeof val === 'string');
      if (failed) {
        error.value = `❌ Further Studies: ${failed[1]}`;
        console.log(`Validation failed for perception_further_studies.${failed[0]}: ${failed[1]}`);
        return false;
      }
    }
    return true;
  } else if (step === 7) {
    if (!form.value.feedback_recommendations.recommendations) {
      error.value = '❌ Please provide feedback and recommendations.';
      console.log('Validation failed for feedback_recommendations.recommendations: empty');
      return false;
    }
    return true;
  }
  return true;
};

const nextStep = () => {
  console.log('Attempting to proceed from Step', currentStep.value);
  if (validateStep(currentStep.value) && currentStep.value < totalSteps) {
    error.value = '';
    currentStep.value++;
    console.log('Proceeded to Step', currentStep.value);
  }
};

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--;
  }
};

const handleVerified = () => {
  form.value.alumni_exists = true;
  alert('✅ Alumni record found. Proceeding to the next step...');
  setTimeout(() => {
    nextStep();
  });
};

const submitForm = async () => {
  if (!validateStep(currentStep.value)) return;
  error.value = '';
  success.value = '';

  const formData = new FormData();
  formData.append('first_name', form.value.first_name || '');
  formData.append('middle_name', form.value.middle_name || '');
  formData.append('last_name', form.value.last_name || '');
  formData.append('email', form.value.email || '');
  formData.append('contact_number', form.value.contact_number || '');
  formData.append('password', form.value.password || '');
  formData.append('confirm_password', form.value.confirm_password || '');
  formData.append('school_id', form.value.school_id || '');
  if (form.value.government_id) formData.append('government_id', form.value.government_id);
  formData.append('program', form.value.program || '');
  formData.append('present_address', form.value.present_address || '');
  formData.append('permanent_address', form.value.permanent_address || '');
  formData.append('birth_date', form.value.birth_date || '');
  formData.append('year_graduated', form.value.year_graduated || '');
  formData.append('employment_status', form.value.employment_status || '');
  if (form.value.profile_picture) formData.append('profile_picture', form.value.profile_picture);
  formData.append('civil_status', form.value.civil_status || '');
  formData.append('gender', form.value.gender || '');
  formData.append('mothers_name', form.value.mothers_name || '');
  formData.append('mothers_occupation', form.value.mothers_occupation || '');
  formData.append('fathers_name', form.value.fathers_name || '');
  formData.append('fathers_occupation', form.value.fathers_occupation || '');
  formData.append('alumni_exists', form.value.alumni_exists);

  // Format work_histories with proper job_type values
  const workHistories = [
    { job_type: 'Current Job', ...form.value.current_job }
  ];
  if (form.value.is_first_job_different) {
    workHistories.push({ job_type: 'First Job', ...form.value.first_job });
  }
  formData.append('work_histories', JSON.stringify(workHistories));

  // Append nested fields as JSON strings with defaults
  formData.append('skills_relevance', JSON.stringify(form.value.skills_relevance || {}));
  formData.append('curriculum_relevance', JSON.stringify(form.value.curriculum_relevance || {}));
  formData.append('perception_further_studies', JSON.stringify(form.value.perception_further_studies || {}));
  formData.append('feedback_recommendations', JSON.stringify(form.value.feedback_recommendations || {}));

  try {
    await api.post('/auth/register/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    success.value = '✅ Registration successful! Please wait for approval.';
    alert(success.value);
    window.location.reload();
  } catch (err) {
    error.value = err.response?.data?.non_field_errors?.[0] || 'Registration failed.';
    console.error('Submission error:', err.response?.data);
  }
};

const updateStep1Form = (newForm) => {
  form.value.first_name = newForm.first_name;
  form.value.middle_name = newForm.middle_name;
  form.value.last_name = newForm.last_name;
  form.value.school_id = newForm.school_id;
  form.value.program = newForm.program;
  form.value.birth_date = newForm.birth_date;
  form.value.year_graduated = newForm.year_graduated;
  form.value.gender = newForm.gender;
};

const updateStep2Form = (newForm) => {
  form.value.email = newForm.email;
  form.value.contact_number = newForm.contact_number;
  form.value.password = newForm.password;
  form.value.confirm_password = newForm.confirm_password;
  form.value.present_address = newForm.present_address;
  form.value.permanent_address = newForm.permanent_address;
  form.value.civil_status = newForm.civil_status;
  form.value.employment_status = newForm.employment_status; // Added this line
  form.value.government_id = newForm.government_id;
  form.value.profile_picture = newForm.profile_picture;
  form.value.mothers_name = newForm.mothers_name;
  form.value.mothers_occupation = newForm.mothers_occupation;
  form.value.fathers_name = newForm.fathers_name;
  form.value.fathers_occupation = newForm.fathers_occupation;
};

const updateStep3Form = (newForm) => {
  form.value.current_job = { ...newForm.current_job };
  form.value.is_first_job_different = newForm.is_first_job_different;
  form.value.first_job = { ...newForm.first_job };
};

const updateStep4Form = (newForm) => {
  form.value.skills_relevance = { ...newForm.skills_relevance };
};

const updateStep5Form = (newForm) => {
  form.value.curriculum_relevance = { ...newForm.curriculum_relevance };
};

const updateStep6Form = (newForm) => {
  form.value.perception_further_studies = { ...newForm.perception_further_studies };
};

const updateStep7Form = (newForm) => {
  form.value.feedback_recommendations = { ...newForm.feedback_recommendations };
};
</script>

<template>
  <div class="min-h-screen bg-cover bg-center flex flex-col" :style="{ backgroundImage: `url(${backgroundImage})` }">
    <div class="fixed top-0 left-0 right-0 z-50">
      <Navbar />
    </div>
    <div class="h-20"></div>
    <div class="flex items-center justify-center px-4 md:px-20 py-12">
      <div class="bg-white bg-opacity-90 backdrop-blur-md shadow-xl rounded-xl p-10 w-full max-w-3xl">
        <h2 class="text-3xl font-bold text-center text-gray-800 mb-8">Register (Alumni Only)</h2>
        <div v-if="currentStep === 1">
          <h3 class="text-xl font-semibold text-center mb-6">Step 1: Verify Alumni Directory</h3>
          <VerifyAlumniDirectory :form="form.value" @update:form="updateStep1Form" @verified="handleVerified" />
        </div>
        <div v-if="currentStep === 2">
          <h3 class="text-xl font-semibold text-center mb-6">Step 2: Personal and Demographic Information</h3>
          <PersonalInfo :form="form.value" @update:form="updateStep2Form" />
        </div>
        <div v-if="currentStep === 3">
          <h3 class="text-xl font-semibold text-center mb-6">Step 3: Work History</h3>
          <WorkHistory :form="form.value" @update:form="updateStep3Form" />
        </div>
        <div v-if="currentStep === 4">
          <h3 class="text-xl font-semibold text-center mb-6">Step 4: Skills Relevance in Workplace</h3>
          <SkillsRelevance :form="form.value" @update:form="updateStep4Form" />
        </div>
        <div v-if="currentStep === 5">
          <h3 class="text-xl font-semibold text-center mb-6">Step 5: Curriculum and Program Relevance</h3>
          <CurriculumRelevance :form="form.value" @update:form="updateStep5Form" />
        </div>
        <div v-if="currentStep === 6">
          <h3 class="text-xl font-semibold text-center mb-6">Step 6: Perception and Further Studies</h3>
          <PerceptionFurtherStudies :form="form.value" @update:form="updateStep6Form" />
        </div>
        <div v-if="currentStep === 7">
          <h3 class="text-xl font-semibold text-center mb-6">Step 7: Feedback and Recommendations</h3>
          <FeedbackRecommendations :form="form.value" @update:form="updateStep7Form" />
        </div>
        <div class="flex justify-between mt-6">
          <button v-if="currentStep > 1" @click="prevStep"
            class="bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600">
            Back
          </button>
          <button v-if="currentStep > 1 && currentStep < totalSteps" @click="nextStep"
            class="bg-green-700 text-white py-2 px-4 rounded hover:bg-green-800 ml-auto">
            Proceed
          </button>
          <button v-if="currentStep === totalSteps" @click="submitForm"
            class="bg-green-700 text-white py-2 px-4 rounded hover:bg-green-800 ml-auto">
            Submit
          </button>
        </div>
        <p v-if="error" class="text-red-500 text-sm text-center mt-2">{{ error }}</p>
        <p v-if="success.value" class="text-green-500 text-sm text-center mt-2">{{ success.value }}</p>
        <p class="text-center text-sm mt-4">
          Already have an account? <router-link to="/login" class="text-blue-600 hover:underline">Login</router-link>
        </p>
      </div>
    </div>
  </div>
</template>