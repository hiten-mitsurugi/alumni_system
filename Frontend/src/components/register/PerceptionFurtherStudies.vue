<script setup>
import { defineProps, defineEmits, reactive, watch } from 'vue'

const emit = defineEmits(['update:form'])

const props = defineProps({
  form: {
    type: Object,
    required: false,
    default: () => ({}),
  },
})

// Default structure for safety
const defaultPerception = {
  pursued_further_studies: null,
  competitiveness: null,
  mode_of_study: '',
  level_of_study: '',
  field_of_study: '',
  specialization: '',
  related_to_undergrad: null,
  reasons_for_further_study: '',
}

// Initialize localForm with fallback for `perception_further_studies`
const localForm = reactive({
  perception_further_studies: {
    ...defaultPerception,
    ...(props.form?.perception_further_studies || {}),
  },
})

// Emit changes to parent
watch(
  () => localForm.perception_further_studies,
  (newVal) => {
    emit('update:form', {
      perception_further_studies: { ...newVal },
    })
  },
  { deep: true }
)
</script>

<template>
  <div>
    <div>
      <label class="block text-sm text-gray-600 mb-1">Have you pursued further studies?</label>
      <label><input type="radio" v-model="localForm.perception_further_studies.pursued_further_studies" :value="true" /> Yes</label>
      <label><input type="radio" v-model="localForm.perception_further_studies.pursued_further_studies" :value="false" /> No</label>
    </div>

    <div class="mt-4">
      <label class="block text-sm text-gray-600 mb-1">Competitiveness of Graduates (1-5)</label>
      <div class="flex gap-2">
        <label v-for="i in 5" :key="i" class="flex items-center">
          <input
            type="radio"
            v-model="localForm.perception_further_studies.competitiveness"
            :value="i"
            class="mr-1"
          />
          {{ i }}
        </label>
      </div>
    </div>

    <div
      v-if="localForm.perception_further_studies.pursued_further_studies"
      class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4"
    >
      <div>
        <label class="block text-sm text-gray-600 mb-1">Mode of Study</label>
        <select
          v-model="localForm.perception_further_studies.mode_of_study"
          class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="" disabled>Select Mode</option>
          <option value="full_time">Full-time</option>
          <option value="part_time">Part-time</option>
          <option value="online">Online</option>
          <option value="others">Others</option>
        </select>
      </div>

      <div>
        <label class="block text-sm text-gray-600 mb-1">Level of Study</label>
        <select
          v-model="localForm.perception_further_studies.level_of_study"
          class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="" disabled>Select Level</option>
          <option value="masters">Master's</option>
          <option value="doctoral">Doctoral</option>
          <option value="certificate">Certificate</option>
        </select>
      </div>

      <div>
        <label class="block text-sm text-gray-600 mb-1">Field of Study</label>
        <input
          v-model="localForm.perception_further_studies.field_of_study"
          placeholder="Field of Study"
          class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label class="block text-sm text-gray-600 mb-1">Specialization</label>
        <input
          v-model="localForm.perception_further_studies.specialization"
          placeholder="Specialization"
          class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label class="block text-sm text-gray-600 mb-1">Related to Undergrad?</label>
        <div class="flex gap-4">
          <label><input type="radio" v-model="localForm.perception_further_studies.related_to_undergrad" :value="true" /> Yes</label>
          <label><input type="radio" v-model="localForm.perception_further_studies.related_to_undergrad" :value="false" /> No</label>
        </div>
      </div>

      <div>
        <label class="block text-sm text-gray-600 mb-1">Reasons for Further Study</label>
        <input
          v-model="localForm.perception_further_studies.reasons_for_further_study"
          placeholder="e.g., Career growth"
          class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
    </div>
  </div>
</template>
