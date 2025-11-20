<template>
  <div v-if="isOpen" class="section-view-overlay" @click="handleOverlayClick">
    <div class="section-view" :class="{ 'section-view--open': isOpen }" @click.stop>
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
          Add Question
        </button>
      </div>

      <!-- Questions Table -->
      <div class="section-view__table-container">
        <div v-if="questions.length > 0" class="section-view__table-wrapper">
          <table class="section-view__table">
            <thead class="section-view__table-head">
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
            <tbody class="section-view__table-body">
              <tr
                v-for="question in sortedQuestions"
                :key="question.id"
                class="section-view__table-row"
              >
                <td class="section-view__table-td section-view__table-td--drag">
                  <div class="section-view__drag-handle" title="Drag to reorder">
                    <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
                      <path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" stroke-width="2"/>
                    </svg>
                  </div>
                </td>
                <td class="section-view__table-td section-view__table-td--order">
                  <span class="section-view__order-badge">{{ question.order }}</span>
                </td>
                <td class="section-view__table-td section-view__table-td--question">
                  <div class="section-view__question-content">
                    <div class="section-view__question-text">
                      {{ question.question_text }}
                    </div>
                    <div v-if="question.help_text" class="section-view__question-help">
                      {{ truncateText(question.help_text, 80) }}
                    </div>
                  </div>
                </td>
                <td class="section-view__table-td">
                  <span class="section-view__type-badge">
                    {{ formatQuestionType(question.question_type) }}
                  </span>
                </td>
                <td class="section-view__table-td section-view__table-td--center">
                  <span 
                    :class="[
                      'section-view__status-badge',
                      question.is_required ? 'section-view__status-badge--required' : 'section-view__status-badge--optional'
                    ]"
                  >
                    <span class="section-view__status-dot"></span>
                    {{ question.is_required ? 'Required' : 'Optional' }}
                  </span>
                </td>
                <td class="section-view__table-td section-view__table-td--center">
                  <div v-if="question.depends_on_question" class="section-view__conditional-info">
                    <span class="section-view__indicator section-view__indicator--conditional" :title="getConditionalTooltip(question)">
                      <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z"/>
                      </svg>
                    </span>
                    <div v-if="question.depends_on_value" class="section-view__conditional-text">
                      <span class="section-view__conditional-value">{{ question.depends_on_value }}</span>
                    </div>
                  </div>
                  <span v-else class="section-view__text-muted">—</span>
                </td>
                <td class="section-view__table-td section-view__table-td--center">
                  <span v-if="hasBranching(question)" class="section-view__indicator section-view__indicator--branching" title="Has branching logic">
                    <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
                      <path d="M8 2v12M8 8h6M8 8H2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    </svg>
                  </span>
                  <span v-else class="section-view__text-muted">—</span>
                </td>
                <td class="section-view__table-td section-view__table-td--actions" @click.stop>
                  <div class="section-view__actions">
                    <button
                      class="section-view__action-btn section-view__action-btn--edit"
                      title="Edit question"
                      @click="handleEditQuestion(question)"
                    >
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M11.013 1.427a1.75 1.75 0 012.474 0l1.086 1.086a1.75 1.75 0 010 2.474l-8.61 8.61c-.21.21-.47.364-.756.445l-3.251.93a.75.75 0 01-.927-.928l.929-3.25a1.75 1.75 0 01.445-.758l8.61-8.61zm1.414 1.06a.25.25 0 00-.354 0L10.811 3.75l1.439 1.44 1.263-1.263a.25.25 0 000-.354l-1.086-1.086zM11.189 6.25L9.75 4.81l-6.286 6.287a.25.25 0 00-.064.108l-.558 1.953 1.953-.558a.249.249 0 00.108-.064l6.286-6.286z"/>
                      </svg>
                    </button>
                    <button
                      class="section-view__action-btn section-view__action-btn--delete"
                      title="Delete question"
                      @click="handleDeleteQuestion(question.id)"
                    >
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M11 1.75V3h2.25a.75.75 0 010 1.5H2.75a.75.75 0 010-1.5H5V1.75C5 .784 5.784 0 6.75 0h2.5C10.216 0 11 .784 11 1.75zM4.496 6.675a.75.75 0 10-1.492.15l.66 6.6A1.75 1.75 0 005.405 15h5.19c.9 0 1.652-.681 1.741-1.576l.66-6.6a.75.75 0 00-1.492-.149l-.66 6.6a.25.25 0 01-.249.225h-5.19a.25.25 0 01-.249-.225l-.66-6.6zM6.5 1.75V3h3V1.75a.25.25 0 00-.25-.25h-2.5a.25.25 0 00-.25.25z"/>
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

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
          Edit Section Details
        </button>
        <button class="section-view__footer-btn section-view__footer-btn--danger" @click="handleDeleteSection">
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
  const sorted = [...questions.value].sort((a, b) => (a.order || 0) - (b.order || 0));
  
  // Debug: Log question data to check fields
  if (sorted.length > 0) {
    console.log('📊 Section questions:', sorted.map(q => ({
      id: q.id,
      text: q.question_text?.substring(0, 30),
      is_required: q.is_required,
      depends_on_question: q.depends_on_question,
      depends_on_value: q.depends_on_value
    })));
  }
  
  return sorted;
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
    year: 'Year'
  };
  return typeMap[type] || type;
}

function getConditionalTooltip(question) {
  if (!question.depends_on_question) return '';
  
  const dependsOnQ = questions.value.find(q => q.id === question.depends_on_question);
  const questionText = dependsOnQ ? dependsOnQ.question_text : 'Unknown question';
  
  return `Shows only if "${questionText}" = ${question.depends_on_value}`;
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
  width: 1100px;
  max-width: 95vw;
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
  background: #F57C00;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s ease;
}

.section-view__add-question-btn:hover {
  background: #dd6b20;
}

.section-view__table-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: #f9fafb;
}

.section-view__table-wrapper {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  background: white;
}

.section-view__table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.section-view__table-head {
  background: linear-gradient(to right, #f8fafc, #f1f5f9);
}

.section-view__table-body {
  background: white;
}

.section-view__table-th {
  text-align: left;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  font-weight: 600;
  color: #475569;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  position: sticky;
  top: 0;
  z-index: 10;
  background: inherit;
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
  transition: background 0.15s ease;
  border-bottom: 1px solid #f1f5f9;
}

.section-view__table-row:hover {
  background: #f8fafc;
}

.section-view__table-td {
  padding: 16px 20px;
  color: #334155;
  vertical-align: middle;
}

.section-view__table-td--drag {
  width: 40px;
  padding-left: 20px;
  padding-right: 8px;
}

.section-view__table-td--order {
  width: 80px;
}

.section-view__table-td--question {
  max-width: 400px;
}

.section-view__table-td--center {
  text-align: center;
  width: 120px;
}

.section-view__table-td--actions {
  text-align: center;
  width: 100px;
}

.section-view__drag-handle {
  color: #cbd5e1;
  cursor: grab;
  display: inline-flex;
  transition: color 0.2s ease;
}

.section-view__drag-handle:hover {
  color: #94a3b8;
}

.section-view__order-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  padding: 4px 10px;
  background: #f1f5f9;
  color: #64748b;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
}

.section-view__question-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.section-view__question-text {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
  line-height: 1.5;
}

.section-view__question-help {
  font-size: 13px;
  color: #64748b;
  line-height: 1.4;
}

.section-view__type-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  background: #ede9fe;
  color: #7c3aed;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.section-view__status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.section-view__status-badge--required {
  background: #fee2e2;
  color: #dc2626;
}

.section-view__status-badge--optional {
  background: #f1f5f9;
  color: #64748b;
}

.section-view__status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.section-view__status-badge--required .section-view__status-dot {
  background: #dc2626;
}

.section-view__status-badge--optional .section-view__status-dot {
  background: #94a3b8;
}

.section-view__text-muted {
  color: #cbd5e1;
  font-size: 14px;
}

.section-view__indicator {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.section-view__conditional-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.section-view__conditional-text {
  font-size: 11px;
  color: #92400e;
  font-weight: 600;
}

.section-view__conditional-value {
  padding: 2px 6px;
  background: #fef3c7;
  border-radius: 4px;
}

.section-view__indicator--conditional {
  color: #f59e0b;
  background: #fef3c7;
}

.section-view__indicator--branching {
  color: #8b5cf6;
  background: #ede9fe;
}

.section-view__actions {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.section-view__action-btn {
  padding: 6px;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: #94a3b8;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.section-view__action-btn--edit:hover {
  background: #ffedd5;
  color: #c2410c;
}

.section-view__action-btn--delete:hover {
  background: #ffedd5;
  color: #c2410c;
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
  background: #dd6b20;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}

.section-view__empty-btn:hover {
  background: #F57C00;
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
