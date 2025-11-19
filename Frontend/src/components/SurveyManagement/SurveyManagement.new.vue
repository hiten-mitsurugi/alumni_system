<template>
  <div class="min-h-screen bg-gradient-to-br from-orange-50 via-white to-orange-50 p-6">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-4xl font-bold bg-gradient-to-r from-orange-600 to-orange-400 bg-clip-text text-transparent mb-2">
          Survey Management
        </h1>
        <p class="text-gray-600">Create and manage Google Forms-like surveys</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
      </div>

      <!-- Main Content -->
      <div v-else>
        <!-- Form List View (default) -->
        <FormList
          v-if="!selectedForm"
          :forms="forms"
          @create="handleCreateForm"
          @edit="handleEditForm"
          @delete="handleDeleteForm"
          @refresh="loadForms"
        />

        <!-- Form Editor View -->
        <FormEditor
          v-else
          :form="selectedForm"
          @back="selectedForm = null"
          @save="handleSaveForm"
          @refresh="loadForms"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useForms } from '@/components/SurveyManagement/composables/useForms'
import FormList from '@/components/SurveyManagement/FormList.vue'
import FormEditor from '@/components/SurveyManagement/FormEditor.vue'

const { forms, loading, loadForms, createForm, updateForm, deleteForm } = useForms()
const selectedForm = ref(null)

onMounted(() => {
  loadForms()
})

const handleCreateForm = async (formData) => {
  const newForm = await createForm(formData)
  if (newForm) {
    await loadForms()
    selectedForm.value = newForm
  }
}

const handleEditForm = (form) => {
  selectedForm.value = form
}

const handleDeleteForm = async (formId) => {
  if (confirm('Are you sure you want to delete this form? This action cannot be undone.')) {
    await deleteForm(formId)
    await loadForms()
  }
}

const handleSaveForm = async (formData) => {
  await updateForm(selectedForm.value.id, formData)
  await loadForms()
  selectedForm.value = null
}
</script>
