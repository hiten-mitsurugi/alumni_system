<template>
  <div v-if="isOpen" class="section-view-overlay" @click="handleOverlayClick">
    <div class="section-view" :class="{ 'section-view--open': isOpen }">
      <!-- Header -->
      <div class="section-view__header">
        <div class="section-view__header-content">
          <h2 class="section-view__title">{{ section?.category?.name || 'Section Details' }}</h2>
          <span v-if="section?.category?.order" class="section-view__order">
            Order: {{ section.category.order }}
          </span>
        </div>
        <button class="section-view__close-btn" @click="handleClose" title="Close">
          <svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor">
            <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>

      <!-- Section Metadata -->
      <div v-if="section" class="section-view__metadata">
        <div v-if="section.category.page_title" class="section-view__meta-item">
          <strong>Page Title:</strong> {{ section.category.page_title }}
        </div>
        <div v-if="section.category.page_description" class="section-view__meta-item">
          <strong>Description:</strong> {{ section.category.page_description }}
        </div>
        <div class="section-view__meta-badges">
          <span v-if="section.category.page_break" class="section-view__badge section-view__badge--page-break">
            Page Break
          </span>
          <span v-if="hasConditions" class="section-view__badge section-view__badge--conditional">
            Conditional
          </span>
        </div>
      </div>

      <!-- Questions Table Header -->
      <div class="section-view__table-header">
        <h3 class="section-view__table-title">
          Questions ({{ questions.length }})
        </h3>
        <button class="section-view__add-question-btn" @click="handleAddQuestion">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 2v12M2 8h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          Add Question
        </button>
      </div>

      <!-- Questions Table -->
      <div class="section-view__table-container">
        <table v-if="questions.length > 0" class="section-view__table">
          <thead>
            <tr>
              <th class="section-view__table-th section-view__table-th--drag"></th>
              <th class="section-view__table-th section-view__table-th--order">Order</th>
              <th class="section-view__table-th">Question</th>
              <th class="section-view__table-th">Type</th>
              <th class="section-view__table-th section-view__table-th--center">Required</th>
              <th class="section-view__table-th section-view__table-th--center">Conditional</th>
              <th class="section-view__table-th section-view__table-th--center">Branching</th>
              <th class="section-view__table-th section-view__table-th--actions">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="question in sortedQuestions"
              :key="question.id"
              class="section-view__table-row"
              @click="handleQuestionClick(question)"
            >
              <td class="section-view__table-td section-view__table-td--drag">
                <div class="section-view__drag-handle" title="Drag to reorder">
                  <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" stroke-width="2"/>
                  </svg>
                </div>
              </td>
              <td class="section-view__table-td section-view__table-td--order">
                {{ question.order }}
              </td>
              <td class="section-view__table-td section-view__table-td--question">
                <div class="section-view__question-text">
                  {{ truncateText(question.question_text, 60) }}
                </div>
              </td>
              <td class="section-view__table-td">
                <span class="section-view__type-badge">
                  {{ formatQuestionType(question.question_type) }}
                </span>
              </td>
              <td class="section-view__table-td section-view__table-td--center">
                <span v-if="question.required" class="section-view__check-icon" title="Required">
                  <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M13 4L6 11 3 8" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>
                  </svg>
                </span>
              </td>
              <td class="section-view__table-td section-view__table-td--center">
                <span v-if="question.depends_on_question" class="section-view__indicator section-view__indicator--conditional" title="Has conditional visibility">
                  <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M8 2l6 12H2L8 2z" stroke="currentColor" stroke-width="1.5" fill="none"/>
                  </svg>
                </span>
              </td>
              <td class="section-view__table-td section-view__table-td--center">
                <span v-if="hasBranching(question)" class="section-view__indicator section-view__indicator--branching" title="Has branching logic">
                  <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M8 2v12M8 8h6M8 8H2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                  </svg>
                </span>
              </td>
              <td class="section-view__table-td section-view__table-td--actions" @click.stop>
                <div class="section-view__actions">
                  <button
                    class="section-view__action-btn"
                    title="Edit question"
                    @click="handleEditQuestion(question)"
                  >
                    <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
                      <path d="M11.5 1.5l3 3-9 9H2.5v-3l9-9z"/>
                    </svg>
                  </button>
                  <button
                    class="section-view__action-btn section-view__action-btn--danger"
                    title="Delete question"
                    @click="handleDeleteQuestion(question.id)"
                  >
                    <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
                      <path d="M5.5 2V1h5v1h3.5v1h-1v11h-10V3h-1V2h3.5z"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Empty State -->
        <div v-else class="section-view__empty">
          <svg width="48" height="48" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="32" cy="32" r="24"/>
            <path d="M32 24v8M32 40h.01"/>
          </svg>
          <p class="section-view__empty-text">No questions in this section yet</p>
          <button class="section-view__empty-btn" @click="handleAddQuestion">
            Add your first question
          </button>
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="section-view__footer">
        <button class="section-view__footer-btn section-view__footer-btn--secondary" @click="handleEditSection">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
            <path d="M11.5 1.5l3 3-9 9H2.5v-3l9-9z"/>
          </svg>
          Edit Section Details
        </button>
        <button class="section-view__footer-btn section-view__footer-btn--danger" @click="handleDeleteSection">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
            <path d="M5.5 2V1h5v1h3.5v1h-1v11h-10V3h-1V2h3.5z"/>
          </svg>
          Delete Section
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  section: {
    type: Object,
    default: null,
    // Shape: { category: {...}, questions: [...] }
  },
});

const emit = defineEmits([
  'close',
  'add-question',
  'edit-question',
  'delete-question',
  'edit-section',
  'delete-section',
  'question-click',
]);

const questions = computed(() => props.section?.questions || []);

const sortedQuestions = computed(() => {
  return [...questions.value].sort((a, b) => (a.order || 0) - (b.order || 0));
});

const hasConditions = computed(() => {
  if (!props.section) return false;
  const cat = props.section.category;
  return !!(cat.depends_on_category || cat.depends_on_question_text || cat.depends_on_value);
});

function hasBranching(question) {
  return question.branching && Object.keys(question.branching).length > 0;
}

function truncateText(text, maxLength) {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

function formatQuestionType(type) {
  const typeMap = {
    text: 'Text',
    textarea: 'Textarea',
    radio: 'Radio',
    checkbox: 'Checkbox',
    select: 'Select',
    number: 'Number',
    email: 'Email',
    date: 'Date',
    rating: 'Rating',
    yes_no: 'Yes/No',
    file: 'File',
  };
  return typeMap[type] || type;
}

function handleClose() {
  emit('close');
}

function handleOverlayClick(event) {
  if (event.target.classList.contains('section-view-overlay')) {
    handleClose();
  }
}

function handleAddQuestion() {
  emit('add-question', props.section?.category?.id);
}

function handleQuestionClick(question) {
  emit('question-click', question);
}

function handleEditQuestion(question) {
  emit('edit-question', question);
}

function handleDeleteQuestion(questionId) {
  emit('delete-question', questionId);
}

function handleEditSection() {
  emit('edit-section', props.section);
}

function handleDeleteSection() {
  emit('delete-section', props.section?.category?.id);
}
</script>

<style scoped>
.section-view-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.section-view {
  width: 700px;
  max-width: 90vw;
  background: white;
  box-shadow: -4px 0 16px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  transform: translateX(100%);
  transition: transform 0.3s ease;
}

.section-view--open {
  transform: translateX(0);
}

.section-view__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.section-view__header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-view__title {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.section-view__order {
  font-size: 12px;
  color: #6b7280;
  background: white;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
}

.section-view__close-btn {
  padding: 6px;
  background: transparent;
  border: none;
  cursor: pointer;
  color: #6b7280;
  border-radius: 4px;
  transition: all 0.15s ease;
}

.section-view__close-btn:hover {
  background: #e5e7eb;
  color: #111827;
}

.section-view__metadata {
  padding: 16px 24px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.section-view__meta-item {
  font-size: 14px;
  color: #374151;
  margin-bottom: 8px;
}

.section-view__meta-item strong {
  color: #111827;
  margin-right: 4px;
}

.section-view__meta-badges {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.section-view__badge {
  font-size: 11px;
  font-weight: 500;
  padding: 3px 8px;
  border-radius: 4px;
  text-transform: uppercase;
}

.section-view__badge--page-break {
  background: #dbeafe;
  color: #1e40af;
}

.section-view__badge--conditional {
  background: #fef3c7;
  color: #92400e;
}

.section-view__table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.section-view__table-title {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.section-view__add-question-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s ease;
}

.section-view__add-question-btn:hover {
  background: #2563eb;
}

.section-view__table-container {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.section-view__table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.section-view__table-th {
  text-align: left;
  padding: 12px 16px;
  background: #f9fafb;
  border-bottom: 2px solid #e5e7eb;
  font-weight: 600;
  color: #374151;
  font-size: 13px;
  position: sticky;
  top: 0;
  z-index: 10;
}

.section-view__table-th--drag {
  width: 40px;
  padding-left: 24px;
}

.section-view__table-th--order {
  width: 60px;
}

.section-view__table-th--center {
  text-align: center;
  width: 80px;
}

.section-view__table-th--actions {
  width: 100px;
  text-align: center;
}

.section-view__table-row {
  cursor: pointer;
  transition: background 0.15s ease;
}

.section-view__table-row:hover {
  background: #f9fafb;
}

.section-view__table-td {
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  color: #374151;
}

.section-view__table-td--drag {
  padding-left: 24px;
}

.section-view__table-td--order {
  font-weight: 500;
  color: #6b7280;
}

.section-view__table-td--question {
  max-width: 250px;
}

.section-view__table-td--center {
  text-align: center;
}

.section-view__table-td--actions {
  text-align: center;
}

.section-view__drag-handle {
  color: #9ca3af;
  cursor: grab;
  display: inline-flex;
}

.section-view__drag-handle:hover {
  color: #6b7280;
}

.section-view__question-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.section-view__type-badge {
  display: inline-block;
  padding: 3px 8px;
  background: #e5e7eb;
  color: #374151;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.section-view__check-icon {
  color: #10b981;
  display: inline-flex;
}

.section-view__indicator {
  display: inline-flex;
}

.section-view__indicator--conditional {
  color: #f59e0b;
}

.section-view__indicator--branching {
  color: #8b5cf6;
}

.section-view__actions {
  display: flex;
  gap: 6px;
  justify-content: center;
}

.section-view__action-btn {
  padding: 4px;
  background: transparent;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  cursor: pointer;
  color: #6b7280;
  display: inline-flex;
  transition: all 0.15s ease;
}

.section-view__action-btn:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
  color: #111827;
}

.section-view__action-btn--danger:hover {
  background: #fee2e2;
  border-color: #fecaca;
  color: #dc2626;
}

.section-view__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 24px;
  color: #6b7280;
  text-align: center;
}

.section-view__empty svg {
  margin-bottom: 12px;
  opacity: 0.5;
}

.section-view__empty-text {
  font-size: 14px;
  margin: 0 0 16px 0;
}

.section-view__empty-btn {
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}

.section-view__empty-btn:hover {
  background: #2563eb;
}

.section-view__footer {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.section-view__footer-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.section-view__footer-btn--secondary {
  background: white;
  color: #374151;
}

.section-view__footer-btn--secondary:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.section-view__footer-btn--danger {
  background: white;
  color: #dc2626;
  border-color: #fecaca;
}

.section-view__footer-btn--danger:hover {
  background: #fee2e2;
  border-color: #fca5a5;
}
</style>
