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

// Define default structure
const defaultCurriculumRelevance = {
  general_education: null,
  core_major: null,
  special_professional: null,
  electives: null,
  internship_ojt: null,
  co_curricular_activities: null,
  extra_curricular_activities: null,
}

// Initialize localForm safely
const localForm = reactive({
  curriculum_relevance: {
    ...defaultCurriculumRelevance,
    ...(props.form?.curriculum_relevance || {}),
  },
})

// Watch for deep changes and emit back to parent
watch(
  () => localForm.curriculum_relevance,
  () => {
    emit('update:form', {
      curriculum_relevance: { ...localForm.curriculum_relevance },
    })
  },
  { deep: true }
)

// Curriculum items
const curricula = [
  { key: 'general_education', label: 'General Education / Minor Courses' },
  { key: 'core_major', label: 'Core / Major Courses' },
  { key: 'special_professional', label: 'Special Professional Courses' },
  { key: 'electives', label: 'Electives' },
  { key: 'internship_ojt', label: 'Internship / OJT' },
  { key: 'co_curricular_activities', label: 'Co-Curricular Activities' },
  { key: 'extra_curricular_activities', label: 'Extra-Curricular Activities' },
]
</script>

<template>
  <div>
    <p class="text-sm text-gray-600 mb-4">
      Rate the usefulness of each in your professional work (1 = Not Useful, 5 = Very Useful)
    </p>
    <div class="space-y-4">
      <div
        v-for="item in curricula"
        :key="item.key"
        class="flex items-center gap-4"
      >
        <label class="w-1/3 text-sm text-gray-600">{{ item.label }}</label>
        <div class="flex gap-2">
          <label v-for="i in 5" :key="i" class="flex items-center">
            <input
              type="radio"
              v-model="localForm.curriculum_relevance[item.key]"
              :value="i"
              class="mr-1"
            />
            {{ i }}
          </label>
        </div>
      </div>
    </div>
  </div>
</template>
