<script setup>
defineOptions({ name: 'AlumniRegister' });
import { ref, computed, onMounted, onUnmounted } from 'vue';
import api from '../services/api';
import Navbar from '@/components/Navbar.vue';
import VerifyAlumniDirectory from '@/components/register/VerifyAlumniDirectory.vue';
import PersonalInfo from '@/components/register/PersonalInfo.vue';
import VerificationAgreement from '@/components/register/VerificationAgreement.vue';
import SurveyConsent from '@/components/register/SurveyConsent.vue';
import DynamicSurveyStep from '@/components/register/DynamicSurveyStep.vue';
import { useRegistrationSurvey } from '@/composables/useRegistrationSurvey';
import backgroundImage from '@/assets/Background.png';

const currentStep = ref(1);
const error = ref('');
const success = ref('');
const agreementAccepted = ref(false);
const skipVerificationAgreement = ref(false);
const surveyConsentGiven = ref(false);

// Use registration survey composable
const {
  loading: surveyLoading,
  error: surveyError,
  surveyCategories,
  surveyResponses,
  surveyErrors,
  loadRegistrationSurvey,
  updateCategoryResponses,
  validateCategory,
  getSurveyResponsesForSubmission,
  clearSurveyData
} = useRegistrationSurvey();

// Calculate total steps dynamically based on conditional logic
const totalSteps = computed(() => {
  let stepCount = 4; // 4 static steps (Verify, PersonalInfo, VerificationAgreement, SurveyConsent)
  
  // Add survey categories that should be visible ONLY if survey consent is given
  if (surveyConsentGiven.value) {
    for (const categoryData of surveyCategories.value) {
      if (shouldShowCategory(categoryData)) {
        stepCount++;
      }
    }
  }
  
  return stepCount;
});

// Function to determine if a category should be shown
const shouldShowCategory = (categoryData) => {
  const category = categoryData.category;
  
  // If no conditional logic, show the category
  if (!category.depends_on_category) {
    return true;
  }
  
  // Check if the dependency condition is met
  const dependsOnCategoryId = category.depends_on_category;
  const dependsOnQuestionText = category.depends_on_question_text;
  const dependsOnValue = JSON.parse(category.depends_on_value || '[]');
  
  // Find the response for the dependency question
  const dependencyCategoryData = surveyCategories.value.find(
    cat => cat.category.id === dependsOnCategoryId
  );
  
  if (!dependencyCategoryData) return false;
  
  // Find the specific question in the dependency category
  const dependencyQuestion = dependencyCategoryData.questions.find(
    q => q.question_text === dependsOnQuestionText
  );
  
  if (!dependencyQuestion) return false;
  
  // Check if user has answered the dependency question with the required value
  const userResponse = surveyResponses.value[dependencyQuestion.id];
  return dependsOnValue.includes(userResponse);
};

// Get visible categories in order
const getVisibleCategories = computed(() => {
  return surveyCategories.value.filter(categoryData => shouldShowCategory(categoryData));
});

// Get current survey category for dynamic steps (considering skipped categories)
const currentSurveyCategory = computed(() => {
  const surveyStepIndex = currentStep.value - 5; // Adjust for 4 static steps (was 4, now 5)
  const visibleCategories = getVisibleCategories.value;
  return visibleCategories[surveyStepIndex] || null;
});

// Static form for steps 1 and 2
const form = ref({
  // Step 1: Alumni Directory Verification
  first_name: '',
  middle_name: '',
  last_name: '',
  school_id: '',
  program: '',
  birth_date: '',
  year_graduated: '',
  sex: '',
  alumni_exists: false,
  
  // Step 2: Personal Information
  email: '',
  contact_number: '',
  password: '',
  confirm_password: '',
  present_address: '',
  permanent_address: '',
  // Structured address data for new system
  present_address_data: {
    address_type: 'philippines',
    region_code: '',
    region_name: '',
    province_code: '',
    province_name: '',
    city_code: '',
    city_name: '',
    barangay: '',
    street_address: '',
    postal_code: '',
    country: '',
    full_address: ''
  },
  permanent_address_data: {
    address_type: 'philippines',
    region_code: '',
    region_name: '',
    province_code: '',
    province_name: '',
    city_code: '',
    city_name: '',
    barangay: '',
    street_address: '',
    postal_code: '',
    country: '',
    full_address: ''
  },
  same_as_present: false,
  gender: '',
  civil_status: '',
  employment_status: '',
  government_id: null,
  profile_picture: null,
  mothers_name: '',
  mothers_occupation: '',
  fathers_name: '',
  fathers_occupation: '',
});

// Get step title
const getStepTitle = computed(() => {
  if (currentStep.value === 1) return 'Step 1: Verify Alumni Directory';
  if (currentStep.value === 2) return 'Step 2: Personal and Demographic Information';
  if (currentStep.value === 3) return 'Step 3: Confirm Your Information';
  if (currentStep.value === 4) return 'Step 4: Survey Participation';
  
  const category = currentSurveyCategory.value;
  return category ? `Step ${currentStep.value}: ${category.category.name}` : '';
});

// Validation function for each step
const validateStep = (step) => {
  if (step === 1) {
    // Step 1: Alumni Directory Verification
    // No validation needed for verification step - it auto-proceeds
    return true;
  } else if (step === 2) {
    // Step 2: Personal Information
    const requiredFields = ['first_name', 'last_name', 'email', 'password', 'confirm_password'];
    for (const field of requiredFields) {
      if (!form.value[field] || form.value[field].trim() === '') {
        error.value = `Please fill in the ${field.replace('_', ' ')} field.`;
        return false;
      }
    }
    
    if (form.value.password !== form.value.confirm_password) {
      error.value = 'Passwords do not match.';
      return false;
    }
    
    return true;
  } else if (step === 3) {
    // Step 3: Verification Agreement - validation not needed, handled by handlers
    return true;
  } else if (step === 4) {
    // Step 4: Survey Consent - validation not needed, handled by handlers
    return true;
  } else {
    // Survey steps validation using the composable
    const surveyStepIndex = step - 5; // Adjust for 4 static steps now
    const visibleCategories = getVisibleCategories.value;
    
    if (surveyStepIndex >= 0 && surveyStepIndex < visibleCategories.length) {
      const categoryData = visibleCategories[surveyStepIndex];
      return validateCategory(categoryData.category.id);
    }
    
    return true;
  }
};

// Enhanced navigation functions that handle category skipping
const nextStep = () => {
  if (!validateStep(currentStep.value)) return;
  
  error.value = '';
  let nextStepNumber = currentStep.value + 1;
  
  // For survey steps, check if we need to skip categories
  if (nextStepNumber > 4) {
    const visibleCategories = getVisibleCategories.value;
    const maxSurveySteps = visibleCategories.length;
    const maxTotalSteps = 4 + maxSurveySteps; // 4 static steps
    
    if (nextStepNumber <= maxTotalSteps) {
      currentStep.value = nextStepNumber;
    }
  } else if (nextStepNumber <= totalSteps.value) {
    currentStep.value = nextStepNumber;
  }
};

const prevStep = () => {
  if (currentStep.value > 1) {
    let prevStepNumber = currentStep.value - 1;
    
    // For survey steps, navigate through visible categories only
    if (currentStep.value > 4) {
      currentStep.value = prevStepNumber;
    } else {
      currentStep.value = prevStepNumber;
    }
  }
};

const handleVerified = () => {
  form.value.alumni_exists = true;
  alert('✅ Alumni record found. Proceeding to the next step...');
  setTimeout(() => {
    nextStep();
  });
};

const handleAgreementProceed = () => {
  agreementAccepted.value = true;
  nextStep();
};

const handleAgreementGoBack = () => {
  agreementAccepted.value = false;
  prevStep();
};

const handleAgreementSkip = () => {
  // Allow user to skip the full survey and register with basic info
  skipVerificationAgreement.value = true;
  // Jump directly to submission
  currentStep.value = totalSteps.value;
};

const handleSurveyConsentAccept = () => {
  surveyConsentGiven.value = true;
  nextStep();
};

const handleSurveyConsentDecline = () => {
  surveyConsentGiven.value = false;
  // Jump directly to submission (skip all surveys)
  currentStep.value = totalSteps.value;
};

const submitForm = async () => {
  if (!validateStep(currentStep.value)) return;
  error.value = '';
  success.value = '';

  const formData = new FormData();
  
  // Add static form data
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
  // Add address data as JSON
  if (form.value.present_address_data) {
    formData.append('present_address_data', JSON.stringify(form.value.present_address_data));
  }
  if (form.value.permanent_address_data) {
    formData.append('permanent_address_data', JSON.stringify(form.value.permanent_address_data));
  }
  
  // Keep legacy address fields for backward compatibility
  formData.append('present_address', form.value.present_address || '');
  formData.append('permanent_address', form.value.permanent_address || '');
  formData.append('birth_date', form.value.birth_date || '');
  formData.append('year_graduated', form.value.year_graduated || '');
  formData.append('employment_status', form.value.employment_status || '');
  formData.append('gender', form.value.gender || '');
  if (form.value.profile_picture) formData.append('profile_picture', form.value.profile_picture);
  formData.append('civil_status', form.value.civil_status || '');
  formData.append('sex', form.value.sex || '');
  formData.append('mothers_name', form.value.mothers_name || '');
  formData.append('mothers_occupation', form.value.mothers_occupation || '');
  formData.append('fathers_name', form.value.fathers_name || '');
  formData.append('fathers_occupation', form.value.fathers_occupation || '');
  formData.append('alumni_exists', form.value.alumni_exists);

  // Add dynamic survey responses
  const surveyResponsesData = getSurveyResponsesForSubmission();
  formData.append('survey_responses', JSON.stringify(surveyResponsesData));

  // Debug logging - let's see exactly what's being sent
  console.log("=== REGISTRATION DEBUG INFO ===");
  console.log("Form data being sent:");
  console.log("- alumni_exists:", form.value.alumni_exists);
  console.log("- email:", form.value.email);
  console.log("- employment_status:", form.value.employment_status);
  console.log("- sex:", form.value.sex);
  console.log("- civil_status:", form.value.civil_status);
  console.log("- present_address_data:", form.value.present_address_data);
  console.log("- permanent_address_data:", form.value.permanent_address_data);
  console.log("- same_as_present:", form.value.same_as_present);
  console.log("- survey_responses:", surveyResponsesData);
  console.log("- survey_responses length:", surveyResponsesData.length);
  console.log("Full form object:", form.value);

  try {
    const response = await api.post('/auth/register/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    success.value = '✅ Registration successful! Please wait for approval.';
    alert(success.value);
    clearSurveyData();
    window.location.reload();
  } catch (err) {
    console.error("=== REGISTRATION ERROR ===");
    console.error('Full error object:', err);
    console.error('Error response:', err.response);
    console.error('Error response data:', err.response?.data);
    console.error('Error status:', err.response?.status);
    
    error.value = err.response?.data?.non_field_errors?.[0] || 'Registration failed.';
    console.error('Submission error:', err.response?.data);
  }
};

// Update functions for static steps
const updateStep1Form = (newForm) => {
  Object.assign(form.value, newForm);
};

const updateStep2Form = (newForm) => {
  Object.assign(form.value, newForm);
};

// Handle dynamic survey step updates
const handleSurveyResponses = (responses) => {
  updateCategoryResponses(responses);
};

// Force light theme while this registration page is mounted and load survey data
onMounted(async () => {
  const wasDark = document.documentElement.classList.contains('dark');
  try { localStorage.setItem('prev-theme-was-dark', wasDark ? '1' : '0'); } catch (e) {}
  document.documentElement.classList.remove('dark');
  await loadRegistrationSurvey();
});

onUnmounted(() => {
  try {
    if (localStorage.getItem('prev-theme-was-dark') === '1') {
      document.documentElement.classList.add('dark');
    }
    localStorage.removeItem('prev-theme-was-dark');
  } catch (e) {}
});
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
        
                <!-- Progress Indicator -->
        <div class="mb-6">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-gray-700">Progress</span>
            <span class="text-sm text-gray-600">Step {{ currentStep }} of {{ totalSteps }}</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              class="bg-orange-500 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${(currentStep / totalSteps) * 100}%` }"
            ></div>
          </div>
        </div>

        <!-- Loading Survey Questions -->
        <div v-if="surveyLoading" class="flex items-center justify-center py-12">
          <div class="text-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500 mx-auto mb-4"></div>
            <p class="text-gray-600">Loading survey questions...</p>
          </div>
        </div>

        <!-- Survey Error -->
        <div v-else-if="surveyError" class="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
          <div class="text-center">
            <h3 class="text-lg font-medium text-red-800 mb-2">Error Loading Survey</h3>
            <p class="text-red-700">{{ surveyError }}</p>
            <button
              @click="loadRegistrationSurvey"
              class="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        </div>

        <!-- Registration Steps -->
        <template v-else>
          <!-- Step 1: Alumni Directory Verification -->
          <div v-if="currentStep === 1">
            <h3 class="text-xl font-semibold text-center mb-6">{{ getStepTitle }}</h3>
            <VerifyAlumniDirectory :form="form" @update:form="updateStep1Form" @verified="handleVerified" />
          </div>

          <!-- Step 2: Personal Information -->
          <div v-if="currentStep === 2">
            <h3 class="text-xl font-semibold text-center mb-6">{{ getStepTitle }}</h3>
            <PersonalInfo :form="form" @update:form="updateStep2Form" />
          </div>

          <!-- Step 3: Verification Agreement -->
          <div v-if="currentStep === 3">
            <h3 class="text-xl font-semibold text-center mb-6">{{ getStepTitle }}</h3>
            <VerificationAgreement 
              :form="form"
              @proceed="handleAgreementProceed"
              @go-back="handleAgreementGoBack"
              @skip-register="handleAgreementSkip"
            />
          </div>

          <!-- Step 4: Survey Consent -->
          <div v-if="currentStep === 4">
            <SurveyConsent
              :form="form"
              @accept="handleSurveyConsentAccept"
              @decline="handleSurveyConsentDecline"
            />
          </div>

          <!-- Dynamic Survey Steps -->
          <div v-if="currentStep > 4 && currentSurveyCategory">
            <h3 class="text-xl font-semibold text-center mb-6">{{ getStepTitle }}</h3>
            <DynamicSurveyStep
              :category="currentSurveyCategory.category"
              :questions="currentSurveyCategory.questions"
              :responses="surveyResponses"
              :errors="surveyErrors"
              @update:responses="handleSurveyResponses"
            />
          </div>
        </template>

        <!-- Navigation Buttons -->
        <div class="flex justify-between mt-6" v-if="!surveyLoading && !surveyError">
          <button 
            v-if="currentStep > 1 && currentStep !== 4" 
            @click="prevStep"
            class="bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600 transition-colors"
          >
            Back
          </button>
          
          <!-- Hide Proceed button for Step 1 (Verify Alumni Directory) since it auto-proceeds -->
          <!-- Hide Proceed button for Step 4 (Survey Consent) since it has custom buttons -->
          <button 
            v-if="currentStep < totalSteps && currentStep !== 1 && currentStep !== 4" 
            @click="nextStep"
            class="bg-orange-500 text-white py-2 px-4 rounded hover:bg-orange-600 ml-auto transition-colors"
          >
            Proceed
          </button>
          
          <button 
            v-if="currentStep === totalSteps" 
            @click="submitForm"
            class="bg-orange-500 text-white py-2 px-4 rounded hover:bg-orange-600 ml-auto transition-colors"
          >
            Submit Registration
          </button>
        </div>

        <!-- Error Message -->
        <p v-if="error" class="text-red-500 text-sm text-center mt-4">{{ error }}</p>
        
        <!-- Success Message -->
        <p v-if="success" class="text-orange-500 text-sm text-center mt-4">{{ success }}</p>
        
        <!-- Login Link -->
        <p class="text-center text-sm mt-6">
          Already have an account? 
          <router-link to="/login" class="text-blue-600 hover:underline">Login</router-link>
        </p>
      </div>
    </div>
  </div>
</template>
