<script setup>
import { defineProps, defineEmits, reactive, watch } from 'vue'

const props = defineProps({
  form: {
    type: Object,
    required: false,
    default: () => ({}),
  },
})

const emit = defineEmits(['update:form'])

const defaultSkillsRelevance = {
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
}

// Merge default into props.form if not present
const localForm = reactive({
  skills_relevance: {
    ...defaultSkillsRelevance,
    ...(props.form?.skills_relevance || {}),
  },
})

// Sync changes back to parent
watch(
  () => localForm.skills_relevance,
  () => {
    emit('update:form', { skills_relevance: { ...localForm.skills_relevance } })
  },
  { deep: true }
)

const skills = [
  { key: 'critical_thinking', label: 'Critical Thinking' },
  { key: 'communication', label: 'Communication' },
  { key: 'innovation', label: 'Innovation' },
  { key: 'collaboration', label: 'Collaboration' },
  { key: 'leadership', label: 'Leadership' },
  { key: 'productivity_accountability', label: 'Productivity and Accountability' },
  { key: 'entrepreneurship', label: 'Entrepreneurship' },
  { key: 'global_citizenship', label: 'Global Citizenship' },
  { key: 'adaptability', label: 'Adaptability' },
  { key: 'accessing_analyzing_synthesizing_info', label: 'Accessing, Analyzing, and Synthesizing Information' },
]
</script>

<template>
  <div>
    <p class="text-sm text-gray-600 mb-4">Rate the relevance of each skill in your work (1 = Not Useful, 5 = Very Useful)</p>
    <div class="space-y-4">
      <div v-for="skill in skills" :key="skill.key" class="flex items-center gap-4">
        <label class="w-1/3 text-sm text-gray-600">{{ skill.label }}</label>
        <div class="flex gap-2">
          <label v-for="i in 5" :key="i" class="flex items-center">
            <input
              type="radio"
              v-model="localForm.skills_relevance[skill.key]"
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
