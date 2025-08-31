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

// Default structure
const defaultFeedback = {
  recommendations: '',
}

// Initialize localForm safely
const localForm = reactive({
  feedback_recommendations: {
    ...defaultFeedback,
    ...(props.form?.feedback_recommendations || {}),
  },
})

// Emit changes to parent on update
watch(
  () => localForm.feedback_recommendations,
  (newVal) => {
    emit('update:form', {
      feedback_recommendations: { ...newVal },
    })
  },
  { deep: true }
)
</script>

<template>
  <div>
    <label class="block text-sm text-gray-600 mb-1">Recommendations to Improve Your Program</label>
    <textarea
      v-model="localForm.feedback_recommendations.recommendations"
      placeholder="Your recommendations..."
      class="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 h-32"
    ></textarea>
  </div>
</template>
