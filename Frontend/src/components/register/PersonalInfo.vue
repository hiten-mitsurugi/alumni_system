<script setup>
import { defineProps, defineEmits, reactive, watch, ref, computed } from 'vue';
import { Eye, EyeOff, Check, X, AlertCircle, CheckCircle2, XCircle, Loader2 } from 'lucide-vue-next';
import api from '@/services/api';
import AddressSelector from '@/components/common/AddressSelector.vue';
import TermsAndConditions from '@/components/TermsAndConditions.vue';

// Define props and emits
const props = defineProps(['form']);
const emit = defineEmits(['update:form', 'validation-change']);

// Password visibility toggles
const showPassword = ref(false);
const showConfirmPassword = ref(false);

// Terms & Conditions
const showTermsModal = ref(false);
const agreedToTerms = ref(false);

// Validation states
const emailExists = ref(false);
const checkingEmail = ref(false);
const emailError = ref('');

// Initialize localForm with all expected fields to prevent undefined errors
  const localForm = reactive({
    email: props.form?.email || '',
    password: props.form?.password || '',
    confirmPassword: props.form?.confirmPassword || '',
    address: props.form?.address || '',
    country: props.form?.country || '',
    state: props.form?.state || '',
    city: props.form?.city || '',
    family_info: props.form?.family_info || '',
    government_id: props.form?.government_id || null,
    id_number: props.form?.id_number || '',
    agreed_to_terms: props.form?.agreed_to_terms || false,
  });

// Password validation rules
const passwordRequirements = computed(() => {
  const password = localForm.password;
  return {
    minLength: password.length >= 8,
    hasUpperCase: /[A-Z]/.test(password),
    hasLowerCase: /[a-z]/.test(password),
    hasNumber: /\d/.test(password),
    hasSpecialChar: /[!@#$%^&*(),.?":{}|<>]/.test(password)
  };
});

const isPasswordValid = computed(() => {
  const reqs = passwordRequirements.value;
  return reqs.minLength && reqs.hasUpperCase && reqs.hasLowerCase && reqs.hasNumber && reqs.hasSpecialChar;
});

const passwordsMatch = computed(() => {
  return localForm.password && localForm.confirm_password && localForm.password === localForm.confirm_password;
});

// Password strength calculation (1 = Weak, 2 = Medium, 3 = Strong)
const passwordStrength = computed(() => {
  if (!localForm.password) return 0;
  
  const reqs = passwordRequirements.value;
  let score = 0;
  
  // Basic requirements (length + 1 type)
  if (reqs.minLength && (reqs.hasLowerCase || reqs.hasUpperCase || reqs.hasNumber)) {
    score = 1; // Weak
  }
  
  // Medium strength (length + 3 types)
  if (reqs.minLength && 
      [reqs.hasUpperCase, reqs.hasLowerCase, reqs.hasNumber, reqs.hasSpecialChar].filter(Boolean).length >= 3) {
    score = 2; // Medium
  }
  
  // Strong (all requirements + good length)
  if (reqs.minLength && reqs.hasUpperCase && reqs.hasLowerCase && reqs.hasNumber && reqs.hasSpecialChar) {
    score = 3; // Strong
  }
  
  return score;
});

const passwordStrengthText = computed(() => {
  switch (passwordStrength.value) {
    case 1: return 'Weak';
    case 2: return 'Medium';
    case 3: return 'Strong';
    default: return '';
  }
});

// Email validation function
const checkEmailExists = async (email) => {
  if (!email || !email.includes('@')) {
    emailError.value = '';
    emailExists.value = false;
    return;
  }

  checkingEmail.value = true;
  emailError.value = '';

  try {
    // Use the correct endpoint path - auth_app.urls is included at 'api/' so the endpoint is 'api/check-email/'
    const response = await api.get(`/auth/check-email/?email=${encodeURIComponent(email)}`);
    
    if (response.data.exists) {
      emailExists.value = true;
      emailError.value = 'This email is already registered. Please use a different email.';
    } else {
      emailExists.value = false;
      emailError.value = '';
    }
  } catch (error) {
    console.error('Email check error:', error);
    // On any error, assume email is available to not block registration
    emailExists.value = false;
    emailError.value = '';
    
    // Only show error message if it's not a network/auth issue
    if (error.response && error.response.status !== 401 && error.response.status !== 403) {
      emailError.value = 'Unable to verify email. Please try again.';
    }
  } finally {
    checkingEmail.value = false;
  }
};

// Debounced email check
let emailCheckTimeout = null;
const debouncedEmailCheck = (email) => {
  clearTimeout(emailCheckTimeout);
  emailCheckTimeout = setTimeout(() => {
    checkEmailExists(email);
  }, 500);
};

// Handle file input
const handleFileChange = (event, field) => {
  localForm[field] = event.target.files[0];
  emit('update:form', { ...localForm });
};

// Emit validation status to parent
const emitValidation = () => {
  const isValid = !emailExists.value && isPasswordValid.value && passwordsMatch.value && localForm.email && localForm.password && agreedToTerms.value;
  emit('validation-change', {
    isValid,
    errors: {
      email: emailError.value,
      password: !isPasswordValid.value ? 'Password does not meet requirements' : '',
      confirmPassword: !passwordsMatch.value ? 'Passwords do not match' : '',
      terms: !agreedToTerms.value ? 'You must agree to the Terms and Conditions' : ''
    }
  });
};

// Watch for "same as present address" checkbox
watch(() => localForm.same_as_present, (newValue) => {
  if (newValue) {
    // Copy present address data to permanent address
    Object.assign(localForm.permanent_address_data, localForm.present_address_data);
    localForm.permanent_address = localForm.present_address;
  }
});

// Watch for changes in present address when "same as present" is checked
watch(() => localForm.present_address_data, (newAddressData) => {
  if (localForm.same_as_present) {
    Object.assign(localForm.permanent_address_data, newAddressData);
    localForm.permanent_address = localForm.present_address;
  }
}, { deep: true });

// Watch for present address text changes
watch(() => localForm.present_address, (newAddress) => {
  if (localForm.same_as_present) {
    localForm.permanent_address = newAddress;
  }
});

// Watch for email changes
watch(() => localForm.email, (newEmail) => {
  if (newEmail) {
    debouncedEmailCheck(newEmail);
  } else {
    emailExists.value = false;
    emailError.value = '';
  }
});

// Watch for password changes
watch([() => localForm.password, () => localForm.confirm_password], () => {
  emitValidation();
});

// Watch for email validation changes
watch([emailExists, emailError], () => {
  emitValidation();
});

// Sync agreed_to_terms from ref to reactive form
watch(
  agreedToTerms,
  (newVal) => {
    localForm.agreed_to_terms = newVal;
  }
);

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
        <div class="relative">
          <input 
            v-model="localForm.email" 
            type="email" 
            :class="[
              'mt-1 w-full border rounded-md p-2 pr-10',
              emailError ? 'border-red-500' : emailExists === false && localForm.email ? 'border-green-500' : ''
            ]"
          />
          <!-- Email validation icons -->
          <div class="absolute inset-y-0 right-0 pr-3 flex items-center">
            <CheckCircle2 
              v-if="emailExists === false && localForm.email" 
              class="h-5 w-5 text-green-500" 
            />
            <XCircle 
              v-if="emailExists === true" 
              class="h-5 w-5 text-red-500" 
            />
            <Loader2 
              v-if="checkingEmail" 
              class="h-5 w-5 text-blue-500 animate-spin" 
            />
          </div>
        </div>
        <!-- Email error message -->
        <div v-if="emailError" class="mt-1 text-xs text-red-600">
          {{ emailError }}
        </div>
        <div v-else-if="emailExists === false && localForm.email" class="mt-1 text-xs text-green-600">
          Email is available
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">Contact Number</label>
        <input v-model="localForm.contact_number" type="text" class="mt-1 w-full border rounded-md p-2" />
      </div>

      <!-- Passwords -->
      <div>
        <label class="block text-sm font-medium text-gray-700">Password</label>
        <div class="relative">
          <input 
            v-model="localForm.password" 
            :type="showPassword ? 'text' : 'password'" 
            :class="[
              'mt-1 w-full border rounded-md p-2 pr-10',
              localForm.password ? (isPasswordValid ? 'border-green-500' : 'border-red-500') : ''
            ]"
          />
          <button
            type="button"
            @click="showPassword = !showPassword"
            class="absolute inset-y-0 right-0 pr-3 flex items-center"
          >
            <Eye v-if="!showPassword" class="h-5 w-5 text-gray-400 hover:text-gray-600" />
            <EyeOff v-else class="h-5 w-5 text-gray-400 hover:text-gray-600" />
          </button>
        </div>
        
        <!-- Password Strength Indicator -->
        <div v-if="localForm.password" class="mt-1">
          <div class="flex items-center gap-2 text-xs">
            <span>Strength:</span>
            <div class="flex gap-1">
              <div :class="['h-1 w-4 rounded', passwordStrength >= 1 ? 'bg-red-500' : 'bg-gray-200']"></div>
              <div :class="['h-1 w-4 rounded', passwordStrength >= 2 ? 'bg-yellow-500' : 'bg-gray-200']"></div>
              <div :class="['h-1 w-4 rounded', passwordStrength >= 3 ? 'bg-green-500' : 'bg-gray-200']"></div>
            </div>
            <span :class="[
              'font-medium', 
              passwordStrength === 1 ? 'text-red-500' : 
              passwordStrength === 2 ? 'text-yellow-500' : 
              passwordStrength === 3 ? 'text-green-500' : 'text-gray-400'
            ]">
              {{ passwordStrengthText }}
            </span>
          </div>
        </div>
        
        <!-- Compact Password Requirements - Only show if password is weak -->
        <div v-if="localForm.password && !isPasswordValid" class="mt-1">
          <div class="text-xs text-gray-600 mb-1">Missing:</div>
          <div class="flex flex-wrap gap-2 text-xs">
            <span v-if="!passwordRequirements.length" class="bg-red-100 text-red-600 px-2 py-1 rounded">8+ chars</span>
            <span v-if="!passwordRequirements.uppercase" class="bg-red-100 text-red-600 px-2 py-1 rounded">A-Z</span>
            <span v-if="!passwordRequirements.lowercase" class="bg-red-100 text-red-600 px-2 py-1 rounded">a-z</span>
            <span v-if="!passwordRequirements.number" class="bg-red-100 text-red-600 px-2 py-1 rounded">0-9</span>
            <span v-if="!passwordRequirements.special" class="bg-red-100 text-red-600 px-2 py-1 rounded">!@#$</span>
          </div>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">Confirm Password</label>
        <div class="relative">
          <input 
            v-model="localForm.confirm_password" 
            :type="showConfirmPassword ? 'text' : 'password'" 
            :class="[
              'mt-1 w-full border rounded-md p-2 pr-10',
              localForm.confirm_password ? (passwordsMatch ? 'border-green-500' : 'border-red-500') : ''
            ]"
          />
          <button
            type="button"
            @click="showConfirmPassword = !showConfirmPassword"
            class="absolute inset-y-0 right-0 pr-3 flex items-center"
          >
            <Eye v-if="!showConfirmPassword" class="h-5 w-5 text-gray-400 hover:text-gray-600" />
            <EyeOff v-else class="h-5 w-5 text-gray-400 hover:text-gray-600" />
          </button>
        </div>
        <div v-if="localForm.confirm_password && !passwordsMatch" class="mt-1 text-xs text-red-600">
          Passwords do not match
        </div>
        <div v-else-if="localForm.confirm_password && passwordsMatch" class="mt-1 text-xs text-green-600">
          Passwords match
        </div>
      </div>

      <!-- Address Section -->
      <div class="col-span-2">
        <h4 class="text-lg font-semibold text-gray-900 mb-4 border-b border-gray-200 pb-2">Address Information</h4>
        
        <!-- Present Address -->
        <div class="mb-6">
          <h5 class="text-md font-medium text-gray-700 mb-3">Present Address</h5>
          <AddressSelector 
            v-model="localForm.present_address_data"
            label="Present Address"
            :required="true"
          />
        </div>

        <!-- Permanent Address -->
        <div class="mb-6">
          <h5 class="text-md font-medium text-gray-700 mb-3">Permanent Address</h5>
          <div class="mb-3">
            <label class="flex items-center">
              <input 
                v-model="localForm.same_as_present"
                type="checkbox"
                class="text-green-600 focus:ring-green-500 rounded"
              />
              <span class="ml-2 text-sm text-gray-700">Same as present address</span>
            </label>
          </div>
          <div v-if="!localForm.same_as_present">
            <AddressSelector 
              v-model="localForm.permanent_address_data"
              label="Permanent Address"
              :required="true"
            />
          </div>
        </div>
      </div>

      <!-- Gender and Civil Status in one row -->
      <div>
        <label class="block text-sm font-medium text-gray-700">Gender</label>
        <select v-model="localForm.gender" class="mt-1 w-full border rounded-md p-2">
          <option value="">Select Gender</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="non_binary">Non-binary</option>
          <option value="transgender">Transgender</option>
          <option value="prefer_not_to_say">Prefer not to say</option>
          <option value="other_specify">Other (please specify)</option>
        </select>
      </div>

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

      <!-- Employment Status - Full row -->
      <div class="md:col-span-2">
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

      <!-- Terms and Conditions -->
      <div class="md:col-span-2 mt-6 pt-6 border-t border-gray-300">
        <div class="flex items-start gap-3">
          <input 
            v-model="agreedToTerms" 
            type="checkbox" 
            class="w-4 h-4 mt-1 text-green-600 border-gray-300 rounded focus:ring-green-500"
          />
          <label class="text-sm text-gray-700">
            I agree to the 
            <button 
              type="button"
              @click="showTermsModal = true" 
              class="text-blue-600 hover:underline font-medium"
            >
              Terms and Conditions
            </button>
          </label>
        </div>
        <p v-if="!agreedToTerms" class="text-red-500 text-xs mt-2">You must accept the Terms and Conditions to proceed</p>
      </div>
    </div>

    <!-- Terms and Conditions Modal -->
    <TermsAndConditions :isOpen="showTermsModal" @close="showTermsModal = false" />
  </div>
</template>