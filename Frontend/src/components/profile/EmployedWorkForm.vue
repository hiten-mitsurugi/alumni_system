<template>
  <div class="space-y-4">
    <!-- 1. Job Title (Occupation) -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Job Title *
      </label>
      <input
        :value="modelValue.occupation"
        @input="updateField('occupation', $event.target.value)"
        type="text"
        required
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
        placeholder="Enter your job title"
      />
    </div>

    <!-- Job Description (Optional) -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Job Description (Optional)
      </label>
      <textarea
        :value="modelValue.description"
        @input="updateField('description', $event.target.value)"
        rows="3"
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
        placeholder="Describe your responsibilities and key achievements"
      ></textarea>
    </div>

    <!-- 2. Company or Agency Name -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Company or Agency Name *
      </label>
      <input
        :value="modelValue.employing_agency"
        @input="updateField('employing_agency', $event.target.value)"
        type="text"
        required
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
        placeholder="Enter company or agency name"
      />
    </div>

    <!-- 3. Company or Agency Address -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Company or Agency Address
      </label>
      <input
        :value="modelValue.company_address"
        @input="updateField('company_address', $event.target.value)"
        type="text"
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
        placeholder="Enter company address"
      />
    </div>

    <!-- 4. Employment Status -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Employment Status *
      </label>
      <select
        :value="modelValue.employment_status"
        @input="updateField('employment_status', $event.target.value)"
        required
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
      >
        <option value="">Select employment status</option>
        <option value="employed_locally">Employed Locally</option>
        <option value="employed_internationally">Employed Internationally</option>
        <option value="self_employed">Self Employed</option>
      </select>
    </div>

    <!-- 5. Classification of Employment / Sector -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Classification of Employment / Sector *
      </label>
      <select
        :value="modelValue.classification"
        @input="updateField('classification', $event.target.value)"
        required
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
      >
        <option value="">Select classification</option>
        <option value="government">Government</option>
        <option value="private">Private</option>
        <option value="ngo">NGO</option>
        <option value="freelance">Freelancer</option>
        <option value="business_owner">Business Owner</option>
        <option value="other">Other (please specify)</option>
      </select>
    </div>

    <!-- Classification Other Specify -->
    <div v-if="modelValue.classification === 'other'">
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Please specify *
      </label>
      <input
        :value="modelValue.classification_other"
        @input="updateField('classification_other', $event.target.value)"
        type="text"
        required
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
        placeholder="Please specify classification"
      />
    </div>

    <!-- Date Range -->
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Start Date
        </label>
        <input
          :value="modelValue.start_date"
          @input="updateField('start_date', $event.target.value)"
          type="date"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          End Date
        </label>
        <input
          :value="modelValue.end_date"
          @input="updateField('end_date', $event.target.value)"
          type="date"
          :disabled="modelValue.is_current_job"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
      </div>
    </div>

    <!-- Currently Working Checkbox -->
    <div class="flex items-center">
      <input
        :checked="modelValue.is_current_job"
        @change="updateField('is_current_job', $event.target.checked)"
        type="checkbox"
        id="currently-working"
        class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
      />
      <label for="currently-working" class="ml-2 block text-sm text-gray-700">
        I am currently working here
      </label>
    </div>

    <!-- 6. How did you get your current job? -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        How did you get your current job? *
      </label>
      <select
        :value="modelValue.how_got_job"
        @input="updateField('how_got_job', $event.target.value)"
        required
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
      >
        <option value="">Select option</option>
        <option value="social_media">Social Media</option>
        <option value="online_job_portals">Online Job Portals</option>
        <option value="government_agency">Government Agency</option>
        <option value="recruitment_agency">Recruitment Agency</option>
        <option value="company_website">Company Website</option>
        <option value="direct_walk_in">Direct walk-in application</option>
        <option value="campus_recruitment">Campus Recruitment</option>
        <option value="internship">Internship</option>
        <option value="referral">Referral</option>
        <option value="internal_transfer">Internal Transfer or Promotion</option>
        <option value="others">Others (please specify)</option>
      </select>
    </div>

    <!-- How got job - Other Specify -->
    <div v-if="modelValue.how_got_job === 'others'">
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Please specify *
      </label>
      <input
        :value="modelValue.how_got_job_other"
        @input="updateField('how_got_job_other', $event.target.value)"
        type="text"
        required
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
        placeholder="Please specify how you got the job"
      />
    </div>

    <!-- 7. Monthly Income -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Monthly Income *
      </label>
      <select
        :value="modelValue.monthly_income"
        @input="updateField('monthly_income', $event.target.value)"
        required
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
      >
        <option value="">Select income range</option>
        <option value="less_than_15k">Less than ₱15,000</option>
        <option value="15k_to_29k">₱15,000 – ₱29,999</option>
        <option value="30k_to_49k">₱30,000 – ₱49,999</option>
        <option value="50k_and_above">₱50,000 and above</option>
        <option value="prefer_not_say">Prefer not to say</option>
      </select>
    </div>

    <!-- 8. Are you the breadwinner? -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Are you the breadwinner? *
      </label>
      <div class="flex items-center space-x-4">
        <label class="flex items-center">
          <input
            :checked="modelValue.is_breadwinner === true"
            @change="updateField('is_breadwinner', true)"
            type="radio"
            name="is_breadwinner"
            required
            class="mr-2 text-green-600 focus:ring-green-500"
          />
          <span class="text-sm text-gray-700">Yes</span>
        </label>
        <label class="flex items-center">
          <input
            :checked="modelValue.is_breadwinner === false"
            @change="updateField('is_breadwinner', false)"
            type="radio"
            name="is_breadwinner"
            required
            class="mr-2 text-green-600 focus:ring-green-500"
          />
          <span class="text-sm text-gray-700">No</span>
        </label>
      </div>
    </div>

    <!-- 9. Length of service -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Length of Service *
      </label>
      <select
        :value="modelValue.length_of_service"
        @input="updateField('length_of_service', $event.target.value)"
        required
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
      >
        <option value="">Select length of service</option>
        <option value="less_than_1_year">Less than 1 year</option>
        <option value="1_to_3_years">1-3 years</option>
        <option value="4_to_6_years">4-6 years</option>
        <option value="7_to_10_years">7-10 years</option>
        <option value="more_than_10_years">More than 10 years</option>
      </select>
    </div>

    <!-- 10. Was college education relevant to first job? -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Was college education relevant to first job? *
      </label>
      <select
        :value="modelValue.college_education_relevant"
        @input="updateField('college_education_relevant', $event.target.value)"
        required
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
      >
        <option value="">Select relevance</option>
        <option value="not_relevant">Not relevant at all</option>
        <option value="slightly_relevant">Slightly relevant</option>
        <option value="moderately_relevant">Moderately relevant</option>
        <option value="very_relevant">Very relevant</option>
        <option value="extremely_relevant">Extremely relevant</option>
      </select>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const updateField = (field, value) => {
  emit('update:modelValue', {
    ...props.modelValue,
    [field]: value
  })
}
</script>
