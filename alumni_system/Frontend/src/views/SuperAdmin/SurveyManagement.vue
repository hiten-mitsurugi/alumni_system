<!-- Survey Management for SuperAdmin -->
<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { Plus, Edit2, Trash2, X, Settings } from 'lucide-vue-next';
import api from '@/services/api';

const categories = ref([]);
const questions = ref([]);
const loading = ref(false);
const message = ref('');
const messageType = ref('');

// Modal states
const showCategoryModal = ref(false);
const showQuestionModal = ref(false);
const editingCategory = ref(null);
const editingQuestion = ref(null);

// Form data
const categoryForm = reactive({
  name: '',
  order: 0
});

const questionForm = reactive({
  category: '',
  question_text: '',
  question_type: 'text',
  options: [],
  is_required: true,
  order: 0
});

const questionTypes = [
  { value: 'text', label: 'Text Input' },
  { value: 'textarea', label: 'Text Area' },
  { value: 'select', label: 'Single Select' },
  { value: 'radio', label: 'Radio Button' },
  { value: 'checkbox', label: 'Multiple Select' },
  { value: 'number', label: 'Number' },
  { value: 'email', label: 'Email' },
  { value: 'date', label: 'Date' },
  { value: 'rating', label: 'Rating Scale' },
  { value: 'yes_no', label: 'Yes/No' }
];

const needsOptions = computed(() => {
  return ['select', 'radio', 'checkbox', 'rating'].includes(questionForm.question_type);
});

const newOption = ref('');

onMounted(() => {
  fetchCategories();
  fetchQuestions();
});

const fetchCategories = async () => {
  try {
    const response = await api.get('/survey/categories/');
    categories.value = response.data;
  } catch {
    showMessage('Failed to fetch categories', 'error');
  }
};

const fetchQuestions = async () => {
  try {
    const response = await api.get('/survey/questions/');
    questions.value = response.data;
  } catch {
    showMessage('Failed to fetch questions', 'error');
  }
};

const showMessage = (msg, type) => {
  message.value = msg;
  messageType.value = type;
  setTimeout(() => {
    message.value = '';
  }, 5000);
};

// Category functions
const openCategoryModal = (category = null) => {
  editingCategory.value = category;
  if (category) {
    categoryForm.name = category.name;
    categoryForm.order = category.order;
  } else {
    categoryForm.name = '';
    categoryForm.order = categories.value.length;
  }
  showCategoryModal.value = true;
};

const saveCategoryForm = async () => {
  loading.value = true;
  try {
    if (editingCategory.value) {
      await api.put(`/survey/categories/${editingCategory.value.id}/`, categoryForm);
      showMessage('Category updated successfully', 'success');
    } else {
      await api.post('/survey/categories/', categoryForm);
      showMessage('Category created successfully', 'success');
    }
    showCategoryModal.value = false;
    fetchCategories();
  } catch {
    showMessage('Failed to save category', 'error');
  } finally {
    loading.value = false;
  }
};

const deleteCategory = async (categoryId) => {
  if (confirm('Are you sure you want to delete this category? This will also delete all questions in this category.')) {
    try {
      await api.delete(`/survey/categories/${categoryId}/`);
      showMessage('Category deleted successfully', 'success');
      fetchCategories();
      fetchQuestions();
    } catch {
      showMessage('Failed to delete category', 'error');
    }
  }
};

// Question functions
const openQuestionModal = (question = null) => {
  editingQuestion.value = question;
  if (question) {
    questionForm.category = question.category;
    questionForm.question_text = question.question_text;
    questionForm.question_type = question.question_type;
    questionForm.options = [...question.options];
    questionForm.is_required = question.is_required;
    questionForm.order = question.order;
  } else {
    questionForm.category = categories.value[0]?.id || '';
    questionForm.question_text = '';
    questionForm.question_type = 'text';
    questionForm.options = [];
    questionForm.is_required = true;
    questionForm.order = 0;
  }
  showQuestionModal.value = true;
};

const addOption = () => {
  if (newOption.value.trim()) {
    questionForm.options.push(newOption.value.trim());
    newOption.value = '';
  }
};

const removeOption = (index) => {
  questionForm.options.splice(index, 1);
};

const saveQuestionForm = async () => {
  loading.value = true;
  try {
    const formData = { ...questionForm };
    if (!needsOptions.value) {
      formData.options = [];
    }

    if (editingQuestion.value) {
      await api.put(`/survey/questions/${editingQuestion.value.id}/`, formData);
      showMessage('Question updated successfully', 'success');
    } else {
      await api.post('/survey/questions/', formData);
      showMessage('Question created successfully', 'success');
    }
    showQuestionModal.value = false;
    fetchQuestions();
  } catch {
    showMessage('Failed to save question', 'error');
  } finally {
    loading.value = false;
  }
};

const deleteQuestion = async (questionId) => {
  if (confirm('Are you sure you want to delete this question?')) {
    try {
      await api.delete(`/survey/questions/${questionId}/`);
      showMessage('Question deleted successfully', 'success');
      fetchQuestions();
    } catch {
      showMessage('Failed to delete question', 'error');
    }
  }
};

const getQuestionsByCategory = (categoryId) => {
  return questions.value.filter(q => q.category === categoryId).sort((a, b) => a.order - b.order);
};
</script>

<template>
  <div class="max-w-7xl mx-auto p-6">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Settings class="w-8 h-8 text-green-600" />
            Survey Management
          </h1>
          <p class="text-gray-600 mt-2">Manage survey categories and questions for alumni registration</p>
        </div>
        <div class="flex gap-3">
          <button
            @click="openCategoryModal()"
            class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
          >
            <Plus class="w-4 h-4" />
            Add Category
          </button>
          <button
            @click="openQuestionModal()"
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
          >
            <Plus class="w-4 h-4" />
            Add Question
          </button>
        </div>
      </div>
    </div>

    <!-- Success/Error Message -->
    <div v-if="message" class="mb-6 p-4 rounded-lg"
         :class="messageType === 'success' ? 'bg-green-100 text-green-700 border border-green-300' : 'bg-red-100 text-red-700 border border-red-300'">
      {{ message }}
    </div>

    <!-- Categories and Questions -->
    <div class="space-y-6">
      <div v-for="category in categories" :key="category.id" class="bg-white rounded-lg shadow-lg overflow-hidden">
        <!-- Category Header -->
        <div class="bg-green-50 p-4 border-b border-green-200">
          <div class="flex justify-between items-center">
            <div>
              <h3 class="text-lg font-semibold text-green-800">{{ category.name }}</h3>
              <p class="text-sm text-green-600">Order: {{ category.order }} | {{ category.questions_count }} questions</p>
            </div>
            <div class="flex gap-2">
              <button
                @click="openCategoryModal(category)"
                class="p-2 text-green-600 hover:bg-green-100 rounded"
              >
                <Edit2 class="w-4 h-4" />
              </button>
              <button
                @click="deleteCategory(category.id)"
                class="p-2 text-red-600 hover:bg-red-100 rounded"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        <!-- Questions in Category -->
        <div class="p-4">
          <div class="space-y-3">
            <div
              v-for="question in getQuestionsByCategory(category.id)"
              :key="question.id"
              class="border border-gray-200 rounded-lg p-4"
            >
              <div class="flex justify-between items-start">
                <div class="flex-1">
                  <h4 class="font-medium text-gray-900">{{ question.question_text }}</h4>
                  <div class="flex gap-4 mt-2 text-sm text-gray-600">
                    <span class="bg-blue-100 text-blue-800 px-2 py-1 rounded">{{ question.question_type }}</span>
                    <span :class="question.is_required ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'" class="px-2 py-1 rounded">
                      {{ question.is_required ? 'Required' : 'Optional' }}
                    </span>
                    <span class="bg-gray-100 text-gray-800 px-2 py-1 rounded">Order: {{ question.order }}</span>
                  </div>
                  <div v-if="question.options.length > 0" class="mt-2">
                    <p class="text-sm text-gray-600">Options:</p>
                    <div class="flex flex-wrap gap-1 mt-1">
                      <span
                        v-for="option in question.options"
                        :key="option"
                        class="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs"
                      >
                        {{ option }}
                      </span>
                    </div>
                  </div>
                </div>
                <div class="flex gap-2 ml-4">
                  <button
                    @click="openQuestionModal(question)"
                    class="p-2 text-blue-600 hover:bg-blue-100 rounded"
                  >
                    <Edit2 class="w-4 h-4" />
                  </button>
                  <button
                    @click="deleteQuestion(question.id)"
                    class="p-2 text-red-600 hover:bg-red-100 rounded"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            <div v-if="getQuestionsByCategory(category.id).length === 0" class="text-center py-8 text-gray-500">
              No questions in this category
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Category Modal -->
    <div v-if="showCategoryModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold mb-4">
          {{ editingCategory ? 'Edit Category' : 'Add Category' }}
        </h3>

        <form @submit.prevent="saveCategoryForm" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Category Name</label>
            <input
              v-model="categoryForm.name"
              type="text"
              class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Order</label>
            <input
              v-model.number="categoryForm.order"
              type="number"
              class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
              required
            />
          </div>

          <div class="flex justify-end gap-3 pt-4">
            <button
              type="button"
              @click="showCategoryModal = false"
              class="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {{ loading ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Question Modal -->
    <div v-if="showQuestionModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h3 class="text-lg font-semibold mb-4">
          {{ editingQuestion ? 'Edit Question' : 'Add Question' }}
        </h3>

        <form @submit.prevent="saveQuestionForm" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select
              v-model="questionForm.category"
              class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
              required
            >
              <option v-for="category in categories" :key="category.id" :value="category.id">
                {{ category.name }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Question Text</label>
            <textarea
              v-model="questionForm.question_text"
              class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
              rows="3"
              required
            ></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Question Type</label>
              <select
                v-model="questionForm.question_type"
                class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                required
              >
                <option v-for="type in questionTypes" :key="type.value" :value="type.value">
                  {{ type.label }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Order</label>
              <input
                v-model.number="questionForm.order"
                type="number"
                class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                required
              />
            </div>
          </div>

          <div class="flex items-center">
            <input
              v-model="questionForm.is_required"
              type="checkbox"
              id="required"
              class="mr-2"
            />
            <label for="required" class="text-sm font-medium text-gray-700">Required</label>
          </div>

          <!-- Options for select, radio, checkbox, rating -->
          <div v-if="needsOptions" class="space-y-3">
            <label class="block text-sm font-medium text-gray-700">Options</label>

            <div class="flex gap-2">
              <input
                v-model="newOption"
                type="text"
                placeholder="Add new option"
                class="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                @keyup.enter="addOption"
              />
              <button
                type="button"
                @click="addOption"
                class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Add
              </button>
            </div>

            <div class="space-y-2">
              <div
                v-for="(option, index) in questionForm.options"
                :key="index"
                class="flex items-center gap-2 p-2 bg-gray-50 rounded"
              >
                <span class="flex-1">{{ option }}</span>
                <button
                  type="button"
                  @click="removeOption(index)"
                  class="p-1 text-red-600 hover:bg-red-100 rounded"
                >
                  <X class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-4">
            <button
              type="button"
              @click="showQuestionModal = false"
              class="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {{ loading ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
