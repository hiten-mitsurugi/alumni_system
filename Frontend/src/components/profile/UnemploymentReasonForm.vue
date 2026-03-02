<template>
  <div class="space-y-4">
    <!-- Reason why unemployed -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Reason why unemployed *
      </label>
      <select
        :value="modelValue.reason_unemployed"
        @input="$emit('update:modelValue', { ...modelValue, reason_unemployed: $event.target.value })"
        required
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
      >
        <option value="">Select reason</option>
        <option value="actively_seeking">Actively seeking employment</option>
        <option value="full_time_parent">Full-time parent</option>
        <option value="retired">Retired</option>
        <option value="student_training">Student or training</option>
        <option value="caregiving">Caregiving (family/elderly)</option>
        <option value="career_break">Career break</option>
        <option value="other">Other (please specify)</option>
      </select>
    </div>

    <!-- Please specify (shown when "Other" is selected) -->
    <div v-if="modelValue.reason_unemployed === 'other'">
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Please specify *
      </label>
      <input
        :value="modelValue.reason_unemployed_other"
        @input="$emit('update:modelValue', { ...modelValue, reason_unemployed_other: $event.target.value })"
        type="text"
        required
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
        placeholder="Please specify your reason"
      />
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

defineEmits(['update:modelValue'])
</script>
