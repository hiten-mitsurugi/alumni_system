<template>
  <div class="space-y-6">
    <!-- Header with Create Button -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">Survey Forms</h2>
        <p class="text-gray-600 mt-1">Manage your survey forms</p>
      </div>
      <button
        @click="showCreateModal = true"
        class="bg-gradient-to-r from-orange-600 to-orange-500 text-white px-6 py-3 rounded-lg hover:from-orange-700 hover:to-orange-600 transition-all shadow-md hover:shadow-lg flex items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
        </svg>
        Create New Form
      </button>
    </div>

    <!-- Forms Grid -->
    <div v-if="forms.length === 0" class="text-center py-20">
      <div class="text-gray-400 text-6xl mb-4">📋</div>
      <h3 class="text-xl font-semibold text-gray-700 mb-2">No forms yet</h3>
      <p class="text-gray-500 mb-6">Create your first survey form to get started</p>
      <button
        @click="showCreateModal = true"
        class="bg-orange-600 text-white px-6 py-2 rounded-lg hover:bg-orange-700 transition"
      >
        Create Form
      </button>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="form in forms"
        :key="form.id"
        class="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow p-6 border border-gray-200"
      >
        <!-- Form Header -->
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900 mb-1">{{ form.name }}</h3>
            <p class="text-sm text-gray-600 line-clamp-2">{{ form.description || 'No description' }}</p>
          </div>
          <div class="flex gap-1 ml-2">
            <span
              v-if="form.is_published"
              class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800"
            >
              Published
            </span>
            <span
              v-else
              class="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800"
            >
              Draft
            </span>
          </div>
        </div>

        <!-- Form Stats -->
        <div class="flex items-center gap-4 text-sm text-gray-600 mb-4">
          <div class="flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
            </svg>
            <span>{{ form.categories?.length || 0 }} sections</span>
          </div>
          <div class="flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <span>Questions</span>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-2">
          <button
            @click="$emit('edit', form)"
            class="flex-1 bg-orange-50 text-orange-700 px-4 py-2 rounded-lg hover:bg-orange-100 transition font-medium"
          >
            Edit
          </button>
          <button
            @click="$emit('delete', form.id)"
            class="px-4 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Create Form Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showCreateModal = false"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold text-gray-900 mb-4">Create New Form</h3>
        <form @submit.prevent="handleCreate">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Form Title *</label>
            <input
              v-model="newForm.name"
              type="text"
              required
              class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="e.g., Customer Satisfaction Survey"
            />
          </div>
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <textarea
              v-model="newForm.description"
              rows="3"
              class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="Brief description of this survey"
            ></textarea>
          </div>
          <div class="flex gap-3">
            <button
              type="button"
              @click="showCreateModal = false"
              class="flex-1 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="flex-1 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition"
            >
              Create
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  forms: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['create', 'edit', 'delete', 'refresh'])

const showCreateModal = ref(false)
const newForm = ref({
  name: '',
  description: ''
})

const handleCreate = () => {
  emit('create', { ...newForm.value })
  showCreateModal.value = false
  newForm.value = { name: '', description: '' }
}
</script>
